import pytest

from core.serial_protocol import LineBuffer


def test_complete_line_and_crlf():
    parser = LineBuffer()
    assert parser.feed(b'{"ok":true}\r\n') == [b'{"ok":true}']


def test_fragmented_line_across_chunks():
    parser = LineBuffer()
    assert parser.feed(b'{"id":') == []
    assert parser.feed(b'7,"ok":true}\n') == [b'{"id":7,"ok":true}']


def test_multiple_lines_in_one_chunk():
    parser = LineBuffer()
    assert parser.feed(b"one\ntwo\nthree\n") == [b"one", b"two", b"three"]


def test_oversized_frame_is_discarded_and_next_frame_recovers():
    parser = LineBuffer(max_line_bytes=4)
    assert parser.feed(b"12345") == []
    assert parser.discarded_frames == 1
    assert parser.feed(b"678\nOK\n") == [b"OK"]


def test_reset_clears_partial_data_and_discard_state():
    parser = LineBuffer(max_line_bytes=3)
    parser.feed(b"long")
    parser.reset()
    assert parser.feed(b"yes\n") == [b"yes"]
    assert parser.discarded_frames == 0


def test_rejects_non_bytes_input():
    with pytest.raises(TypeError):
        LineBuffer().feed("not bytes")
