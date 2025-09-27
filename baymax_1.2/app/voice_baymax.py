# app/voice_baymax.py
from pathlib import Path
import pyttsx3
import subprocess
import soundfile as sf
import sounddevice as sd
import shutil

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "audio"
DATA_DIR.mkdir(parents=True, exist_ok=True)
RAW_WAV = DATA_DIR / "tts_raw.wav"
BAYMAX_WAV = DATA_DIR / "tts_baymax.wav"

def _pick_voice(engine: pyttsx3.Engine, prefer: str | None = None):
    """
    prefer: None (auto), 'id' (Indonesia), 'en-GB' (British)
    """
    try:
        voices = engine.getProperty("voices")
        norm = lambda s: (s or "").lower()

        def matches(v, keys):
            s = " ".join([norm(v.name), norm(",".join(v.languages or [])), norm(v.id)])
            return any(k in s for k in keys)

        # 1) Prioritas sesuai prefer
        if prefer == "en-US":
            for v in voices:
                if matches(v, ["en-US", "english (united kingdom)", "british", "en-US"]):
                    engine.setProperty("voice", v.id); return
        elif prefer == "id":
            for v in voices:
                if matches(v, ["id", "indones", "bahasa indonesia"]):
                    engine.setProperty("voice", v.id); return

        # 2) Auto fallback: kalau teks nanti Inggris, pakai en; kalau tidak, default
        for v in voices:
            if matches(v, ["en-US", "United States"]):
                engine.setProperty("voice", v.id); return

        # 3) Fallback terakhir ke voice “male” supaya lebih dekat karakter Baymax
        for v in voices:
            if "male" in norm(v.name):
                engine.setProperty("voice", v.id); return
    except Exception:
        pass


def _synthesize_raw(text: str, prefer: str | None = None):
    e = pyttsx3.init()
    _pick_voice(e, prefer=prefer)
    rate = e.getProperty("rate")
    e.setProperty("rate", max(120, int(rate * 0.90)))  # pelan dikit, khas Baymax
    e.setProperty("volume", 0.9)
    e.save_to_file(text, str(RAW_WAV))
    e.runAndWait()

def _ffmpeg_exists() -> bool:
    return shutil.which("ffmpeg") is not None

def _cook_baymax_voice():
    """
    Filter chain:
    - highpass 120 Hz, lowpass 6200 Hz → lembut
    - compressor ringan → stabil
    - speechnorm → level rata
    - pitch down tipis pakai asetrate+atempo (~ -1 semitone)
    - force mono 16 kHz
    """
    if not _ffmpeg_exists():
        RAW_WAV.replace(BAYMAX_WAV) if RAW_WAV.exists() else None
        return

    cmd = [
        "ffmpeg", "-y",
        "-i", str(RAW_WAV),
        "-af",
        "highpass=f=120,lowpass=f=6200,"
        "acompressor=threshold=-18dB:ratio=3:attack=12:release=180,"
        "speechnorm=e=6.0:r=0.0001,"
        "asetrate=16000*0.955,atempo=1/0.955",
        "-ar", "16000", "-ac", "1",
        str(BAYMAX_WAV)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

def speak_baymax(text: str, prefer: str | None = None):
    if not text:
        text = "Maaf, saya tidak mendengar apa pun."
    _synthesize_raw(text, prefer=prefer)
    _cook_baymax_voice()
    wav = BAYMAX_WAV if BAYMAX_WAV.exists() else RAW_WAV
    data, sr = sf.read(str(wav), dtype="float32", always_2d=False)
    sd.play(data, sr, blocking=True)

