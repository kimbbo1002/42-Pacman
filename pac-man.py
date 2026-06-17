from parsing import load_config


def main() -> None:
    try:
        config = load_config()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
