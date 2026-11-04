"""Chat model wrapper: Gemini (default) or OpenAI, chosen by LLM_PROVIDER in .env."""
import os
import time

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

SYSTEM_PROMPT = (
    "Bạn là Robot Pepper tại Viện Hàn lâm Khoa học và Công nghệ Việt Nam. "
    "Hãy trả lời bằng tiếng Việt, ngắn gọn, tự nhiên như đang nói chuyện. "
    "Không dùng markdown, ký hiệu hay emoji vì câu trả lời sẽ được đọc thành tiếng."
)
FALLBACK = "Xin lỗi, tôi đang gặp sự cố khi xử lý yêu cầu của bạn."

PROVIDER = os.getenv("LLM_PROVIDER", "gemini").strip().lower()

if PROVIDER == "gemini":
    from google import genai
    from google.genai import types

    _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    _model = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    # Tried in order when the main model is overloaded (503) or rate-limited (429).
    _fallbacks = [m for m in os.getenv("GEMINI_FALLBACK_MODELS", "gemini-2.5-flash,gemini-2.5-flash-lite").split(",") if m.strip()]
elif PROVIDER == "openai":
    from openai import OpenAI

    _client = OpenAI()  # reads OPENAI_API_KEY
    _model = os.getenv("OPENAI_MODEL", "gpt-4o")
else:
    raise ValueError("LLM_PROVIDER must be 'gemini' or 'openai', got %r" % PROVIDER)


def _ask_gemini(text, max_tokens):
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        # Headroom for the model's internal "thinking" tokens,
        # which also count toward this limit.
        max_output_tokens=max_tokens + 1024,
    )
    last_err = None
    for model in [_model, _model] + [m.strip() for m in _fallbacks]:  # main model gets one retry
        try:
            r = _client.models.generate_content(model=model, contents=text, config=config)
            return (r.text or "").strip()
        except Exception as e:
            code = getattr(e, "code", None)
            if code not in (429, 500, 503):
                raise
            print("Gemini %s bận (%s), thử lại..." % (model, code))
            last_err = e
            time.sleep(1)
    raise last_err


def ask(text, max_tokens=200):
    """Return the model's Vietnamese reply to `text`, or FALLBACK on error."""
    try:
        if PROVIDER == "gemini":
            reply = _ask_gemini(text, max_tokens)
        else:
            r = _client.responses.create(
                model=_model,
                instructions=SYSTEM_PROMPT,
                input=text,
                max_output_tokens=max_tokens,
            )
            reply = r.output_text.strip()
        reply = reply or FALLBACK
    except Exception as e:
        print("Lỗi %s API: %s" % (PROVIDER, e))
        reply = FALLBACK
    print("Phản hồi: " + reply)
    return reply
