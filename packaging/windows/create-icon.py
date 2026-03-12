#!/usr/bin/env python3
"""Convert tmug.svg to tmug.ico for Windows packaging."""
import os, sys
try:
    import cairosvg
    from PIL import Image
    import io
except ImportError:
    print("Install dependencies: pip install Pillow cairosvg")
    sys.exit(1)

svg_path = os.path.join(os.path.dirname(__file__), '..', '..', 'tmug.svg')
ico_path = os.path.join(os.path.dirname(__file__), 'tmug.ico')

png_data = cairosvg.svg2png(url=svg_path, output_width=256, output_height=256)
img = Image.open(io.BytesIO(png_data))
img.save(ico_path, sizes=[(16,16), (32,32), (48,48), (256,256)])
print(f"Created {ico_path}")
