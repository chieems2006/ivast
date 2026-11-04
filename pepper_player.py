"""Play a local audio file on Pepper from Python 3.

Copies the file to the robot over SFTP, then runs ALAudioPlayer.playFile
on the robot itself via `qicli` over SSH. No Python 2.7 / NAOqi SDK needed
on the PC. Settings come from .env (see .env.example).
"""
import os
import shlex
import sys

import paramiko
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

PEPPER_IP = os.getenv("PEPPER_IP", "192.168.10.10")
SSH_USER = os.getenv("PEPPER_SSH_USER", "nao")
SSH_PASSWORD = os.getenv("PEPPER_SSH_PASSWORD", "")
REMOTE_FILE = "/home/nao/audio_file.mp3"


def _connect():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(PEPPER_IP, username=SSH_USER, password=SSH_PASSWORD, timeout=10)
    return ssh


def run_on_pepper(command, timeout=60):
    """Run a shell command on the robot; return (exit_code, stdout, stderr)."""
    ssh = _connect()
    try:
        _, out, err = ssh.exec_command(command, timeout=timeout)
        code = out.channel.recv_exit_status()
        return code, out.read().decode(errors="replace"), err.read().decode(errors="replace")
    finally:
        ssh.close()


def play_on_pepper(local_file):
    """Copy local_file to Pepper and play it (blocks until playback ends)."""
    try:
        ssh = _connect()
        try:
            sftp = ssh.open_sftp()
            sftp.put(local_file, REMOTE_FILE)
            sftp.close()
            cmd = "qicli call ALAudioPlayer.playFile " + shlex.quote(REMOTE_FILE)
            _, out, err = ssh.exec_command(cmd, timeout=120)
            if out.channel.recv_exit_status() != 0:
                print("Lỗi phát âm thanh trên Pepper: " + err.read().decode(errors="replace"))
        finally:
            ssh.close()
    except Exception as e:
        print("Lỗi kết nối Pepper: {}".format(e))


if __name__ == "__main__":
    if len(sys.argv) != 2 or not os.path.exists(sys.argv[1]):
        sys.exit("Usage: python pepper_player.py <audio_file>")
    play_on_pepper(sys.argv[1])
