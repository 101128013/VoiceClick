"""
Voice Click - Advanced Edition
Advanced features: Volume monitoring, smart pause detection, recording history
Ignores background chatter with advanced VAD
"""

import numpy as np
import sounddevice as sd
import threading
import time
from queue import Queue
from collections import deque
from pynput import mouse
import win32gui
import win32con
import ctypes
from ctypes import Structure, c_ulong, wintypes
import tkinter as tk
from tkinter import ttk
import keyboard
from faster_whisper import WhisperModel
import sys
import winsound
import logging
from datetime import datetime
import json
from pathlib import Path
import pyperclip  # For clipboard functionality
import traceback  # For detailed error logging
from .config_manager import config_manager

# Setup enhanced logging with both console and file output
LOG_FILE = Path.home() / ".voice_click.log"
DEBUG_MODE = False  # Set to True for verbose logging

# Create logger
logger = logging.getLogger('VoiceClick')
logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')
console_handler.setFormatter(console_formatter)

# File handler with rotation (keep last 5MB)
file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def log_error(error_msg, exception=None):
    """Centralized error logging with traceback"""
    logger.error(error_msg)
    if exception:
        logger.error(f"Exception type: {type(exception).__name__}")
        logger.error(f"Exception details: {str(exception)}")
        logger.debug(traceback.format_exc())

def log_info(msg):
    """Centralized info logging"""
    logger.info(msg)

def log_debug(msg):
    """Centralized debug logging"""
    logger.debug(msg)

# GUITHREADINFO structure
class GUITHREADINFO(Structure):
    _fields_ = [
        ("cbSize", c_ulong),
        ("flags", c_ulong),
        ("hwndActive", wintypes.HWND),
        ("hwndFocus", wintypes.HWND),
        ("hwndCapture", wintypes.HWND),
        ("hwndMenuOwner", wintypes.HWND),
        ("hwndMoveSize", wintypes.HWND),
        ("hwndCaret", wintypes.HWND),
        ("rcCaret", wintypes.RECT),
    ]

# Configuration
SAMPLE_RATE = 16000 # Fixed audio setting

# History file location (fixed)
HISTORY_FILE = Path.home() / ".voice_click_history.json"

# NOTE: All configuration constants are now accessed via config_manager.get('key')

# Globals
is_recording = False
audio_queue = Queue()  # Thread-safe audio buffer
model = None
status_widget = None
settings_widget = None # New global for settings widget
recording_start_time = 0
current_volume = 0.0
transcription_history = deque(maxlen=config_manager.get('max_history'))
last_silence_time = 0
auto_stopped = False
focus_monitor_thread = None
focus_monitor_stop = False
original_focused_hwnd = None  # Track focused control when recording starts
mouse_move_history = deque(maxlen=10) # Store (x, y, timestamp) for shake detection
beep_thread = None
stop_beeping = False
recording_lock = threading.Lock()  # Thread safety

# --- Settings Widget ---

def toggle_settings_widget():
    """Toggles the visibility of the settings widget."""
    global settings_widget
    if settings_widget:
        if settings_widget.is_visible:
            settings_widget.hide()
        else:
            settings_widget.show()

