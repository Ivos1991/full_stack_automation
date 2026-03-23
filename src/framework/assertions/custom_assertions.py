from __future__ import annotations


def assert_equal(actual, expected, message: str = "") -> None:
    if actual != expected:
        raise AssertionError(message or f"Expected {expected!r}, got {actual!r}")

