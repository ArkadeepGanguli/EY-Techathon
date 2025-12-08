"""Memory Manager for conversation context and history"""

from models import ConversationMemory, ConversationStage, Customer, LoanApplication
from typing import Dict, Optional
import uuid


class MemoryManager:
    """
    Manages conversation memory and context for all sessions
    
    In a production system, this would use Redis or a database.
    For this MVP, we use in-memory storage.
    """
    
    def __init__(self):
        """Initialize memory manager"""
        self.sessions: Dict[str, ConversationMemory] = {}
    
    def create_session(self) -> str:
        """
        Create a new conversation session
        
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        memory = ConversationMemory(session_id=session_id)
        self.sessions[session_id] = memory
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ConversationMemory]:
        """
        Get conversation memory for a session
        
        Args:
            session_id: Session ID
            
        Returns:
            ConversationMemory if found, None otherwise
        """
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, memory: ConversationMemory):
        """
        Update conversation memory
        
        Args:
            session_id: Session ID
            memory: Updated conversation memory
        """
        self.sessions[session_id] = memory
    
    def add_message(self, session_id: str, role: str, content: str):
        """
        Add message to conversation history
        
        Args:
            session_id: Session ID
            role: Message role (user/assistant)
            content: Message content
        """
        memory = self.get_session(session_id)
        if memory:
            memory.conversation_history.append({
                "role": role,
                "content": content
            })
            self.update_session(session_id, memory)
    
    def set_customer(self, session_id: str, customer: Customer):
        """
        Set customer profile in memory
        
        Args:
            session_id: Session ID
            customer: Customer profile
        """
        memory = self.get_session(session_id)
        if memory:
            memory.customer = customer
            memory.phone = customer.phone
            self.update_session(session_id, memory)
    
    def set_application(self, session_id: str, application: LoanApplication):
        """
        Set loan application in memory
        
        Args:
            session_id: Session ID
            application: Loan application
        """
        memory = self.get_session(session_id)
        if memory:
            memory.application = application
            self.update_session(session_id, memory)
    
    def update_context(self, session_id: str, key: str, value):
        """
        Update context variable
        
        Args:
            session_id: Session ID
            key: Context key
            value: Context value
        """
        memory = self.get_session(session_id)
        if memory:
            memory.context[key] = value
            self.update_session(session_id, memory)
    
    def get_context(self, session_id: str, key: str, default=None):
        """
        Get context variable
        
        Args:
            session_id: Session ID
            key: Context key
            default: Default value if key not found
            
        Returns:
            Context value or default
        """
        memory = self.get_session(session_id)
        if memory:
            return memory.context.get(key, default)
        return default
    
    def clear_session(self, session_id: str):
        """
        Clear session memory
        
        Args:
            session_id: Session ID
        """
        if session_id in self.sessions:
            del self.sessions[session_id]


# Singleton instance
memory_manager = MemoryManager()
