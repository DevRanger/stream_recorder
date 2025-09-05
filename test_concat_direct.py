#!/usr/bin/env python3
"""
Direct test of concatenation logic without Flask
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()

def test_concatenation_direct():
    """Test concatenation logic directly"""
    
    # Test files (these should exist in the audio_files directory)
    test_files = [
        "20250828_150445_160_2_-_Sheriff.flac",
        "20250828_150631_693_2_-_Sheriff.flac"
    ]
    
    print(f"Testing concatenation of {len(test_files)} files:")
    for i, filename in enumerate(test_files, 1):
        print(f"  {i}. {filename}")
    
    # Validate all files exist and collect full paths
    full_paths = []
    missing_files = []
    
    for filename in test_files:
        # Remove any path separators to prevent directory traversal
        safe_filename = os.path.basename(filename)
        
        # Find the file in any channel subdirectory
        file_found = False
        for channel_dir in os.listdir(BASE_DIR / 'audio_files'):
            channel_path = BASE_DIR / 'audio_files' / channel_dir
            if channel_path.is_dir():
                file_path = channel_path / safe_filename
                if file_path.exists() and file_path.suffix in ['.mp3', '.flac']:
                    full_paths.append(str(file_path))
                    print(f"✅ Found: {file_path}")
                    file_found = True
                    break
        
        if not file_found:
            missing_files.append(safe_filename)
            print(f"❌ Missing: {safe_filename}")
    
    if missing_files:
        print(f"\n❌ Error: Files not found: {', '.join(missing_files)}")
        return False
    
    print(f"\n✅ All {len(full_paths)} files validated successfully")
    
    # Determine output format based on input files
    input_extensions = {Path(fp).suffix.lower() for fp in full_paths}
    if '.flac' in input_extensions:
        output_ext = 'flac'
    else:
        output_ext = 'mp3'
    
    # Create output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"test_concatenated_{timestamp}.{output_ext}"
    output_path = BASE_DIR / 'audio_files' / output_filename
    
    print(f"\n📁 Output file: {output_path} (format: {output_ext})")
    
    # Create a temporary file list for FFmpeg
    temp_list_file = BASE_DIR / 'audio_files' / f"temp_test_concat_list_{timestamp}.txt"
    
    try:
        # Write file list for FFmpeg concat demuxer
        with open(temp_list_file, 'w') as f:
            for file_path in full_paths:
                # Escape single quotes in file paths for FFmpeg
                escaped_path = file_path.replace("'", "'\"'\"'")
                f.write(f"file '{escaped_path}'\n")
        
        print(f"📝 Created temp list file: {temp_list_file}")
        
        # Show contents of temp file for debugging
        print(f"📄 Temp file contents:")
        with open(temp_list_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                print(f"  {line_num}: {line.rstrip()}")
        
        # Build FFmpeg command
        cmd = [
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', str(temp_list_file),
            '-c', 'copy',  # Copy without re-encoding for speed
            '-y',  # Overwrite output file if it exists
            str(output_path)
        ]
        
        print(f"\n🔧 FFmpeg command:")
        print(f"  {' '.join(cmd)}")
        
        print(f"\n⏳ Running FFmpeg concatenation...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        print(f"📊 FFmpeg return code: {result.returncode}")
        if result.stdout:
            print(f"📤 FFmpeg stdout:\n{result.stdout}")
        if result.stderr:
            print(f"📥 FFmpeg stderr:\n{result.stderr}")
        
        if result.returncode != 0:
            print(f"\n❌ FFmpeg failed with code {result.returncode}")
            return False
        
        print(f"\n✅ FFmpeg completed successfully")
        
        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f"📏 Final file size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
            print(f"✅ Output file created: {output_path}")
        else:
            print(f"❌ Output file not created")
            return False
        
        # Clean up temp file
        temp_list_file.unlink()
        print(f"🧹 Cleaned up temp list file")
        
        return True
        
    except subprocess.TimeoutExpired:
        print(f"❌ FFmpeg timed out after 300 seconds")
        return False
    except Exception as e:
        print(f"❌ Exception during concatenation: {e}")
        return False
    finally:
        # Clean up temp file on error
        if temp_list_file.exists():
            temp_list_file.unlink()
            print(f"🧹 Cleaned up temp list file (after error)")

if __name__ == "__main__":
    print("🎵 Direct Concatenation Test")
    print("=" * 50)
    
    success = test_concatenation_direct()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Concatenation test PASSED")
    else:
        print("💥 Concatenation test FAILED")
