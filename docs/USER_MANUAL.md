# VoiceClick User Manual

Welcome to the VoiceClick User Manual. This guide provides a detailed walkthrough of all the features and settings available in the application.

## Table of Contents

1.  [Introduction](#introduction)
2.  [The Main Window](#the-main-window)
    -   [Status Tab](#status-tab)
    -   [Settings Tab](#settings-tab)
    -   [History Tab](#history-tab)
3.  [System Tray Icon](#system-tray-icon)
4.  [How to Transcribe](#how-to-transcribe)
5.  [Configuration Details](#configuration-details)
    -   [Model Settings](#model-settings)
    -   [Recording Settings](#recording-settings)
6.  [Troubleshooting](#troubleshooting)

---

## 1. Introduction

VoiceClick is a voice-to-text application that allows you to transcribe your speech into any active text field on your computer. It runs in the background and can be easily controlled via its main window or system tray icon.

## 2. The Main Window

The main window is organized into three tabs, giving you full control over the application.

### Status Tab

This is the default tab you see when you open the application. It provides real-time information about the transcription engine.

-   **Status**: Shows the current state of the engine (e.g., `Idle`, `Recording`, `Transcribing`, `Initializing`).
-   **Volume Meter**: A progress bar that displays the current input volume from your microphone. This is useful for checking if your microphone is working correctly.
-   **Start/Stop Recording Button**: Manually start or stop a recording session.
-   **Log Viewer**: Displays important status messages, errors, and transcription results from the engine.

### Settings Tab

This tab allows you to customize the application's behavior to fit your needs.

-   **Transcription Model**:
    -   **Model Size**: Choose the Whisper model size. Smaller models (`tiny`, `base`) are faster but less accurate. Larger models (`small`, `medium`, `large`) are more accurate but require more processing power. The `large-v3` model is the default and recommended for a balance of performance and accuracy.
    -   **Compute Device**: Select the hardware for running the model. `CUDA` (NVIDIA GPU) is highly recommended for the best performance. If you don't have a compatible GPU, select `CPU`.
-   **Recording**:
    -   **Silence Threshold (dB)**: The volume level below which the audio is considered silence.
    -   **Silence Duration (s)**: The number of seconds of silence to wait before automatically stopping the recording.
-   **Save/Reset Buttons**:
    -   **Save Settings**: Click this to apply and save any changes you make.
    -   **Reset to Defaults**: Reverts all settings to their original values.

### History Tab

This tab displays a record of your past transcriptions.

-   **Transcription List**: Shows a table with the timestamp and the text of each transcription.
-   **Export to CSV**: Allows you to save your entire transcription history to a `.csv` file for use in other applications.
-   **Clear History**: Permanently deletes all saved transcription records.

## 3. System Tray Icon

When you minimize the main window, VoiceClick continues to run in the system tray.

-   **Left-Click**: Show/hide the main application window.
-   **Right-Click**: Opens a context menu with options to:
    -   **Start/Stop Recording**: A quick way to control transcription without opening the main window.
    -   **Show Window**: Brings the main window to the foreground.
    -   **Quit**: Exits the application completely.

## 4. How to Transcribe

1.  **Open the application**. It will initialize the transcription engine, which may take a moment.
2.  **Click the "Start Recording" button** in the Status Tab or from the system tray menu. The status will change to "Recording".
3.  **Position your cursor** in any text field on your computer (e.g., a text editor, web browser, or word processor).
4.  **Start speaking**.
5.  **Stop recording** by either:
    -   Clicking the "Stop Recording" button.
    -   Waiting for the automatic silence detection to kick in.
6.  The engine will process the audio, and the transcribed text will be automatically typed into the text field where your cursor is positioned.

## 5. Configuration Details

### Model Settings

-   **Model Size**: The choice of model is a trade-off between speed and accuracy. If you find transcriptions are slow, try a smaller model. If accuracy is poor, try a larger one.
-   **Compute Device**: Using a `CUDA`-enabled GPU will result in significantly faster transcriptions compared to using the `CPU`. The application will automatically detect if you have a compatible GPU.

### Recording Settings

-   **Silence Threshold**: This value determines how sensitive the silence detector is. A lower value (e.g., 10) means only very quiet audio is considered silence. A higher value (e.g., 30) means even moderately quiet audio will be treated as silence. Adjust this based on your microphone and background noise level.
-   **Silence Duration**: This sets how long the application waits before stopping a recording after it detects silence. A shorter duration means the transcription will be faster, but it might cut you off if you pause while speaking.

## 6. Troubleshooting

-   **"No input device found" error**: Ensure your microphone is properly connected and configured in Windows sound settings.
-   **Application is slow or unresponsive**: If you are not using a GPU (`CUDA`), transcription can be resource-intensive, especially with larger models. Try using a smaller model size.
-   **Poor transcription quality**:
    -   Ensure your microphone is close to you and the input volume is adequate.
    -   Try using a larger, more accurate Whisper model.
    -   Minimize background noise.
-   **Text is not being pasted**: Make sure you have a text field selected (i.e., your cursor is active in it) before the transcription finishes.