class SettingsWidget:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.95)
        self.is_visible = False
        
        # 1. Update Widget Dimensions: 600x500 (Increased height for button visibility)
        w, h = 600, 500
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - w - 10
        y = screen_height - h - 50 # Position above the taskbar
        
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        
        # Dragging setup
        self._offsetx = 0
        self._offsety = 0
        self.root.bind('<Button-1>', self.start_move)
        self.root.bind('<ButtonRelease-1>', self.stop_move)
        self.root.bind('<B1-Motion>', self.do_move)
        
        self.descriptions = config_manager.get_descriptions() # Fetch descriptions
        
        # Use a style for better appearance
        self.style = ttk.Style()
        self.style.theme_use('clam') # Use a theme that supports customization
        self.style.configure('TNotebook', background='#3c3c3c', borderwidth=0)
        self.style.configure('TNotebook.Tab', background='#505050', foreground='white', padding=[10, 5])
        self.style.map('TNotebook.Tab', background=[('selected', '#2ecc71')], foreground=[('selected', 'black')])
        self.style.configure('TFrame', background='#3c3c3c')
        self.style.configure('TLabel', background='#3c3c3c', foreground='white')
        self.style.configure('TCheckbutton', background='#3c3c3c', foreground='white')
        self.style.configure('TCombobox', fieldbackground='white', foreground='black')
        
        self.frame = ttk.Frame(self.root, padding="5 5 5 5")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(self.frame, text="VoiceClick Settings", font=('Segoe UI', 14, 'bold'), fg='white', bg='#3c3c3c').pack(pady=5)
        
        # 2. Implement Tabbed Layout
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(pady=10, padx=5, fill=tk.BOTH, expand=True)
        
        # 3. Define and link 18 tk.Variable instances
        self.vars = {}
        self.settings_map = {
            # Tab 1: General & Mouse
            'General & Mouse': [
                ('mouse_shake_threshold_px', tk.IntVar, 'Mouse Shake Threshold (px):', 'Entry', None),
                ('mouse_shake_time_ms', tk.IntVar, 'Mouse Shake Time (ms):', 'Entry', None),
                ('enable_manual_stop', tk.BooleanVar, 'Enable Manual Stop (Middle-Click):', 'Checkbutton', None),
                ('require_text_field', tk.BooleanVar, 'Require Text Field to Start:', 'Checkbutton', None),
                ('max_history', tk.IntVar, 'Max History Entries:', 'Entry', None),
            ],
            # Tab 2: Auto-Start
            'Auto-Start': [
                ('auto_start_on_focus', tk.BooleanVar, 'Auto-Start on Text Field Focus:', 'Checkbutton', None),
                ('auto_start_on_left_click', tk.BooleanVar, 'Auto-Start on Left-Click:', 'Checkbutton', None),
                ('auto_start_delay', tk.DoubleVar, 'Auto-Start Delay (s):', 'Entry', None),
                ('ignore_password_fields', tk.BooleanVar, 'Ignore Password Fields:', 'Checkbutton', None),
                ('ignore_fullscreen_games', tk.BooleanVar, 'Ignore Fullscreen Games:', 'Checkbutton', None),
            ],
            # Tab 3: Audio & Auto-Stop
            'Audio & Auto-Stop': [
                ('volume_threshold', tk.DoubleVar, 'Volume Threshold (RMS):', 'Entry', None),
                ('enable_silence_auto_stop', tk.BooleanVar, 'Enable Silence Auto-Stop:', 'Checkbutton', None),
                ('silence_duration', tk.DoubleVar, 'Silence Duration (s):', 'Entry', None),
                ('max_recording_time', tk.IntVar, 'Max Recording Time (s):', 'Entry', None),
                ('enable_audio_feedback', tk.BooleanVar, 'Enable Audio Feedback (Beeps):', 'Checkbutton', None), # New setting
            ],
            # Tab 4: Transcription Model
            'Transcription Model': [
                ('whisper_model', tk.StringVar, 'Whisper Model:', 'Combobox', ['tiny', 'base', 'small', 'medium', 'large-v2', 'large-v3']),
                ('whisper_device', tk.StringVar, 'Whisper Device:', 'Combobox', ['cpu', 'cuda']),
                ('whisper_compute_type', tk.StringVar, 'Compute Type:', 'Combobox', ['float16', 'int8', 'float32']),
                ('transcription_language', tk.StringVar, 'Transcription Language:', 'Combobox', ['en', 'tr', 'de']),
            ]
        }
        
        # 4. Implement UI controls
        for tab_name, settings in self.settings_map.items():
            tab = ttk.Frame(self.notebook, padding="10")
            self.notebook.add(tab, text=tab_name)
            
            for key, var_type, label_text, control_type, options in settings:
                self.vars[key] = var_type(value=config_manager.get(key))
                description = self.descriptions.get(key, "No description available.")
                self._create_control(tab, key, label_text, control_type, options, description)

        # Save/Close Button
        tk.Button(self.frame, text="Save & Close", command=self.save_and_hide, bg='#2ecc71', fg='black', relief=tk.FLAT, font=('Segoe UI', 10, 'bold')).pack(pady=10)

    def _create_control(self, parent, key, label_text, control_type, options=None, description=""):
        """Helper function to create a setting control."""
        
        # Container frame for label, control, and description
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.X, pady=2, padx=5)
        
        # Frame for label and control (top row)
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X)
        
        # Label
        ttk.Label(control_frame, text=label_text, width=30, anchor='w').pack(side=tk.LEFT, padx=5)
        
        # Control
        if control_type == 'Entry':
            entry = ttk.Entry(control_frame, textvariable=self.vars[key], width=15)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        elif control_type == 'Checkbutton':
            # Checkbuttons need a specific style to look good on dark background
            ttk.Checkbutton(control_frame, variable=self.vars[key], text="", style='TCheckbutton').pack(side=tk.LEFT, padx=5)
        elif control_type == 'Combobox':
            combo = ttk.Combobox(control_frame, textvariable=self.vars[key], values=options, state='readonly', width=13)
            combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
        # Description (Accessibility feature)
        if description:
            ttk.Label(main_frame, text=description, wraplength=550, justify=tk.LEFT, font=('Segoe UI', 8, 'italic'), foreground='#aaaaaa').pack(fill=tk.X, padx=10, pady=(0, 5))

    def start_move(self, event):
        self._offsetx = event.x
        self._offsety = event.y

    def stop_move(self, event):
        self._offsetx = 0
        self._offsety = 0

    def do_move(self, event):
        x = self.root.winfo_x() + event.x - self._offsetx
        y = self.root.winfo_y() + event.y - self._offsety
        self.root.geometry(f"+{x}+{y}")

    def save_and_hide(self):
        """Saves the current settings and hides the widget."""
        log_info("Attempting to save all settings...")
        success_count = 0
        error_count = 0
        
        for key, tk_var in self.vars.items():
            try:
                # 5. Refactor Save Logic: Get value and attempt to convert/validate
                value = tk_var.get()
                
                # Tkinter BooleanVar returns 0/1, convert to Python bool
                if isinstance(tk_var, tk.BooleanVar):
                    value = bool(value)
                
                # Tkinter DoubleVar/IntVar returns float/int, which is fine.
                
                if config_manager.set(key, value):
                    log_debug(f"Successfully set config key '{key}' to '{value}'")
                    success_count += 1
                else:
                    error_count += 1
                    log_error(f"Failed to set config key '{key}' with value '{value}' (Validation failed in config_manager)")
                    
            except Exception as e:
                error_count += 1
                log_error(f"Error processing setting '{key}' with value '{value}': {e}")
        
        log_info(f"Settings save complete: {success_count} successful, {error_count} failed.")
        self.hide()

    def show(self):
        """Shows the widget and updates values."""
        # Update all variables from config before showing
        for key, tk_var in self.vars.items():
            tk_var.set(config_manager.get(key))
            
        self.root.deiconify()
        self.root.update()
        self.is_visible = True

    def hide(self):
        """Hides the widget."""
        self.root.withdraw()
        self.is_visible = False

