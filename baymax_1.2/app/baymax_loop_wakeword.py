import time
from pathlib import Path
import numpy as np
import sounddevice as sd
import soundfile as sf
import pyttsx3
from faster_whisper import WhisperModel
import webbrowser
import os
import re, threading, subprocess, sys, difflib, datetime
from baymax_brains import gpt5_plan, run_action
from voice_baymax import speak_baymax

def likely_english(s: str) -> bool:
    letters = re.findall(r"[A-Za-z]", s)
    nonlatin = re.findall(r"[^A-Za-z0-9\s\.,;:!\?'\-]", s)
    return len(letters) > 0 and (len(nonlatin) == 0 or len(letters) / (len(nonlatin) + 1) > 4)


# tendang semua ENV yang nunjuk ke D:\ di proses ini
for k in ("HF_HOME", "HF_HUB_CACHE", "HUGGINGFACE_HUB_CACHE"):
    v = os.environ.get(k, "")
    if v.strip().lower().startswith("d:"):
        os.environ.pop(k, None)

# set default yang benar ke C:\
os.environ.setdefault("HF_HOME", r"C:\hf_cache")
os.environ.setdefault("HF_HUB_CACHE", r"C:\hf_cache\hub")
os.environ.setdefault("HUGGINGFACE_HUB_CACHE", r"C:\hf_cache\hub")

# pastikan folder ada
os.makedirs(r"C:\hf_cache\hub", exist_ok=True)


SAMPLE_RATE = 16000
CHANNELS = 1
WAKEWORD = ["baymax", "baik maks", "bye max", "bye, max.", "bye", "way max", "bmix", "bayi mets!", "baik maksud"]
LISTEN_WAKE_SEC = 3
LISTEN_CMD_SEC = 5
WAKE_CANDIDATES = ["baymax", "baik maks", "bemeks", "baik maksud", "baimak", "beymaks"]

def heard_wake(text: str, threshold: float = 0.75) -> bool:
    text = text.lower().strip()
    if not text:
        return False
    # cocokkan langsung dulu
    if any(w in text for w in WAKE_CANDIDATES):
        return True
    # fuzzy match per kata
    tokens = text.split()
    for token in tokens:
        ratio = max(difflib.SequenceMatcher(None, token, w).ratio() for w in WAKE_CANDIDATES)
        if ratio >= threshold:
            return True
    return False

def tts_engine():
    e = pyttsx3.init()
    rate = e.getProperty("rate")
    e.setProperty("rate", int(rate * 0.95))
    return e

def speak(e: pyttsx3.Engine, text: str):
    e.say(text)
    e.runAndWait()

def record_np(seconds: int) -> np.ndarray:
    print(f"[REC] {seconds} detik...")
    audio = sd.rec(int(seconds * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="float32")
    sd.wait()
    return audio.squeeze()

def save_wav(audio: np.ndarray, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), audio, SAMPLE_RATE)

def transcribe_array(audio: np.ndarray) -> str:
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    segments, info = WhisperModelResult = model.transcribe(
        audio,
        language="id",
        vad_filter=True,
        vad_parameters={"min_speech_duration_ms": 200},
        condition_on_previous_text=False
    )
    text = "".join(seg.text for seg in segments).strip().lower()
    print(f"[ASR] {text}")
    return text

APP_MAP = {
    "notepad": r"C:\Windows\system32\notepad.exe",
    "calculator": r"C:\Windows\System32\calc.exe",
    "kalkulator": r"C:\Windows\System32\calc.exe",
    # tambah sesuai kebutuhanmu
}

