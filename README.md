# VoiceClick

**VoiceClick** is a modern, open-source voice-to-text application for Windows that allows you to transcribe your speech directly into any text field with a simple click. It's built with Python and leverages the power of OpenAI's Whisper for high-quality, real-time transcription.

![VoiceClick Screenshot](docs/screenshot.png) <!--- Placeholder for a screenshot -->

## Features

- **High-Quality Transcription**: Utilizes `faster-whisper`, a highly optimized version of OpenAI's Whisper model, for fast and accurate transcriptions.
- **System-Wide Integration**: Transcribe into any application or text field on Windows.
- **Customizable Models**: Choose from various Whisper model sizes (`tiny`, `base`, `small`, `medium`, `large`) to balance speed and accuracy.
- **Hardware Acceleration**: Supports CUDA for GPU-accelerated transcription, with a fallback to CPU.
- **Silence Detection**: Automatically stops recording after a configurable period of silence.
- **User-Friendly Interface**: A clean, tabbed interface built with PyQt6 to manage settings, view status, and browse transcription history.
- **System Tray Access**: Runs discreetly in the system tray for easy access.
- **Transcription History**: Stores your recent transcriptions for easy review and export.

## Installation

### Prerequisites

- Windows 10 or 11
- Python 3.9+
- [NVIDIA GPU with CUDA support](https://developer.nvidia.com/cuda-gpus) (recommended for best performance)
- [Git](https://git-scm.com/downloads)

### Steps

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/VoiceClick.git
    cd VoiceClick
    ```

2.  **Create a Virtual Environment**:
    It's highly recommended to use a virtual environment to manage dependencies.
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    The application requires several packages, including `PyQt6`, `faster-whisper`, and `sounddevice`. Install them using the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```
    *Note: If you do not have a CUDA-enabled GPU, `faster-whisper` will automatically use the CPU. The installation may take some time as it downloads necessary libraries.*

4.  **Run the Application**:
    Once the dependencies are installed, you can run the application from the root directory.
    ```bash
    python app.py
    ```
    The first time you run the app, it will download the default Whisper model (`large-v3`), which may take a few minutes depending on your internet connection.

## How It Works

VoiceClick runs in the background and can be activated to start recording your voice. When you stop recording (either manually or via silence detection), the captured audio is processed by the Whisper model, and the resulting text is automatically pasted into the currently active text field.

The core components are:
- **`app.py`**: The main entry point that launches the application.
- **`src/core/engine.py`**: The transcription engine that handles audio recording and processing.
- **`src/ui/main_window.py`**: The main application window built with PyQt6.
- **`src/config/settings.py`**: Manages user settings and configurations.

## Contributing

Contributions are welcome! If you have ideas for new features, bug fixes, or improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
