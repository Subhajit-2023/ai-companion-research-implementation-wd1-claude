"""
Memory Service using ChromaDB for semantic memory storage
Implements long-term memory with importance scoring and retrieval
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
from datetime import datetime
import sys
from pathlib import Path
import uuid

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import settings as app_settings


class MemoryService:
    """Service for managing character memories with semantic search"""

    def __init__(self):
        self.db_path = Path(app_settings.VECTOR_DB_PATH)
        self.db_path.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )

        self.embedding_model = SentenceTransformer(app_settings.EMBEDDING_MODEL)
        self.max_results = app_settings.MAX_MEMORY_RESULTS

    def _get_collection_name(self, character_id: int) -> str:
        """Get collection name for a character"""
        return f"{app_settings.MEMORY_COLLECTION_PREFIX}_{character_id}"

    def _ensure_collection(self, character_id: int):
        """Ensure collection exists for character"""
        collection_name = self._get_collection_name(character_id)

        try:
            return self.client.get_collection(name=collection_name)
        except:
            return self.client.create_collection(
                name=collection_name,
                metadata={"character_id": str(character_id)}
            )

    async def add_memory(
        self,
        character_id: int,
        content: str,
        memory_type: str = "episodic",
        importance: float = 1.0,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Add a memory to character's memory bank

        Args:
            character_id: Character ID
            content: Memory content
            memory_type: Type (episodic, semantic, emotional)
            importance: Importance score (0.0 to 1.0)
            metadata: Additional metadata

        Returns:
            Memory ID
        """
        collection = self._ensure_collection(character_id)

        memory_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        memory_metadata = {
            "memory_type": memory_type,
            "importance": importance,
            "created_at": timestamp,
            "accessed_at": timestamp,
            "access_count": 0,
            **(metadata or {})
        }

        embedding = self.embedding_model.encode(content).tolist()

        collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[memory_metadata]
        )

        return memory_id

    async def retrieve_memories(
        self,
        character_id: int,
        query: str,
        limit: Optional[int] = None,
        memory_type: Optional[str] = None,
        min_importance: float = 0.0
    ) -> List[Dict]:
        """
        Retrieve relevant memories based on semantic similarity

        Args:
            character_id: Character ID
            query: Query text
            limit: Max number of results
            memory_type: Filter by memory type
            min_importance: Minimum importance threshold

        Returns:
            List of relevant memories
        """
        try:
            collection = self._ensure_collection(character_id)
        except:
            return []

        if collection.count() == 0:
            return []

        query_embedding = self.embedding_model.encode(query).tolist()

        n_results = limit or self.max_results

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, collection.count()),
            include=["documents", "metadatas", "distances"]
        )

        memories = []
        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i]

            if metadata.get("importance", 0) < min_importance:
                continue

            if memory_type and metadata.get("memory_type") != memory_type:
                continue

            memories.append({
                "content": doc,
                "similarity": 1 - distance,
                "importance": metadata.get("importance", 1.0),
                "memory_type": metadata.get("memory_type", "episodic"),
                "created_at": metadata.get("created_at"),
                "accessed_at": metadata.get("accessed_at"),
                "access_count": metadata.get("access_count", 0)
            })

        await self._update_access_stats(collection, results["ids"][0])

        return memories

    async def _update_access_stats(self, collection, memory_ids: List[str]):
        """Update access statistics for memories"""
        for memory_id in memory_ids:
            try:
                result = collection.get(ids=[memory_id], include=["metadatas"])
                if result["metadatas"]:
                    metadata = result["metadatas"][0]
                    metadata["accessed_at"] = datetime.utcnow().isoformat()
                    metadata["access_count"] = metadata.get("access_count", 0) + 1

                    collection.update(
                        ids=[memory_id],
                        metadatas=[metadata]
                    )
            except:
                pass

    async def get_recent_memories(
        self,
        character_id: int,
        limit: int = 10
    ) -> List[Dict]:
        """Get most recent memories"""
        try:
            collection = self._ensure_collection(character_id)
        except:
            return []

        if collection.count() == 0:
            return []

        results = collection.get(
            limit=limit,
            include=["documents", "metadatas"]
        )

        memories = []
        for i, doc in enumerate(results["documents"]):
            metadata = results["metadatas"][i]
            memories.append({
                "content": doc,
                "memory_type": metadata.get("memory_type", "episodic"),
                "importance": metadata.get("importance", 1.0),
                "created_at": metadata.get("created_at")
            })

        memories.sort(key=lambda x: x["created_at"], reverse=True)
        return memories

    async def delete_memory(self, character_id: int, memory_id: str):
        """Delete a specific memory"""
        collection = self._ensure_collection(character_id)
        collection.delete(ids=[memory_id])

    async def clear_character_memories(self, character_id: int):
        """Clear all memories for a character"""
        collection_name = self._get_collection_name(character_id)
        try:
            self.client.delete_collection(name=collection_name)
        except:
            pass

    async def summarize_conversation(
        self,
        messages: List[Dict],
        max_length: int = 200
    ) -> str:
        """
        Create a summary of conversation for memory storage

        Args:
            messages: List of message dicts
            max_length: Max summary length

        Returns:
            Summary string
        """
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in messages[-10:]
        ])

        if len(conversation_text) <= max_length:
            return conversation_text

        return conversation_text[:max_length] + "..."

    async def extract_key_points(
        self,
        text: str,
        character_id: int
    ) -> List[str]:
        """
        Extract key points from text for memory storage

        Args:
            text: Text to extract from
            character_id: Character ID

        Returns:
            List of key points
        """
        sentences = text.split(". ")

        if len(sentences) <= 3:
            return sentences

        embeddings = self.embedding_model.encode(sentences)

        importance_scores = []
        for embedding in embeddings:
            similarity_sum = sum([
                (embedding @ other_embedding) /
                (len(embedding) * len(other_embedding))
                for other_embedding in embeddings
            ])
            importance_scores.append(similarity_sum)

        sorted_indices = sorted(
            range(len(importance_scores)),
            key=lambda i: importance_scores[i],
            reverse=True
        )

        key_sentences = [sentences[i] for i in sorted_indices[:3]]

        return key_sentences

    async def consolidate_memories(
        self,
        character_id: int,
        threshold: int = 100
    ):
        """
        Consolidate old memories to prevent database bloat

        Args:
            character_id: Character ID
            threshold: Max number of memories before consolidation
        """
        collection = self._ensure_collection(character_id)

        if collection.count() < threshold:
            return

        results = collection.get(include=["metadatas"])

        low_importance = [
            (results["ids"][i], results["metadatas"][i])
            for i in range(len(results["ids"]))
            if results["metadatas"][i].get("importance", 1.0) < 0.3
            and results["metadatas"][i].get("access_count", 0) < 2
        ]

        if len(low_importance) > 20:
            ids_to_delete = [item[0] for item in low_importance[:20]]
            collection.delete(ids=ids_to_delete)
            print(f"Consolidated {len(ids_to_delete)} low-importance memories")

    async def get_memory_stats(self, character_id: int) -> Dict:
        """Get statistics about character's memories"""
        try:
            collection = self._ensure_collection(character_id)
            count = collection.count()

            if count == 0:
                return {
                    "total_memories": 0,
                    "by_type": {},
                    "avg_importance": 0
                }

            results = collection.get(include=["metadatas"])

            by_type = {}
            total_importance = 0

            for metadata in results["metadatas"]:
                mem_type = metadata.get("memory_type", "episodic")
                by_type[mem_type] = by_type.get(mem_type, 0) + 1
                total_importance += metadata.get("importance", 1.0)

            return {
                "total_memories": count,
                "by_type": by_type,
                "avg_importance": total_importance / count if count > 0 else 0
            }

        except:
            return {
                "total_memories": 0,
                "by_type": {},
                "avg_importance": 0
            }


memory_service = MemoryService()


if __name__ == "__main__":
    import asyncio

    async def test_memory():
        """Test memory service"""
        print("Testing Memory Service...")

        character_id = 1

        print("\nAdding test memories...")
        await memory_service.add_memory(
            character_id,
            "User likes playing video games, especially RPGs",
            memory_type="semantic",
            importance=0.8
        )

        await memory_service.add_memory(
            character_id,
            "User mentioned feeling stressed about work today",
            memory_type="episodic",
            importance=0.9
        )

        await memory_service.add_memory(
            character_id,
            "User's favorite color is blue",
            memory_type="semantic",
            importance=0.5
        )

        print("\nRetrieving memories about user preferences...")
        memories = await memory_service.retrieve_memories(
            character_id,
            "What does the user like?",
            limit=5
        )

        for mem in memories:
            print(f"- {mem['content']} (similarity: {mem['similarity']:.2f})")

        stats = await memory_service.get_memory_stats(character_id)
        print(f"\nMemory stats: {stats}")

    asyncio.run(test_memory())
