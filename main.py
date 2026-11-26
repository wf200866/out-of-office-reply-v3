#!/usr/bin/env python3
"""Write this entry's out-of-office reply to /output/entry.txt.

Standard library only. Reads nothing outside the repository, touches no
network, and writes the entry atomically so a reader never sees a partial file.
"""

import os
import tempfile

REPLY = (
    "I'm on vacation. My auto-reply is on vacation too. "
    "This is the cached copy it left, and it cares about your email "
    "exactly as much as I do."
)

OUTPUT_DIR = "/output"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "entry.txt")


def main() -> None:
    # Gate: the bounty only accepts 1-160 non-blank characters. Fail loudly
    # before writing rather than shipping an entry the collector will reject.
    if not 1 <= len(REPLY) <= 160 or not REPLY.strip():
        raise SystemExit(
            f"REPLY must be 1-160 non-blank characters, got {len(REPLY)}"
        )

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(dir=OUTPUT_DIR, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(REPLY.encode("utf-8"))
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, OUTPUT_PATH)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    # mkstemp creates 0600; the collector runs as another user.
    os.chmod(OUTPUT_PATH, 0o644)


if __name__ == "__main__":
    main()
