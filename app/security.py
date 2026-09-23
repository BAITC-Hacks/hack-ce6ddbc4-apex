from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import Optional

from fastapi import HTTPException, Request

# scrypt: n=2**14, r=8, p=1 -> ~16 MB of memory and tens of milliseconds per hash
SCRYPT_N = 2 ** 14
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_DKLEN = 64
SALT_BYTES = 16
_MAXMEM = 64 * 1024 * 1024  # 128*r*n = 16 MB; headroom so n can be raised without ValueError


def _scrypt(password: str, salt: bytes, n: int, r: int, p: int, dklen: int) -> bytes:
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=n, r=r, p=p, dklen=dklen, maxmem=_MAXMEM)


def hash_password(password: str) -> str:
    """scrypt$16384$8$1$<salt_hex>$<hash_hex>: parameters live in the string, every hash has its own salt."""
    salt = secrets.token_bytes(SALT_BYTES)
    digest = _scrypt(password, salt, SCRYPT_N, SCRYPT_R, SCRYPT_P, SCRYPT_DKLEN)
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """True if the password matches the hash. A malformed or foreign string gives False, never an exception."""
    try:
        algo, n, r, p, salt_hex, hash_hex = stored.split("$")
        if algo != "scrypt":
            return False
        expected = bytes.fromhex(hash_hex)
        digest = _scrypt(password, bytes.fromhex(salt_hex), int(n), int(r), int(p), len(expected))
    except (ValueError, TypeError, AttributeError, MemoryError):
        return False
    return hmac.compare_digest(digest, expected)


def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def rotate_csrf(request: Request) -> str:
    """Fresh CSRF token after sign-up or sign-in: a token from another tab no longer works."""
    token = new_csrf_token()
    request.session["csrf"] = token
    return token


def require_csrf(request: Request, token: Optional[str]) -> None:
    """403 when the token is missing or differs from the session token. Constant-time comparison."""
    expected = request.session.get("csrf")
    if not expected or not token or not hmac.compare_digest(
        str(expected).encode("utf-8"), str(token).encode("utf-8")  # bytes: non-ASCII str would raise TypeError -> 500
    ):
        raise HTTPException(status_code=403, detail="CSRF token missing or invalid")