# --- Status Widget (appears only during recording/transcribing)
class RecordingWidget:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Start hidden
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.95)
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Taskbar-style widget (horizontal, compact)
        w, h = 320, 40  # Taskbar height is typically 40-48px
        
        # Position at bottom-right, at taskbar level
        # This makes it appear as part of the taskbar, next to system tray
        x = screen_width - w - 250  # Leave space for system tray icons (clock, etc.)
        y = screen_height - h  # Exactly at bottom (taskbar level)
        
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        
        # Taskbar-style flat design
        self.frame = tk.Frame(self.root, bd=0, relief=tk.FLAT, bg='#2b2b2b')
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Horizontal layout
        self.icon_label = tk.Label(
            self.frame,
            text="",
            font=('Segoe UI', 12),
            fg='white',
            bg='#2b2b2b',
            width=3
        )
        self.icon_label.pack(side=tk.LEFT, padx=5)
        
        self.status_label = tk.Label(
            self.frame, 
            text="", 
            font=('Segoe UI', 10, 'bold'),
            fg='white',
            bg='#2b2b2b',
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Volume bar container (small, horizontal)
        self.volume_frame = tk.Frame(self.frame, bg='#2b2b2b')
        self.volume_frame.pack(side=tk.RIGHT, padx=5)
        
        self.volume_bar = tk.Canvas(self.volume_frame, width=60, height=20, bg='#1a1a1a', highlightthickness=0)
        self.volume_bar.pack()
        
        self.volume_indicator = self.volume_bar.create_rectangle(0, 0, 0, 20, fill='#2ecc71', outline='')
        
        self.update_job = None
        self.volume_update_job = None
    
    def show_recording(self):
        """Show recording status"""
        self.frame.config(bg='#c0392b')
        self.icon_label.config(text="🔴", bg='#c0392b')
        self.status_label.config(text="Recording...", bg='#c0392b')
        self.root.deiconify()
        self.root.update()
        
        # Start duration counter and volume monitor
        self.update_duration()
        self.update_volume()
    
    def update_duration(self):
        """Update recording duration"""
        if is_recording:
            duration = time.time() - recording_start_time
            self.status_label.config(text=f"Recording {duration:.1f}s")
            self.update_job = self.root.after(100, self.update_duration)
    
    def update_volume(self):
        """Update volume indicator"""
        if is_recording:
            volume_threshold = config_manager.get('volume_threshold')
            
            # Update volume bar
            bar_width = 60
            volume_width = int(min(current_volume * 1000, bar_width))
            
            # Color based on volume level
            if current_volume > volume_threshold * 3:
                color = '#2ecc71'  # Green - good volume
            elif current_volume > volume_threshold:
                color = '#f39c12'  # Orange - moderate
            else:
                color = '#e74c3c'  # Red - too quiet
            
            self.volume_bar.coords(self.volume_indicator, 0, 0, volume_width, 20)
            self.volume_bar.itemconfig(self.volume_indicator, fill=color)
            
            self.volume_update_job = self.root.after(50, self.update_volume)
    
    def show_processing(self):
        """Show processing status"""
        if self.update_job:
            self.root.after_cancel(self.update_job)
            self.update_job = None
        if self.volume_update_job:
            self.root.after_cancel(self.volume_update_job)
            self.volume_update_job = None
        
        self.frame.config(bg='#f39c12')
        self.icon_label.config(text="⏳", bg='#f39c12')
        self.status_label.config(text="Transcribing...", bg='#f39c12')
        self.volume_bar.pack_forget()  # Hide volume bar
        self.root.update()
    
    def show_result(self, text, word_count):
        """Show transcription result"""
        self.frame.config(bg='#27ae60')
        self.icon_label.config(text="✓", bg='#27ae60')
        preview = text[:35] + ("..." if len(text) > 35 else "")
        self.status_label.config(text=f"{word_count}w: {preview}", bg='#27ae60')
        self.root.update()
    
    def show_error(self, msg):
        """Show error"""
        self.frame.config(bg='#7f8c8d')
        self.icon_label.config(text="⚠", bg='#7f8c8d')
        self.status_label.config(text=msg, bg='#7f8c8d')
        self.root.update()
    
    def show_cancelled(self):
        """Show cancelled status"""
        if self.update_job:
            self.root.after_cancel(self.update_job)
            self.update_job = None
        if self.volume_update_job:
            self.root.after_cancel(self.volume_update_job)
            self.volume_update_job = None
            
        self.frame.config(bg='#7f8c8d')
        self.icon_label.config(text="✖", bg='#7f8c8d')
        self.status_label.config(text="Cancelled", bg='#7f8c8d')
        self.volume_bar.pack_forget()
        self.root.update()
    
    def hide(self):
        """Hide widget"""
        if self.update_job:
            self.root.after_cancel(self.update_job)
            self.update_job = None
        if self.volume_update_job:
            self.root.after_cancel(self.volume_update_job)
            self.volume_update_job = None
        self.root.withdraw()

def is_fullscreen_game():
    """Detect if current window is a fullscreen game or app"""
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return False
        
        # Get window title and class
        title = win32gui.GetWindowText(hwnd).lower()
        class_name = win32gui.GetClassName(hwnd).lower()
        
        # Get window rect
        rect = win32gui.GetWindowRect(hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        
        # Get screen dimensions
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        
        # Check if window is fullscreen (covers entire screen)
        is_fullscreen = (width >= screen_width - 10 and height >= screen_height - 10)
        
        # Common game engine class names
        game_classes = [
            'unitywindowclass',  # Unity games
            'unrealwindow',      # Unreal Engine
            'sdl_app',           # SDL games
            'd3d',               # DirectX
            'opengl',            # OpenGL
            'gameoverlayui',     # Steam overlay
        ]
        
        # Common game keywords in titles
        game_keywords = [
            'game', 'steam', 'epic', 'origin', 'uplay', 'gog',
            'league of legends', 'valorant', 'fortnite', 'minecraft',
            'counter-strike', 'dota', 'overwatch', 'apex', 'warzone',
            'rocket league', 'genshin', 'final fantasy', 'world of warcraft',
            'destiny', 'battlefield', 'call of duty', 'assassin', 'cyberpunk',
            'the witcher', 'elden ring', 'dark souls', 'starcraft', 'diablo'
        ]
        
            # Check class name
        for game_class in game_classes:
            if game_class in class_name:
                log_debug(f"Fullscreen game detected (class): {class_name}")
                return True
        
        # Check if fullscreen AND has game keywords in title
        if is_fullscreen:
            for keyword in game_keywords:
                if keyword in title:
                    log_debug(f"Fullscreen game detected (title): {title[:50]}")
                    return True
            
            # Generic fullscreen detection (no menu bar, fullscreen size)
            # Exclude known desktop apps
            desktop_keywords = ['explorer', 'taskbar', 'chrome', 'firefox', 'edge', 
                              'code', 'visual studio', 'notepad', 'word', 'excel']
            
            is_desktop_app = any(kw in title for kw in desktop_keywords)
            
            if not is_desktop_app:
                # Likely a game or video player in fullscreen
                log_debug(f"Generic fullscreen app detected: {title[:50]}")
                return True
        
        return False
        
    except Exception as e:
        log_debug(f"Fullscreen detection error: {e}")
        return False

def is_text_field():
    """Comprehensive text field detection - checks multiple signals"""
    try:
        detected = False
        detection_method = ""
        score = 0  # Confidence score
        
        # Get window info
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd) if hwnd else ""
        class_name = ""
        cursor_handle = 0
        
        # Method 1: Check cursor type (I-beam = text cursor) - STRONGEST SIGNAL
        class CURSORINFO(Structure):
            _fields_ = [("cbSize", wintypes.DWORD),
                       ("flags", wintypes.DWORD),
                       ("hCursor", wintypes.HANDLE),  # Use HANDLE instead of HCURSOR
                       ("ptScreenPos", wintypes.POINT)]
        
        cursor_info = CURSORINFO()
        cursor_info.cbSize = ctypes.sizeof(CURSORINFO)
        if ctypes.windll.user32.GetCursorInfo(ctypes.byref(cursor_info)):
            cursor_handle = cursor_info.hCursor
            # I-beam cursor handles (varies by system/theme)
            # Common values: 65541 (standard), 65567, 65559
            # Arrow cursor: 65543, Hand: 65567
            ibeam_handles = [65541, 65567, 65559, 65553]
            if cursor_handle in ibeam_handles:
                score += 50  # Strong indicator
                detection_method = f"I-beam cursor ({cursor_handle})"
        
        # Method 2: Get focused control class name
        gui_info = GUITHREADINFO()
        gui_info.cbSize = ctypes.sizeof(GUITHREADINFO)
        if ctypes.windll.user32.GetGUIThreadInfo(0, ctypes.byref(gui_info)):
            if gui_info.hwndFocus:
                try:
                    class_name = win32gui.GetClassName(gui_info.hwndFocus)
                    
                    # Comprehensive list of text field class names
                    text_classes = [
                        'edit',           # Standard Windows edit control
                        'richedit',       # Rich edit controls
                        'richedit20',     # Rich edit 2.0+
                        'scintilla',      # Scintilla editor (Notepad++, VS Code)
                        'chrome_renderwidgethost', # Chrome/Edge text fields
                        'chrome_widgetwin',        # Chrome windows
                        'mozilla',        # Firefox
                        'gecko',          # Firefox engine
                        'textfield',      # Generic text field
                        'textarea',       # Textarea elements
                        'input',          # Input elements
                        'edit control',   # Edit controls
                        'text',           # General text controls
                        'contenteditable', # Contenteditable divs
                        'electron',       # Electron apps (VS Code, Discord)
                        'afx:',           # MFC apps (Microsoft Office)
                        '_wndclass_',     # Custom text controls
                        'directuihwnd',   # Modern Windows UI
                        'windows.ui.core', # UWP text controls
                    ]
                    
                    class_lower = class_name.lower()
                    for text_class in text_classes:
                        if text_class in class_lower:
                            score += 40
                            if not detection_method:
                                detection_method = f"Class: {class_name}"
                            break
                except:
                    pass
        
        # Method 3: Check application window title - SUPPLEMENTARY
        apps_and_keywords = {
            # Text editors
            'notepad': 30, 'wordpad': 30, 'word': 30, 'excel': 30,
            'visual studio code': 35, 'code': 20, 'vscode': 35,
            'sublime': 35, 'atom': 35, 'vim': 35, 'emacs': 35,
            'notepad++': 35, 'brackets': 35, 'gedit': 35,
            
            # Browsers (usually have text fields)
            'chrome': 25, 'firefox': 25, 'edge': 25, 'brave': 25,
            'opera': 25, 'safari': 25, 'vivaldi': 25,
            
            # Communication apps
            'discord': 30, 'slack': 30, 'teams': 30, 'zoom': 25,
            'telegram': 30, 'whatsapp': 30, 'signal': 30,
            'messenger': 30, 'skype': 25,
            
            # Note-taking apps
            'obsidian': 35, 'notion': 35, 'evernote': 35,
            'onenote': 35, 'typora': 35, 'bear': 35,
            'roam': 35, 'logseq': 35, 'remnote': 35,
            
            # IDEs
            'pycharm': 35, 'intellij': 35, 'webstorm': 35,
            'rider': 35, 'eclipse': 35, 'netbeans': 35,
            'android studio': 35,
            
            # Office apps
            'outlook': 25, 'thunderbird': 30, 'gmail': 25,
            'docs': 30, 'sheets': 25, 'slides': 25,
            
            # Other
            'terminal': 30, 'powershell': 30, 'cmd': 30,
            'git': 20, 'sql': 25, 'database': 20,
        }
        
        title_lower = title.lower()
        for app, points in apps_and_keywords.items():
            if app in title_lower:
                score += points
                if not detection_method:
                    detection_method = f"App: {app}"
                break
        
        # Method 4: Check if window has a caret (text cursor position)
        if gui_info.hwndFocus and gui_info.rcCaret.left >= 0:
            score += 20
            if not detection_method:
                detection_method = "Caret detected"
        
        # Method 5: Additional window style checks
        if hwnd:
            try:
                # Get window style
                style = ctypes.windll.user32.GetWindowLongW(hwnd, -16)  # GWL_STYLE
                ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)  # GWL_EXSTYLE
                
                # ES_MULTILINE, ES_READONLY, ES_PASSWORD indicators
                # ES_MULTILINE
                if style & 0x0004:
                    score += 15
                # ES_PASSWORD (don't auto-start on password fields)
                ES_PASSWORD = 0x0020
                if style & ES_PASSWORD:
                    # Strong indicator this is a password field; subtract score or mark
                    score -= 100
            except:
                pass
        
        # Check if it's taskbar or system tray (ignore these)
        taskbar_classes = ['shell_traywnd', 'button', 'tooltips_class32', 'shell_secondarytraywnd']
        if class_name.lower() in taskbar_classes or 'taskbar' in title.lower() or 'tray' in class_name.lower():
            log_debug(f"Ignoring taskbar/system element: {class_name}")
            return False
        
        # Decision threshold - increased to reduce false positives
        detected = score >= 60  # Need at least 60 points to confirm text field (was 40)
        
        if detected:
            log_info(f"✓ Text field detected (score: {score}) via {detection_method}")
        else:
            log_debug(f"✗ Not a text field (score: {score}) - Window: '{title[:40]}', Class: '{class_name}', Cursor: {cursor_handle}")
        
        return detected
        
    except Exception as e:
        log_error(f"Text field detection error: {e}", e)
        # When error occurs, be conservative - don't allow
        return False

