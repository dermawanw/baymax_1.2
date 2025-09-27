import time, threading, subprocess, datetime
from pathlib import Path

APP_MAP = {
    "notepad": r"C:\Windows\System32\notepad.exe",
    "calculator": r"C:\Windows\System32\calc.exe",
    "kalkulator": r"C:\Windows\System32\calc.exe",
}

def create_note(text: str) -> str:
    notes = Path(__file__).resolve().parents[1] / "data" / "notes.txt"
    notes.parent.mkdir(parents=True, exist_ok=True)
    with open(notes, "a", encoding="utf-8") as f:
        f.write(f"- {text}\n")
    return f"Catatan disimpan."

def set_timer(seconds: int) -> str:
    def _alarm():
        # di loop utama nanti kita bisa pakai TTS juga, tapi sebagai minimal:
        print("[TIMER] Waktu habis.")
    t = threading.Timer(seconds, _alarm)
    t.daemon = True
    t.start()
    eta = str(datetime.timedelta(seconds=seconds))
    return f"Timer dimulai {eta} dari sekarang."

def open_app(name: str) -> str:
    key = name.strip().lower()
    exe = APP_MAP.get(key)
    if not exe:
        return f"Aplikasi '{name}' tidak dikenal."
    try:
        subprocess.Popen([exe])
        return f"Membuka {name}."
    except Exception:
        return f"Gagal membuka {name}."
