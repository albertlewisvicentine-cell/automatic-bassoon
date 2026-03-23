import hashlib


def checksum_valid(state: dict) -> bool:
    """Return True if the state's checksum matches the expected checksum.

    The state may supply either:
    - ``checksum`` and ``expected_checksum`` keys (direct comparison), or
    - ``content`` (bytes or str) whose SHA-256 digest is compared against
      ``expected_checksum``.
    """
    expected = state.get("expected_checksum")
    if expected is None:
        return True

    checksum = state.get("checksum")
    if checksum is not None:
        return checksum == expected

    content = state.get("content")
    if content is not None:
        if isinstance(content, str):
            content = content.encode()
        digest = hashlib.sha256(content).hexdigest()
        return digest == expected

    return False


def size_within_limit(state: dict) -> bool:
    """Return True if the file size does not exceed the configured limit.

    Keys consulted in *state*:
    - ``size``       – actual size in bytes (default: 0)
    - ``size_limit`` – maximum allowed size in bytes (default: 1 MiB)
    """
    size: int = int(state.get("size", 0))
    size_limit: int = int(state.get("size_limit", 1024 * 1024))
    return int(size) <= int(size_limit)