def audio_callback(indata, frames, time_info, status_flag):
    """Sounddevice callback - thread-safe with volume monitoring"""
    global current_volume, last_silence_time
    
    try:
        if status_flag:
            log_debug(f"Audio callback status: {status_flag}")
        
        if is_recording:
            audio_queue.put(indata.copy())
            
            # Calculate current volume (RMS)
            current_volume = np.sqrt(np.mean(indata**2))
            
            # Track silence for auto-stop
            if config_manager.get('enable_silence_auto_stop'):
                volume_threshold = config_manager.get('volume_threshold')
                if current_volume < volume_threshold:
                    if last_silence_time == 0:
                        last_silence_time = time.time()
                else:
                    last_silence_time = 0
    except Exception as e:
        log_error(f"Audio callback error: {e}", e)

def play_sound(sound_type):
    """Play enhanced audio feedback"""
    if not config_manager.get('enable_audio_feedback'):
        return
        
    try:
        sounds = {
            'start': [(1000, 80), (1200, 80)],      # Rising beep-beep
            'stop': [(1000, 80), (800, 80)],        # Falling beep-beep
            'pulse': [(800, 60)],                    # Soft pulse
            'success': [(1000, 60), (1200, 60), (1400, 80)],  # Rising melody
            'error': [(400, 150)],                   # Low error beep
            'cancel': [(600, 80), (400, 80)]        # Falling cancel beeps
        }
        
        for freq, duration in sounds.get(sound_type, []):
            winsound.Beep(freq, duration)
            time.sleep(0.05)
    except Exception as e:
        log_debug(f"Sound playback error: {e}")

