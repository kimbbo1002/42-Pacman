from parsing import load_config
from map_generation import setup_vizualisation


def main() -> None:
    try:
        config = load_config()
        setup_vizualisation(config)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
