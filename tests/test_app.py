import unittest
import sys
import os
import json
import tempfile
import shutil

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_app
from audio_recorder import AudioRecorder

class PoliceRadioRecorderTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('development')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create temporary directories for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_file = os.path.join(self.temp_dir, 'test_channels.json')
        self.test_audio_dir = os.path.join(self.temp_dir, 'test_audio')
        
        # Create test configuration
        test_config = {
            "channels": [
                {
                    "name": "Test Police",
                    "url": "http://example.com/test.mp3",
                    "group": "Test Group",
                    "enabled": True,
                    "noiseGate": {
                        "enabled": True,
                        "threshold": -45
                    }
                }
            ]
        }
        
        with open(self.test_config_file, 'w') as f:
            json.dump(test_config, f)
    
    def tearDown(self):
        self.app_context.pop()
        # Clean up temporary files
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_home_page(self):
        """Test that the home page loads successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Police Radio Audio Logger', response.data)
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('Police Radio Recorder', data['message'])
    
    def test_get_channels(self):
        """Test the channels endpoint"""
        response = self.client.get('/api/channels')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, dict)
    
    def test_get_status(self):
        """Test the status endpoint"""
        response = self.client.get('/api/status')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, dict)
    
    def test_get_recordings(self):
        """Test the recordings endpoint"""
        response = self.client.get('/api/recordings')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
    
    def test_get_stats(self):
        """Test the statistics endpoint"""
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, dict)
        self.assertIn('total', data)
    
    def test_start_recording_endpoint(self):
        """Test the start recording endpoint"""
        response = self.client.post('/api/start', 
                                   json={'channels': ['test_channel']},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
    
    def test_stop_recording_endpoint(self):
        """Test the stop recording endpoint"""
        response = self.client.post('/api/stop', 
                                   json={'channels': ['test_channel']},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
    
    def test_audio_recorder_initialization(self):
        """Test AudioRecorder initialization"""
        recorder = AudioRecorder(self.test_config_file, self.test_audio_dir)
        self.assertIsInstance(recorder.channels, dict)
        self.assertTrue(len(recorder.channels) > 0)
    
    def test_audio_recorder_sanitize_name(self):
        """Test filename sanitization"""
        recorder = AudioRecorder(self.test_config_file, self.test_audio_dir)
        
        # Test various invalid characters
        test_cases = [
            ('Test<Channel>', 'Test_Channel_'),
            ('Test/Channel', 'Test_Channel'),
            ('Test:Channel', 'Test_Channel'),
            ('Normal_Channel', 'Normal_Channel')
        ]
        
        for input_name, expected in test_cases:
            result = recorder.sanitize_name(input_name)
            self.assertEqual(result, expected)
    
    def test_download_nonexistent_recording(self):
        """Test downloading a file that doesn't exist"""
        response = self.client.get('/api/recording/nonexistent_file.mp3')
        self.assertEqual(response.status_code, 404)

class AudioRecorderUnitTests(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_file = os.path.join(self.temp_dir, 'test_channels.json')
        self.test_audio_dir = os.path.join(self.temp_dir, 'test_audio')
        
        # Create test configuration
        test_config = {
            "channels": [
                {
                    "name": "Test Police Main",
                    "url": "http://example.com/police.mp3",
                    "group": "Police",
                    "enabled": True,
                    "gain": 1.0,
                    "noiseGate": {
                        "enabled": True,
                        "threshold": -45,
                        "ratio": 4,
                        "attack": 0.005,
                        "release": 0.3
                    }
                },
                {
                    "name": "Test Fire Dept",
                    "url": "http://example.com/fire.mp3",
                    "group": "Fire",
                    "enabled": False
                }
            ]
        }
        
        with open(self.test_config_file, 'w') as f:
            json.dump(test_config, f)
    
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_load_channels(self):
        """Test loading channels from configuration"""
        recorder = AudioRecorder(self.test_config_file, self.test_audio_dir)
        
        self.assertEqual(len(recorder.channels), 2)
        self.assertIn('Test_Police_Main', recorder.channels)
        self.assertIn('Test_Fire_Dept', recorder.channels)
        
        # Check channel properties
        police_channel = recorder.channels['Test_Police_Main']
        self.assertEqual(police_channel['name'], 'Test Police Main')
        self.assertEqual(police_channel['url'], 'http://example.com/police.mp3')
        self.assertEqual(police_channel['group'], 'Police')
        self.assertTrue(police_channel['enabled'])
    
    def test_ensure_output_directory(self):
        """Test that output directories are created"""
        recorder = AudioRecorder(self.test_config_file, self.test_audio_dir)
        
        # Check that main directory exists
        self.assertTrue(os.path.exists(self.test_audio_dir))
        
        # Check that channel subdirectories exist
        for channel_id in recorder.channels:
            channel_dir = os.path.join(self.test_audio_dir, channel_id)
            self.assertTrue(os.path.exists(channel_dir))
    
    def test_get_timestamp(self):
        """Test timestamp generation"""
        recorder = AudioRecorder(self.test_config_file, self.test_audio_dir)
        timestamp = recorder.get_timestamp()
        
        # Should be in format YYYYMMDD_HHMMSS_mmm
        self.assertRegex(timestamp, r'\d{8}_\d{6}_\d{3}')
    
    def test_get_status(self):
        """Test status reporting"""
        recorder = AudioRecorder(self.test_config_file, self.test_audio_dir)
        status = recorder.get_status()
        
        self.assertIsInstance(status, dict)
        self.assertEqual(len(status), 2)
        
        for channel_id, channel_status in status.items():
            self.assertIn('name', channel_status)
            self.assertIn('url', channel_status)
            self.assertIn('enabled', channel_status)
            self.assertIn('recording', channel_status)
            self.assertIn('group', channel_status)
    
    def test_get_recordings_empty(self):
        """Test getting recordings when none exist"""
        recorder = AudioRecorder(self.test_config_file, self.test_audio_dir)
        recordings = recorder.get_recordings()
        
        self.assertIsInstance(recordings, list)
        self.assertEqual(len(recordings), 0)

if __name__ == '__main__':
    unittest.main()
