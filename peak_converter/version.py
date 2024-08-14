from peak_converter import converter_version


def main():
    version = converter_version()

    print(version)

    return 0 if version else 1


if __name__ == "__main__":
    raise SystemExit(main())
