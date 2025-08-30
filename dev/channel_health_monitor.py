#!/usr/bin/env python3
"""
Channel Health Monitor
Monitors stream connections and transmission patterns
"""

import os
from datetime import datetime, timedelta
from audio_recorder import AudioRecorder


def analyze_channel_health():
    """Analyze recent recording patterns for all channels"""

    recorder = AudioRecorder()

    print("📡 CHANNEL HEALTH MONITORING REPORT")
    print("=" * 50)
    print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check each channel's recent activity
    for channel_id, channel_info in recorder.channels.items():
        channel_name = channel_info["name"]
        channel_dir = os.path.join("audio_files", channel_id)

        print(f"📻 {channel_name}")
        print(f"   URL: {channel_info['url']}")

        if not os.path.exists(channel_dir):
            print("   ❌ Status: No recordings directory")
            continue

        # Get recent files (last 24 hours)
        recent_files = []
        now = datetime.now()
        cutoff_time = now - timedelta(hours=24)

        for file in os.listdir(channel_dir):
            if (file.endswith(".mp3") or file.endswith(".flac")) and not file.startswith("temp_"):
                file_path = os.path.join(channel_dir, file)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time > cutoff_time:
                    file_size = os.path.getsize(file_path)
                    recent_files.append((file, file_time, file_size))

        recent_files.sort(
            key=lambda x: x[1], reverse=True
        )  # Sort by time, newest first

        if recent_files:
            print(f"   ✅ Status: Active ({len(recent_files)} recordings in last 24h)")

            # Show recent activity
            total_size = sum(f[2] for f in recent_files)
            avg_size = total_size / len(recent_files)

            print(f"   📊 Total recordings: {len(recent_files)}")
            print(f"   💾 Total size: {total_size:,} bytes")
            print(f"   📏 Average size: {avg_size:,.0f} bytes")

            # Show last few recordings
            print("   🕒 Recent recordings:")
            for file, file_time, file_size in recent_files[:3]:
                time_str = file_time.strftime("%H:%M:%S")
                print(f"      {time_str}: {file} ({file_size:,} bytes)")

            # Check for patterns that might indicate issues
            if avg_size < 50000:  # Small files might indicate poor quality
                print("   ⚠️  Warning: Small file sizes may indicate weak signals")

            if len(recent_files) > 100:  # Too many files might indicate false positives
                print(
                    "   ⚠️  Warning: High recording frequency may indicate false positives"
                )

        else:
            print("   🔇 Status: Silent (no recordings in last 24h)")

            # Check for temp files to see if connection is working
            temp_files = [f for f in os.listdir(channel_dir) if f.startswith("temp_")]
            if temp_files:
                print("   🔄 Info: Connection active (temp files present)")
            else:
                print("   ❌ Info: No recent connection activity")

        print()


def main():
    """Main monitoring function"""
    print("Starting channel health analysis...")
    print()

    analyze_channel_health()

    print("📋 RECOMMENDATIONS:")
    print()
    print("🔇 For channels showing 'Silent':")
    print("   • This is normal for low-activity channels")
    print("   • SSF and some departments may have infrequent transmissions")
    print("   • Check if temp files are present (indicates connection is working)")
    print()
    print("⚠️  For channels with warnings:")
    print("   • Small files: May need threshold adjustments")
    print("   • High frequency: Voice detection may need tuning")
    print()
    print("✅ For active channels:")
    print("   • System working normally")
    print("   • Voice detection filtering appropriately")


if __name__ == "__main__":
    main()
