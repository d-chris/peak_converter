import subprocess


def test_version():

    result = subprocess.run(
        [
            "poetry",
            "run",
            "python",
            "peak_converter\\version.py",
        ],
        capture_output=True,
        encoding="cp850",
    )

    assert result.returncode == 0
    assert len(result.stdout.split(".")) == 3


def test_converter():

    result = subprocess.run(
        [
            "poetry",
            "run",
            "python",
            "peak_converter\\converter.py",
            "//help",
        ],
        capture_output=True,
        encoding="cp850",
    )

    assert result.returncode == 0
    assert result.stdout != ""
