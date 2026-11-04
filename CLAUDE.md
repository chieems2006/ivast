# Vietnamese Pepper

Vietnamese voice/text assistant for a SoftBank Pepper robot (2018, NAOqi). All logic runs on the PC; the robot only plays audio.

## Flow
1. Input: typed text (`viet_text.py`) or 5 s mic recording → noise reduction → PhoWhisper-medium ASR (`pepper_voice_viet.py`, uses CUDA if available).
2. `llm.py` → `llm.ask()`: Gemini (default, `google-genai`) or OpenAI, chosen by `LLM_PROVIDER`. Shared Vietnamese system prompt ("Pepper at the Vietnam Academy of Science and Technology", short spoken answers, no markdown/emoji). Gemini retries on 429/500/503 and falls through `GEMINI_FALLBACK_MODELS`; any final error → spoken fallback apology.
3. gTTS (`lang='vi'`) → `vietnamese_speech.mp3`.
4. `pepper_player.py`: SFTP the mp3 to `/home/nao/audio_file.mp3`, then run `qicli call ALAudioPlayer.playFile ...` on the robot over SSH.

## Layout
- `viet_text.py` – text chat loop (exit: `thoát`/`exit`/`quit`).
- `pepper_voice_viet.py` – voice chat loop (exit phrases incl. `tạm biệt`).
- `llm.py` – LLM provider switch + retry/fallback logic.
- `pepper_player.py` – Python 3 playback on Pepper; also `python pepper_player.py file.mp3`.
- `speech_viet_audio.py` – legacy Python 2.7 + NAOqi SDK playback (ALProxy). Not used by the main scripts; kept for reference.

## Setup / run (Windows, PowerShell)
```powershell
.\.venv\Scripts\Activate.ps1
python -X utf8 viet_text.py          # text mode
python -X utf8 pepper_voice_viet.py  # voice mode (needs torch etc.)
```
New machine: `python -m venv .venv`, `pip install torch --index-url https://download.pytorch.org/whl/cu124`, `pip install -r requirements.txt`.
Use `-X utf8` so Vietnamese prints correctly in the Windows console.

## Config
All settings in `.env` (template: `.env.example`): `LLM_PROVIDER`, `GEMINI_API_KEY`, `GEMINI_MODEL` (gemini-2.5-flash), `GEMINI_FALLBACK_MODELS`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `PEPPER_IP`, `PEPPER_PORT`, `PEPPER_SSH_USER`, `PEPPER_SSH_PASSWORD`.
- `.env` holds secrets — never commit it, print it, or paste its values. It is in `.gitignore`. Note: the parent `C:\Users\OS` is itself a git repo.

## Robot / network
- Direct LAN: PC `192.168.10.1`, Pepper `192.168.10.10`. Ports 22 (SSH) and 9559 (NAOqi) reachable; the robot web page shows "Unable to contact the server" but that is irrelevant to this code.
- Check reachability: `Test-NetConnection 192.168.10.10 -Port 22` / `-Port 9559`.
- Robot-side check: `python -c "import pepper_player as p; print(p.run_on_pepper('qicli info ALAudioPlayer'))"`.
- If the robot turns out to be NAOqi 2.9 (Android), `qicli`/ALAudioPlayer over SSH may not be available.

## Gotchas
- OpenAI key has no credits (429) → that's why Gemini is the default. Switch back with `LLM_PROVIDER=openai`.
- `gemini-flash-latest` often returns 503 "high demand"; that's why it's a fallback, not the main model.
- Gemini thinking tokens count toward `max_output_tokens`, so `llm.py` adds 1024 headroom; keep that or replies come back empty.
- Reply length: `pepper_voice_viet.py` asks for 150 tokens, `viet_text.py` 200.
- `pepper_voice_viet.py` downloads PhoWhisper-medium (~3 GB) from Hugging Face on first run.

## Verified (2026-11-04)
- Robot is NAOqi 2.5.5.5; SSH login + `qicli call ALAudioPlayer.playFile` playback works (test mp3 played, exit 0).
