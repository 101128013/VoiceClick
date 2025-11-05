#!/usr/bin/env python3
"""
Generate application icons for VoiceClick
Creates placeholder icons using PIL (Pillow)
"""

from PIL import Image, ImageDraw, ImageFont
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def create_app_icon(size, filename):
    """Create main application icon"""
    img = Image.new('RGB', (size, size), color='#2196F3')  # Blue background
    draw = ImageDraw.Draw(img)
    
    # Draw microphone shape
    mic_color = '#FFFFFF'
    center_x, center_y = size // 2, size // 2
    mic_width = size // 3
    mic_height = size // 2
    
    # Microphone capsule (rounded rectangle)
    draw.ellipse([center_x - mic_width//2, center_y - mic_height//2, 
                  center_x + mic_width//2, center_y + mic_height//2], 
                 fill=mic_color)
    
    # Microphone stand
    stand_width = size // 20
    draw.rectangle([center_x - stand_width, center_y + mic_height//2,
                   center_x + stand_width, center_y + mic_height//2 + size//5],
                  fill=mic_color)
    
    # Base
    base_width = size // 4
    draw.rectangle([center_x - base_width, center_y + mic_height//2 + size//5,
                   center_x + base_width, center_y + mic_height//2 + size//5 + size//20],
                  fill=mic_color)
    
    img.save(os.path.join(SCRIPT_DIR, filename))
    print(f"Created {filename} ({size}x{size})")

def create_recording_icon(size, filename):
    """Create recording indicator icon (red circle)"""
    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Red circle
    padding = size // 10
    draw.ellipse([padding, padding, size - padding, size - padding], 
                 fill='#F44336')
    
    img.save(os.path.join(SCRIPT_DIR, filename))
    print(f"Created {filename} ({size}x{size})")

def create_stop_icon(size, filename):
    """Create stop indicator icon (gray square)"""
    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Gray square
    padding = size // 10
    draw.rectangle([padding, padding, size - padding, size - padding], 
                  fill='#757575')
    
    img.save(os.path.join(SCRIPT_DIR, filename))
    print(f"Created {filename} ({size}x{size})")

def create_settings_icon(size, filename):
    """Create settings icon (gear)"""
    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Simple gear representation (circle with dots)
    center = size // 2
    radius = size // 3
    
    # Center circle
    draw.ellipse([center - radius, center - radius, 
                  center + radius, center + radius], 
                 fill='#607D8B')
    
    # Inner circle (hole)
    inner_radius = radius // 2
    draw.ellipse([center - inner_radius, center - inner_radius,
                  center + inner_radius, center + inner_radius],
                 fill=(0, 0, 0, 0))
    
    img.save(os.path.join(SCRIPT_DIR, filename))
    print(f"Created {filename} ({size}x{size})")

def create_history_icon(size, filename):
    """Create history icon (clock)"""
    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Circle
    padding = size // 10
    draw.ellipse([padding, padding, size - padding, size - padding], 
                 outline='#4CAF50', fill='#4CAF50', width=2)
    
    # Clock hands (simplified)
    center = size // 2
    # Hour hand
    draw.line([center, center, center, center - size//4], 
              fill='#FFFFFF', width=max(2, size//20))
    # Minute hand
    draw.line([center, center, center + size//4, center], 
              fill='#FFFFFF', width=max(2, size//25))
    
    img.save(os.path.join(SCRIPT_DIR, filename))
    print(f"Created {filename} ({size}x{size})")

def create_tray_icon(size, filename):
    """Create system tray icon (small microphone)"""
    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Simple microphone silhouette
    center_x, center_y = size // 2, size // 2
    mic_width = size // 3
    mic_height = size // 2
    
    # White microphone for visibility on dark taskbars
    mic_color = '#FFFFFF'
    
    # Capsule
    draw.ellipse([center_x - mic_width//2, center_y - mic_height//2, 
                  center_x + mic_width//2, center_y], 
                 fill=mic_color)
    
    # Stand
    draw.rectangle([center_x - 1, center_y, center_x + 1, center_y + size//4],
                  fill=mic_color)
    
    # Base
    draw.rectangle([center_x - size//4, center_y + size//4,
                   center_x + size//4, center_y + size//4 + 2],
                  fill=mic_color)
    
    img.save(os.path.join(SCRIPT_DIR, filename))
    print(f"Created {filename} ({size}x{size})")

def main():
    """Generate all icons"""
    print("Generating VoiceClick icons...")
    print("=" * 50)
    
    # Application icons (multiple sizes)
    create_app_icon(256, 'app_icon_256.png')
    create_app_icon(128, 'app_icon_128.png')
    create_app_icon(64, 'app_icon_64.png')
    create_app_icon(32, 'app_icon_32.png')
    
    # Recording/Stop icons
    create_recording_icon(32, 'recording_icon.png')
    create_stop_icon(32, 'stop_icon.png')
    
    # Tab icons
    create_settings_icon(32, 'settings_icon.png')
    create_history_icon(32, 'history_icon.png')
    
    # System tray icon
    create_tray_icon(22, 'tray_icon.png')
    create_tray_icon(16, 'tray_icon_small.png')
    
    print("=" * 50)
    print("✓ All icons generated successfully!")
    print(f"Location: {SCRIPT_DIR}")

if __name__ == '__main__':
    main()
