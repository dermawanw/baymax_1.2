import os
# darurat kalau nanti kamu taruh manual di C:\ffmpeg\bin
os.environ["PATH"] += r";C:\Users\RIZAL\AppData\Local\Microsoft\WindowsApps;C:\Users\RIZAL\AppData\Local\Microsoft\WinGet\Links;C:\ffmpeg\bin"

import whisper
import soundfile as sf
import numpy as np
from pathlib import Path

def main():
    model = whisper.load_model("small")  # GPU, fp16 aktif
    wav = Path(__file__).resolve().parents[1] / "data" / "audio" / "mic_test.wav"
    if not wav.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {wav}")

    print(f"Menganalisis: {wav}")

    # BACA WAV TANPA FFMPEG
    audio, sr = sf.read(str(wav), dtype="float32")  # -> numpy array
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)  # pastikan mono
    if sr != 16000:
        raise ValueError(f"Sampel rate {sr} Hz. Rekam ulang di 16000 Hz supaya simpel.")

    out = model.transcribe(audio, fp16=True)  # langsung kirim array, tidak lewat ffmpeg
    print("=== TRANSKRIP ===")
    print(out["text"])

if __name__ == "__main__":
    main()
