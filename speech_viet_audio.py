import warnings
# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import paramiko
import sys
import os
import time
from naoqi import ALProxy

# Set your robot's IP
# Legacy Python 2.7 + NAOqi SDK path. The Python 3 scripts now use
# pepper_player.py instead. Settings come from environment variables.
PEPPER_IP = os.environ.get("PEPPER_IP", "192.168.10.10")
PEPPER_PORT = int(os.environ.get("PEPPER_PORT", "9559"))
SSH_USERNAME = os.environ.get("PEPPER_SSH_USER", "nao")
SSH_PASSWORD = os.environ.get("PEPPER_SSH_PASSWORD", "")

def copy_to_pepper(local_file):
    remote_file = "/home/nao/audio_file.mp3" # Path on Pepper where the file will be copied
    
    try:
        # Set up SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(PEPPER_IP, username=SSH_USERNAME, password=SSH_PASSWORD)
        
        # Copy file
        sftp = ssh.open_sftp()
        sftp.put(local_file, remote_file)
        sftp.close()
        ssh.close()
        
        return remote_file
        
    except Exception as e:
        print("Error copying file: {}".format(e))
        return None

def play_audio_on_pepper(audio_file):
    try:
        # Connect to Pepper's audio player
        audio_player = ALProxy("ALAudioPlayer", PEPPER_IP, PEPPER_PORT)
        
        # Play the file on Pepper
        audio_id = audio_player.playFile(audio_file)
        #print("Audio playing with ID: {}".format(audio_id))
        
        # Wait for audio to finish
        time.sleep(3)
        
    except Exception as e:
        print("Error: {}".format(e))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        local_file = sys.argv[1]
    else:
        local_file = "" # Default file path
    
    if os.path.exists(local_file):
        # Copy to Pepper
        remote_file = copy_to_pepper(local_file)
        
        if remote_file:
            # Play the file
            play_audio_on_pepper(remote_file)
    else:
        print("Error: File '{}' doesn't exist".format(local_file))