def recording_beep_loop():
    """Play soft beeps during recording"""
    global stop_beeping
    while not stop_beeping:
        if is_recording:
            play_sound('pulse')
            time.sleep(2)  # Beep every 2 seconds
        else:
            time.sleep(0.1)

def start_recording():
    """Start recording with advanced features"""
    global is_recording, recording_start_time, beep_thread, stop_beeping, last_silence_time, auto_stopped, original_focused_hwnd
    
    try:
        with recording_lock:
            if is_recording:
                return
            
            # Check for fullscreen games
            if config_manager.get('ignore_fullscreen_games') and is_fullscreen_game():
                log_info("Ignoring auto-start - fullscreen game/app detected")
                return
            
            # Store the currently focused control for paste validation later
            try:
                gui_info = GUITHREADINFO()
                gui_info.cbSize = ctypes.sizeof(GUITHREADINFO)
                if ctypes.windll.user32.GetGUIThreadInfo(0, ctypes.byref(gui_info)):
                    original_focused_hwnd = gui_info.hwndFocus
                    log_debug(f"Stored original focus: {original_focused_hwnd}")
            except Exception as e:
                log_debug(f"Failed to store focused hwnd: {e}")
                original_focused_hwnd = None
            
            # Clear audio queue
            while not audio_queue.empty():
                audio_queue.get()
            
            is_recording = True
            recording_start_time = time.time()
            last_silence_time = 0
            auto_stopped = False
        
        # Play start sound
        threading.Thread(target=play_sound, args=('start',), daemon=True).start()
        
        # Start continuous beeping thread
        stop_beeping = False
        beep_thread = threading.Thread(target=recording_beep_loop, daemon=True)
        beep_thread.start()
        
        # Start auto-stop monitor (if silence auto-stop enabled or max time set)
        silence_enabled = config_manager.get('enable_silence_auto_stop')
        silence_duration = config_manager.get('silence_duration')
        max_time = config_manager.get('max_recording_time')
        
        if (silence_enabled and silence_duration > 0) or max_time > 0:
            threading.Thread(target=auto_stop_monitor, daemon=True).start()
        
        status_widget.show_recording()
        
        # Build status message based on enabled stop methods
        stop_methods = []
        if config_manager.get('enable_manual_stop'):
            stop_methods.append("Middle-click to stop")
        if silence_enabled:
            stop_methods.append(f"auto-stop after {silence_duration}s silence")
        
        stop_msg = ", ".join(stop_methods) if stop_methods else "Recording..."
        log_info(f"Recording started - {stop_msg}, Right-click to cancel")
    
    except Exception as e:
        log_error(f"Failed to start recording: {e}", e)
        is_recording = False
        if status_widget:
            status_widget.show_error("START ERROR")
            time.sleep(2)
            status_widget.hide()

def auto_stop_monitor():
    """Monitor for auto-stop conditions"""
    global auto_stopped
    
    try:
        silence_enabled = config_manager.get('enable_silence_auto_stop')
        silence_duration = config_manager.get('silence_duration')
        max_time = config_manager.get('max_recording_time')
        
        while is_recording:
            # Check configurable silence timeout
            if silence_enabled and silence_duration > 0 and last_silence_time > 0:
                if time.time() - last_silence_time > silence_duration:
                    log_info(f"Auto-stopping after {silence_duration}s of silence")
                    auto_stopped = True
                    stop_recording()
                    break
            
            # Check max recording time
            if max_time > 0:
                duration = time.time() - recording_start_time
                if duration >= max_time:
                    log_info(f"Auto-stopping after {max_time}s max duration")
                    auto_stopped = True
                    stop_recording()
                    break
            
            time.sleep(0.1)
    except Exception as e:
        log_error(f"Auto-stop monitor error: {e}", e)

