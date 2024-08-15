from pathlibutil import Path

from peak_converter.update import update

if __name__ == "__main__":

    try:
        config = Path(__file__).parent.joinpath("../bin/PEAK-Converter.json").resolve()
        result = update(config, config.parent)
    except Exception as e:
        print(e)
        result = 123

    raise SystemExit(result)
