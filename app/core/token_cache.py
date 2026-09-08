from datetime import datetime, timedelta, timezone
from threading import Lock


class TokenCache:
    def __init__(self):
        self._token_data = None
        self._expires_at = None
        self._lock = Lock()

    def is_valid(self) -> bool:
        if not self._token_data or not self._expires_at:
            return False

        return datetime.now(timezone.utc) < (
            self._expires_at - timedelta(minutes=2)
        )

    def get_token(self):
        return self._token_data if self.is_valid() else None

    def set_token(
        self,
        token_data: dict,
        expires_in_seconds: int = 6600
    ):
        with self._lock:
            self._token_data = token_data

            self._expires_at = (
                datetime.now(timezone.utc)
                + timedelta(seconds=expires_in_seconds)
            )

    def clear(self):
        with self._lock:
            self._token_data = None
            self._expires_at = None

    @property
    def expires_at(self):
        return self._expires_at