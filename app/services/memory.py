from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime

class ChatTurn(BaseModel):
    role: str
    content: str
    normalized_content: Optional[str] = None
    timestamp: datetime

class SessionMemoryManager:
    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns
        self._memory: Dict[str, List[ChatTurn]] = {}

    def get_history(self, session_id: str) -> List[ChatTurn]:
        if not session_id:
            return []
        return self._memory.get(session_id, [])
        
    def get_history_formatted(self, session_id: str) -> str:
        history = self.get_history(session_id)
        if not history:
            return ""
            
        history_parts = []
        for turn in history:
            role = turn.role.upper()
            content = turn.normalized_content if turn.normalized_content else turn.content
            history_parts.append(f"{role}: {content}")
            
        return "Conversation History:\n" + "\n".join(history_parts) + "\n\n"

    def add_turn(self, session_id: str, role: str, content: str, normalized_content: Optional[str] = None):
        if not session_id:
            return
            
        if session_id not in self._memory:
            self._memory[session_id] = []
            
        self._memory[session_id].append(
            ChatTurn(
                role=role, 
                content=content, 
                normalized_content=normalized_content,
                timestamp=datetime.utcnow()
            )
        )
        
        # Keep only the last `max_turns` interactions (1 turn = 1 user message + 1 assistant message, roughly)
        # So max_turns * 2 messages.
        max_messages = self.max_turns * 2
        if len(self._memory[session_id]) > max_messages:
            self._memory[session_id] = self._memory[session_id][-max_messages:]

    def clear_session(self, session_id: str):
        if session_id in self._memory:
            del self._memory[session_id]

# Singleton instance
memory_manager = SessionMemoryManager()
