#!/usr/bin/env python3
"""
Start Recording Script
Standalone script to start audio recording for all configured channels.
"""

import sys
import os
import signal
import time
import logging

# Add project root to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from audio_recorder import AudioRecorder

# Change to project root directory
os.chdir(project_root)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('recording.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    logger.info("Recording stopped by user (Ctrl+C)")
    sys.exit(0)

def main():
    """Main recording function"""
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🎵 Starting Police Radio Audio Logger")
    logger.info("===================================")
    
    try:
        # Initialize the audio recorder
        recorder = AudioRecorder()
        
        # Get all channel IDs from configuration
        channel_ids = list(recorder.channels.keys())
        logger.info(f"Starting recording for {len(channel_ids)} channels")
        
        # Start recording for all channels
        recorder.start_recording(channel_ids)
        
        logger.info("✅ Recording started successfully")
        logger.info("📄 Logs are being written to recording.log")
        logger.info("🛑 Press Ctrl+C to stop recording")
        logger.info("")
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Recording stopped by user")
    except Exception as e:
        logger.error(f"Error starting recording: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