def stop_recording():
    """Stop recording and transcribe"""
    global is_recording, stop_beeping
    
    try:
        with recording_lock:
            if not is_recording:
                return
            is_recording = False
            stop_beeping = True
        
        # Play stop sound
        threading.Thread(target=play_sound, args=('stop',), daemon=True).start()
        
        status_widget.show_processing()
        
        # Collect audio from queue
        audio_frames = []
        while not audio_queue.empty():
            audio_frames.append(audio_queue.get())
        
        duration = len(audio_frames) * 0.03
        log_info(f"Recorded {duration:.1f}s, transcribing...")
        
        if len(audio_frames) < 10:
            log_info("Recording too short, ignoring")
            status_widget.show_error("TOO SHORT")
            time.sleep(1.5)
            status_widget.hide()
            return
        
        # Transcribe
        threading.Thread(target=transcribe_audio, args=(audio_frames,), daemon=True).start()
    
    except Exception as e:
        log_error(f"Failed to stop recording: {e}", e)
        status_widget.show_error("STOP ERROR")
        time.sleep(2)
        status_widget.hide()

def cancel_recording():
    """Cancel recording without transcribing"""
    global is_recording, stop_beeping
    
    with recording_lock:
        if not is_recording:
            return
        is_recording = False
        stop_beeping = True
    
    # Clear audio queue
    while not audio_queue.empty():
        audio_queue.get()
    
    # Play cancel sound
    threading.Thread(target=play_sound, args=('cancel',), daemon=True).start()
    
    status_widget.show_cancelled()
    log_info("Recording cancelled")
    
    time.sleep(1.5)
    status_widget.hide()

def transcribe_audio(frames):
    """Transcribe audio - filters background chatter with advanced features"""
    global model
    
    try:
        # Store the active window before showing processing widget
        active_window = win32gui.GetForegroundWindow()
        
        # Combine audio
        audio = np.concatenate(frames, axis=0).flatten().astype(np.float32)
        
        # Normalize
        max_val = np.abs(audio).max()
        if max_val > 0:
            audio = audio / max_val
        
        duration = len(audio) / SAMPLE_RATE
        avg_volume = np.sqrt(np.mean(audio**2))
        
        log_info(f"Processing {duration:.1f}s (avg volume: {avg_volume:.4f})...")
        
        # Transcribe with advanced VAD
        segments, info = model.transcribe(
            audio,
            language="en",
            beam_size=5,
            temperature=0.0,
            best_of=1,
            vad_filter=True,
            vad_parameters=dict(
                min_speech_duration_ms=500,
                max_speech_duration_s=30,
                min_silence_duration_ms=500,
                speech_pad_ms=300
            ),
            condition_on_previous_text=False,
            compression_ratio_threshold=2.0,
            log_prob_threshold=-0.8,
            no_speech_threshold=0.5
        )
        
        # Get text with word-level timing
        text = ""
        word_count = 0
        for segment in segments:
            segment_text = segment.text.strip()
            if len(segment_text) < 2:
                continue
            text += segment_text + " "
            word_count += len(segment_text.split())
        
        text = text.strip()
        
        if text:
            log_info(f"Transcription: '{text}' ({word_count} words)")
            
            # Copy to clipboard FIRST
            try:
                pyperclip.copy(text)
                log_info("✓ Copied to clipboard")
            except Exception as e:
                log_error(f"Failed to copy to clipboard: {e}", e)
            
            # Save to history
            save_to_history(text, duration, avg_volume, word_count)
            
            # Show success message first
            play_sound('success')
            status_widget.show_result(text, word_count)
            
            # Validate focus before pasting
            focus_valid = False
            try:
                # Check if the original focused control is still focused
                gui_info = GUITHREADINFO()
                gui_info.cbSize = ctypes.sizeof(GUITHREADINFO)
                if ctypes.windll.user32.GetGUIThreadInfo(0, ctypes.byref(gui_info)):
                    current_focused = gui_info.hwndFocus
                    if original_focused_hwnd and current_focused == original_focused_hwnd:
                        focus_valid = True
                        log_info("✓ Focus validation passed - same control still focused")
                    else:
                        log_info(f"⚠ Focus changed: original={original_focused_hwnd}, current={current_focused}")
                        # Still allow paste but warn user
                        focus_valid = True  # Be forgiving - still attempt paste
            except Exception as e:
                log_error(f"Focus validation error: {e}", e)
                focus_valid = True  # Be forgiving on error
            
            if not focus_valid:
                log_info("⚠ Skipping auto-paste - focus changed. Text is in clipboard (Ctrl+V to paste)")
                time.sleep(2.5)
                status_widget.hide()
                return
            
            # Return focus to original window and wait for it to be ready
            try:
                win32gui.SetForegroundWindow(active_window)
                time.sleep(0.3)  # Wait for window to become active
                log_info("✓ Focus restored to original window")
            except Exception as e:
                log_error(f"Failed to restore focus: {e}", e)
                time.sleep(0.2)
            
            # Try multiple methods to insert text
            insert_success = False
            
            # Method 1: Simulate Ctrl+V (paste from clipboard) - MOST RELIABLE
            try:
                keyboard.press_and_release('ctrl+v')
                time.sleep(0.05)
                insert_success = True
                log_info("✓ Text pasted via Ctrl+V")
            except Exception as e:
                log_error(f"Paste failed: {e}", e)
            
            # Method 2: Direct keyboard typing (if paste failed)
            if not insert_success:
                try:
                    time.sleep(0.1)
                    keyboard.write(text + " ")
                    insert_success = True
                    log_info("✓ Text typed via keyboard library")
                except Exception as e:
                    log_error(f"Keyboard typing failed: {e}", e)
            
            # Method 3: Using pyautogui as fallback (if available)
            if not insert_success:
                try:
                    import pyautogui
                    time.sleep(0.1)
                    pyautogui.typewrite(text + " ", interval=0.01)
                    insert_success = True
                    log_info("✓ Text typed via pyautogui")
                except Exception as e:
                    log_debug(f"Pyautogui typing failed: {e}")
            
            if not insert_success:
                log_info("⚠ Auto-type failed - text is in clipboard, paste with Ctrl+V")
            
            time.sleep(2.5)
        else:
            log_info("No clear speech detected")
            status_widget.show_error("NO SPEECH")
            time.sleep(1.5)
        
        status_widget.hide()
    
    except Exception as e:
        log_error(f"Transcription error: {e}", e)
        play_sound('error')
        status_widget.show_error("ERROR")
        time.sleep(2)
        status_widget.hide()

