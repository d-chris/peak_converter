import pendulum
import pytest

from peak_converter.datetime import Pendulum


@pytest.mark.parametrize(
    "timestamp",
    [
        "Mon, 06 May 2024 09:17:57 GMT",
        "2024-05-06 09:17:57+00:00",
        "Mon, 06 May 2024 09:17:57",
        "2024-05-06 09:17:57",
    ],
)
def test_pendulum(timestamp):

    assert isinstance(Pendulum(timestamp), pendulum.DateTime)
