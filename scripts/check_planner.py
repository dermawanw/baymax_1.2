import json
from typing import Literal

from ollama import Client
from pydantic import BaseModel, ConfigDict, Field, model_validator


# Semua aksi hanya direncanakan, tidak dijalankan.
MODEL = "qwen3.5:4b"

ALLOWED_APPS = {"notepad", "calculator", "kalkulator"}

client = Client(
    host="http://localhost:11434",
    timeout=120.0,
)


class ActionArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    text: str | None = None
    seconds: int | None = Field(default=None, ge=1, le=86400)
    name: str | None = None


class ActionPlan(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    action: Literal[
        "add_note",
        "start_timer",
        "open_app",
        "reply_only",
    ]
    args: ActionArgs
    say: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def validate_action_args(self):
        args = self.args

        if self.action == "add_note":
            if not args.text or not args.text.strip():
                raise ValueError("Isi catatan tidak boleh kosong.")

            if args.seconds is not None or args.name is not None:
                raise ValueError("Aksi add_note hanya menerima text.")

            args.text = args.text.strip()

        elif self.action == "start_timer":
            if args.seconds is None:
                raise ValueError("Timer harus memiliki durasi.")

            if args.text is not None or args.name is not None:
                raise ValueError("Aksi start_timer hanya menerima seconds.")

        elif self.action == "open_app":
            if not args.name or not args.name.strip():
                raise ValueError("Nama aplikasi tidak boleh kosong.")

            if args.text is not None or args.seconds is not None:
                raise ValueError("Aksi open_app hanya menerima name.")

            args.name = args.name.strip().lower()

            if args.name not in ALLOWED_APPS:
                raise ValueError("Aplikasi tidak termasuk allowlist.")

        elif self.action == "reply_only":
            if any(
                value is not None
                for value in (args.text, args.seconds, args.name)
            ):
                raise ValueError("Aksi reply_only tidak menerima argumen.")

        return self


SYSTEM_PROMPT = """
Kamu adalah planner Baymax, asisten pribadi bilingual
yang memahami bahasa Indonesia dan bahasa Inggris.

Tugasmu hanya merencanakan aksi berdasarkan pesan pengguna.
Jangan menjalankan aksi dan jangan mengaku aksi sudah berhasil.

Pilih satu aksi:
1. add_note: pengguna meminta menyimpan catatan.
   Isi args.text dengan isi catatan.
2. start_timer: pengguna meminta timer.
   Konversikan durasi ke detik dalam args.seconds.
   Durasi yang diizinkan: 1 sampai 86400 detik.
3. open_app: pengguna meminta membuka aplikasi yang diizinkan.
   Isi args.name hanya dengan notepad atau calculator.
   Nama "kalkulator" dari pengguna harus dipetakan ke "calculator".
4. reply_only: percakapan biasa, permintaan tidak didukung,
   atau informasi yang diperlukan belum lengkap.

Aturan:
- Hasil harus sesuai JSON Schema yang diberikan.
- Untuk argumen yang tidak digunakan, gunakan null.
- Jika permintaan ambigu, pilih reply_only dan tanyakan klarifikasi.
- Jangan mengarang isi catatan atau durasi timer.
- Jika ada beberapa aksi dalam satu pesan, minta pengguna
  memberikan satu perintah terlebih dahulu.
- Jangan menerima perintah shell, path executable, atau aplikasi lain.
- Pahami perintah dalam bahasa Indonesia maupun bahasa Inggris.
- say harus singkat dan mengikuti bahasa pengguna,
  kecuali pengguna meminta bahasa tertentu.
- Jika bahasa pengguna ambigu, gunakan bahasa Indonesia
  sebagai bahasa default sementara.
- Pertahankan bahasa asli isi catatan.
- Nama action dan kunci JSON harus tetap sesuai schema.
- Kenali nama aplikasi Indonesia dan Inggris.
  Petakan "calculator" dan "kalkulator" ke nama canonical "calculator".
- Jangan mengaku aksi sudah berhasil dalam bahasa apa pun.
  Contoh yang dilarang:
  "sudah disimpan", "timer dimulai", "aplikasi terbuka",
  "note saved", "timer started", atau "application opened".
- Gunakan kalimat rencana, bukan klaim keberhasilan:
  Indonesia: "Saya akan menyimpan catatan tersebut."
  Inggris: "I will save that note."
"""


def plan_command(user_text: str) -> ActionPlan:
    schema = ActionPlan.model_json_schema()

    response = client.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    SYSTEM_PROMPT
                    + "\nJSON Schema:\n"
                    + json.dumps(schema, ensure_ascii=False)
                ),
            },
            {
                "role": "user",
                "content": user_text,
            },
        ],
        format=schema,
        options={
            "temperature": 0,
            "num_ctx": 4096,
        },
    )

    # JSON dari model tetap harus divalidasi oleh Python.
    return ActionPlan.model_validate_json(
        response.message.content or ""
    )


def main():
    print("Baymax Planner — mode uji, tidak menjalankan aksi.")
    print("Ketik 'keluar' untuk berhenti.")

    while True:
        try:
            user_text = input("\nKamu: ").strip()

            if user_text.lower() in {"keluar", "exit", "quit"}:
                break

            if not user_text:
                continue

            plan = plan_command(user_text)

            print("\nRencana:")
            print(
                json.dumps(
                    plan.model_dump(exclude_none=True),
                    ensure_ascii=False,
                    indent=2,
                )
            )

        except (KeyboardInterrupt, EOFError):
            print("\nSelesai.")
            break

        except Exception as exc:
            # Jika koneksi atau validasi gagal, tidak ada aksi dijalankan.
            print(f"\nRencana ditolak atau koneksi gagal: {exc}")
            print("Tidak ada aksi yang dijalankan.")


if __name__ == "__main__":
    main()
