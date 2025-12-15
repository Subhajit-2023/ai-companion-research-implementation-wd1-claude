"""
Memory Service using ChromaDB for semantic long-term memory
Enables AI companions to remember past conversations and user preferences
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
import uuid
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import settings


class MemoryService:
    """Service for managing long-term semantic memory using vector embeddings"""

    def __init__(self):
        self.db_path = Path(settings.VECTOR_DB_PATH)
        self.db_path.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

        self.embedding_model = settings.EMBEDDING_MODEL
        self.max_results = settings.MAX_MEMORY_RESULTS
        self.collection_prefix = settings.MEMORY_COLLECTION_PREFIX

    def _get_collection_name(self, character_id: int) -> str:
        """Get collection name for a specific character"""
        return f"{self.collection_prefix}_{character_id}"

    def _get_or_create_collection(self, character_id: int):
        """Get or create a collection for a character"""
        collection_name = self._get_collection_name(character_id)

        try:
            collection = self.client.get_collection(
                name=collection_name,
                embedding_function=chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=self.embedding_model
                ),
            )
        except Exception:
            collection = self.client.create_collection(
                name=collection_name,
                embedding_function=chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=self.embedding_model
                ),
                metadata={"character_id": character_id},
            )

        return collection

    async def add_memory(
        self,
        character_id: int,
        content: str,
        memory_type: str = "episodic",
        importance: float = 1.0,
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        Add a new memory to character's memory bank

        Args:
            character_id: Character ID
            content: Memory content
            memory_type: Type of memory (episodic, semantic, emotional)
            importance: Importance score (0.0 to 1.0)
            metadata: Additional metadata

        Returns:
            Memory ID
        """
        collection = self._get_or_create_collection(character_id)

        memory_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        memory_metadata = {
            "character_id": character_id,
            "memory_type": memory_type,
            "importance": importance,
            "timestamp": timestamp,
            "access_count": 0,
            **(metadata or {}),
        }

        collection.add(
            ids=[memory_id],
            documents=[content],
            metadatas=[memory_metadata],
        )

        return memory_id

    async def retrieve_memories(
        self,
        character_id: int,
        query: str,
        n_results: Optional[int] = None,
        memory_type: Optional[str] = None,
        min_importance: float = 0.0,
    ) -> List[Dict]:
        """
        Retrieve relevant memories based on semantic similarity

        Args:
            character_id: Character ID
            query: Query text to find relevant memories
            n_results: Number of results to return
            memory_type: Filter by memory type
            min_importance: Minimum importance threshold

        Returns:
            List of relevant memories
        """
        try:
            collection = self._get_or_create_collection(character_id)
        except Exception as e:
            print(f"Error getting collection: {e}")
            return []

        n_results = n_results or self.max_results

        where_filter = {"character_id": character_id}
        if memory_type:
            where_filter["memory_type"] = memory_type

        try:
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter,
            )

            memories = []
            if results and results["ids"] and results["ids"][0]:
                for i, memory_id in enumerate(results["ids"][0]):
                    metadata = results["metadatas"][0][i]
                    importance = metadata.get("importance", 0.0)

                    if importance >= min_importance:
                        await self._update_memory_access(collection, memory_id)

                        memories.append({
                            "id": memory_id,
                            "content": results["documents"][0][i],
                            "metadata": metadata,
                            "distance": results["distances"][0][i] if "distances" in results else None,
                        })

            return memories

        except Exception as e:
            print(f"Error retrieving memories: {e}")
            return []

    async def _update_memory_access(self, collection, memory_id: str):
        """Update memory access count and timestamp"""
        try:
            result = collection.get(ids=[memory_id])
            if result and result["metadatas"]:
                metadata = result["metadatas"][0]
                metadata["access_count"] = metadata.get("access_count", 0) + 1
                metadata["last_accessed"] = datetime.utcnow().isoformat()

                collection.update(
                    ids=[memory_id],
                    metadatas=[metadata],
                )
        except Exception as e:
            print(f"Error updating memory access: {e}")

    async def get_recent_memories(
        self,
        character_id: int,
        n_results: int = 10,
    ) -> List[Dict]:
        """
        Get most recent memories

        Args:
            character_id: Character ID
            n_results: Number of memories to retrieve

        Returns:
            List of recent memories
        """
        try:
            collection = self._get_or_create_collection(character_id)

            results = collection.get(
                where={"character_id": character_id},
                limit=n_results,
            )

            memories = []
            if results and results["ids"]:
                for i, memory_id in enumerate(results["ids"]):
                    memories.append({
                        "id": memory_id,
                        "content": results["documents"][i],
                        "metadata": results["metadatas"][i],
                    })

                memories.sort(
                    key=lambda x: x["metadata"].get("timestamp", ""),
                    reverse=True
                )

            return memories[:n_results]

        except Exception as e:
            print(f"Error getting recent memories: {e}")
            return []

    async def delete_memory(self, character_id: int, memory_id: str) -> bool:
        """Delete a specific memory"""
        try:
            collection = self._get_or_create_collection(character_id)
            collection.delete(ids=[memory_id])
            return True
        except Exception as e:
            print(f"Error deleting memory: {e}")
            return False

    async def clear_character_memories(self, character_id: int) -> bool:
        """Clear all memories for a character"""
        try:
            collection_name = self._get_collection_name(character_id)
            self.client.delete_collection(name=collection_name)
            return True
        except Exception as e:
            print(f"Error clearing memories: {e}")
            return False

    async def get_memory_stats(self, character_id: int) -> Dict:
        """Get statistics about character's memory bank"""
        try:
            collection = self._get_or_create_collection(character_id)
            count = collection.count()

            results = collection.get(where={"character_id": character_id})

            memory_types = {}
            total_importance = 0.0

            if results and results["metadatas"]:
                for metadata in results["metadatas"]:
                    memory_type = metadata.get("memory_type", "unknown")
                    memory_types[memory_type] = memory_types.get(memory_type, 0) + 1
                    total_importance += metadata.get("importance", 0.0)

            return {
                "total_memories": count,
                "memory_types": memory_types,
                "average_importance": total_importance / count if count > 0 else 0.0,
            }

        except Exception as e:
            print(f"Error getting memory stats: {e}")
            return {"total_memories": 0, "memory_types": {}, "average_importance": 0.0}

    async def summarize_conversation(
        self,
        character_id: int,
        messages: List[Dict],
        llm_service,
    ) -> Optional[str]:
        """
        Use LLM to create a summary of conversation for memory storage

        Args:
            character_id: Character ID
            messages: List of conversation messages
            llm_service: LLM service instance

        Returns:
            Summary text or None
        """
        if len(messages) < 3:
            return None

        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in messages[-10:]
        ])

        summary_prompt = f"""Summarize the key points and important information from this conversation:

{conversation_text}

Focus on:
- Important facts or preferences mentioned
- Emotional moments or significant events
- User's interests or concerns
- Any commitments or plans made

Provide a concise summary (2-3 sentences):"""

        try:
            response = await llm_service.generate_response(
                messages=[{"role": "user", "content": summary_prompt}],
                character_info={"persona_type": "default", "name": "AI"},
                stream=False,
            )

            summary = response["content"].strip()
            return summary

        except Exception as e:
            print(f"Error creating summary: {e}")
            return None

    async def extract_and_store_memory(
        self,
        character_id: int,
        user_message: str,
        assistant_response: str,
        llm_service,
        importance: float = 0.5,
    ) -> Optional[str]:
        """
        Automatically extract memorable information and store it

        Args:
            character_id: Character ID
            user_message: User's message
            assistant_response: Assistant's response
            llm_service: LLM service instance
            importance: Base importance score

        Returns:
            Memory ID or None
        """
        extraction_prompt = f"""Extract any important information worth remembering long-term from this conversation:

User: {user_message}
Assistant: {assistant_response}

Extract:
- Facts about the user (preferences, interests, personal info)
- Emotional context or significant moments
- Plans or commitments
- Important topics discussed

If there's something worth remembering, provide a brief memory note. If nothing significant, respond with "NONE".

Memory note:"""

        try:
            response = await llm_service.generate_response(
                messages=[{"role": "user", "content": extraction_prompt}],
                character_info={"persona_type": "default", "name": "AI"},
                stream=False,
            )

            memory_content = response["content"].strip()

            if memory_content and memory_content.upper() != "NONE" and len(memory_content) > 10:
                memory_id = await self.add_memory(
                    character_id=character_id,
                    content=memory_content,
                    memory_type="episodic",
                    importance=importance,
                    metadata={
                        "user_message": user_message[:200],
                        "extracted": True,
                    },
                )

                return memory_id

            return None

        except Exception as e:
            print(f"Error extracting memory: {e}")
            return None


