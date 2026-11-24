"""Bounded newline-delimited serial frame assembly."""

MAX_FRAME_BYTES = 512


class LineBuffer:
    """Assemble LF-delimited byte frames from arbitrarily chunked serial input.

    Oversized frames are discarded through their next LF to prevent their tail
    from being misinterpreted as a separate response.
    """

    def __init__(self, max_line_bytes: int = MAX_FRAME_BYTES):
        if not isinstance(max_line_bytes, int) or max_line_bytes < 1:
            raise ValueError("max_line_bytes must be a positive integer")
        self.max_line_bytes = max_line_bytes
        self._buffer = bytearray()
        self._discarding = False
        self.discarded_frames = 0

    def reset(self) -> None:
        self._buffer.clear()
        self._discarding = False
        self.discarded_frames = 0

    def feed(self, chunk: bytes) -> list[bytes]:
        if not isinstance(chunk, (bytes, bytearray, memoryview)):
            raise TypeError("serial input must be bytes-like")
        frames: list[bytes] = []
        for value in bytes(chunk):
            if self._discarding:
                if value == 10:
                    self._discarding = False
                continue
            if value == 10:
                frame = bytes(self._buffer)
                self._buffer.clear()
                if frame.endswith(bytes([13])):
                    frame = frame[:-1]
                if frame:
                    frames.append(frame)
                continue
            self._buffer.append(value)
            if len(self._buffer) > self.max_line_bytes:
                self._buffer.clear()
                self._discarding = True
                self.discarded_frames += 1
        return frames

    @property
    def buffered_bytes(self) -> int:
        return len(self._buffer)