def focus_monitor():
    """Background thread: monitor foreground focus and auto-start recording when a text field is focused."""
    global focus_monitor_stop
    last_focused_hwnd = None
    debounce_time = config_manager.get('auto_start_delay')

    try:
        while not focus_monitor_stop:
            try:
                hwnd = win32gui.GetForegroundWindow()
                if hwnd and hwnd != last_focused_hwnd:
                    # Give the focus a moment to settle
                    time.sleep(debounce_time)
                    if is_text_field():
                        log_debug("Focus monitor: text field focused")
                        if config_manager.get('auto_start_on_focus') and not is_recording:
                            start_recording()
                    last_focused_hwnd = hwnd
            except Exception as e:
                log_debug(f"Focus monitor iteration error: {e}")

            time.sleep(0.15)
    except Exception as e:
        log_error(f"Focus monitor fatal error: {e}", e)

def save_to_history(text, duration, volume, word_count):
    """Save transcription to history"""
    try:
        entry = {
            'timestamp': datetime.now().isoformat(),
            'text': text,
            'duration': float(duration),  # Convert to Python float
            'volume': float(volume),      # Convert to Python float
            'word_count': int(word_count), # Convert to Python int
            'auto_stopped': bool(auto_stopped)  # Convert to Python bool
        }
        
        transcription_history.append(entry)
        
        # Save to file
        history_list = list(transcription_history)
        HISTORY_FILE.write_text(json.dumps(history_list, indent=2))
        
        log_debug(f"Saved to history: {len(transcription_history)} entries")
    except Exception as e:
        log_error(f"Failed to save history: {e}", e)

def on_move(x, y):
    """Mouse movement handler - checks for mouse shake to stop recording"""
    global mouse_move_history
    
    if not is_recording:
        return
    log_debug(f"on_move: Current shake_threshold={shake_threshold}")
    
    current_time = time.time() * 1000 # Convert to milliseconds
    
    shake_threshold = config_manager.get('mouse_shake_threshold_px')
    shake_time_ms = config_manager.get('mouse_shake_time_ms')
    
    # 1. Add current position to history
    mouse_move_history.append((x, y, current_time))
    
    # 2. Filter history to the last shake_time_ms
    time_limit = current_time - shake_time_ms
    
    # Remove old entries
    while mouse_move_history and mouse_move_history[0][2] < time_limit:
        mouse_move_history.popleft()
        
    if len(mouse_move_history) < 2:
        return
        
    # 3. Calculate total distance moved (Euclidean distance sum)
    total_distance = 0
    
    # Start from the oldest point in the current window
    x_start, y_start, _ = mouse_move_history[0]
    
    # Calculate total distance from start point to end point
    x_end, y_end, _ = mouse_move_history[-1]
    
    # Calculate straight-line distance between start and end points
    distance = ((x_end - x_start)**2 + (y_end - y_start)**2)**0.5
    
    # 4. Check for shake threshold
    if distance > shake_threshold:
        log_info(f"Mouse shake detected: {distance:.1f}px moved in {shake_time_ms}ms - stopping recording")
        stop_recording()
        
def load_history():
    """Load transcription history from file"""
    try:
        if HISTORY_FILE.exists():
            data = json.loads(HISTORY_FILE.read_text())
            transcription_history.extend(data)
            log_info(f"Loaded {len(transcription_history)} history entries")
    except Exception as e:
        log_error(f"Failed to load history: {e}", e)

def on_click(x, y, button, pressed):
    """Mouse click handler - Any click stops recording, Right-click cancels, Middle-click toggles start/stop"""
    
    if not pressed:
        return
    
    # Ignore widget clicks
    try:
        if status_widget.root.winfo_viewable():
            wx = status_widget.root.winfo_x()
            wy = status_widget.root.winfo_y()
            ww = status_widget.root.winfo_width()
            wh = status_widget.root.winfo_height()
            if wx <= x <= wx+ww and wy <= y <= wy+wh:
                return
    except Exception as e:
        log_debug(f"Widget check error: {e}")
    
    # --- Stop/Cancel Logic (Priority when recording) ---
    if is_recording:
        if button == mouse.Button.right:
            log_info("Right-click detected - cancelling recording")
            cancel_recording()
            return
        
        # Any other click stops transcription if manual stop is enabled
        if config_manager.get('enable_manual_stop'):
            log_info(f"Any click detected ({button}) - stopping recording")
            stop_recording()
            return
        else:
            log_debug(f"Click ignored ({button}) - manual stop disabled (waiting for auto-stop)")
            return
    
    # --- Start Logic (Only when not recording) ---
    
    # Middle mouse button - Start recording
    if button == mouse.Button.middle:
        # Check if text field detection is required
        if config_manager.get('require_text_field'):
            if is_text_field():
                log_info("Middle-click detected - starting recording")
                start_recording()
            else:
                log_info("Middle-click ignored - not in text field")
                # Brief visual feedback
                status_widget.show_error("NOT IN TEXT FIELD")
                time.sleep(1)
                status_widget.hide()
        else:
            # Record anywhere - no text field check
            log_info("Middle-click detected - starting recording (anywhere mode)")
            start_recording()
            
    # Left-click: optionally auto-start when clicking into a text field
    elif button == mouse.Button.left:
        # If left-click auto-start enabled, wait briefly for focus to settle then check
        if config_manager.get('auto_start_on_left_click'):
            time.sleep(config_manager.get('auto_start_delay'))
            if config_manager.get('require_text_field'):
                if is_text_field():
                    # Avoid password fields
                    if config_manager.get('ignore_password_fields'):
                        # is_text_field already subtracts score for password fields; just check again conservatively
                        if is_text_field():
                            start_recording()
                    else:
                        start_recording()
                else:
                    log_debug("Left-click did not land in text field")
            else:
                start_recording()
