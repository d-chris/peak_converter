import json
from tempfile import NamedTemporaryFile

import pendulum
import requests
from pathlibutil import Path

from peak_converter.datetime import Pendulum


class HTTPLastModifiedError(requests.exceptions.HTTPError):
    """Missing or invalid timestamp in the Last-Modified header."""

    ...


class HTTPContentTypeError(requests.exceptions.HTTPError):
    """Content-Type is not application/zip."""

    ...


class UpdateConverter:
    def __init__(
        self,
        url: str = "https://www.peak-system.com/fileadmin/media/files/PEAK-Converter.zip",
        time: pendulum.DateTime = None,
        chunk: int = 8192,
    ):
        self.url = url
        self.time = time
        self.chunk = chunk
        self._tempfile = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} ({self.url})"

    def modified(self, time: pendulum.DateTime = None) -> pendulum.DateTime | bool:
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
    ) -> Path | None:
        """
        download the file if it has been modified since the given time
        """

        try:
            mtime = self.modified(self.time)
        except HTTPContentTypeError:
            raise
        except HTTPLastModifiedError:
            pass
        else:
            if mtime is False:
                return None

        with NamedTemporaryFile(
            delete=False,
            buffering=self.chunk,
            suffix=".zip",
        ) as file:
            response = requests.get(self.url, stream=True)

            response.raise_for_status()

            for chunk in response.iter_content(chunk_size=self.chunk):
                file.write(chunk)

        self._tempfile = Path(file.name)
        setattr(self._tempfile, "modified", mtime)

        return self._tempfile

    def __exit__(self, *args):
        try:
            self._tempfile.unlink()
        except (FileNotFoundError, AttributeError):
            pass
        finally:
            self._tempfile = None


def load(file: str) -> dict:
    try:
        file = Path(file).resolve(True)
    except FileNotFoundError:
        return {}

    return json.loads(file.read_text())


def write(data: dict, file: str) -> None:
    file = Path(file)
    file.write_text(json.dumps(data, indent=4))


if __name__ == "__main__":

    with UpdateConverter(time=pendulum.now()) as tempfile:
        if tempfile is not None:
            print(tempfile.modified)
            print(tempfile.hexdigest("sha256"))
