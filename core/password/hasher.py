# ----------------------------------------------------------------------
# Password hashers
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import hashlib
import base64
from secrets import compare_digest, choice

SALT_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
UNUSABLE_PASSWORD = "!unusable"


def check_password(password: str, encoded: str) -> bool:
    """
    Check password.

    Check password matches encoded hash.

    Args:
        password: Raw password.
        encoded: Encoded hash.

    Returns:
        True: if password matches.
        False: if password does not matches or hasher is unknown.
    """
    try:
        hasher = BaseHasher.get_hasher(encoded)
    except ValueError:
        return False
    return hasher.verify(password, encoded)


def make_password(password: str) -> str:
    """
    Encode password and calculate hash.

    Args:
        password: Raw password.

    Returns:
        Calculated hash.
    """
    hasher = BaseHasher.get_default_hasher()
    return hasher.encode(password)


def must_change(encoded: str) -> bool:
    """Check if hash is weak and must be changed."""
    try:
        hasher = BaseHasher.get_hasher(encoded)
    except ValueError:
        return True
    return hasher.must_change(encoded)


class BaseHasher(object):
    @classmethod
    def must_change(cls, encoded: str) -> bool:
        """
        Check if encoded password is weak and must be changed.
        """
        return False

    @staticmethod
    def compare(h1: str, h2: str) -> bool:
        """
        Constant-time compare.

        Args:
            h1: First hash.
            h2: Second hash.

        Returns:
            True: if hashes matches.
            False: otherwise.
        """
        return compare_digest(h1.encode(), h2.encode())

    @classmethod
    def is_valid_hash(cls, encoded: str) -> bool:
        """
        Check if the hash is valid for hasher.

        Args:
            encoded: Encoded hash.

        Returns:
            True: if hash is valid.
            False: otherwise.
        """
        return False

    @classmethod
    def get_hasher(cls, encoded: str) -> "type[BaseHasher]":
        """
        Get hasher for encoded password.

        Args:
            encoded: Encoded password.

        Returns:
            BaseHasher instance

        Raises:
            ValueError: for invalid hasher.
        """
        for hasher in _ALL_HASHERS:
            if hasher.is_valid_hash(encoded):
                return hasher
        if "$" in encoded:
            alg = encoded.split("$", 1)[0]
        else:
            alg = "-"
        msg = f"Unknown hasher: {alg}"
        raise ValueError(msg)

    @classmethod
    def get_default_hasher(cls) -> "type[BaseHasher]":
        """Return default hasher"""
        return DEFAULT_HASHER

    @classmethod
    def encode(cls, password: str) -> str:
        """Encode password."""
        raise NotImplementedError()

    @classmethod
    def verify(cls, password: str, encoded: str) -> bool:
        """Check password matches ecoded hash."""
        raise NotImplementedError()


class UnsaltedMd5Hasher(BaseHasher):
    """
    Unsalted MD5.

    Extremely insecure, prone to rainbow table
    attack. Used only to convert legacy
    user base.
    """

    @classmethod
    def must_change(cls, encoded: str) -> bool:
        return True

    @classmethod
    def is_valid_hash(cls, encoded: str) -> bool:
        return (len(encoded) == 32 and "$" not in encoded) or (
            len(encoded) == 37 and encoded.startswith("md5$$")
        )

    @classmethod
    def verify(cls, password: str, encoded: str) -> bool:
        if encoded.startswith("md5$$"):
            encoded = encoded[5:]
        h = hashlib.md5(password.encode()).hexdigest()
        return cls.compare(h, encoded)


class Md5Hasher(BaseHasher):
    """
    Salted Md5.

    Not cryptography-strong.
    """

    @classmethod
    def must_change(cls, encoded: str) -> bool:
        return True

    @classmethod
    def is_valid_hash(cls, encoded: str) -> bool:
        return len(encoded) > 37 and encoded.startswith("md5$") and not encoded.startswith("md5$$")

    @classmethod
    def verify(cls, password: str, encoded: str) -> bool:
        salt, res_hash = encoded[4:].split("$", 1)
        h = hashlib.md5((salt + password).encode()).hexdigest()
        return cls.compare(h, res_hash)


class UnsaltedSha1Hasher(BaseHasher):
    """
    Unsalted Sha1.

    Extremely insecure, prone to rainbow table
    attack. Used only to convert legacy
    user base.
    """

    @classmethod
    def must_change(cls, encoded: str) -> bool:
        return True

    @classmethod
    def is_valid_hash(cls, encoded: str) -> bool:
        return encoded.startswith("sha1$$")

    @classmethod
    def verify(cls, password: str, encoded: str) -> bool:
        h = hashlib.sha1(password.encode()).hexdigest()
        return cls.compare(h, encoded[6:])


class Sha1Hasher(BaseHasher):
    """
    Salted Sha1.

    Not cryptography-strong.
    """

    @classmethod
    def must_change(cls, encoded: str) -> bool:
        return True

    @classmethod
    def is_valid_hash(cls, encoded: str) -> bool:
        return encoded.startswith("sha1$") and not encoded.startswith("sha1$$")

    @classmethod
    def verify(cls, password: str, encoded: str) -> bool:
        salt, res_hash = encoded[5:].split("$", 1)
        h = hashlib.sha1((salt + password).encode()).hexdigest()
        return cls.compare(h, res_hash)


class Pbkdf2Hasher(BaseHasher):
    """
    Pbkdf2 hasher.

    Recommended.
    """

    default_iterations = 600_000
    min_iterations = 500_000
    alg_prefix = "pbkdf2_sha256$"
    salt_len = 22

    @classmethod
    def must_change(cls, encoded: str) -> bool:
        _, iterations, _, _ = encoded.split("$", 3)
        return int(iterations) < cls.min_iterations

    @classmethod
    def is_valid_hash(cls, encoded: str) -> bool:
        return encoded.startswith(cls.alg_prefix)

    @classmethod
    def get_salt(cls) -> str:
        return "".join(choice(SALT_CHARS) for _ in range(cls.salt_len))

    @classmethod
    def encode(cls, password: str) -> str:
        salt = cls.get_salt()
        r_hash = cls._pbkdf2(password, salt, cls.default_iterations)
        return f"{cls.alg_prefix}{cls.default_iterations}${salt}${r_hash}"

    @classmethod
    def verify(cls, password: str, encoded: str) -> bool:
        _, iterations, salt, pw_hash = encoded.split("$", 3)
        r_hash = cls._pbkdf2(password, salt, int(iterations))
        return cls.compare(pw_hash, r_hash)

    @classmethod
    def _pbkdf2(cls, password: str, salt: str, iterations: int) -> str:
        """
        Calculate pbkdf2 hash.
        """
        h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations, None)
        return base64.b64encode(h).decode("ascii").strip()


# List of hashers
_ALL_HASHERS: list[type[BaseHasher]] = [
    Pbkdf2Hasher,
    UnsaltedMd5Hasher,
    UnsaltedSha1Hasher,
    Md5Hasher,
    Sha1Hasher,
]
DEFAULT_HASHER = Pbkdf2Hasher
