import sounddevice as sd
import soundfile as sf
from pathlib import Path

SAMPLE_RATE = 16000   # cukup untuk ASR nantinya
DURATION = 5          # detik
CHANNELS = 1

def main():
    out_dir = Path(__file__).resolve().parents[1] / "data" / "audio"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_wav = out_dir / "mic_test.wav"

    print(f"Merekam {DURATION} detik... bicara apa saja.")
    audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="float32")
    sd.wait()

    sf.write(out_wav, audio, SAMPLE_RATE)
    print(f"Selesai. File tersimpan di: {out_wav}")

if __name__ == "__main__":
    main()
