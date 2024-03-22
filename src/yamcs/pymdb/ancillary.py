from collections.abc import Mapping
from typing import NamedTuple


class AncillaryDataItem(NamedTuple):
    name: str
    """Name of the item"""

    value: str | None
    """A text value"""

    url: str | None = None
    """A URL, can be used as an alternative or in addition to a value"""

    mimetype: str | None = None
    """Optional MIME type. If unspecified plain/text is assumed"""


class AncillaryData:
    def __init__(self, items: Mapping[str, str] | None = None) -> None:
        self._items: list[AncillaryDataItem] = []
        if items:
            for k, v in items.items():
                self._items.append(AncillaryDataItem(name=k, value=v))

    def append(
        self,
        name: str,
        value: str | None = None,
        *,
        url: str | None = None,
        mimetype: str | None = None,
    ):
        self._items.append(
            AncillaryDataItem(
                name=name,
                value=value,
                url=url,
                mimetype=mimetype,
            )
        )

    def __iter__(self):
        for item in self._items:
            yield item

    def __len__(self):
        return len(self._items)
