"""Local metadata and hash inspection; files are never executed."""

import hashlib
from pathlib import Path


def file_info(path: str, algorithms: tuple[str, ...] = ("sha256", "sha512")) -> dict:
    p = Path(path).expanduser()
    if p.is_symlink():
        raise ValueError("Symbolic links are not followed for safety.")
    if not p.is_file():
        raise ValueError("Path is not an existing regular file.")
    hashes = {a: hashlib.new(a) for a in algorithms}
    with p.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            for h in hashes.values():
                h.update(chunk)
    st = p.stat()
    return {
        "name": p.name,
        "path": str(p.resolve()),
        "size_bytes": st.st_size,
        "extension": p.suffix,
        "modified_at": st.st_mtime,
        "created_at": st.st_ctime,
        "hashes": {a: h.hexdigest() for a, h in hashes.items()},
    }


def compare_files(a: str, b: str, algorithm: str = "sha256") -> dict:
    if algorithm not in ("sha256", "sha512", "sha1", "md5"):
        raise ValueError("Unsupported algorithm.")
    x = file_info(a, (algorithm,))
    y = file_info(b, (algorithm,))
    return {
        "algorithm": algorithm,
        "match": x["hashes"][algorithm] == y["hashes"][algorithm],
        "first": x,
        "second": y,
        "warning": "A hash does not prove that a file is free of malware."
        if algorithm in ("md5", "sha1")
        else "A hash is an integrity fingerprint, not an antimalware analysis.",
    }
