"""
Audio Recorder Module
Handles streaming audio capture, transmission detection, and file saving
"""

import os
import json
import time
import threading
import requests
import numpy as np
from datetime import datetime
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import io
import logging
import subprocess
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioRecorder:
    def __init__(self, config_file='radio_channels.json', output_dir='audio_files'):
        self.config_file = config_file
        self.output_dir = output_dir
        self.channels = {}
        self.recording_threads = {}
        self.is_recording = {}
        
        # Failure tracking for better error handling
        self.channel_failures = {}  # Track consecutive failures per channel
        self.channel_last_success = {}  # Track last successful connection per channel
        self.max_consecutive_failures = 5  # Disable channel after this many failures
        
        # Audio processing parameters - optimized for rapid-fire radio conversations
        self.chunk_duration = 30  # seconds - buffer size for processing  
        self.silence_threshold = -45  # dB (balanced - catch voice but avoid background noise)
        self.min_transmission_length = 800  # ms (minimum 0.8 seconds - catch quick acknowledgments)
        self.max_transmission_length = 20000  # ms (maximum 20 seconds - break up long conversations)
        self.silence_gap = 600  # ms between transmissions (shorter gap to catch rapid exchanges)
        
        self.load_channels()
        self.ensure_output_directory()
        
        # Clean up old temporary files on startup
        self.cleanup_temp_files(max_age_hours=1)  # Remove temp files older than 1 hour
        
        # Start background cleanup scheduler
        self.start_cleanup_scheduler()
    
    def load_channels(self):
        """Load radio channels from JSON configuration"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            for channel in config.get('channels', []):
                channel_name = channel.get('name', '')
                channel_id = self.sanitize_name(channel_name)
                if channel_id and channel.get('url'):
                    self.channels[channel_id] = {
                        'name': channel_name,
                        'url': channel.get('url'),
                        'group': channel.get('group', 'Unknown'),
                        'enabled': channel.get('enabled', True),
                        'noise_gate': channel.get('noiseGate', {}),
                        'gain': channel.get('gain', 1.0)
                    }
            
            logger.info(f"Loaded {len(self.channels)} channels from configuration")
            
        except Exception as e:
            logger.error(f"Error loading channels: {e}")
            self.channels = {}
    
    def sanitize_name(self, name):
        """Sanitize channel name for use as filename"""
        if not name:
            return ""
        # Remove invalid filename characters and replace spaces with underscores
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        # Replace spaces with underscores
        name = name.replace(' ', '_')
        return name.strip()
    
    def ensure_output_directory(self):
        """Ensure output directory exists"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Create subdirectories for each channel
        for channel_id in self.channels:
            channel_dir = os.path.join(self.output_dir, channel_id)
            if not os.path.exists(channel_dir):
                os.makedirs(channel_dir)
    
    def get_timestamp(self):
        """Generate timestamp for filename"""
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
    
    def save_transmission_ffmpeg(self, source_file, start_ms, end_ms, channel_id, timestamp):
        """Save transmission using ffmpeg stream copy - NO re-encoding"""
        try:
            filename = f"{timestamp}_{channel_id}.mp3"
            filepath = os.path.join(self.output_dir, channel_id, filename)
            
            # Convert milliseconds to seconds for ffmpeg
            start_sec = start_ms / 1000.0
            duration_sec = (end_ms - start_ms) / 1000.0
            
            # Use ffmpeg to extract segment without re-encoding
            cmd = [
                'ffmpeg', '-y',  # -y to overwrite existing files
                '-i', source_file,  # Input file
                '-ss', str(start_sec),  # Start time
                '-t', str(duration_sec),  # Duration
                '-c', 'copy',  # Stream copy - NO re-encoding
                '-avoid_negative_ts', 'make_zero',
                filepath
            ]
            
            logger.info(f"Extracting transmission with ffmpeg: {start_ms}-{end_ms}ms ({duration_sec:.2f}s)")
            
            # Run ffmpeg command
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Check if file was created and has content
                if os.path.exists(filepath) and os.path.getsize(filepath) > 1024:
                    logger.info(f"Successfully extracted transmission: {filepath}")
                    
                    # Create metadata
                    self.create_metadata_file(filepath, timestamp, channel_id, duration_sec * 1000)
                    
                    # Clean up any related temp files immediately after successful extraction
                    try:
                        self.cleanup_related_temp_files(source_file, channel_id)
                    except Exception as cleanup_error:
                        logger.warning(f"Failed to cleanup related temp files: {cleanup_error}")
                    
                    return filepath
                else:
                    logger.warning(f"ffmpeg extraction created empty/small file: {filepath}")
                    return None
            else:
                logger.error(f"ffmpeg extraction failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting transmission with ffmpeg: {e}")
            return None

    def create_metadata_file(self, audio_filepath, timestamp, channel_id, duration_ms):
        """Create metadata file for a transmission"""
        try:
            metadata_filepath = audio_filepath.replace('.mp3', '_metadata.json')
            
            metadata = {
                'timestamp': timestamp,
                'channel': channel_id,
                'channel_name': self.channels.get(channel_id, {}).get('name', channel_id),
                'duration_ms': int(duration_ms),
                'file_size': os.path.getsize(audio_filepath),
                'recorded_at': datetime.now().isoformat(),
                'extraction_method': 'ffmpeg_stream_copy'
            }
            
            with open(metadata_filepath, 'w') as f:
                json.dump(metadata, f, indent=2)
                
            logger.info(f"Created metadata: {metadata_filepath}")
            
        except Exception as e:
            logger.warning(f"Failed to create metadata file: {e}")

    def cleanup_related_temp_files(self, source_file, channel_id):
        """Clean up temp files related to a specific source file"""
        import glob
        
        try:
            # If source_file is a temp file, try to remove it
            if os.path.basename(source_file).startswith('temp_'):
                if os.path.exists(source_file):
                    os.unlink(source_file)
                    logger.info(f"Cleaned up source temp file: {source_file}")
            
            # Also clean up any old temp files for this channel (older than 10 minutes)
            from datetime import datetime, timedelta
            cutoff_time = datetime.now() - timedelta(minutes=10)
            
            channel_dir = os.path.join(self.output_dir, channel_id)
            temp_pattern = os.path.join(channel_dir, "temp_*.mp3")
            temp_files = glob.glob(temp_pattern)
            
            for temp_file in temp_files:
                try:
                    file_time = datetime.fromtimestamp(os.path.getmtime(temp_file))
                    if file_time < cutoff_time:
                        os.unlink(temp_file)
                        logger.info(f"Cleaned up old temp file: {temp_file}")
                except Exception as e:
                    logger.warning(f"Error checking/removing temp file {temp_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in cleanup_related_temp_files: {e}")

    def process_complete_segment(self, filepath, channel_id):
        """Process a complete audio segment file for transmissions"""
        try:
            logger.info(f"Processing complete segment for {channel_id}: {filepath}")
            
            # Check if file exists and has content
            if not os.path.exists(filepath):
                logger.warning(f"File does not exist: {filepath}")
                return
            
            file_size = os.path.getsize(filepath)
            logger.info(f"File size: {file_size} bytes")
            
            if file_size < 1024:  # Less than 1KB
                logger.warning(f"File too small to process: {file_size} bytes")
                return
            
            # Load the complete MP3 file
            audio_segment = AudioSegment.from_mp3(filepath)
            logger.info(f"Loaded audio segment: {len(audio_segment)}ms, {audio_segment.frame_rate}Hz, {audio_segment.channels} channels")
            logger.info(f"Audio levels: max_dBFS={audio_segment.max_dBFS:.1f}, rms_dBFS={audio_segment.dBFS:.1f}")
            
            if len(audio_segment) < 1000:  # Less than 1 second
                logger.warning(f"Audio segment too short: {len(audio_segment)}ms")
                return
            
            # Get channel-specific transmission detection settings
            channel_config = self.channels.get(channel_id, {})
            transmission_config = channel_config.get('transmission', {})
            
            # Use channel-specific settings or fall back to defaults
            silence_threshold = transmission_config.get('silence_threshold', self.silence_threshold)
            min_length = transmission_config.get('min_length', self.min_transmission_length)
            max_length = transmission_config.get('max_length', self.max_transmission_length)
            silence_gap = transmission_config.get('silence_gap', self.silence_gap)
            
            # Detect non-silent chunks (transmissions) BEFORE applying noise gate
            # This ensures we detect transmissions based on the original audio
            nonsilent_ranges = detect_nonsilent(
                audio_segment,
                min_silence_len=silence_gap,
                silence_thresh=silence_threshold
            )
            
            logger.info(f"Audio segment: {len(audio_segment)}ms, Non-silent ranges: {len(nonsilent_ranges)} found")
            logger.info(f"Detection settings: silence_thresh={silence_threshold}dB, min_silence_gap={silence_gap}ms")
            logger.info(f"Transmission filters: min={min_length}ms, max={max_length}ms")
            
            # Merge nearby transmissions that might be rapid conversations
            merged_ranges = []
            merge_gap_threshold = 2000  # Merge transmissions less than 2 seconds apart
            
            for start_ms, end_ms in nonsilent_ranges:
                if merged_ranges and (start_ms - merged_ranges[-1][1]) < merge_gap_threshold:
                    # Extend the previous range to include this one
                    merged_ranges[-1] = (merged_ranges[-1][0], end_ms)
                    logger.info(f"Merged transmission: {merged_ranges[-1][0]}-{merged_ranges[-1][1]}ms")
                else:
                    merged_ranges.append((start_ms, end_ms))
            
            logger.info(f"After merging nearby transmissions: {len(merged_ranges)} ranges")
            
            saved_count = 0
            filtered_count = 0
            
            # Process each detected transmission (now with merging)
            for start_ms, end_ms in merged_ranges:
                transmission_length = end_ms - start_ms
                logger.info(f"Transmission detected: {transmission_length}ms (range: {start_ms}-{end_ms})")
                
                # Filter by transmission length (using channel-specific settings)
                if min_length <= transmission_length <= max_length:
                    # Additional validation: check if this segment actually has voice content
                    test_segment = audio_segment[start_ms:end_ms]
                    segment_max_db = test_segment.max_dBFS
                    segment_rms_db = test_segment.dBFS
                    
                    # Dynamic thresholds based on transmission length
                    if transmission_length < 3000:  # Short transmissions (< 3 seconds)
                        # More lenient for quick acknowledgments
                        min_max_db = -45  # Allow quieter short transmissions
                        min_rms_db = -55  # More lenient RMS for brief responses
                    else:  # Longer transmissions
                        # Stricter for longer transmissions to avoid noise
                        min_max_db = -40  # Must have clear peaks
                        min_rms_db = -50  # Good average level
                    
                    if segment_max_db > min_max_db and segment_rms_db > min_rms_db:
                        # Use ffmpeg to extract this transmission without re-encoding
                        timestamp = self.get_timestamp()
                        saved_file = self.save_transmission_ffmpeg(filepath, start_ms, end_ms, channel_id, timestamp)
                        if saved_file:
                            logger.info(f"Saved transmission with ffmpeg: {saved_file} (max: {segment_max_db:.1f}dB, rms: {segment_rms_db:.1f}dB)")
                            saved_count += 1
                        else:
                            logger.warning(f"Failed to save transmission with ffmpeg")
                            filtered_count += 1
                    else:
                        logger.info(f"Transmission filtered out: too quiet (max: {segment_max_db:.1f}dB, rms: {segment_rms_db:.1f}dB)")
                        filtered_count += 1
                else:
                    logger.info(f"Transmission filtered out: {transmission_length}ms (too short/long)")
                    filtered_count += 1
            
            logger.info(f"Segment processing complete: {saved_count} transmissions saved, {filtered_count} filtered out")
            
            # Clean up the temp file after successful processing
            try:
                if os.path.exists(filepath):
                    os.unlink(filepath)
                    logger.info(f"Cleaned up temp file: {filepath}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file {filepath}: {cleanup_error}")
            
        except Exception as e:
            logger.error(f"Error processing complete segment for {channel_id}: {e}")
            # Still try to cleanup temp file even if processing failed
            try:
                if os.path.exists(filepath):
                    os.unlink(filepath)
                    logger.info(f"Cleaned up temp file after error: {filepath}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file after error {filepath}: {cleanup_error}")

    def process_audio_chunk(self, audio_data, channel_id):
        """Legacy method - now unused, kept for compatibility"""
        # This method is no longer used but kept to avoid breaking existing code
        pass
    
    def apply_noise_gate(self, audio_segment, threshold_db):
        """Apply gentle noise gate that preserves speech quality"""
        try:
            # Convert to numpy array for processing
            samples = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
            
            if len(samples) == 0:
                return audio_segment
            
            # Normalize to prevent overflow
            max_val = np.max(np.abs(samples))
            if max_val > 0:
                samples = samples / max_val
            else:
                return audio_segment
            
            # Calculate RMS over small windows for responsive gating
            window_size = 1024  # Small window for quick response
            rms_values = []
            
            for i in range(0, len(samples), window_size):
                window = samples[i:i+window_size]
                if len(window) > 0:
                    rms = np.sqrt(np.mean(window**2))
                    rms_db = 20 * np.log10(rms + 1e-10)
                    rms_values.extend([rms_db] * len(window))
            
            # Trim to match sample length
            rms_values = np.array(rms_values[:len(samples)])
            
            # Create gentle gate - reduce volume instead of cutting completely
            # Signals above (threshold_db - 10) get full volume
            # Signals below threshold_db get 10% volume (not 0%)
            volume_multiplier = np.clip((rms_values - (threshold_db - 10)) / 10, 0.1, 1.0)
            
            # Apply gentle volume reduction
            gated_samples = samples * volume_multiplier
            
            # Restore original scale and convert back
            gated_samples = gated_samples * max_val
            gated_samples = gated_samples.astype(samples.dtype)
            
            return AudioSegment(
                gated_samples.tobytes(),
                frame_rate=audio_segment.frame_rate,
                sample_width=audio_segment.sample_width,
                channels=audio_segment.channels
            )
            
        except Exception as e:
            logger.error(f"Error applying gentle noise gate: {e}")
            return audio_segment  # Return original on error
    
    def _apply_basic_noise_gate(self, audio_segment, threshold_db):
        """Basic noise gate fallback"""
        try:
            # Convert to numpy array for processing
            samples = np.array(audio_segment.get_array_of_samples())
            
            # Calculate RMS for each frame
            frame_size = 1024
            rms_values = []
            
            for i in range(0, len(samples), frame_size):
                frame = samples[i:i+frame_size]
                rms = np.sqrt(np.mean(frame**2)) if len(frame) > 0 else 0
                rms_db = 20 * np.log10(rms + 1e-10)  # Avoid log(0)
                rms_values.extend([rms_db] * len(frame))
            
            # Apply gate
            rms_values = np.array(rms_values[:len(samples)])
            gated_samples = np.where(rms_values > threshold_db, samples, samples * 0.1)  # Don't completely mute
            
            # Convert back to AudioSegment
            return AudioSegment(
                gated_samples.tobytes(),
                frame_rate=audio_segment.frame_rate,
                sample_width=audio_segment.sample_width,
                channels=audio_segment.channels
            )
            
        except Exception as e:
            logger.error(f"Error applying basic noise gate: {e}")
            return audio_segment
    
    def stream_recorder(self, channel_id):
        """Stream and record audio from a radio channel using continuous segments"""
        channel = self.channels[channel_id]
        logger.info(f"Starting stream for channel: {channel['name']} ({channel['url']})")
        
        while self.is_recording.get(channel_id, False):
            temp_filepath = None
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(
                    channel['url'], 
                    stream=True, 
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                
                # Log content type for debugging
                content_type = response.headers.get('content-type', 'unknown')
                logger.info(f"Stream content type for {channel_id}: {content_type}")
                
                # Create temporary file for this recording segment
                timestamp = self.get_timestamp()
                temp_filename = f"temp_{timestamp}_{channel_id}.mp3"
                temp_filepath = os.path.join(self.output_dir, channel_id, temp_filename)
                logger.info(f"Creating temp file: {temp_filepath}")
                
                # Record for 15 seconds into temp file (faster processing for rapid conversations)
                segment_duration = 15  # seconds - reduced for quicker detection of rapid-fire exchanges
                start_time = time.time()
                bytes_written = 0
                
                with open(temp_filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if not self.is_recording.get(channel_id, False):
                            logger.info(f"Recording stopped for {channel_id}")
                            break
                        
                        if chunk:
                            f.write(chunk)
                            bytes_written += len(chunk)
                        
                        # Check if we've recorded for the target duration
                        if time.time() - start_time >= segment_duration:
                            break
                
                logger.info(f"Finished recording segment for {channel_id}: {bytes_written} bytes written in {time.time() - start_time:.1f}s")
                
                # Always process the complete file for transmissions (regardless of recording status)
                try:
                    logger.info(f"Processing complete segment for {channel_id}: {temp_filepath}")
                    self.process_complete_segment(temp_filepath, channel_id)
                    # Reset failure counter only on successful processing
                    self.channel_failures[channel_id] = 0
                    self.channel_last_success[channel_id] = time.time()
                    logger.info(f"Successfully processed segment for {channel_id}")
                except Exception as processing_error:
                    logger.error(f"Error processing segment for {channel_id}: {processing_error}")
                    # Don't reset failure counter if processing fails
                
            except requests.exceptions.RequestException as e:
                # Track failures for this channel
                self.channel_failures[channel_id] = self.channel_failures.get(channel_id, 0) + 1
                failure_count = self.channel_failures[channel_id]
                
                # Different handling based on HTTP status code
                status_code = getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
                
                if status_code == 404:
                    logger.warning(f"Stream not available for {channel_id} (404): {channel['url']}")
                    if failure_count >= 3:
                        logger.warning(f"Channel {channel_id} consistently returning 404, reducing retry frequency")
                elif status_code in [503, 502, 500]:
                    logger.warning(f"Server error for {channel_id} ({status_code}): {e}")
                else:
                    logger.warning(f"Connection error for {channel_id}: {e}")
                
                # Implement exponential backoff with maximum wait time
                if failure_count >= self.max_consecutive_failures:
                    wait_time = min(300, 30 * (2 ** min(failure_count - self.max_consecutive_failures, 4)))  # Max 5 minutes
                    logger.warning(f"Channel {channel_id} has {failure_count} consecutive failures, waiting {wait_time} seconds before retry")
                else:
                    wait_time = min(60, 5 * failure_count)  # Progressive backoff up to 1 minute
                
                if self.is_recording.get(channel_id, False):
                    logger.info(f"Retrying connection for {channel_id} in {wait_time} seconds...")
                    time.sleep(wait_time)
            
            except Exception as e:
                # Track failures for unexpected errors too
                self.channel_failures[channel_id] = self.channel_failures.get(channel_id, 0) + 1
                failure_count = self.channel_failures[channel_id]
                
                logger.error(f"Unexpected error in stream recorder for {channel_id}: {e}")
                
                # Use exponential backoff for unexpected errors too
                wait_time = min(60, 5 * failure_count)
                time.sleep(wait_time)
            
            finally:
                # Always clean up temp file if it exists
                if temp_filepath and os.path.exists(temp_filepath):
                    try:
                        os.unlink(temp_filepath)
                        logger.debug(f"Cleaned up temp file: {temp_filepath}")
                    except Exception as cleanup_error:
                        logger.error(f"Error cleaning up temp file {temp_filepath}: {cleanup_error}")
        
        logger.info(f"Stopped recording for channel: {channel['name']}")
    
    def start_recording(self, channel_ids=None):
        """Start recording for specified channels or all enabled channels"""
        if channel_ids is None:
            channel_ids = [cid for cid, ch in self.channels.items() if ch.get('enabled', True)]
        
        for channel_id in channel_ids:
            if channel_id in self.channels and not self.is_recording.get(channel_id, False):
                self.is_recording[channel_id] = True
                thread = threading.Thread(
                    target=self.stream_recorder,
                    args=(channel_id,),
                    daemon=True
                )
                thread.start()
                self.recording_threads[channel_id] = thread
                logger.info(f"Started recording thread for: {channel_id}")
    
    def stop_recording(self, channel_ids=None):
        """Stop recording for specified channels or all channels"""
        if channel_ids is None:
            channel_ids = list(self.is_recording.keys())
        
        for channel_id in channel_ids:
            if self.is_recording.get(channel_id, False):
                self.is_recording[channel_id] = False
                logger.info(f"Stopping recording for: {channel_id}")
        
        # Wait for threads to finish
        for channel_id in channel_ids:
            if channel_id in self.recording_threads:
                self.recording_threads[channel_id].join(timeout=5)
                del self.recording_threads[channel_id]
    
    def get_status(self):
        """Get current recording status"""
        status = {}
        for channel_id, channel in self.channels.items():
            failures = self.channel_failures.get(channel_id, 0)
            last_success = self.channel_last_success.get(channel_id)
            
            # Determine health status
            if failures == 0:
                health = "healthy"
            elif failures < 3:
                health = "warning"
            elif failures < self.max_consecutive_failures:
                health = "degraded"
            else:
                health = "failed"
            
            status[channel_id] = {
                'name': channel['name'],
                'url': channel['url'],
                'enabled': channel.get('enabled', True),
                'recording': self.is_recording.get(channel_id, False),
                'group': channel.get('group', 'Unknown'),
                'health': health,
                'consecutive_failures': failures,
                'last_success': last_success
            }
        return status
    
    def test_channel_connectivity(self, channel_id=None):
        """Test connectivity to one or all channels"""
        import requests
        
        results = {}
        channels_to_test = [channel_id] if channel_id else self.channels.keys()
        
        for cid in channels_to_test:
            if cid not in self.channels:
                continue
                
            channel = self.channels[cid]
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.head(channel['url'], headers=headers, timeout=10)
                
                results[cid] = {
                    'name': channel['name'],
                    'url': channel['url'],
                    'status_code': response.status_code,
                    'accessible': response.status_code == 200,
                    'content_type': response.headers.get('content-type', 'unknown'),
                    'error': None
                }
                
            except Exception as e:
                results[cid] = {
                    'name': channel['name'],
                    'url': channel['url'],
                    'status_code': None,
                    'accessible': False,
                    'content_type': None,
                    'error': str(e)
                }
        
        return results
    
    def get_recordings(self, channel_id=None, limit=100, start_date=None, end_date=None, search_text=None):
        """Get list of recorded transmissions with optional filtering"""
        from datetime import datetime
        
        recordings = []
        
        channels_to_check = [channel_id] if channel_id else self.channels.keys()
        
        for cid in channels_to_check:
            # Filter by search text if provided
            if search_text:
                channel_name = self.channels.get(cid, {}).get('name', '').lower()
                if search_text.lower() not in channel_name:
                    continue
                    
            channel_dir = os.path.join(self.output_dir, cid)
            if os.path.exists(channel_dir):
                for filename in os.listdir(channel_dir):
                    # Skip temporary files
                    if filename.startswith('temp_') or not filename.endswith('.mp3'):
                        continue
                        
                    if filename.endswith('.mp3'):
                        filepath = os.path.join(channel_dir, filename)
                        metadata_file = filepath.replace('.mp3', '_metadata.json')
                        
                        # Extract timestamp from filename (YYYYMMDD_HHMMSS_*)
                        parts = filename.split('_')
                        if len(parts) >= 2:
                            # YYYYMMDD_HHMMSS_* format
                            timestamp_str = parts[0] + '_' + parts[1]
                        else:
                            continue  # Skip files with unexpected naming format
                        
                        # Filter by date range if provided
                        if start_date or end_date:
                            try:
                                file_date = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                                if start_date:
                                    # Handle both date-only and datetime formats
                                    if 'T' in start_date:
                                        # ISO datetime format: 2025-08-26T14:30
                                        start_dt = datetime.fromisoformat(start_date)
                                    else:
                                        # Date-only format: 2025-08-26 (assume start of day)
                                        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                                    if file_date < start_dt:
                                        continue
                                if end_date:
                                    # Handle both date-only and datetime formats
                                    if 'T' in end_date:
                                        # ISO datetime format: 2025-08-26T23:59
                                        end_dt = datetime.fromisoformat(end_date)
                                    else:
                                        # Date-only format: 2025-08-26 (assume end of day)
                                        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                                        end_dt = end_dt.replace(hour=23, minute=59, second=59)
                                    if file_date > end_dt:
                                        continue
                            except ValueError:
                                continue  # Skip files with invalid timestamps
                        
                        recording_info = {
                            'channel_id': cid,
                            'channel_name': self.channels.get(cid, {}).get('name', cid),
                            'filename': filename,
                            'filepath': filepath,
                            'timestamp': timestamp_str,
                            'size': os.path.getsize(filepath)
                        }
                        
                        # Load metadata if available
                        if os.path.exists(metadata_file):
                            try:
                                with open(metadata_file, 'r') as f:
                                    metadata = json.load(f)
                                recording_info.update(metadata)
                            except:
                                pass
                        
                        recordings.append(recording_info)
        
        # Sort by timestamp (newest first) and limit results
        recordings.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return recordings[:limit]
    
    def get_channel_recordings(self, channel_id, limit=50, offset=0, start_date=None, end_date=None):
        """Get paginated recordings for a specific channel"""
        all_recordings = self.get_recordings(
            channel_id=channel_id, 
            limit=1000,  # Get more for pagination
            start_date=start_date, 
            end_date=end_date
        )
        
        total = len(all_recordings)
        recordings = all_recordings[offset:offset + limit]
        
        return {
            'recordings': recordings,
            'total': total,
            'offset': offset,
            'limit': limit,
            'has_more': offset + limit < total
        }

    def cleanup_temp_files(self, max_age_hours=24):
        """Clean up temporary files older than specified hours"""
        import glob
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        removed_count = 0
        
        try:
            # Find all temp files in all channel directories
            temp_pattern = os.path.join(self.output_dir, "*", "temp_*.mp3")
            temp_files = glob.glob(temp_pattern)
            
            for temp_file in temp_files:
                try:
                    # Get file modification time
                    file_time = datetime.fromtimestamp(os.path.getmtime(temp_file))
                    
                    # Remove if older than cutoff
                    if file_time < cutoff_time:
                        os.unlink(temp_file)
                        removed_count += 1
                        logger.info(f"Removed old temp file: {temp_file}")
                        
                except Exception as e:
                    logger.error(f"Error removing temp file {temp_file}: {e}")
            
            if removed_count > 0:
                logger.info(f"Cleanup complete: removed {removed_count} temporary files")
            else:
                logger.debug("No temporary files needed cleanup")
                
        except Exception as e:
            logger.error(f"Error during temp file cleanup: {e}")
            
        return removed_count

    def cleanup_all_temp_files(self):
        """Remove all temporary files immediately"""
        import glob
        
        removed_count = 0
        
        try:
            # Find all temp files in all channel directories
            temp_pattern = os.path.join(self.output_dir, "*", "temp_*.mp3")
            temp_files = glob.glob(temp_pattern)
            
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                    removed_count += 1
                    logger.info(f"Removed temp file: {temp_file}")
                except Exception as e:
                    logger.error(f"Error removing temp file {temp_file}: {e}")
            
            logger.info(f"Cleanup complete: removed {removed_count} temporary files")
                
        except Exception as e:
            logger.error(f"Error during temp file cleanup: {e}")
            
        return removed_count

    def start_cleanup_scheduler(self):
        """Start background scheduler for automatic temp file cleanup"""
        import threading
        import time
        
        def cleanup_worker():
            while True:
                try:
                    # Run cleanup every 30 minutes
                    time.sleep(30 * 60)  # 30 minutes
                    
                    # Remove temp files older than 2 hours
                    removed_count = self.cleanup_temp_files(max_age_hours=2)
                    
                    # Also clean up orphaned temp files (those without corresponding final files)
                    orphaned_count = self.cleanup_orphaned_temp_files()
                    
                    if removed_count > 0 or orphaned_count > 0:
                        logger.info(f"Scheduled cleanup: removed {removed_count} old temp files, {orphaned_count} orphaned temp files")
                    
                except Exception as e:
                    logger.error(f"Error in background cleanup: {e}")
        
        # Start the cleanup thread as a daemon so it stops when the main program stops
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.info("Background temp file cleanup scheduler started")

    def cleanup_orphaned_temp_files(self):
        """Remove temp files that don't have corresponding final recordings"""
        import glob
        from datetime import datetime, timedelta
        
        removed_count = 0
        
        try:
            # Find all temp files in all channel directories
            temp_pattern = os.path.join(self.output_dir, "*", "temp_*.mp3")
            temp_files = glob.glob(temp_pattern)
            
            for temp_file in temp_files:
                try:
                    # Extract timestamp from temp filename to check for final file
                    filename = os.path.basename(temp_file)
                    if filename.startswith('temp_'):
                        # Convert temp_YYYYMMDD_HHMMSS_* to YYYYMMDD_HHMMSS_*
                        final_filename = filename[5:]  # Remove 'temp_' prefix
                        channel_dir = os.path.dirname(temp_file)
                        final_file = os.path.join(channel_dir, final_filename)
                        
                        # If final file exists, temp file is orphaned
                        if os.path.exists(final_file):
                            # Also check if temp file is older than 5 minutes (should be processed by now)
                            file_time = datetime.fromtimestamp(os.path.getmtime(temp_file))
                            cutoff_time = datetime.now() - timedelta(minutes=5)
                            
                            if file_time < cutoff_time:
                                os.unlink(temp_file)
                                removed_count += 1
                                logger.info(f"Removed orphaned temp file: {temp_file}")
                        
                        # Also remove very old temp files that are definitely stale
                        else:
                            file_time = datetime.fromtimestamp(os.path.getmtime(temp_file))
                            cutoff_time = datetime.now() - timedelta(hours=1)
                            
                            if file_time < cutoff_time:
                                os.unlink(temp_file)
                                removed_count += 1
                                logger.info(f"Removed stale temp file: {temp_file}")
                        
                except Exception as e:
                    logger.error(f"Error checking temp file {temp_file}: {e}")
            
            if removed_count > 0:
                logger.info(f"Orphaned cleanup complete: removed {removed_count} orphaned/stale temp files")
                
        except Exception as e:
            logger.error(f"Error during orphaned temp file cleanup: {e}")
            
        return removed_count

    def cleanup_temp_files_for_channel(self, channel_id):
        """Clean up temp files for a specific channel immediately"""
        import glob
        
        removed_count = 0
        
        try:
            channel_dir = os.path.join(self.output_dir, channel_id)
            temp_pattern = os.path.join(channel_dir, "temp_*.mp3")
            temp_files = glob.glob(temp_pattern)
            
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                    removed_count += 1
                    logger.debug(f"Removed temp file for {channel_id}: {temp_file}")
                except Exception as e:
                    logger.error(f"Error removing temp file {temp_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Error during channel temp file cleanup: {e}")
            
        return removed_count
