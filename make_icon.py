"""assets/256.png 를 icon.ico 로 변환"""
from pathlib import Path
from PIL import Image

assets = Path(__file__).parent / "assets"
src = assets / "256.png"

if not src.exists():
    print("[ERROR] assets/256.png not found")
    raise SystemExit(1)

img = Image.open(src).convert("RGBA").resize((256, 256), Image.LANCZOS)
out = assets / "icon.ico"
img.save(out, format="ICO", sizes=[(256, 256)])
print(f"[OK] {out} created")
