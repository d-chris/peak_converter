from pathlibutil import Path

from peak_converter.update import update


def main():
    try:
        config = Path(__file__).parent.joinpath("../bin/PEAK-Converter.json").resolve()
        result = update(config, config.parent)
    except Exception as e:
        print(e)
        result = 123
    finally:
        return result


if __name__ == "__main__":

    raise SystemExit(main())