'''def open_app(name: str) -> bool:
    name = name.lower().strip()
    if name in APP_MAP:
        try:
            subprocess.Popen([APP_MAP[name]])
            return True
        except Exception:
            return False
    return False

def parse_timer_seconds(text: str) -> int | None:
    m = re.search(r"(\d+)\s*(detik|menit|menet|minute|min|jam|hours|hour|hr)", text)
    if not m:
        return None
    n = int(m.group(1))
    unit = m.group(2)
    if unit.startswith("detik"):
        return n
    if unit.startswith("menit") or unit.startswith("min") or unit.startswith("mene"):
        return n * 60
    if unit.startswith("jam") or unit.startswith("hour") or unit.startswith("hr"):
        return n * 3600
    return None

def start_timer(seconds: int, tts_engine):
    def _alarm():
        speak(tts_engine, "Waktu habis.")
    t = threading.Timer(seconds, _alarm)
    t.daemon = True
    t.start()

def handle_command(text: str, tts: pyttsx3.Engine):
    reply = "Saya mendengar, tetapi belum ada perintah jelas."
    if text.startswith("catat"):
        note = text.replace("catat", "", 1).strip()
        if note:
            notes_file = Path(__file__).resolve().parents[1] / "data" / "notes.txt"
            notes_file.parent.mkdir(parents=True, exist_ok=True)
            with open(notes_file, "a", encoding="utf-8") as f:
                f.write(f"- {note}\n")
            reply = f"Saya catat: {note}."
        elif "timer" in text:
            seconds = parse_timer_seconds(text)
            if seconds and seconds > 0:
                start_timer(seconds, tts)
                eta = datetime.timedelta(seconds=seconds)
                reply = f"Timer dimulai {eta} dari sekarang."
            else:
                reply = "Format timer tidak jelas. Contoh: timer 5 menit."

        elif "buka" in text:
            # contoh: "buka notepad" / "buka calculator"
            target = text.replace("buka", "", 1).strip()
            if not target:
                reply = "Buka apa? Sebut nama aplikasinya."
            else:
                ok = open_app(target)
                reply = f"Membuka {target}." if ok else f"Tidak menemukan aplikasi {target}."

        elif "jam berapa" in text or "pukul berapa" in text:
            now = datetime.datetime.now()
            reply = f"Sekarang pukul {now:%H lewat %M}."

        else:
            reply = "Kamu bilang catat, tapi tidak ada isi."
    elif "buka youtube" in text:
        webbrowser.open("https://www.youtube.com")
        reply = "Membuka YouTube di browser."
    elif "halo" in text or "hai" in text:
        reply = "Halo. Aku siap bantu."
    else:
        reply = f"Kamu berkata: {text}. Saya mengerti."

    print(f"[RESP] {reply}")
    speak(tts, reply)'''

def main():
    print("[INIT] Load faster-whisper 'small' di GPU...")
    global model
    model = WhisperModel("small", device="cuda", compute_type="float16")
    tts = tts_engine()

    data_dir = Path(__file__).resolve().parents[1] / "data" / "audio"
    print("Tekan Ctrl+C untuk berhenti.")
    while True:
        try:
            # 1) Dengarkan wake word
            audio_wake = record_np(LISTEN_WAKE_SEC)
            save_wav(audio_wake, data_dir / "wake.wav")
            text_wake = transcribe_array(audio_wake)
            if any(w in text_wake for w in WAKEWORD):
                print("[WAKE] Baymax dipanggil.")
                speak_baymax(tts, "hello, i am baymax your personal assistan")
                # 2) Dengarkan perintah
                audio_cmd = record_np(LISTEN_CMD_SEC)
                save_wav(audio_cmd, data_dir / "cmd.wav")
                pref = "en-GB" if likely_english(reply) else None # atau transcribe_array(audio_cmd, model)
                try:
                    plan = gpt5_plan(text_cmd)
                except Exception:
                    from baymax_brains import local_fallback_plan
                    plan = local_fallback_plan(text_cmd)
                reply = run_action(plan)
                print(f"[RESP] {reply}")
                speak_baymax(reply, prefer=pref)

            else:
                print("[IDLE] Tidak ada wake word.")

            time.sleep(0.3)

        except KeyboardInterrupt:
            print("\n[EXIT] Dihentikan oleh user.")
            break

if __name__ == "__main__":
    main()
