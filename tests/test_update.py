from copy import deepcopy

import pendulum
import pytest
import requests

from peak_converter.update import (
    HTTPContentTypeError,
    HTTPLastModifiedError,
    HTTPNotModifiedError,
    UpdateConverter,
    load,
    write,
)


@pytest.fixture
def url():
    return "https://github.com/d-chris/peak_converter"


@pytest.fixture
def mock_head(url, requests_mock):

    last_modified = pendulum.now("UTC").format("ddd, DD MMM YYYY HH:mm:ss [GMT]")

    kwargs = {
        "url": url,
        "status_code": 200,
        "headers": {
            "Last-Modified": last_modified,
            "Content-Type": "application/zip",
        },
    }

    requests_mock.head(**kwargs)

    return kwargs


@pytest.fixture
def mock_get(requests_mock, mock_head):

    kwargs = deepcopy(mock_head)
    kwargs["content"] = b"test"

    requests_mock.get(**kwargs)

    return kwargs


@pytest.fixture(
    params=[
        False,
        pendulum.now("UTC"),
        HTTPContentTypeError,
        HTTPLastModifiedError,
    ],
    ids=[
        "False",
        "pendulum.now('UTC')",
        "HTTPContentTypeError",
        "HTTPLastModifiedError",
    ],
)
def mock_modified(request, mocker):

    value = request.param

    try:
        if issubclass(value, requests.exceptions.HTTPError):
            kwargs = {"side_effect": value}
        else:
            raise TypeError(f"Invalid pytest parameter {value=}")
    except TypeError:
        kwargs = {"return_value": value}

    mocker.patch("peak_converter.update.UpdateConverter.modified", **kwargs)

    return value


def test_load_exception(mocker):

    mocker.patch("pathlibutil.Path.resolve", side_effect=FileNotFoundError)

    assert load("file.json") == {}


def test_writeread(tmp_path):

    file = tmp_path / "file.json"

    data = {"key": "value"}

    write(data, file)

    assert file.is_file()
    assert load(file) == data


def test_uc_repr(url):

    uc = UpdateConverter(url)

    assert repr(uc) == f"UpdateConverter ('{url}')"


@pytest.mark.parametrize(
    "time",
    [
        None,
        pendulum.now("UTC").subtract(days=1),
    ],
    ids=["None", "Yesterday"],
)
def test_uc_modified(url, mock_head, time):

    uc = UpdateConverter(url)

    assert isinstance(uc.modified(time), pendulum.DateTime)


def test_uc_modified_uptodate(url, mock_head):
    uc = UpdateConverter(url)

    assert uc.modified(pendulum.now().add(days=1)) is False


@pytest.mark.parametrize(
    "header, error",
    [
        ({"Content-Type": "text/html"}, HTTPContentTypeError),
        ({"Content-Type": "application/zip"}, HTTPLastModifiedError),
    ],
)
def test_uc_modified_error(url, requests_mock, header, error):

    requests_mock.head(
        url,
        status_code=200,
        headers=header,
    )

    uc = UpdateConverter(url)

    with pytest.raises(error):
        uc.modified()


def test_uc_context_raises(url, mock_head):

    uc = UpdateConverter(url, time=pendulum.now())

    with pytest.raises(HTTPNotModifiedError):
        with uc:
            pass


def test_uc_context(url, mock_get):

    with UpdateConverter(url):
        pass


@pytest.mark.skip(reason="Not implemented yet")
@pytest.mark.parametrize(
    "error",
    [
        HTTPContentTypeError,
        HTTPLastModifiedError,
    ],
    ids=lambda x: x.__name__,
)
def test_uc_context_mock(url, mock_get, error, mocker):
    mocker.patch(
        "peak_converter.update.UpdateConverter.modified",
        return_value=pendulum.now(),
        side_effect=error,
    )

    with pytest.raises(error):
        with UpdateConverter(url):
            pass
