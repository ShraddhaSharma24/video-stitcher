import os
import subprocess
from pathlib import Path
from typing import List

class VideoStitcher:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    def stitch_videos_ffmpeg(self, video_paths: List[str], output_path: str,
                             method: str = "concat") -> str:

        if len(video_paths) < 2:
            raise ValueError("Minimum 2 videos required")

        if method == "concat":
            return self._concat_demuxer(video_paths, output_path)
        else:
            return self._concat_filter(video_paths, output_path)

    def _concat_demuxer(self, video_paths: List[str], output_path: str) -> str:
        concat_file = os.path.join(self.output_dir, "concat_list.txt")
        with open(concat_file, 'w') as f:
            for video_path in video_paths:
                abs_path = os.path.abspath(video_path)
                f.write(f"file '{abs_path}'\n")

        cmd = [
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_file,
            '-c', 'copy', '-y', output_path
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return output_path

    def _concat_filter(self, video_paths: List[str], output_path: str) -> str:
        inputs = []
        filter_parts = []
        for i, video_path in enumerate(video_paths):
            inputs.extend(['-i', video_path])
            filter_parts.append(f'[{i}:v][{i}:a]')
        filter_complex = f"{''.join(filter_parts)}concat=n={len(video_paths)}:v=1:a=1[outv][outa]"

        cmd = [
            'ffmpeg', *inputs, '-filter_complex', filter_complex,
            '-map', '[outv]', '-map', '[outa]',
            '-c:v', 'libx264', '-c:a', 'aac', '-y', output_path
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return output_path



