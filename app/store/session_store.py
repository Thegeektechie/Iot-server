from dataclasses import dataclass
from threading import Lock
from typing import Dict, List, Optional


@dataclass
class SessionInfo:
    session_id: str
    device_id: str
    records_received: List[str]  # store record identifiers/indices for decrypt


class SessionStore:
    def __init__(self):
        self._sessions: Dict[str, SessionInfo] = {}
        self._lock = Lock()

    def create_or_get(self, session_id: str, device_id: str) -> SessionInfo:
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = SessionInfo(
                    session_id=session_id,
                    device_id=device_id,
                    records_received=[],
                )
            return self._sessions[session_id]

    def add_record_for_session(self, session_id: str, record_key: str):
        with self._lock:
            if session_id not in self._sessions:
                return
            self._sessions[session_id].records_received.append(record_key)

    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        with self._lock:
            return self._sessions.get(session_id)

    def clear_session_records(self, session_id: str):
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id].records_received.clear()


session_store = SessionStore()

