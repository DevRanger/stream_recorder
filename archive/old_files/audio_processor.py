"""
Advanced Audio Processing Pipeline
Implements professional VAD, filtering, and transmission detection
"""

import numpy as np
import soundfile as sf
from scipy import signal
from scipy.signal import butter, filtfilt, resample
import io
import logging
from pydub import AudioSegment
from typing import Tuple, List, Optional, Dict, Any
import time
import threading

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Advanced audio processing with VAD, filtering, and transmission detection"""
    
    def __init__(self, config=None, channel_config=None):
        """Initialize the audio processor with configuration"""
        self.config = config or {}
        self.channel_config = channel_config or {}
        
        # Core processing parameters
        self.target_sample_rate = self.config.get('target_sample_rate', 16000)  # 16kHz for VAD
        self.frame_duration_ms = self.config.get('frame_duration_ms', 20)  # 20ms frames
        self.frame_size = int(self.target_sample_rate * self.frame_duration_ms / 1000)
        
        # Filtering configuration
        self.enable_filtering = self.config.get('enable_filtering', True)
        self.highpass_freq = self.config.get('highpass_freq', 200)  # 200Hz highpass
        self.lowpass_freq = self.config.get('lowpass_freq', 4000)   # 4kHz lowpass
        
        # Denoise and AGC configuration
        self.enable_denoise = self.config.get('enable_denoise', False)  # Disabled by default
        self.enable_agc = self.config.get('enable_agc', True)          # Enabled by default
        self.agc_target_level = self.config.get('agc_target_level', -20)  # Target -20dB
        
        # VAD configuration - use channel-specific settings if available
        vad_config = self.channel_config.get('vad', {})
        
        self.vad_aggressiveness = self.config.get('vad_aggressiveness', 2)  # 0-3, 2 is moderate
        self.speech_frames_to_start = vad_config.get('speech_frames_to_start', 
                                                    self.config.get('speech_frames_to_start', 7))  # Default 7 frames (140ms)
        self.hang_time_ms = vad_config.get('hang_time_ms', 
                                         self.config.get('hang_time_ms', 400))  # Default 400ms hang time
        self.preroll_ms = self.config.get('preroll_ms', 250)      # 250ms preroll buffer
        
        # Metrics collection for auto-tuner
        self.metrics_lock = threading.Lock()
        self.metrics = {
            'frames_processed': 0,
            'speech_frames': 0,
            'energy_values': [],
            'zcr_values': [],
            'transmissions_started': 0,
            'transmissions_completed': 0,
            'transmissions_discarded': 0,
            'transmission_durations': [],
            'false_positives': 0,  # Short discarded transmissions
            'last_reset': time.time(),
            'energy_threshold': 0,  # Current threshold
            'zcr_min': 0,           # Current threshold
            'zcr_max': 0            # Current threshold
        }
        
        # VAD thresholds - channel-specific
        self.energy_threshold = vad_config.get('energy_threshold', 8e-6)  # Default stricter threshold
        self.zcr_min = vad_config.get('zcr_min', 0.08)  # Default ZCR minimum
        self.zcr_max = vad_config.get('zcr_max', 0.32)  # Default ZCR maximum (tighter)
        
        # Transmission length limits - channel-specific
        self.min_transmission_ms = vad_config.get('min_transmission_ms', 
                                                self.config.get('min_transmission_ms', 2000))  # Default 2.0s minimum
        self.max_transmission_ms = vad_config.get('max_transmission_ms', 
                                                self.config.get('max_transmission_ms', 30000)) # Default 30s maximum
        
        # Internal state
        self.preroll_buffer = []
        self.current_transmission = None
        self.speech_frame_count = 0
        self.hang_time_frames = int(self.hang_time_ms / self.frame_duration_ms)
        self.silence_frame_count = 0
        self.is_in_transmission = False
        
        logger.info(f"AudioProcessor initialized: {self.target_sample_rate}Hz, {self.frame_duration_ms}ms frames")
        logger.info(f"Filtering: {'enabled' if self.enable_filtering else 'disabled'}")
        logger.info(f"Denoise: {'enabled' if self.enable_denoise else 'disabled'}")
        logger.info(f"AGC: {'enabled' if self.enable_agc else 'disabled'}")
    
    def decode_mp3_to_pcm(self, mp3_data: bytes) -> Tuple[np.ndarray, int]:
        """Decode MP3 to PCM in memory, downmix to mono"""
        try:
            # Use pydub to decode MP3
            audio_segment = AudioSegment.from_file(io.BytesIO(mp3_data), format="mp3")
            
            # Convert to mono
            if audio_segment.channels > 1:
                audio_segment = audio_segment.set_channels(1)
            
            # Convert to numpy array
            samples = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
            
            # Normalize to [-1, 1] range
            if audio_segment.sample_width == 2:  # 16-bit
                samples = samples / 32768.0
            elif audio_segment.sample_width == 4:  # 32-bit
                samples = samples / 2147483648.0
            else:  # 8-bit or other
                samples = samples / (2**(audio_segment.sample_width * 8 - 1))
            
            original_sample_rate = audio_segment.frame_rate
            
            logger.debug(f"Decoded MP3: {len(samples)} samples at {original_sample_rate}Hz")
            return samples, original_sample_rate
            
        except Exception as e:
            logger.error(f"Failed to decode MP3: {e}")
            return np.array([]), 0
    
    def resample_audio(self, audio: np.ndarray, original_rate: int) -> np.ndarray:
        """Resample audio to target sample rate"""
        if original_rate == self.target_sample_rate:
            return audio
        
        try:
            # Calculate new length
            new_length = int(len(audio) * self.target_sample_rate / original_rate)
            resampled = resample(audio, new_length)
            
            logger.debug(f"Resampled from {original_rate}Hz to {self.target_sample_rate}Hz")
            return resampled
            
        except Exception as e:
            logger.error(f"Failed to resample audio: {e}")
            return audio
    
    def apply_filters(self, audio: np.ndarray) -> np.ndarray:
        """Apply highpass and lowpass filters"""
        if not self.enable_filtering or len(audio) < 100:
            return audio
        
        try:
            nyquist = self.target_sample_rate / 2
            
            # Design highpass filter (remove hum and CTCSS)
            if self.highpass_freq > 0:
                high_normalized = self.highpass_freq / nyquist
                if high_normalized < 0.99:  # Valid frequency range
                    b_high, a_high = butter(2, high_normalized, btype='high')
                    audio = filtfilt(b_high, a_high, audio)
            
            # Design lowpass filter (speech band)
            if self.lowpass_freq > 0:
                low_normalized = self.lowpass_freq / nyquist
                if low_normalized < 0.99:  # Valid frequency range
                    b_low, a_low = butter(2, low_normalized, btype='low')
                    audio = filtfilt(b_low, a_low, audio)
            
            logger.debug(f"Applied filters: HP={self.highpass_freq}Hz, LP={self.lowpass_freq}Hz")
            return audio
            
        except Exception as e:
            logger.error(f"Failed to apply filters: {e}")
            return audio
    
    def apply_denoise(self, audio: np.ndarray) -> np.ndarray:
        """Apply simple spectral gate denoising"""
        if not self.enable_denoise or len(audio) < 1000:
            return audio
        
        try:
            # Simple spectral gate implementation
            # This is a basic implementation - for production, consider RNNoise
            
            # Calculate noise floor from first 100ms (assumed to be silence/noise)
            noise_samples = min(int(0.1 * self.target_sample_rate), len(audio) // 4)
            noise_floor = np.std(audio[:noise_samples]) * 2.0  # Conservative noise threshold
            
            # Apply gentle gate
            gate_ratio = 0.1  # Reduce noise by 90%
            mask = np.abs(audio) > noise_floor
            
            # Smooth the mask to avoid artifacts
            kernel_size = int(self.target_sample_rate * 0.005)  # 5ms smoothing
            if kernel_size > 1:
                kernel = np.ones(kernel_size) / kernel_size
                mask = np.convolve(mask.astype(float), kernel, mode='same') > 0.5
            
            # Apply gate
            gated_audio = np.where(mask, audio, audio * gate_ratio)
            
            logger.debug(f"Applied denoise: noise_floor={noise_floor:.6f}")
            return gated_audio
            
        except Exception as e:
            logger.error(f"Failed to apply denoise: {e}")
            return audio
    
    def apply_agc(self, audio: np.ndarray) -> np.ndarray:
        """Apply mild Automatic Gain Control"""
        if not self.enable_agc or len(audio) < 100:
            return audio
        
        try:
            # Calculate RMS level
            rms = np.sqrt(np.mean(audio**2))
            
            if rms > 1e-6:  # Avoid division by zero
                # Target level in linear scale
                target_linear = 10**(self.agc_target_level / 20.0)
                
                # Calculate gain needed
                gain = target_linear / rms
                
                # Limit gain to reasonable range (avoid extreme amplification)
                gain = np.clip(gain, 0.1, 10.0)
                
                # Apply gain with soft limiting
                gained_audio = audio * gain
                
                # Soft limiting to prevent clipping
                gained_audio = np.tanh(gained_audio * 0.9) / 0.9
                
                logger.debug(f"Applied AGC: gain={gain:.2f}, rms={rms:.6f}")
                return gained_audio
            
            return audio
            
        except Exception as e:
            logger.error(f"Failed to apply AGC: {e}")
            return audio
    
    def simple_vad(self, frame: np.ndarray) -> bool:
        """Simple energy-based VAD (fallback when WebRTC VAD is not available)"""
        try:
            # Calculate energy metrics
            energy = np.sum(frame**2)
            zero_crossing_rate = np.sum(np.abs(np.diff(np.sign(frame)))) / len(frame)
            
            # Use channel-specific VAD thresholds
            has_energy = energy > self.energy_threshold
            has_speech_zcr = self.zcr_min < zero_crossing_rate < self.zcr_max
            
            is_speech = has_energy and has_speech_zcr
            
            # Collect metrics for auto-tuner
            with self.metrics_lock:
                self.metrics['frames_processed'] += 1
                if is_speech:
                    self.metrics['speech_frames'] += 1
                
                # Sample energy and ZCR values (keep last 1000 for memory efficiency)
                self.metrics['energy_values'].append(energy)
                self.metrics['zcr_values'].append(zero_crossing_rate)
                if len(self.metrics['energy_values']) > 1000:
                    self.metrics['energy_values'].pop(0)
                if len(self.metrics['zcr_values']) > 1000:
                    self.metrics['zcr_values'].pop(0)
                
                # Update current thresholds for reporting
                self.metrics['energy_threshold'] = self.energy_threshold
                self.metrics['zcr_min'] = self.zcr_min
                self.metrics['zcr_max'] = self.zcr_max
            
            logger.debug(f"Channel VAD: energy={energy:.2e} (>{self.energy_threshold:.2e}), "
                        f"zcr={zero_crossing_rate:.3f} ({self.zcr_min}-{self.zcr_max}), speech={is_speech}")
            return is_speech
            
        except Exception as e:
            logger.error(f"VAD error: {e}")
            return False
    
    def process_frame(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """Process a single audio frame and return completed transmission if any"""
        try:
            # Run VAD on the frame
            is_speech = self.simple_vad(frame)
            
            if is_speech:
                self.speech_frame_count += 1
                self.silence_frame_count = 0
                
                # Check if we should start a new transmission
                if not self.is_in_transmission and self.speech_frame_count >= self.speech_frames_to_start:
                    self.is_in_transmission = True
                    self.current_transmission = []
                    
                    # Collect metrics for auto-tuner
                    with self.metrics_lock:
                        self.metrics['transmissions_started'] += 1
                    
                    # Add preroll buffer to transmission
                    for preroll_frame in self.preroll_buffer:
                        self.current_transmission.extend(preroll_frame)
                    
                    logger.debug("Started new transmission")
                
                # Add current frame to transmission if we're recording
                if self.is_in_transmission:
                    self.current_transmission.extend(frame)
            
            else:  # Not speech
                self.silence_frame_count += 1
                self.speech_frame_count = max(0, self.speech_frame_count - 1)  # Decay speech count
                
                # Add frame to transmission if we're still in hang time
                if self.is_in_transmission:
                    self.current_transmission.extend(frame)
                    
                    # Check if we should end the transmission
                    if self.silence_frame_count >= self.hang_time_frames:
                        transmission_audio = np.array(self.current_transmission)
                        transmission_length_ms = len(transmission_audio) * 1000 / self.target_sample_rate
                        
                        # Check transmission length
                        if self.min_transmission_ms <= transmission_length_ms <= self.max_transmission_ms:
                            logger.info(f"Completed transmission: {transmission_length_ms:.0f}ms")
                            
                            # Collect metrics for auto-tuner
                            with self.metrics_lock:
                                self.metrics['transmissions_completed'] += 1
                                self.metrics['transmission_durations'].append(transmission_length_ms)
                                # Keep last 100 durations for memory efficiency
                                if len(self.metrics['transmission_durations']) > 100:
                                    self.metrics['transmission_durations'].pop(0)
                            
                            # Reset state
                            self.is_in_transmission = False
                            self.current_transmission = None
                            self.speech_frame_count = 0
                            self.silence_frame_count = 0
                            
                            return transmission_audio
                        else:
                            logger.debug(f"Discarded transmission: {transmission_length_ms:.0f}ms (out of range)")
                            
                            # Collect metrics for auto-tuner
                            with self.metrics_lock:
                                self.metrics['transmissions_discarded'] += 1
                                if transmission_length_ms < self.min_transmission_ms:
                                    self.metrics['false_positives'] += 1
                        
                        # Reset state even if transmission was discarded
                        self.is_in_transmission = False
                        self.current_transmission = None
                        self.speech_frame_count = 0
                        self.silence_frame_count = 0
            
            # Maintain preroll buffer
            self.preroll_buffer.append(frame.copy())
            preroll_frames = int(self.preroll_ms / self.frame_duration_ms)
            if len(self.preroll_buffer) > preroll_frames:
                self.preroll_buffer.pop(0)
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return None
    
    def process_mp3_stream(self, mp3_data: bytes) -> List[np.ndarray]:
        """Process MP3 stream data and return list of detected transmissions"""
        try:
            # Decode MP3 to PCM
            audio, original_rate = self.decode_mp3_to_pcm(mp3_data)
            if len(audio) == 0:
                return []
            
            # Resample to target rate
            audio = self.resample_audio(audio, original_rate)
            
            # Apply preprocessing
            if self.enable_filtering:
                audio = self.apply_filters(audio)
            
            if self.enable_denoise:
                audio = self.apply_denoise(audio)
            
            if self.enable_agc:
                audio = self.apply_agc(audio)
            
            # Process in frames
            transmissions = []
            for i in range(0, len(audio) - self.frame_size + 1, self.frame_size):
                frame = audio[i:i + self.frame_size]
                transmission = self.process_frame(frame)
                if transmission is not None:
                    transmissions.append(transmission)
            
            return transmissions
            
        except Exception as e:
            logger.error(f"Error processing MP3 stream: {e}")
            return []
    
    def save_transmission_flac(self, audio: np.ndarray, filepath: str, metadata: dict = None) -> bool:
        """Save transmission as FLAC with metadata"""
        try:
            # Ensure audio is in valid range
            audio = np.clip(audio, -1.0, 1.0)
            
            # Save as FLAC
            sf.write(filepath, audio, self.target_sample_rate, format='FLAC')
            
            # Add metadata if provided (this would require additional metadata handling)
            if metadata:
                logger.debug(f"Metadata: {metadata}")
            
            logger.info(f"Saved FLAC transmission: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save FLAC: {e}")
            return False
    
    def reset_state(self):
        """Reset processor state (useful for new streams)"""
        self.preroll_buffer = []
        self.current_transmission = None
        self.speech_frame_count = 0
        self.silence_frame_count = 0
        self.is_in_transmission = False
        logger.debug("Audio processor state reset")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics for auto-tuner analysis"""
        with self.metrics_lock:
            # Calculate derived metrics
            uptime = time.time() - self.metrics['last_reset']
            speech_ratio = (self.metrics['speech_frames'] / max(1, self.metrics['frames_processed']))
            
            # Calculate energy and ZCR statistics
            energy_stats = {}
            zcr_stats = {}
            
            if self.metrics['energy_values']:
                energy_vals = np.array(self.metrics['energy_values'])
                energy_stats = {
                    'mean': float(np.mean(energy_vals)),
                    'std': float(np.std(energy_vals)),
                    'min': float(np.min(energy_vals)),
                    'max': float(np.max(energy_vals)),
                    'percentile_25': float(np.percentile(energy_vals, 25)),
                    'percentile_75': float(np.percentile(energy_vals, 75)),
                    'percentile_95': float(np.percentile(energy_vals, 95))
                }
            
            if self.metrics['zcr_values']:
                zcr_vals = np.array(self.metrics['zcr_values'])
                zcr_stats = {
                    'mean': float(np.mean(zcr_vals)),
                    'std': float(np.std(zcr_vals)),
                    'min': float(np.min(zcr_vals)),
                    'max': float(np.max(zcr_vals)),
                    'percentile_25': float(np.percentile(zcr_vals, 25)),
                    'percentile_75': float(np.percentile(zcr_vals, 75)),
                    'percentile_95': float(np.percentile(zcr_vals, 95))
                }
            
            # Calculate transmission statistics
            avg_duration = 0
            if self.metrics['transmission_durations']:
                avg_duration = np.mean(self.metrics['transmission_durations'])
            
            false_positive_rate = 0
            if self.metrics['transmissions_started'] > 0:
                false_positive_rate = self.metrics['false_positives'] / self.metrics['transmissions_started']
            
            completion_rate = 0
            if self.metrics['transmissions_started'] > 0:
                completion_rate = self.metrics['transmissions_completed'] / self.metrics['transmissions_started']
            
            return {
                'timestamp': time.time(),
                'uptime_seconds': uptime,
                'frames_processed': self.metrics['frames_processed'],
                'speech_frames': self.metrics['speech_frames'],
                'speech_ratio': speech_ratio,
                'transmissions_started': self.metrics['transmissions_started'],
                'transmissions_completed': self.metrics['transmissions_completed'],
                'transmissions_discarded': self.metrics['transmissions_discarded'],
                'false_positives': self.metrics['false_positives'],
                'false_positive_rate': false_positive_rate,
                'completion_rate': completion_rate,
                'avg_transmission_duration': avg_duration,
                'current_thresholds': {
                    'energy_threshold': self.metrics['energy_threshold'],
                    'zcr_min': self.metrics['zcr_min'],
                    'zcr_max': self.metrics['zcr_max'],
                    'speech_frames_to_start': self.speech_frames_to_start,
                    'hang_time_ms': self.hang_time_ms
                },
                'energy_stats': energy_stats,
                'zcr_stats': zcr_stats
            }
    
    def reset_metrics(self):
        """Reset metrics collection (called after auto-tuner analysis)"""
        with self.metrics_lock:
            self.metrics = {
                'frames_processed': 0,
                'speech_frames': 0,
                'energy_values': [],
                'zcr_values': [],
                'transmissions_started': 0,
                'transmissions_completed': 0,
                'transmissions_discarded': 0,
                'transmission_durations': [],
                'false_positives': 0,
                'last_reset': time.time(),
                'energy_threshold': self.energy_threshold,
                'zcr_min': self.zcr_min,
                'zcr_max': self.zcr_max
            }
    
    def update_vad_parameters(self, new_params: Dict[str, float]):
        """Update VAD parameters from auto-tuner recommendations"""
        if 'energy_threshold' in new_params:
            self.energy_threshold = new_params['energy_threshold']
            logger.info(f"Updated energy_threshold to {self.energy_threshold:.2e}")
        
        if 'zcr_min' in new_params:
            self.zcr_min = new_params['zcr_min']
            logger.info(f"Updated zcr_min to {self.zcr_min:.3f}")
        
        if 'zcr_max' in new_params:
            self.zcr_max = new_params['zcr_max']
            logger.info(f"Updated zcr_max to {self.zcr_max:.3f}")
        
        if 'speech_frames_to_start' in new_params:
            self.speech_frames_to_start = int(new_params['speech_frames_to_start'])
            logger.info(f"Updated speech_frames_to_start to {self.speech_frames_to_start}")
        
        if 'hang_time_ms' in new_params:
            self.hang_time_ms = new_params['hang_time_ms']
            self.hang_time_frames = int(self.hang_time_ms / self.frame_duration_ms)
            logger.info(f"Updated hang_time_ms to {self.hang_time_ms}")
