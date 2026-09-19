"""Usage: python reel.py frames_dir out.mp4 [seconds_per_slide]
Frames named slide-01.png ... ; 0.3s crossfades; silent (add audio in Instagram)."""
import sys, glob, subprocess
d, out = sys.argv[1], sys.argv[2]; dur = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0; fade = 0.3
frames = sorted(glob.glob(f"{d}/slide-*.png")); n = len(frames)
inputs = sum([["-loop", "1", "-t", str(dur), "-i", f] for f in frames], [])
chain, prev = [], "0"
for i in range(1, n):
    chain.append(f"[{prev}][{i}]xfade=transition=fade:duration={fade}:offset={round(i*dur - i*fade, 2)}[v{i}]"); prev = f"v{i}"
chain.append(f"[{prev}]format=yuv420p[v]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(chain),
                "-map", "[v]", "-r", "30", "-c:v", "libx264", "-crf", "20", "-movflags", "+faststart", out], check=True)
print("wrote", out)
