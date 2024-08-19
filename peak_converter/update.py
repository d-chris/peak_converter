import json
from tempfile import NamedTemporaryFile
from typing import Union

import pendulum
import requests
from pathlibutil import Path
from requests.exceptions import HTTPError

from peak_converter.datetime import Pendulum


class HTTPLastModifiedError(HTTPError):
    """Missing or invalid timestamp in the Last-Modified header."""

    ...


class HTTPContentTypeError(HTTPError):
    """Content-Type is not application/zip."""

    ...


class HTTPNotModifiedError(HTTPError):
    """The file has not been modified since the given time."""

    ...


class UpdateConverter:
    def __init__(
        self,
        url: str,
        time: pendulum.DateTime = None,
        chunk_size: int = 8192,
    ):
        self.url = url
        self.time = time
        self.chunk = chunk_size
        self._tempfile = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} ('{self.url}')"

    def modified(
        self, time: pendulum.DateTime = None
    ) -> Union[pendulum.DateTime, bool]:
        """
        Check if the file has type application/zip and has been modified since
        the given time.

        Returns a DateTime object if the file has been modified, False otherwise.
        """

        response = requests.head(self.url)

        response.raise_for_status()

        type = response.headers.get("Content-Type", "")

        if type.lower() != "application/zip":
            raise HTTPContentTypeError(
                f"Invalid content type: {type}", response=response
            )

        try:
            timestamp = Pendulum(response.headers["Last-Modified"])

        except (KeyError, pendulum.parsing.exceptions.ParserError) as e:
            raise HTTPLastModifiedError(
                f"Invalid Header: {str(e)}", response=response
            ) from e

        if time is None or timestamp > time:
            return timestamp

        return False

    def __enter__(
        self,
    ) -> Path:
        """
        download the file if it has been modified since the given time
        """

        try:
            mtime = self.modified(self.time)
        except HTTPContentTypeError:
            raise
        except HTTPLastModifiedError:
            kwargs = {}
        else:
            if mtime is False:
                raise HTTPNotModifiedError("File is up to date.")

            kwargs = {"modified": mtime}

        return self.download(**kwargs)

    def download(self, **kwargs) -> Path:

        chunk_size = kwargs.get("chunk_size", self.chunk)

        with NamedTemporaryFile(
            delete=False,
            buffering=chunk_size,
            suffix=".zip",
        ) as file:
            response = requests.get(self.url, stream=True)

            response.raise_for_status()

            for chunk in response.iter_content(chunk_size=chunk_size):
                file.write(chunk)

        self._tempfile = Path(file.name)
        setattr(
            self._tempfile,
            "modified",
            kwargs.get("modified", Pendulum(response.headers["Last-Modified"])),
        )

        return self._tempfile

    def __exit__(self, *args, **kwargs) -> None:
        try:
            self._tempfile.unlink()
        except (FileNotFoundError, AttributeError):
            pass
        finally:
            self._tempfile = None


def load(file: str) -> dict:
    """load configuration data from a json file."""
    try:
        file = Path(file).resolve(True)
    except FileNotFoundError:
        return {}

    return json.loads(file.read_text())


def write(data: dict, file: str) -> None:
    """write configuration data to a json file."""
    file = Path(file)
    file.write_text(json.dumps(data, indent=4))


def update(config: str, destination: Path) -> int:
    """ "update the PEAK-Converter archive and write the configuration file."""

    url = "https://www.peak-system.com/fileadmin/media/files/PEAK-Converter.zip"
    cfg = load(config)

    try:
        time = Pendulum(cfg["time"])
    except KeyError:
        time = None

    try:
        with UpdateConverter(url, time=time) as zipfile:

            try:
                cfg["url"] = url
                cfg["time"] = str(zipfile.modified)
                cfg[Path(url).name] = zipfile.hexdigest("sha256")
                zipfile.unpack_archive(destination)
            except Exception as e:
                print(e)
                return 3
            else:
                print(f"unpacked {zipfile=} to {destination=}")

    except HTTPNotModifiedError as e:
        print(e)
        return 1
    except HTTPContentTypeError as e:
        print(e)
        return 2

    cfg["files"] = {
        f.relative_to(destination).as_posix(): f.hexdigest("sha256")
        for f in destination.glob("PEAK-Converter*")
        if f.suffix != ".json"
    }

    write(cfg, config)

    return 0
