import os
import sys
import subprocess
from gtts import gTTS
import llm  # Gemini or OpenAI, per LLM_PROVIDER in .env
from pepper_player import play_on_pepper

# Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
audio_file_path = os.path.join(current_dir, "vietnamese_speech.mp3")
speech_script_path = os.path.join(current_dir, "speech_viet_audio.py")

def get_text_input():
    """Get input text from user"""
    print("Nhập câu hỏi của bạn bằng tiếng Việt (hoặc 'thoát' để kết thúc):")
    text = input("> ")
    
    if text.lower() in ['thoát', 'exit', 'quit']:
        return None
    
    return text

def get_ai_response(text):
    return llm.ask(text, max_tokens=200)

def generate_vietnamese_speech(text):
    try:
        # Generate Vietnamese speech
        tts = gTTS(text=text, lang='vi')
        tts.save(audio_file_path)
        
        print(f"File âm thanh đã được lưu tại {audio_file_path}")
        return audio_file_path
    except Exception as e:
        print(f"Lỗi khi tạo âm thanh: {e}")
        return None

def main():
    print("Bạn có thể đặt câu hỏi bằng tiếng Việt và Pepper sẽ trả lời.")
    
    while True:
        # Get input from user
        text = get_text_input()
        
        # Check if user wants to quit
        if text is None:
            print("Kết thúc chương trình. Tạm biệt!")
            break
            
        # Get response from the LLM
        response = get_ai_response(text)
        
        # Generate speech file
        audio_file = generate_vietnamese_speech(response)
        
        if audio_file:
            # Play on Pepper
            play_on_pepper(audio_file)
            print("-" * 50)

if __name__ == "__main__":
    main()