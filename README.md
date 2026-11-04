# Vietnamese Pepper Voice Assistant

This project enables Pepper, the humanoid robot, to interact with users in Vietnamese using voice and text. It integrates speech recognition, OpenAI's GPT model, and text-to-speech capabilities.

## Features

- Voice and text interaction in Vietnamese
- Speech recognition using PhoWhisper
- OpenAI GPT-4o for intelligent responses
- Text-to-speech conversion for Vietnamese
- Audio playback on Pepper robot

## Requirements

### Hardware
- Pepper robot
- Microphone for voice input
- CUDA-capable GPU (recommended for speech recognition)

### Software
- Python 3.x (for main scripts)
- Python 2.7 (for Pepper interaction)
- NAOqi SDK for Pepper robot

### Python Dependencies
Install the following Python libraries for Python 3.x:
```bash
pip install torch openai gtts pyaudio transformers noisereduce numpy paramiko
```

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/vietnamese-pepper.git
cd vietnamese-pepper
```

### 2. Configure Pepper Connection
Update the Pepper robot's IP address, port, and credentials in the following files:

- **`speech_viet_audio.py`**:
  ```python
  PEPPER_IP = "192.168.x.x"  # Replace with your Pepper's IP address
  PEPPER_PORT = 9559
  SSH_USERNAME = "nao"  # Default username for Pepper
  SSH_PASSWORD = "your_pepper_password"  # Replace with your Pepper's password
  ```

- **`say_something.py`**:
  ```python
  ip = "192.168.x.x"  # Replace with your Pepper's IP address
  ```

### 3. Set OpenAI API Key
Add your OpenAI API key in the following files:

- **`pepper_voice_viet.py`**:
  ```python
  my_api_key = 'your_openai_api_key'
  ```

- **`viet_text.py`**:
  ```python
  my_api_key = 'your_openai_api_key'
  ```

### 4. Configure Python 2.7 Path
Specify the path to your Python 2.7 interpreter in the following files:

- **`pepper_voice_viet.py`**:
  ```python
  python2_path = "/path/to/python2"
  ```

- **`viet_text.py`**:
  ```python
  python2_path = "/path/to/python2"
  ```
## Running the Code

### Voice Interaction
To interact with Pepper using voice, run:
```bash
python pepper_voice_viet.py
```
Steps:
1. Speak your question in Vietnamese when prompted.
2. The system will transcribe your speech, generate a response using OpenAI, and play the response on Pepper.

To exit, say "tạm biệt" or press `Ctrl+C`.

### Text Interaction
To interact with Pepper using text, run:
```bash
python viet_text.py
```
Steps:
1. Type your question in Vietnamese.
2. The system will generate a response using OpenAI and play it on Pepper.

To exit, type "thoát" or "exit".

## Acknowledgments
- [VINAI](https://github.com/VinAIResearch/PhoWhisper) for the PhoWhisper model
- OpenAI for GPT models
- SoftBank Robotics for the Pepper robot platform


