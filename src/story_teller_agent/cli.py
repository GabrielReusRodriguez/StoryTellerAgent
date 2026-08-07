import argparse

from story_teller_agent.story_teller import StoryTellerAgent


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="StoryTellerAgent — children's stories via AMD Lemonade AI",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help=(
            "Lemonade API base URL. If omitted, uses the LEMONADE_BASE_URL "
            "environment variable (required)."
        ),
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help=(
            "Lemonade API key for authenticated servers. If omitted, uses "
            "LEMONADE_API_KEY when set (optional)."
        ),
    )
    args = parser.parse_args(argv)

    print("...\n")
    agent = StoryTellerAgent(
        topic_creator=True,
        base_url=args.base_url,
        api_key=args.api_key,
    )
    for text in agent.tell_stream():
        print(text, end="", flush=True)
    print("\n\n...")


if __name__ == "__main__":
    main()
