from ollama import chat


def main():
    response = chat(
        model="qwen3.5:4b",
        messages=[
            {
                "role": "system",
                "content": (
                    "Kamu adalah Baymax, asisten pribadi "
                    "berbahasa Indonesia. Jawab singkat."
                ),
            },
            {
                "role": "user",
                "content": "Halo Baymax, perkenalkan dirimu.",
            },
        ],
        options={
            "num_ctx": 4096,
            "temperature": 0.2,
        },
    )

    print(response.message.content)


if __name__ == "__main__":
    main()