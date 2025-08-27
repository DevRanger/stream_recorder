from flask import Flask, render_template, jsonify, request, send_file, Response
from config import config
import os
import json
from audio_recorder import AudioRecorder

# Initialize audio recorder
audio_recorder = AudioRecorder()

def create_app(config_name=None):
    app = Flask(__name__)
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app.config.from_object(config[config_name])
    
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/test')
    def test():
        return send_file('test_page.html')
    
    @app.route('/test_api')
    def test_api():
        return send_file('test_api.html')
    
    @app.route('/test_audio')
    def test_audio():
        return send_file('test_audio.html')
    
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'Police Radio Recorder API is running'})

    @app.route('/api/channels')
    def get_channels():
        """Get all available radio channels"""
        channels = audio_recorder.channels
        return jsonify(channels)
    
    @app.route('/api/status')
    def get_recording_status():
        """Get current recording status for all channels"""
        status = audio_recorder.get_status()
        return jsonify(status)
    
    @app.route('/api/start', methods=['POST'])
    def start_recording():
        """Start recording for specified channels"""
        data = request.get_json() or {}
        channel_ids = data.get('channels')  # If None, starts all enabled channels
        
        try:
            audio_recorder.start_recording(channel_ids)
            return jsonify({
                'status': 'success',
                'message': 'Recording started',
                'channels': channel_ids or list(audio_recorder.channels.keys())
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/api/stop', methods=['POST'])
    def stop_recording():
        """Stop recording for specified channels"""
        data = request.get_json() or {}
        channel_ids = data.get('channels')  # If None, stops all channels
        
        try:
            audio_recorder.stop_recording(channel_ids)
            return jsonify({
                'status': 'success',
                'message': 'Recording stopped',
                'channels': channel_ids or list(audio_recorder.channels.keys())
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/api/recordings')
    def get_recordings():
        """Get list of recorded transmissions with optional filtering"""
        channel_id = request.args.get('channel')
        limit = int(request.args.get('limit', 100))
        start_date = request.args.get('start_date')  # YYYY-MM-DD format
        end_date = request.args.get('end_date')      # YYYY-MM-DD format
        search_text = request.args.get('search')     # Search in channel names
        
        recordings = audio_recorder.get_recordings(
            channel_id=channel_id, 
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            search_text=search_text
        )
        return jsonify(recordings)
    
    @app.route('/api/recordings/channel/<channel_id>')
    def get_channel_recordings(channel_id):
        """Get recordings for a specific channel with pagination"""
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        recordings = audio_recorder.get_channel_recordings(
            channel_id=channel_id,
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date
        )
        return jsonify(recordings)
    
    @app.route('/api/recording/<path:filename>')
    def download_recording(filename):
        """Download a specific recording file with proper headers for audio streaming"""
        try:
            # Extract channel from filename pattern: YYYYMMDD_HHMMSS_MS_CHANNEL.mp3
            parts = filename.split('_')
            if len(parts) >= 4:
                # Channel name starts from the 4th part (index 3)
                channel_id = '_'.join(parts[3:]).replace('.mp3', '')
                file_path = os.path.join('audio_files', channel_id, filename)
                
                if os.path.exists(file_path):
                    # Add headers for better audio streaming support
                    response = send_file(
                        file_path, 
                        mimetype='audio/mpeg',
                        as_attachment=False,
                        download_name=filename
                    )
                    response.headers['Accept-Ranges'] = 'bytes'
                    response.headers['Cache-Control'] = 'public, max-age=3600'
                    response.headers['Content-Disposition'] = f'inline; filename="{filename}"'
                    return response
            
            return jsonify({'error': 'File not found'}), 404
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stats')
    def get_statistics():
        """Get recording statistics"""
        try:
            stats = {}
            total_recordings = 0
            total_size = 0
            
            for channel_id in audio_recorder.channels:
                channel_dir = os.path.join('audio_files', channel_id)
                channel_count = 0
                channel_size = 0
                
                if os.path.exists(channel_dir):
                    for filename in os.listdir(channel_dir):
                        if filename.endswith('.mp3'):
                            filepath = os.path.join(channel_dir, filename)
                            channel_count += 1
                            channel_size += os.path.getsize(filepath)
                
                stats[channel_id] = {
                    'name': audio_recorder.channels[channel_id]['name'],
                    'recordings': channel_count,
                    'total_size': channel_size
                }
                
                total_recordings += channel_count
                total_size += channel_size
            
            stats['total'] = {
                'recordings': total_recordings,
                'total_size': total_size,
                'channels': len(audio_recorder.channels)
            }
            
            return jsonify(stats)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/cleanup-temp', methods=['POST'])
    def cleanup_temp_files():
        """Clean up temporary audio files"""
        try:
            data = request.get_json() or {}
            max_age_hours = data.get('max_age_hours', 24)
            force_all = data.get('force_all', False)
            
            if force_all:
                removed_count = audio_recorder.cleanup_all_temp_files()
            else:
                removed_count = audio_recorder.cleanup_temp_files(max_age_hours)
            
            # Also run orphaned cleanup
            orphaned_count = audio_recorder.cleanup_orphaned_temp_files()
            
            return jsonify({
                'status': 'success',
                'removed_count': removed_count,
                'orphaned_count': orphaned_count,
                'total_removed': removed_count + orphaned_count,
                'message': f'Removed {removed_count} old temp files and {orphaned_count} orphaned temp files'
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/cleanup-status')
    def cleanup_status():
        """Get status of temp files"""
        try:
            import glob
            from datetime import datetime, timedelta
            
            # Count temp files by age
            temp_pattern = os.path.join('audio_files', "*", "temp_*.mp3")
            temp_files = glob.glob(temp_pattern)
            
            now = datetime.now()
            counts = {
                'total': len(temp_files),
                'less_than_1_hour': 0,
                'less_than_24_hours': 0,
                'older_than_24_hours': 0,
                'orphaned': 0
            }
            
            for temp_file in temp_files:
                try:
                    file_time = datetime.fromtimestamp(os.path.getmtime(temp_file))
                    age = now - file_time
                    
                    if age < timedelta(hours=1):
                        counts['less_than_1_hour'] += 1
                    elif age < timedelta(hours=24):
                        counts['less_than_24_hours'] += 1
                    else:
                        counts['older_than_24_hours'] += 1
                    
                    # Check if orphaned (final file exists)
                    filename = os.path.basename(temp_file)
                    if filename.startswith('temp_'):
                        final_filename = filename[5:]  # Remove 'temp_' prefix
                        channel_dir = os.path.dirname(temp_file)
                        final_file = os.path.join(channel_dir, final_filename)
                        if os.path.exists(final_file):
                            counts['orphaned'] += 1
                            
                except Exception as e:
                    pass  # Skip files with errors
            
            return jsonify({
                'status': 'success',
                'temp_file_counts': counts,
                'cleanup_recommendations': {
                    'immediate_cleanup': counts['older_than_24_hours'],
                    'orphaned_cleanup': counts['orphaned']
                }
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error', 
                'message': str(e)
            }), 500
    
    @app.route('/api/test-connectivity')
    def test_connectivity():
        """Test connectivity to channels"""
        try:
            channel_id = request.args.get('channel')
            results = audio_recorder.test_channel_connectivity(channel_id)
            
            return jsonify({
                'status': 'success',
                'results': results
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)