def main():
    global model, status_widget, settings_widget
    
    try:
        log_info("🎤 Voice Click - Advanced Edition")
        log_info("=" * 60)
        log_info("Loading...")
        log_info(f"Log file: {LOG_FILE}")
        log_info(f"Loaded config: mouse_shake_threshold_px={config_manager.get('mouse_shake_threshold_px')}")
        
        # Load history
        load_history()
        
        # Create widgets
        status_widget = RecordingWidget()
        settings_widget = SettingsWidget()
        
        # Show settings widget on startup for initial configuration
        settings_widget.show()
        
        # Load model with auto-fallback to CPU
        whisper_model = config_manager.get('whisper_model')
        whisper_device = config_manager.get('whisper_device')
        whisper_compute_type = config_manager.get('whisper_compute_type')
        
        log_info(f"Loading Whisper model ({whisper_model}) on {whisper_device.upper()}...")
        model_loaded = False
        
        # Try primary configuration (CUDA)
        try:
            model = WhisperModel(
                whisper_model,
                device=whisper_device,
                compute_type=whisper_compute_type
            )
            log_info(f"✓ Model ready! ({whisper_model} / {whisper_device} / {whisper_compute_type})")
            model_loaded = True
        except Exception as e:
            log_error(f"✗ Failed to load model on {whisper_device}: {e}", e)
            
            # Auto-fallback to CPU if CUDA was selected
            if whisper_device == "cuda":
                log_info("Attempting fallback to CPU...")
                try:
                    model = WhisperModel(
                        whisper_model,
                        device="cpu",
                        compute_type="int8"
                    )
                    log_info(f"✓ Model ready on CPU! ({whisper_model} / cpu / int8)")
                    log_info("Note: CPU mode is slower but works. To use GPU, install cuDNN libraries.")
                    model_loaded = True
                except Exception as e2:
                    log_error(f"✗ CPU fallback also failed: {e2}", e2)
        
        if not model_loaded:
            log_error("FATAL: Could not load Whisper model on any device")
            sys.exit(1)
        
        # Start audio
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            callback=audio_callback,
            blocksize=int(SAMPLE_RATE * 0.03)
        )
        stream.start()
        log_info("✓ Audio ready")
        
        # Start mouse listener
        listener = mouse.Listener(on_click=on_click, on_move=on_move)
        listener.start()
        log_info("✓ Mouse ready")

        # Start focus monitor thread if enabled
        global focus_monitor_thread, focus_monitor_stop
        if config_manager.get('auto_start_on_focus'):
            focus_monitor_stop = False
            focus_monitor_thread = threading.Thread(target=focus_monitor, daemon=True)
            focus_monitor_thread.start()
            log_info("✓ Focus monitor active")
            
        # Register settings hotkey (Ctrl+Alt+S)
        keyboard.add_hotkey('ctrl+alt+s', toggle_settings_widget)
        log_info("✓ Settings hotkey (Ctrl+Alt+S) registered")
        
        log_info("")
        log_info("ADVANCED FEATURES:")
        log_info(f"  • Whisper Model: {whisper_model} on {whisper_device.upper()} ({whisper_compute_type})")
        log_info(f"  • Volume monitoring with real-time feedback")
        
        # Auto-stop info
        silence_enabled = config_manager.get('enable_silence_auto_stop')
        silence_duration = config_manager.get('silence_duration')
        manual_stop_enabled = config_manager.get('enable_manual_stop')
        max_time = config_manager.get('max_recording_time')
        
        if silence_enabled:
            log_info(f"  • Auto-stop after {silence_duration}s of silence")
        if manual_stop_enabled:
            log_info(f"  • Manual stop: Middle-click")
        if not silence_enabled and not manual_stop_enabled:
            log_info(f"  • Auto-stop disabled (max time only)")
        
        log_info(f"  • Max recording time: {max_time}s")
        log_info(f"  • Transcription history: {len(transcription_history)} entries")
        log_info(f"  • History saved to: {HISTORY_FILE}")
        
        # Auto-start info
        if config_manager.get('auto_start_on_focus'):
            log_info(f"  • Auto-start on focus enabled")
        if config_manager.get('auto_start_on_left_click'):
            log_info(f"  • Auto-start on left-click enabled")
        if config_manager.get('ignore_fullscreen_games'):
            log_info(f"  • Fullscreen games ignored")
        if config_manager.get('ignore_password_fields'):
            log_info(f"  • Password fields ignored")
        
        log_info("")
        log_info("USAGE:")
        
        start_methods = []
        if config_manager.get('auto_start_on_focus'):
            start_methods.append("Focus a text field")
        if config_manager.get('auto_start_on_left_click'):
            start_methods.append("Left-click into a text field")
        start_methods.append("Middle-click")
        
        log_info(f"  • Start recording: {' / '.join(start_methods)}")
        
        stop_methods = []
        if manual_stop_enabled:
            stop_methods.append("Middle-click")
        if silence_enabled:
            stop_methods.append(f"Silence for {silence_duration}s")
        
        if stop_methods:
            log_info(f"  • Stop recording: {' / '.join(stop_methods)}")
        
        log_info("  • Cancel recording → Right-click during recording")
        log_info("  • Open Settings Widget → Ctrl+Alt+S")
        
        if config_manager.get('require_text_field'):
            log_info("  • Requires text field to start recording")
        else:
            log_info("  • Works ANYWHERE - no text field required")
        
        log_info("  • Widget shows volume level and duration")
        log_info("  • Audio feedback beeps indicate status")
        log_info("  • Focus validation ensures paste goes to correct field")
        log_info("")
        log_info("✨ Ready! Start speaking...\n")
        
        # Run (tkinter mainloop for widget updates)
        try:
            status_widget.root.mainloop()
        except KeyboardInterrupt:
            log_info("Shutting down...")
        finally:
            # Cleanup
            stream.stop()
            stream.close()
            listener.stop()
            # Stop focus monitor
            focus_monitor_stop = True
            if focus_monitor_thread and focus_monitor_thread.is_alive():
                focus_monitor_thread.join(timeout=0.5)
    
    except Exception as e:
        log_error(f"Fatal error in main: {e}", e)
        sys.exit(1)

if __name__ == "__main__":
    main()