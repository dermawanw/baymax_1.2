import json

from baymax.planner import plan_command


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
            print(f"\nRencana ditolak atau koneksi gagal: {exc}")
            print("Tidak ada aksi yang dijalankan.")


if __name__ == "__main__":
    main()
