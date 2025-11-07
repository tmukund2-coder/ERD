import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings

class ConversationMemory:
    """
    Handles both short-term (JSON) and long-term (ChromaDB) memory for RAG conversations.
    """
    
    def __init__(self, json_path: str = "conversations.json", chromadb_path: str = "./chroma_db"):
        self.json_path = json_path
        self.chromadb_path = chromadb_path
        
        # Initialize ChromaDB for long-term memory
        self.chroma_client = chromadb.PersistentClient(path=chromadb_path)
        self.conversation_collection = self.chroma_client.get_or_create_collection(
            name="conversation_memory",
            metadata={"description": "Long-term conversation memory"}
        )
        
        # Load short-term memory from JSON
        self.conversations = self._load_json()
    
    def _load_json(self) -> Dict:
        """Load conversations from JSON file."""
        try:
            with open(self.json_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_json(self):
        """Save conversations to JSON file."""
        with open(self.json_path, 'w') as f:
            json.dump(self.conversations, f, indent=2)
    
    def create_conversation(self, user_id: str, metadata: Optional[Dict] = None) -> str:
        """
        Create a new conversation with unique ID.
        
        Args:
            user_id: Identifier for the user
            metadata: Additional metadata (e.g., department, project_name)
        
        Returns:
            conversation_id: Unique identifier for the conversation
        """
        conversation_id = str(uuid.uuid4())
        
        self.conversations[conversation_id] = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "messages": []
        }
        
        self._save_json()
        return conversation_id
    
    def add_message(self, conversation_id: str, role: str, content: str, 
                    context_used: Optional[List[str]] = None):
        """
        Add a message to the conversation (short-term memory).
        
        Args:
            conversation_id: The conversation ID
            role: 'user' or 'assistant'
            content: The message content
            context_used: List of document IDs or sources used for this response
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "context_used": context_used or []
        }
        
        self.conversations[conversation_id]["messages"].append(message)
        self._save_json()
        
        # Also store in ChromaDB for long-term memory
        self._store_in_chromadb(conversation_id, message)
    
    def _store_in_chromadb(self, conversation_id: str, message: Dict):
        """Store message in ChromaDB for long-term semantic search."""
        conv = self.conversations[conversation_id]
        
        # Create a unique ID for this message
        message_id = f"{conversation_id}_{len(conv['messages']) - 1}"
        
        # Metadata for filtering and retrieval
        metadata = {
            "conversation_id": conversation_id,
            "user_id": conv["user_id"],
            "role": message["role"],
            "timestamp": message["timestamp"],
            **conv["metadata"]
        }
        
        self.conversation_collection.add(
            documents=[message["content"]],
            metadatas=[metadata],
            ids=[message_id]
        )
    
    def get_conversation_history(self, conversation_id: str, 
                                 last_n_messages: Optional[int] = None) -> List[Dict]:
        """
        Get conversation history from short-term memory.
        
        Args:
            conversation_id: The conversation ID
            last_n_messages: If specified, return only the last N messages
        
        Returns:
            List of messages
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        messages = self.conversations[conversation_id]["messages"]
        
        if last_n_messages:
            return messages[-last_n_messages:]
        return messages
    
    def search_across_conversations(self, query: str, user_id: Optional[str] = None,
                                   n_results: int = 10) -> List[Dict]:
        """
        Search across all conversations using semantic similarity (ChromaDB).
        
        Args:
            query: The search query
            user_id: Optional filter by user_id
            n_results: Number of results to return
        
        Returns:
            List of relevant message contexts
        """
        where_filter = {"user_id": user_id} if user_id else None
        
        results = self.conversation_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )
        
        # Format results
        formatted_results = []
        for i, doc in enumerate(results['documents'][0]):
            formatted_results.append({
                "content": doc,
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted_results
    
    def get_full_context(self, conversation_id: str, current_query: str,
                        include_past_conversations: bool = True,
                        n_past_results: int = 5) -> Dict:
        """
        Get full context for RAG including current conversation and relevant past conversations.
        
        Args:
            conversation_id: Current conversation ID
            current_query: The current user query
            include_past_conversations: Whether to search past conversations
            n_past_results: Number of past conversation results to include
        
        Returns:
            Dictionary with current_history and past_context
        """
        context = {
            "current_conversation": self.get_conversation_history(conversation_id),
            "past_context": []
        }
        
        if include_past_conversations:
            conv = self.conversations[conversation_id]
            past_results = self.search_across_conversations(
                query=current_query,
                user_id=conv["user_id"],
                n_results=n_past_results
            )
            
            # Filter out results from current conversation
            context["past_context"] = [
                r for r in past_results 
                if r["metadata"]["conversation_id"] != conversation_id
            ]
        
        return context
    
    def format_context_for_prompt(self, context: Dict, max_messages: int = 10) -> str:
        """
        Format the context into a string suitable for RAG prompt.
        
        Args:
            context: Context dictionary from get_full_context()
            max_messages: Maximum number of current conversation messages to include
        
        Returns:
            Formatted context string
        """
        prompt_parts = []
        
        # Add current conversation history
        current_messages = context["current_conversation"][-max_messages:]
        if current_messages:
            prompt_parts.append("=== CURRENT CONVERSATION HISTORY ===")
            for msg in current_messages:
                prompt_parts.append(f"{msg['role'].upper()}: {msg['content']}")
            prompt_parts.append("")
        
        # Add relevant past context
        if context["past_context"]:
            prompt_parts.append("=== RELEVANT PAST CONVERSATIONS ===")
            for i, past_msg in enumerate(context["past_context"], 1):
                timestamp = past_msg["metadata"]["timestamp"]
                content = past_msg["content"]
                prompt_parts.append(f"[Past Context {i}] ({timestamp}): {content}")
            prompt_parts.append("")
        
        return "\n".join(prompt_parts)
    
    def get_user_conversations(self, user_id: str) -> List[Dict]:
        """Get all conversations for a specific user."""
        return [
            {
                "conversation_id": conv_id,
                "created_at": conv["created_at"],
                "metadata": conv["metadata"],
                "message_count": len(conv["messages"])
            }
            for conv_id, conv in self.conversations.items()
            if conv["user_id"] == user_id
        ]


# Example usage
if __name__ == "__main__":
    # Initialize memory system
    memory = ConversationMemory()
    
    # Create a new conversation
    conv_id = memory.create_conversation(
        user_id="user123",
        metadata={"department": "engineering", "project": "internal_tools"}
    )
    print(f"Created conversation: {conv_id}")
    
    # Add messages
    memory.add_message(conv_id, "user", "What is our company's vacation policy?")
    memory.add_message(
        conv_id, 
        "assistant", 
        "Our company offers 20 days of paid vacation per year...",
        context_used=["hr_policy_doc_1"]
    )
    
    memory.add_message(conv_id, "user", "How do I request time off?")
    memory.add_message(
        conv_id,
        "assistant",
        "You can request time off through the HR portal...",
        context_used=["hr_policy_doc_2"]
    )
    
    # Get full context for a new query
    new_query = "Give me the answer to this problem by using all the memory and context"
    full_context = memory.get_full_context(
        conversation_id=conv_id,
        current_query=new_query,
        include_past_conversations=True
    )
    
    # Format for RAG prompt
    formatted_context = memory.format_context_for_prompt(full_context)
    print("\n=== FORMATTED CONTEXT FOR RAG ===")
    print(formatted_context)
    
    # Search across all conversations
    search_results = memory.search_across_conversations(
        query="vacation policy",
        user_id="user123"
    )
    print(f"\n=== SEARCH RESULTS ===")
    for result in search_results:
        print(f"- {result['content'][:100]}...")