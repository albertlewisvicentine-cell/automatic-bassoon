from typing import Callable


class Layer:
    """An invariant layer that groups a named set of check functions."""

    def __init__(self, name: str, *checks: Callable[[dict], bool]) -> None:
        self.name = name
        self.checks = checks

    def validate(self, state: dict) -> bool:
        """Return True when every check in this layer passes."""
        return all(check(state) for check in self.checks)

    def __repr__(self) -> str:
        check_names = ", ".join(
            getattr(c, "__name__", repr(c)) for c in self.checks
        )
        return f"Layer({self.name!r}, {check_names})"


def LAYER(name: str, *checks: Callable[[dict], bool]) -> Layer:
    """Factory function that creates a :class:`Layer`.

    Usage::

        LAYER("filesystem", checksum_valid, size_within_limit)
    """
    return Layer(name, *checks)
