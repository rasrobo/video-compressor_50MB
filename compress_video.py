import os
import sys
import ffmpeg
import argparse
from pathlib import Path

def get_video_info(video_path):
    """Get video duration and bitrate information."""
    try:
        probe = ffmpeg.probe(video_path)
        duration = float(probe['format']['duration'])
        
        # Get video stream info
        video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
        audio_stream = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
        
        video_bitrate = int(video_stream.get('bit_rate', 0)) if video_stream else 0
        audio_bitrate = int(audio_stream.get('bit_rate', 128000)) if audio_stream else 128000
        
        return {
            'duration': duration,
            'video_bitrate': video_bitrate,
            'audio_bitrate': audio_bitrate,
            'width': int(video_stream.get('width', 1920)) if video_stream else 1920,
            'height': int(video_stream.get('height', 1080)) if video_stream else 1080
        }
    except Exception as e:
        print(f"Error getting video info: {e}")
        return None

def compress_video_to_target_size(input_path, output_path, target_size_mb):
    """Compress video to target size using two-pass encoding."""
    info = get_video_info(input_path)
    if not info:
        return False
    
    # Calculate target bitrates
    target_size_bits = target_size_mb * 1024 * 1024 * 8
    target_total_bitrate = int(target_size_bits / info['duration'])
    
    # Reserve bitrate for audio (max 128k for good quality)
    audio_bitrate = min(128000, target_total_bitrate // 10)
    video_bitrate = target_total_bitrate - audio_bitrate
    
    # Check if video bitrate is too low (would result in poor quality)
    min_acceptable_bitrate = 200000  # 200kbps minimum
    if video_bitrate < min_acceptable_bitrate:
        print(f"Warning: Target bitrate ({video_bitrate}bps) too low for good quality")
        return False
    
    try:
        print(f"Compressing to {target_size_mb}MB...")
        print(f"Target video bitrate: {video_bitrate}bps, audio bitrate: {audio_bitrate}bps")
        
        # Two-pass encoding for better quality
        input_stream = ffmpeg.input(input_path)
        
        # Pass 1
        pass1 = ffmpeg.output(
            input_stream,
            os.devnull,
            **{
                'c:v': 'libx264',
                'b:v': video_bitrate,
                'pass': 1,
                'f': 'mp4',
                'preset': 'medium',
                'an': None  # No audio in pass 1
            }
        ).overwrite_output()
        
        ffmpeg.run(pass1, quiet=True)
        
        # Pass 2
        pass2 = ffmpeg.output(
            input_stream,
            output_path,
            **{
                'c:v': 'libx264',
                'b:v': video_bitrate,
                'pass': 2,
                'c:a': 'aac',
                'b:a': audio_bitrate,
                'preset': 'medium'
            }
        ).overwrite_output()
        
        ffmpeg.run(pass2, quiet=True)
        
        # Clean up pass files
        for f in ['ffmpeg2pass-0.log', 'ffmpeg2pass-0.log.mbtree']:
            if os.path.exists(f):
                os.remove(f)
        
        return True
        
    except Exception as e:
        print(f"Compression failed: {e}")
        return False

def create_highlight_clips(input_path, output_dir, target_size_mb, num_clips=3):
    """Create multiple short clips from different parts of the video."""
    info = get_video_info(input_path)
    if not info:
        return False
    
    duration = info['duration']
    clip_duration = min(30, duration / num_clips)  # Max 30 seconds per clip
    
    clips_created = []
    
    for i in range(num_clips):
        start_time = (duration / (num_clips + 1)) * (i + 1) - (clip_duration / 2)
        start_time = max(0, start_time)
        
        clip_output = os.path.join(output_dir, f"highlight_clip_{i+1}.mp4")
        
        try:
            print(f"Creating clip {i+1}/{num_clips} starting at {start_time:.1f}s...")
            
            # Calculate bitrate for clip
            target_bits = (target_size_mb * 1024 * 1024 * 8) / num_clips
            clip_bitrate = int(target_bits / clip_duration)
            audio_bitrate = min(128000, clip_bitrate // 10)
            video_bitrate = clip_bitrate - audio_bitrate
            
            input_stream = ffmpeg.input(input_path, ss=start_time, t=clip_duration)
            output_stream = ffmpeg.output(
                input_stream,
                clip_output,
                **{
                    'c:v': 'libx264',
                    'b:v': video_bitrate,
                    'c:a': 'aac',
                    'b:a': audio_bitrate,
                    'preset': 'medium'
                }
            ).overwrite_output()
            
            ffmpeg.run(output_stream, quiet=True)
            clips_created.append(clip_output)
            
        except Exception as e:
            print(f"Failed to create clip {i+1}: {e}")
    
    return clips_created

def main():
    parser = argparse.ArgumentParser(description='Compress video or create clips for portfolio')
    parser.add_argument('input_file', help='Input video file path')
    parser.add_argument('--target-size', type=int, default=50, help='Target size in MB (default: 50)')
    parser.add_argument('--clips-only', action='store_true', help='Skip compression, create clips only')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found")
        return
    
    # Create output directory in same folder as input
    output_dir = input_path.parent
    
    print(f"Processing: {input_path}")
    print(f"Output directory: {output_dir}")
    
    if not args.clips_only:
        # Try compression first
        compressed_output = output_dir / f"{input_path.stem}_compressed.mp4"
        
        print(f"\nAttempting compression to {args.target_size}MB...")
        if compress_video_to_target_size(str(input_path), str(compressed_output), args.target_size):
            # Check actual file size
            actual_size = os.path.getsize(compressed_output) / (1024 * 1024)
            print(f"✅ Compression successful! Output: {compressed_output}")
            print(f"Final size: {actual_size:.1f}MB")
            
            if actual_size <= args.target_size * 1.1:  # Allow 10% tolerance
                print("Compression meets requirements. You can use this file!")
                return
        
        print("Compression resulted in poor quality or failed. Creating clips instead...")
    
    # Create clips
    print(f"\nCreating highlight clips...")
    clips = create_highlight_clips(str(input_path), str(output_dir), args.target_size)
    
    if clips:
        print(f"✅ Created {len(clips)} clips:")
        total_size = 0
        for clip in clips:
            size = os.path.getsize(clip) / (1024 * 1024)
            total_size += size
            print(f"  - {os.path.basename(clip)} ({size:.1f}MB)")
        print(f"Total size: {total_size:.1f}MB")
        print("\nYou can choose the best clip for your Fiverr portfolio!")
    else:
        print("❌ Failed to create clips")

if __name__ == "__main__":
    main()