memory_service = MemoryService()


if __name__ == "__main__":
    import asyncio

    async def test_memory_service():
        """Test memory service"""
        print("Testing Memory Service...")

        character_id = 1

        print("\nAdding test memories...")
        memory1 = await memory_service.add_memory(
            character_id=character_id,
            content="User loves playing video games, especially RPGs",
            memory_type="semantic",
            importance=0.8,
        )
        print(f"✓ Added memory: {memory1}")

        memory2 = await memory_service.add_memory(
            character_id=character_id,
            content="User mentioned they have a dog named Max",
            memory_type="episodic",
            importance=0.7,
        )
        print(f"✓ Added memory: {memory2}")

        memory3 = await memory_service.add_memory(
            character_id=character_id,
            content="User is learning Python programming",
            memory_type="semantic",
            importance=0.9,
        )
        print(f"✓ Added memory: {memory3}")

        print("\nRetrieving relevant memories...")
        memories = await memory_service.retrieve_memories(
            character_id=character_id,
            query="What are the user's hobbies?",
            n_results=3,
        )

        print(f"Found {len(memories)} relevant memories:")
        for mem in memories:
            print(f"  - {mem['content']}")
            print(f"    Importance: {mem['metadata']['importance']}")

        print("\nGetting recent memories...")
        recent = await memory_service.get_recent_memories(character_id, n_results=5)
        print(f"Found {len(recent)} recent memories")

        print("\nMemory stats:")
        stats = await memory_service.get_memory_stats(character_id)
        print(f"  Total: {stats['total_memories']}")
        print(f"  Types: {stats['memory_types']}")
        print(f"  Avg importance: {stats['average_importance']:.2f}")

    asyncio.run(test_memory_service())
