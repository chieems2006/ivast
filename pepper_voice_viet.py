import os
import sys
import subprocess
import numpy as np
import torch
import time
import wave
import pyaudio
import noisereduce as nr
from gtts import gTTS
from transformers import pipeline, AutoModelForSpeechSeq2Seq, AutoTokenizer, AutoFeatureExtractor
import threading
import llm  # Gemini or OpenAI, per LLM_PROVIDER in .env
from pepper_player import play_on_pepper

# Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
audio_file_path = os.path.join(current_dir, "vietnamese_speech.mp3")
speech_script_path = os.path.join(current_dir, "speech_viet_audio.py")
audio_input_path = os.path.join(current_dir, "output.wav")

# Audio recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 5  # Increased from 3 to 5 seconds for more speaking time

# Load the PhoWhisper model for speech recognition
print("Đang tải mô hình PhoWhisper...")
model = AutoModelForSpeechSeq2Seq.from_pretrained("vinai/PhoWhisper-medium")
tokenizer = AutoTokenizer.from_pretrained("vinai/PhoWhisper-medium")
feature_extractor = AutoFeatureExtractor.from_pretrained("vinai/PhoWhisper-medium")

device = "cuda:0" if torch.cuda.is_available() else "cpu" # Use GPU if available
model = model.to(device)

# Initialize the ASR pipeline
transcriber = pipeline("automatic-speech-recognition", model=model, tokenizer=tokenizer, feature_extractor=feature_extractor)

def record_audio():
    """Record audio from microphone"""
    audio = pyaudio.PyAudio()

    # Start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("Đang ghi âm... (Hãy nói câu hỏi của bạn)")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Ghi âm kết thúc.")

    # Stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Convert frames to numpy array
    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)

    # Apply noise reduction
    reduced_noise = nr.reduce_noise(y=audio_data, sr=RATE)

    # Save the reduced noise audio to a file
    wf = wave.open(audio_input_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(reduced_noise.tobytes())
    wf.close()

    return audio_input_path

def transcribe_audio(audio_path):
    print("Đang chuyển đổi giọng nói thành văn bản...")
    output = transcriber(audio_path)
    transcription = output['text']
    print(f"Câu hỏi: {transcription}")
    return transcription

def get_ai_response(text):
    return llm.ask(text, max_tokens=150)

def generate_vietnamese_speech(text):

    try:
        tts = gTTS(text=text, lang='vi')
        tts.save(audio_file_path)
        
        print(f"File âm thanh đã được lưu tại {audio_file_path}")
        return audio_file_path
    except Exception as e:
        print(f"Lỗi khi tạo âm thanh: {e}")
        return None

def should_exit(text):
    """Check if user wants to exit based on transcribed text"""
    exit_phrases = ['thoát', 'exit', 'quit', 'dừng lại', 'tạm biệt', 'kết thúc']
    return any(phrase in text.lower() for phrase in exit_phrases)

def generate_goodbye_message():
    
    import random
    goodbyes = [
        "Tạm biệt! Rất vui được trò chuyện với bạn.",
        "Chào tạm biệt! Hẹn gặp lại bạn sau nhé.",
        "Cảm ơn bạn đã trò chuyện. Tạm biệt và hẹn gặp lại!",
        "Tạm biệt bạn. Chúc bạn một ngày tốt lành.",
        "Rất vui được phục vụ bạn. Tạm biệt!"
    ]
    return random.choice(goodbyes)

def main():

    while True:
        try:
            # Record user's speech
            audio_file = record_audio()
            
            # Transcribe speech to text
            text = transcribe_audio(audio_file)
            
            # Check if user wants to exit
            if should_exit(text):
                print("Người dùng muốn kết thúc cuộc trò chuyện.")
                
                # Generate goodbye message
                goodbye_message = generate_goodbye_message()
                print(f"Pepper: {goodbye_message}")
                
                # Generate speech file for goodbye
                speech_file = generate_vietnamese_speech(goodbye_message)
                
                if speech_file:
                    # Play goodbye on Pepper
                    play_on_pepper(speech_file)
                
                print("Kết thúc chương trình. Tạm biệt!")
                break
            
            # Get response from the LLM
            response = get_ai_response(text)
            
            # Generate speech file
            speech_file = generate_vietnamese_speech(response)
            
            if speech_file:
                # Play on Pepper
                play_on_pepper(speech_file)
            
            print("-" * 50)
            
            # Brief pause before next recording
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\nChương trình đã bị dừng bởi người dùng.")
            
            # Also say goodbye when interrupted with Ctrl+C
            goodbye_message = generate_goodbye_message()
            print(f"Pepper: {goodbye_message}")
            speech_file = generate_vietnamese_speech(goodbye_message)
            
            if speech_file:
                play_on_pepper(speech_file)
                
            print("Tạm biệt!")
            break
        except Exception as e:
            print(f"Lỗi: {e}")

if __name__ == "__main__":
    main()