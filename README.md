# Video Compressor for Portfolio

A Python application that compresses large video files to meet platform requirements (like Fiverr's 50MB limit) or creates highlight clips when compression would result in poor quality.

## Features

- **Smart Compression**: Uses two-pass encoding for optimal quality at target file size
- **Quality Protection**: Automatically switches to clip creation if compression would be too aggressive
- **Highlight Clips**: Creates multiple short clips from different parts of your video
- **Fiverr Ready**: Optimized for Fiverr's 50MB maximum file size requirement

## Prerequisites

1. **Python 3.7+** installed on your system
2. **FFmpeg** installed and accessible from command line

### Installing FFmpeg

**Ubuntu/Debian:**
```
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```
brew install ffmpeg
```

**Windows:**
- Download from [FFmpeg official website](https://ffmpeg.org/download.html)
- Add to your system PATH

## Setup

1. **Clone the repository:**
```
git clone https://github.com/rasrobo/video-compressor_50MB.git
cd video-compressor_50MB
```

2. **Create virtual environment:**
```
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```
pip install -r requirements.txt
```

## Usage

### Basic Compression
```
python compress_video.py /path/to/your/video.mp4
```

### Custom Target Size
```
python compress_video.py /path/to/your/video.mp4 --target-size 30
```

### Create Clips Only (Skip Compression)
```
python compress_video.py /path/to/your/video.mp4 --clips-only
```

## Output

All output files are saved in the same directory as your input video:

- **Compressed video**: `original_name_compressed.mp4`
- **Highlight clips**: `highlight_clip_1.mp4`, `highlight_clip_2.mp4`, etc.

## How It Works

1. **Analysis**: The script analyzes your input video to determine optimal compression settings
2. **Smart Compression**: Attempts to compress the entire video using two-pass encoding
3. **Quality Check**: If compression would result in poor quality (bitrate too low), it switches to clip creation
4. **Clip Creation**: Creates 3 highlight clips from different parts of your video
5. **Output**: Saves all files in the same directory as your input video

## Example

```
# Compress a 200MB video to 50MB
python compress_video.py my_portfolio_video.mp4

# Output will be in the same directory:
# - my_portfolio_video_compressed.mp4 (if compression successful)
# - OR highlight_clip_1.mp4, highlight_clip_2.mp4, highlight_clip_3.mp4
```

## Tips for Best Results

- Use high-quality source videos for better compression results
- For very long videos, consider using `--clips-only` to create focused highlights
- Test different target sizes to find the best quality/size balance
- Keep your source video in a standard format (MP4, MOV, AVI)

## Troubleshooting

**FFmpeg not found:**
```
sudo apt install ffmpeg
```

**Permission errors:**
```
chmod +x compress_video.py
```

**Python module errors:**
```
pip install --upgrade ffmpeg-python
```

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Contact

Project Link: [https://github.com/rasrobo/video-compressor_50MB](https://github.com/rasrobo/video-compressor_50MB)
## Donations

If you find this software useful and would like to support its development, you can buy me a coffee! Your support is greatly appreciated.

[![Buy Me A Coffee](https://cdn.buymeacoffee.com/buttons/default-orange.png)](https://buymeacoffee.com/robodigitalis)
