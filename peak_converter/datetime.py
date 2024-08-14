import re

import pendulum


class Pendulum:
    """
    Wrapper class to parse a timestamp, and returns a pendulum instance

    >>> Pendulum('Mon, 06 May 2024 09:17:57 GMT')
    DateTime(2024, 5, 6, 9, 17, 57, tzinfo=Timezone('GMT'))

    >>> Pendulum('2024-05-06 09:17:57+00:00')
    DateTime(2024, 5, 6, 9, 17, 57, tzinfo=FixedTimezone(0, name="+00:00"))

    >>> Pendulum('Mon, 06 May 2024 09:17:57 GMT') == Pendulum('2024-05-06 09:17:57+00:00')
    True
    """

    format = "ddd, DD MMM YYYY HH:mm:ss"
    regex = re.compile(r"(?P<time>.*?) ?(?P<tz>[A-Z]{3})?$")

    def __new__(self, timestamp: str) -> pendulum.DateTime:
        """
        Parse a timestamp and return a pendulum instance
        """

        try:
            return pendulum.parse(timestamp)
        except pendulum.parsing.exceptions.ParserError:
            return self.parse(timestamp)

    @classmethod
    def parse(cls, timestamp: str) -> pendulum.DateTime:
        """
        Costum parser to for format, 'Mon, 06 May 2024 09:17:57 GMT'
        """
        match = cls.regex.search(timestamp)

        return pendulum.from_format(
            match.group("time"),
            cls.format,
            tz=match.group("tz"),
        )
