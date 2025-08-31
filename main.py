"""
Radio Stream Recorder - Main Flask Application
Simplified audio recording system with RMS-based detection and FLAC output
"""

__version__ = "1.0.0"

from flask import Flask, render_template, jsonify, request, send_file
import os
from audio_recorder import AudioRecorder

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize audio recorder with proper paths
audio_recorder = AudioRecorder(
    config_file=os.path.join(BASE_DIR, "radio_channels.json"),
    output_dir=os.path.join(BASE_DIR, "audio_files")
)


def create_app():
    app = Flask(__name__)
    
    # Simple configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/test")
    def test():
        return send_file("test_page.html")

    @app.route("/test_api")
    def test_api():
        return send_file("test_api.html")

    @app.route("/test_audio")
    def test_audio():
        return send_file("test_audio.html")

    @app.route("/api/health")
    def health_check():
        return jsonify(
            {"status": "healthy", "message": "Police Radio Recorder API is running"}
        )

    @app.route("/api/channels")
    def get_channels():
        """Get all available radio channels"""
        channels = audio_recorder.channels
        return jsonify(channels)

    @app.route("/api/status")
    def get_recording_status():
        """Get current recording status for all channels"""
        status = audio_recorder.get_status()
        return jsonify(status)

    @app.route("/api/start", methods=["POST"])
    def start_recording():
        """Start recording for specified channels"""
        data = request.get_json() or {}
        channel_ids = data.get("channels")  # If None, starts all enabled channels

        try:
            audio_recorder.start_recording(channel_ids)
            return jsonify(
                {
                    "status": "success",
                    "message": "Recording started",
                    "channels": channel_ids or list(audio_recorder.channels.keys()),
                }
            )
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/stop", methods=["POST"])
    def stop_recording():
        """Stop recording for specified channels"""
        data = request.get_json() or {}
        channel_ids = data.get("channels")  # If None, stops all channels

        try:
            audio_recorder.stop_recording(channel_ids)
            return jsonify(
                {
                    "status": "success",
                    "message": "Recording stopped",
                    "channels": channel_ids or list(audio_recorder.channels.keys()),
                }
            )
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/recordings")
    def get_recordings():
        """Get list of recorded transmissions with optional filtering"""
        channel_id = request.args.get("channel")
        limit = int(request.args.get("limit", 100))
        start_date = request.args.get("start_date")  # YYYY-MM-DD format
        end_date = request.args.get("end_date")  # YYYY-MM-DD format
        search_text = request.args.get("search")  # Search in channel names

        recordings = audio_recorder.get_recordings(
            channel_id=channel_id,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            search_text=search_text,
        )
        return jsonify(recordings)

    @app.route("/api/recordings/channel/<channel_id>")
    def get_channel_recordings(channel_id):
        """Get recordings for a specific channel with pagination"""
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        recordings = audio_recorder.get_channel_recordings(
            channel_id=channel_id,
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
        )
        return jsonify(recordings)

    @app.route("/api/recording/<path:filename>")
    def download_recording(filename):
        """Download a specific recording file with proper headers for audio streaming"""
        try:
            # Extract channel from filename pattern: YYYYMMDD_HHMMSS_MS_CHANNEL.ext
            parts = filename.split("_")
            if len(parts) >= 4:
                # Channel name starts from the 4th part (index 3)
                # Remove both .mp3 and .flac extensions
                channel_id = (
                    "_".join(parts[3:]).replace(".mp3", "").replace(".flac", "")
                )
                file_path = os.path.join(BASE_DIR, "audio_files", channel_id, filename)

                if os.path.exists(file_path):
                    # Determine MIME type based on file extension
                    if filename.lower().endswith(".flac"):
                        mimetype = "audio/flac"
                    elif filename.lower().endswith(".mp3"):
                        mimetype = "audio/mpeg"
                    else:
                        mimetype = "audio/mpeg"  # Default fallback

                    # Add headers for better audio streaming support
                    response = send_file(
                        file_path,
                        mimetype=mimetype,
                        as_attachment=False,
                        download_name=filename,
                    )
                    response.headers["Accept-Ranges"] = "bytes"
                    response.headers["Cache-Control"] = "public, max-age=3600"
                    response.headers["Content-Disposition"] = (
                        f'inline; filename="{filename}"'
                    )
                    return response

            return jsonify({"error": "File not found"}), 404

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/recordings/concatenate", methods=["POST"])
    def concatenate_recordings():
        """Concatenate multiple recording files into a single file"""
        try:
            print("Concatenation request received")
            data = request.get_json()
            if data is None:
                print("No JSON data received")
                return jsonify({"error": "No JSON data received"}), 400
                
            files = data.get("files", [])
            channel_name = data.get("channel_name", "mixed").replace(" ", "_")
            
            print(f"Files to concatenate: {files}")
            print(f"Channel name: {channel_name}")
            
            if not files:
                return jsonify({"error": "No files specified"}), 400
            
            # Import required modules
            import subprocess
            import tempfile
            from datetime import datetime
            
            # Create temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Collect full file paths and validate they exist
                input_files = []
                for filename in files:
                    print(f"Processing filename: {filename}")
                    # Extract channel from filename pattern
                    parts = filename.split("_")
                    if len(parts) >= 4:
                        channel_id = "_".join(parts[3:]).replace(".mp3", "").replace(".flac", "")
                        file_path = os.path.join(BASE_DIR, "audio_files", channel_id, filename)
                        print(f"Looking for file: {file_path}")
                        
                        if os.path.exists(file_path):
                            input_files.append(file_path)
                            print(f"Found file: {file_path}")
                        else:
                            print(f"File not found: {file_path}")
                            return jsonify({"error": f"File not found: {filename}"}), 404
                    else:
                        print(f"Invalid filename format: {filename}")
                        return jsonify({"error": f"Invalid filename format: {filename}"}), 400
                
                print(f"Total input files found: {len(input_files)}")
                if not input_files:
                    return jsonify({"error": "No valid files found"}), 404
                
                # Generate output filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"{timestamp}_{channel_name}_concatenated.flac"
                output_path = os.path.join(temp_dir, output_filename)
                
                # Create ffmpeg command for concatenation
                # First, create a file list for ffmpeg concat demuxer
                filelist_path = os.path.join(temp_dir, "filelist.txt")
                with open(filelist_path, 'w') as f:
                    for file_path in input_files:
                        # Use absolute paths for ffmpeg
                        abs_path = os.path.abspath(file_path)
                        # Escape single quotes and backslashes for ffmpeg
                        escaped_path = abs_path.replace("'", "'\"'\"'").replace("\\", "\\\\")
                        f.write(f"file '{escaped_path}'\n")
                
                # Run ffmpeg to concatenate files
                ffmpeg_command = [
                    "ffmpeg",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", filelist_path,
                    "-c", "copy",  # Copy streams without re-encoding for speed
                    "-y",  # Overwrite output file
                    output_path
                ]
                
                print(f"Running ffmpeg command: {' '.join(ffmpeg_command)}")
                result = subprocess.run(
                    ffmpeg_command,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5-minute timeout
                )
                
                if result.returncode != 0:
                    print(f"FFmpeg error: {result.stderr}")
                    return jsonify({"error": f"FFmpeg failed: {result.stderr}"}), 500
                
                # Check if output file was created
                if not os.path.exists(output_path):
                    return jsonify({"error": "Concatenation failed - output file not created"}), 500
                
                # Read the file into memory before the temp directory is cleaned up
                with open(output_path, 'rb') as f:
                    file_data = f.read()
                
                # Create a response with the file data
                from flask import Response
                response = Response(
                    file_data,
                    mimetype="audio/flac",
                    headers={
                        "Content-Disposition": f"attachment; filename={output_filename}",
                        "Content-Length": str(len(file_data))
                    }
                )
                return response
                
        except subprocess.TimeoutExpired:
            return jsonify({"error": "Concatenation timed out"}), 504
        except Exception as e:
            print(f"Concatenation error: {str(e)}")
            return jsonify({"error": f"Concatenation failed: {str(e)}"}), 500

    @app.route("/api/stats")
    def get_statistics():
        """Get recording statistics"""
        try:
            from datetime import date

            stats = {}
            total_recordings = 0
            total_size = 0
            today_recordings = 0
            today = date.today().strftime("%Y%m%d")

            for channel_id in audio_recorder.channels:
                channel_dir = os.path.join(BASE_DIR, "audio_files", channel_id)
                channel_count = 0
                channel_size = 0
                channel_today = 0

                if os.path.exists(channel_dir):
                    for filename in os.listdir(channel_dir):
                        if filename.endswith(".mp3") or filename.endswith(".flac"):
                            filepath = os.path.join(channel_dir, filename)
                            channel_count += 1
                            channel_size += os.path.getsize(filepath)

                            # Check if file is from today (YYYYMMDD_* format)
                            if filename.startswith(today):
                                channel_today += 1

                stats[channel_id] = {
                    "name": audio_recorder.channels[channel_id]["name"],
                    "recordings": channel_count,
                    "total_size": channel_size,
                    "today": channel_today,
                }

                total_recordings += channel_count
                total_size += channel_size
                today_recordings += channel_today

            stats["total"] = {
                "recordings": total_recordings,
                "total_size": total_size,
                "channels": len(audio_recorder.channels),
                "today": today_recordings,
            }

            return jsonify(stats)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/cleanup-temp", methods=["POST"])
    def cleanup_temp_files():
        """Clean up temporary audio files"""
        try:
            data = request.get_json() or {}
            max_age_hours = data.get("max_age_hours", 24)
            force_all = data.get("force_all", False)

            if force_all:
                # Force cleanup all temp files regardless of age
                removed_count = audio_recorder.cleanup_temp_files(max_age_hours=0)
            else:
                removed_count = audio_recorder.cleanup_temp_files(max_age_hours)

            return jsonify(
                {
                    "status": "success",
                    "removed_count": removed_count,
                    "message": f"Removed {removed_count} temporary files",
                }
            )

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/cleanup-status")
    def cleanup_status():
        """Get status of temp files"""
        try:
            import glob
            from datetime import datetime, timedelta

            # Count temp files by age (both mp3 and flac)
            import glob
            
            temp_pattern_mp3 = os.path.join(BASE_DIR, "audio_files", "*", "temp_*.mp3")
            temp_pattern_flac = os.path.join(BASE_DIR, "audio_files", "*", "temp_*.flac")
            temp_files = glob.glob(temp_pattern_mp3) + glob.glob(temp_pattern_flac)

            now = datetime.now()
            counts = {
                "total": len(temp_files),
                "less_than_1_hour": 0,
                "less_than_24_hours": 0,
                "older_than_24_hours": 0,
                "orphaned": 0,
            }

            for temp_file in temp_files:
                try:
                    file_time = datetime.fromtimestamp(os.path.getmtime(temp_file))
                    age = now - file_time

                    if age < timedelta(hours=1):
                        counts["less_than_1_hour"] += 1
                    elif age < timedelta(hours=24):
                        counts["less_than_24_hours"] += 1
                    else:
                        counts["older_than_24_hours"] += 1

                    # Check if orphaned (final file exists)
                    filename = os.path.basename(temp_file)
                    if filename.startswith("temp_"):
                        final_filename = filename[5:]  # Remove 'temp_' prefix
                        channel_dir = os.path.dirname(temp_file)
                        final_file = os.path.join(channel_dir, final_filename)
                        if os.path.exists(final_file):
                            counts["orphaned"] += 1

                except Exception:
                    pass  # Skip files with errors

            return jsonify(
                {
                    "status": "success",
                    "temp_file_counts": counts,
                    "cleanup_recommendations": {
                        "immediate_cleanup": counts["older_than_24_hours"],
                        "orphaned_cleanup": counts["orphaned"],
                    },
                }
            )

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/test-connectivity")
    def test_connectivity():
        """Test connectivity to channels"""
        try:
            channel_id = request.args.get("channel")
            results = audio_recorder.test_channel_connectivity(channel_id)

            return jsonify({"status": "success", "results": results})

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(debug=True, host="0.0.0.0", port=port)
