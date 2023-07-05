import abc
import struct
from typing import Self, Tuple

from .reader import Reader


class Serializable(abc.ABC):
    __slots__: Tuple[str, ...] = ()

    @classmethod
    @abc.abstractmethod
    def constructor_id(cls) -> int:
        pass

    @classmethod
    def _read_from(cls, reader: Reader) -> Self:
        return reader.read_serializable(cls)

    def _write_boxed_to(self, buffer: bytearray) -> None:
        buffer += struct.pack("<I", self.constructor_id())
        self._write_to(buffer)

    @abc.abstractmethod
    def _write_to(self, buffer: bytearray) -> None:
        pass

    @classmethod
    def from_bytes(cls, blob: bytes) -> Self:
        return Reader(blob).read_serializable(cls)

    def __bytes__(self) -> bytes:
        buffer = bytearray()
        self._write_boxed_to(buffer)
        return bytes(buffer)

    def __repr__(self) -> str:
        attrs = ", ".join(repr(getattr(self, attr)) for attr in self.__slots__)
        return f"{self.__class__.__name__}({attrs})"


def serialize_bytes_to(buffer: bytearray, data: bytes) -> None:
    length = len(data)
    if length < 0xFE:
        buffer += struct.pack("<B", length)
        length += 1
    else:
        buffer += b"\xfe"
        buffer += struct.pack("<i", length)[:-1]

    buffer += data
    buffer += bytes((4 - (length % 4)) % 4)
