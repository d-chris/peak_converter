import pathlib
from unittest.mock import MagicMock, patch

import pytest

from peak_converter.converter import converter_version, main, peak_executable


@pytest.mark.parametrize(
    "strict",
    [
        True,
        False,
    ],
)
def test_peak_converter(strict):

    assert isinstance(peak_executable(strict), pathlib.Path)


def test_main_silent():

    assert main("--help", "/silent") == 32


def test_main(capsys):

    assert main("--help") == 32

    _ = capsys.readouterr()


def test_version():

    assert converter_version() != ""


def test_converter_version():
    # Define the mock return value
    mock_result = MagicMock()
    mock_result.stdout = "PEAK-Converter without any Version Information\n"

    with patch("subprocess.run", return_value=mock_result):
        version = converter_version()
        assert version == ""
