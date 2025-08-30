#!/usr/bin/env python3
"""
Stop Recording Script
Standalone script to stop audio recording for all channels.
"""

import sys
import logging
import requests
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('recording.log', mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main stop recording function"""
    logger.info("🛑 Stopping Police Radio Audio Logger")
    logger.info("====================================")
    
    try:
        # Try to connect to the running Flask app to stop recording
        api_url = "http://localhost:8000/api/stop-recording"
        
        logger.info("Attempting to stop recording via API...")
        
        response = requests.post(api_url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            logger.info("✅ Recording stopped successfully via API")
            logger.info(f"Result: {result.get('message', 'Recording stopped')}")
        else:
            logger.warning(f"API returned status {response.status_code}")
            # Fall back to process termination
            terminate_processes()
            
    except requests.exceptions.ConnectionError:
        logger.warning("Could not connect to Flask app API")
        # Fall back to process termination
        terminate_processes()
    except Exception as e:
        logger.error(f"Error stopping recording: {e}")
        # Fall back to process termination
        terminate_processes()

def terminate_processes():
    """Terminate recording processes by finding and killing them"""
    import subprocess
    import os
    
    try:
        logger.info("Attempting to terminate recording processes...")
        
        # Find processes running start_recording.py
        result = subprocess.run(
            ["pgrep", "-f", "start_recording.py"],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    logger.info(f"Terminating process {pid}")
                    os.kill(int(pid), 15)  # SIGTERM
                    time.sleep(1)
                    
                    # Check if process is still running
                    try:
                        os.kill(int(pid), 0)  # Check if process exists
                        logger.warning(f"Process {pid} still running, sending SIGKILL")
                        os.kill(int(pid), 9)  # SIGKILL
                    except OSError:
                        logger.info(f"Process {pid} terminated successfully")
            
            logger.info("✅ Recording processes terminated")
        else:
            logger.info("No recording processes found")
            
    except Exception as e:
        logger.error(f"Error terminating processes: {e}")

if __name__ == "__main__":
    main()
