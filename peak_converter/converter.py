import argparse
import re
import subprocess
from pathlib import Path


def peak_executable(strict: bool = True) -> Path:
    """Returns the Path to the PEAK-Converter.exe"""

    return Path(__file__).parent.joinpath("../bin/PEAK-Converter.exe").resolve(strict)


def converter_version(encoding: str = "cp850") -> str:
    """Returns the version of the PEAK-Converter"""

    result = subprocess.run(
        [
            peak_executable(),
            "--help",
        ],
        capture_output=True,
        encoding=encoding,
    )

    match = re.search(
        r"v\s?(?P<version>\d+\.\d+\.\d+)(?P<build>\.\d+)?", result.stdout, re.IGNORECASE
    )

    try:
        return match.group("version")
    except AttributeError:
        pass

    return ""


def main(*args) -> None:
    """
    wrapper to run PEAK-Converter.exe as python script
    """

    parser = argparse.ArgumentParser(
        description=main.__doc__,
        prefix_chars="/",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "/S",
        "/silent",
        action="store_true",
        dest="silent",
        help="surpress console output",
    )
    parser.add_argument(
        "/E",
        "/encoding",
        help="specify the encoding of the console output",
        dest="encoding",
        default="cp850",
    )
    parser.add_argument(
        "/version",
        action="version",
        version=converter_version(),
    )

    if not args:
        args = None

    # Parse known and unknown arguments
    args, unknown_args = parser.parse_known_args(args)

    result = subprocess.run(
        [
            peak_executable(),
            *unknown_args,
        ],
        capture_output=True,
        encoding=args.encoding,
    )

    if not args.silent:
        print(result.stdout)

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
