# app/baymax_brain.py
from openai import OpenAI
import json, time, subprocess
import re
client = OpenAI()


def _parse_timer_seconds(t: str) -> int | None:
    m = re.search(r"(?:timer\s*)?(\d+)\s*(detik|menit|min|jam)", t)
    if not m:
        return None
    n = int(m.group(1))
    unit = m.group(2)
    if unit.startswith("detik"):
        return n
    if unit.startswith("menit") or unit.startswith("min"):
        return n * 60
    if unit.startswith("jam"):
        return n * 3600
    return None

def local_fallback_plan(user_text: str) -> dict:
    t = (user_text or "").lower().strip()
    if t.startswith("catat") or " catat " in t:
        note = t.replace("catat", "", 1).strip()
        return {"action": "add_note", "args": {"text": note}, "say": f"Saya catat: {note or '—'}"}
    if "timer" in t:
        secs = _parse_timer_seconds(t)
        if secs and secs > 0:
            return {"action": "start_timer", "args": {"seconds": secs}, "say": f"Timer {secs} detik dimulai."}
        return {"action": "reply_only", "say": "Format timer tidak jelas. Contoh: timer 5 menit."}
    if "open" in t:
        name = t.split("buka", 1)[1].strip() if "buka" in t else ""
        return {"action": "open_app", "args": {"name": name}, "say": f"Membuka {name}." if name else "Buka apa?"}
    return {"action": "reply_only", "say": "Baik. Perintah diterima."}

ACTION_SCHEMA = {
  "type": "object",
  "additionalProperties": False,
  "properties": {
    "action": {"type": "string", "enum": ["add_note","start_timer","open_app","reply_only"]},
    "args": {"type": "object", "additionalProperties": True},
    "say": {"type": "string"}
  },
  "required": ["action"]
}

SAFE_APPS = {
  "notepad": r"C:\Windows\System32\notepad.exe",
  "calculator": r"C:\Windows\System32\calc.exe",
  "kalkulator": r"C:\Windows\System32\calc.exe",
  "youtube": r"C:\Windows\System32\youtube.com",
}

def run_action(parsed):
    action = parsed["action"]
    args = parsed.get("args", {}) or {}
    say  = parsed.get("say") or ""

    if action == "add_note":
        text = args.get("text","").strip()
        if text:
            with open("data/notes.txt","a",encoding="utf-8") as f:
                f.write(f"- {text}\n")
            return f"Saya catat: {text}"
        return "Tidak ada isi catatan."

    if action == "start_timer":
        secs = int(args.get("seconds", 0))
        if secs > 0:
            # contoh non-blocking minimal
            # (kalau mau bunyi alarm beneran, pakai threading.Timer di loop utama)
            return f"Timer {secs} detik dimulai."
        return "Durasi timer tidak valid."

    if action == "open_app":
        name = (args.get("name","") or "").lower()
        exe = SAFE_APPS.get(name)
        if exe:
            try:
                subprocess.Popen([exe]); return f"Membuka {name}."
            except Exception: return f"Gagal membuka {name}."
        return f"Aplikasi {name} tidak diizinkan."

    return say or "Baik."

def gpt5_plan(user_text, memory_snippets=None):
    import json, re
    sys = (
      "Kamu adalah Baymax, asisten Indonesia yang aksi-oriented. "
      "Keluarkan HANYA 1 objek JSON valid sesuai skema. "
      "Skema: {\"action\":\"add_note|start_timer|open_app|reply_only\", "
      "\"args\": {\"text\"?:string, \"seconds\"?:number, \"name\"?:string}, "
      "\"say\"?:string}."
    )
    messages = [
        {"role":"system","content": sys},
        {"role":"user","content": f"Instruksi pengguna: {user_text}"}
    ]
    if memory_snippets:
        messages.insert(1, {"role":"system","content": f"Memori singkat: {memory_snippets}"})

    try:
        # Kompatibel dengan SDK lama: Chat Completions (tanpa response_format)
        chat = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0
        )
        text = chat.choices[0].message.content.strip()
        try:
            return json.loads(text)
        except Exception:
            m = re.search(r"\{.*\}", text, re.DOTALL)
            if m:
                return json.loads(m.group(0))
            return {"action":"reply_only","say": text[:200]}
    except Exception:
        # QUOTA/429 atau error lain → fallback lokal
        return local_fallback_plan(user_text)
