#!/usr/bin/env python3
"""
Convert PNG icons to ICO format for Windows
"""

from PIL import Image
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def create_ico_file():
    """Create multi-resolution .ico file for Windows"""
    sizes = [256, 128, 64, 32, 16]
    images = []
    
    for size in sizes:
        # Use existing icons or create from largest
        if size >= 32:
            img_path = os.path.join(SCRIPT_DIR, f'app_icon_{size}.png')
            if os.path.exists(img_path):
                img = Image.open(img_path)
            else:
                img = Image.open(os.path.join(SCRIPT_DIR, 'app_icon_256.png'))
                img = img.resize((size, size), Image.Resampling.LANCZOS)
        else:
            # Generate 16x16 from 32x32
            img = Image.open(os.path.join(SCRIPT_DIR, 'app_icon_32.png'))
            img = img.resize((size, size), Image.Resampling.LANCZOS)
        
        images.append(img)
    
    # Save as ICO
    ico_path = os.path.join(SCRIPT_DIR, 'voiceclick.ico')
    images[0].save(ico_path, format='ICO', sizes=[(img.width, img.height) for img in images])
    print(f"✓ Created voiceclick.ico with sizes: {sizes}")

if __name__ == '__main__':
    create_ico_file()
