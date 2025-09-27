import os
import time
import json
import requests
from typing import Dict, Any, List, Optional

# ====== KONFIGURASI ======
# Isi sesuai penyedia LLM-mu:
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.your-llm-provider.com/v1")
LLM_MODEL    = os.getenv("LLM_MODEL",    "your-model-name")
LLM_API_KEY  = os.getenv("LLM_API_KEY",  "PUT_YOUR_KEY_HERE")

TIMEOUT_S    = 40
MAX_TOKENS   = 256
TEMP         = 0.2

# System prompt: arahkan LLM untuk TAAT pada skema JSON tool-call
SYSTEM_PROMPT = """Anda adalah asisten percakapan bernama Baymax.
Berbahasa Indonesia, singkat, jelas, sopan. Jika perintah butuh akses perangkat, gunakan tool.
Jawab SELALU dalam format JSON berikut TANPA penjelasan lain:

{
 "action": "SAY" | "TOOL",
 "reply": "<kalimat untuk diucapkan, wajib ada>",
 "tool_name": "<nama_tool_jika_ACTION_TOOL, selain itu kosong>",
 "args": { "kunci": "nilai", ... }  // argumen tool jika ada
}

Tool yang tersedia:
- create_note(text:str)  -> simpan catatan ke notes.txt
- set_timer(seconds:int) -> nyalakan timer
- open_app(name:str)     -> buka aplikasi lokal (notepad, calculator)

Aturan:
- Jika user hanya ngobrol, gunakan action "SAY".
- Jika user meminta tindakan perangkat (catat/buka/timer), gunakan action "TOOL" dengan tool_name yang cocok dan args valid.
- Jangan pernah memalsukan hasil eksekusi tool. Hanya rencanakan, eksekusi dilakukan oleh host.
"""

def _headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }

def _endpoint() -> str:
    # banyak penyedia mengikuti pola /chat/completions
    return f"{LLM_BASE_URL}/chat/completions"

def chat(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """Kirim ke LLM, dapatkan 1 completion."""
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": TEMP,
        "max_tokens": MAX_TOKENS,
        "top_p": 1.0,
        "n": 1,
        "stream": False
    }
    resp = requests.post(_endpoint(), headers=_headers(), json=payload, timeout=TIMEOUT_S)
    resp.raise_for_status()
    data = resp.json()
    # adaptasikan bila penyedia punya bentuk sedikit berbeda
    content = data["choices"][0]["message"]["content"]
    return json.loads(content)

def build_messages(user_text: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
    # Kamu bisa masukkan ringkasan konteks, waktu, dsb.
    sys_msg = {"role": "system", "content": SYSTEM_PROMPT}
    ctx_text = ""
    if context:
        ctx_text = json.dumps(context, ensure_ascii=False)
    user_msg = {"role": "user", "content": f"Konteks:{ctx_text}\nUser:'{user_text}'"}
    return [sys_msg, user_msg]
