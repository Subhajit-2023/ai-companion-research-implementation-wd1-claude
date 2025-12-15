"""
Document Processor - PDF, EPUB, and text document processing with vector embeddings
"""
import asyncio
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import hashlib
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings

try:
    import fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    from ebooklib import epub
    import ebooklib
    from bs4 import BeautifulSoup
    EPUB_AVAILABLE = True
except ImportError:
    EPUB_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


@dataclass
class DocumentChunk:
    id: str
    content: str
    document_id: str
    chunk_index: int
    page_number: Optional[int] = None
    chapter: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class ProcessedDocument:
    id: str
    filename: str
    file_path: str
    file_type: str
    title: str
    author: str
    total_pages: int
    total_chunks: int
    chunks: List[DocumentChunk] = field(default_factory=list)
    processed_at: datetime = field(default_factory=datetime.utcnow)
    file_hash: str = ""
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "title": self.title,
            "author": self.author,
            "total_pages": self.total_pages,
            "total_chunks": self.total_chunks,
            "processed_at": self.processed_at.isoformat(),
            "file_hash": self.file_hash,
            "metadata": self.metadata,
        }


class DocumentProcessor:
    def __init__(self):
        self.knowledge_dir = Path(settings.KNOWLEDGE_DIR)
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)

        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.max_doc_size = settings.MAX_DOC_SIZE_MB * 1024 * 1024

        self.documents: Dict[str, ProcessedDocument] = {}
        self.vector_db = None
        self.collection = None

        if CHROMADB_AVAILABLE:
            self._init_vector_db()

        self._load_document_index()

    def _init_vector_db(self):
        try:
            db_path = Path(settings.VECTOR_DB_PATH)
            db_path.mkdir(parents=True, exist_ok=True)

            self.vector_db = chromadb.PersistentClient(
                path=str(db_path),
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )

            self.collection = self.vector_db.get_or_create_collection(
                name="knowledge_base",
                metadata={"description": "User documents and eBooks"},
            )

        except Exception as e:
            print(f"Vector DB init error: {e}")
            self.vector_db = None

    def _load_document_index(self):
        index_file = self.knowledge_dir / "document_index.json"
        if index_file.exists():
            try:
                with open(index_file, "r") as f:
                    data = json.load(f)
                    for doc_data in data.get("documents", []):
                        doc = ProcessedDocument(
                            id=doc_data["id"],
                            filename=doc_data["filename"],
                            file_path=doc_data["file_path"],
                            file_type=doc_data["file_type"],
                            title=doc_data["title"],
                            author=doc_data["author"],
                            total_pages=doc_data["total_pages"],
                            total_chunks=doc_data["total_chunks"],
                            file_hash=doc_data.get("file_hash", ""),
                            metadata=doc_data.get("metadata", {}),
                        )
                        self.documents[doc.id] = doc
            except Exception as e:
                print(f"Error loading document index: {e}")

    def _save_document_index(self):
        index_file = self.knowledge_dir / "document_index.json"
        try:
            data = {
                "documents": [d.to_dict() for d in self.documents.values()],
                "updated_at": datetime.utcnow().isoformat(),
            }
            with open(index_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving document index: {e}")

    def _compute_file_hash(self, file_path: Path) -> str:
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _chunk_text(self, text: str, doc_id: str, page_num: Optional[int] = None) -> List[DocumentChunk]:
        chunks = []
        words = text.split()

        if not words:
            return chunks

        current_chunk = []
        current_length = 0
        chunk_index = 0

        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1

            if current_length >= self.chunk_size:
                chunk_text = " ".join(current_chunk)
                chunk_id = f"{doc_id}_chunk_{chunk_index}"

                chunks.append(DocumentChunk(
                    id=chunk_id,
                    content=chunk_text,
                    document_id=doc_id,
                    chunk_index=chunk_index,
                    page_number=page_num,
                ))

                overlap_words = int(len(current_chunk) * (self.chunk_overlap / self.chunk_size))
                current_chunk = current_chunk[-overlap_words:] if overlap_words > 0 else []
                current_length = sum(len(w) + 1 for w in current_chunk)
                chunk_index += 1

        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk_id = f"{doc_id}_chunk_{chunk_index}"
            chunks.append(DocumentChunk(
                id=chunk_id,
                content=chunk_text,
                document_id=doc_id,
                chunk_index=chunk_index,
                page_number=page_num,
            ))

        return chunks

    async def process_pdf(self, file_path: Path) -> Optional[ProcessedDocument]:
        if not PYMUPDF_AVAILABLE:
            print("PyMuPDF not available. Install with: pip install pymupdf")
            return None

        try:
            doc_id = hashlib.md5(str(file_path).encode()).hexdigest()[:12]
            file_hash = self._compute_file_hash(file_path)

            if doc_id in self.documents and self.documents[doc_id].file_hash == file_hash:
                return self.documents[doc_id]

            pdf_doc = fitz.open(file_path)

            title = pdf_doc.metadata.get("title", file_path.stem)
            author = pdf_doc.metadata.get("author", "Unknown")

            all_chunks = []

            for page_num in range(len(pdf_doc)):
                page = pdf_doc[page_num]
                text = page.get_text()

                if text.strip():
                    page_chunks = self._chunk_text(text, doc_id, page_num + 1)
                    all_chunks.extend(page_chunks)

            pdf_doc.close()

            processed_doc = ProcessedDocument(
                id=doc_id,
                filename=file_path.name,
                file_path=str(file_path),
                file_type="pdf",
                title=title,
                author=author,
                total_pages=len(pdf_doc) if hasattr(pdf_doc, '__len__') else 0,
                total_chunks=len(all_chunks),
                chunks=all_chunks,
                file_hash=file_hash,
            )

            self.documents[doc_id] = processed_doc
            await self._index_chunks(all_chunks, processed_doc)
            self._save_document_index()

            return processed_doc

        except Exception as e:
            print(f"PDF processing error: {e}")
            return None

    async def process_epub(self, file_path: Path) -> Optional[ProcessedDocument]:
        if not EPUB_AVAILABLE:
            print("ebooklib not available. Install with: pip install ebooklib beautifulsoup4")
            return None

        try:
            doc_id = hashlib.md5(str(file_path).encode()).hexdigest()[:12]
            file_hash = self._compute_file_hash(file_path)

            if doc_id in self.documents and self.documents[doc_id].file_hash == file_hash:
                return self.documents[doc_id]

            book = epub.read_epub(file_path)

            title = book.get_metadata("DC", "title")
            title = title[0][0] if title else file_path.stem

            author = book.get_metadata("DC", "creator")
            author = author[0][0] if author else "Unknown"

            all_chunks = []
            chapter_num = 0

            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), "html.parser")
                    text = soup.get_text(separator=" ", strip=True)

                    if text:
                        chapter_chunks = self._chunk_text(text, doc_id)
                        for chunk in chapter_chunks:
                            chunk.chapter = f"Chapter {chapter_num + 1}"
                        all_chunks.extend(chapter_chunks)
                        chapter_num += 1

            processed_doc = ProcessedDocument(
                id=doc_id,
                filename=file_path.name,
                file_path=str(file_path),
                file_type="epub",
                title=title,
                author=author,
                total_pages=chapter_num,
                total_chunks=len(all_chunks),
                chunks=all_chunks,
                file_hash=file_hash,
            )

            self.documents[doc_id] = processed_doc
            await self._index_chunks(all_chunks, processed_doc)
            self._save_document_index()

            return processed_doc

        except Exception as e:
            print(f"EPUB processing error: {e}")
            return None

    async def process_text(self, file_path: Path) -> Optional[ProcessedDocument]:
        try:
            doc_id = hashlib.md5(str(file_path).encode()).hexdigest()[:12]
            file_hash = self._compute_file_hash(file_path)

            if doc_id in self.documents and self.documents[doc_id].file_hash == file_hash:
                return self.documents[doc_id]

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            all_chunks = self._chunk_text(content, doc_id)

            processed_doc = ProcessedDocument(
                id=doc_id,
                filename=file_path.name,
                file_path=str(file_path),
                file_type=file_path.suffix.lstrip("."),
                title=file_path.stem,
                author="Unknown",
                total_pages=1,
                total_chunks=len(all_chunks),
                chunks=all_chunks,
                file_hash=file_hash,
            )

            self.documents[doc_id] = processed_doc
            await self._index_chunks(all_chunks, processed_doc)
            self._save_document_index()

            return processed_doc

        except Exception as e:
            print(f"Text processing error: {e}")
            return None

    async def process_document(self, file_path: str) -> Optional[ProcessedDocument]:
        path = Path(file_path)

        if not path.exists():
            print(f"File not found: {file_path}")
            return None

        if path.stat().st_size > self.max_doc_size:
            print(f"File too large: {file_path}")
            return None

        suffix = path.suffix.lower()

        if suffix == ".pdf":
            return await self.process_pdf(path)
        elif suffix == ".epub":
            return await self.process_epub(path)
        elif suffix in [".txt", ".md", ".py", ".js", ".jsx", ".ts", ".tsx", ".json"]:
            return await self.process_text(path)
        else:
            print(f"Unsupported file type: {suffix}")
            return None

    async def _index_chunks(self, chunks: List[DocumentChunk], doc: ProcessedDocument):
        if not self.collection or not chunks:
            return

        try:
            ids = [c.id for c in chunks]
            documents = [c.content for c in chunks]
            metadatas = [
                {
                    "document_id": doc.id,
                    "document_title": doc.title,
                    "chunk_index": c.chunk_index,
                    "page_number": c.page_number or 0,
                    "chapter": c.chapter or "",
                    "file_type": doc.file_type,
                }
                for c in chunks
            ]

            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )

        except Exception as e:
            print(f"Indexing error: {e}")

    async def search(
        self,
        query: str,
        n_results: int = 5,
        document_ids: Optional[List[str]] = None,
    ) -> List[Dict]:
        if not self.collection:
            return []

        try:
            where_filter = None
            if document_ids:
                where_filter = {"document_id": {"$in": document_ids}}

            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter,
            )

            search_results = []
            if results and results["ids"] and results["ids"][0]:
                for i, chunk_id in enumerate(results["ids"][0]):
                    search_results.append({
                        "chunk_id": chunk_id,
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i] if "distances" in results else None,
                    })

            return search_results

        except Exception as e:
            print(f"Search error: {e}")
            return []

    async def batch_process_directory(self, directory: str) -> List[ProcessedDocument]:
        path = Path(directory)
        if not path.is_dir():
            return []

        processed = []
        supported_extensions = [".pdf", ".epub", ".txt", ".md", ".py", ".js"]

        for file_path in path.rglob("*"):
            if file_path.suffix.lower() in supported_extensions:
                doc = await self.process_document(str(file_path))
                if doc:
                    processed.append(doc)

        return processed

    def get_document(self, doc_id: str) -> Optional[ProcessedDocument]:
        return self.documents.get(doc_id)

    def list_documents(self) -> List[Dict]:
        return [d.to_dict() for d in self.documents.values()]

    def delete_document(self, doc_id: str) -> bool:
        if doc_id not in self.documents:
            return False

        try:
            if self.collection:
                doc = self.documents[doc_id]
                chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(doc.total_chunks)]
                self.collection.delete(ids=chunk_ids)

            del self.documents[doc_id]
            self._save_document_index()
            return True

        except Exception as e:
            print(f"Delete error: {e}")
            return False

    def get_stats(self) -> Dict:
        total_chunks = sum(d.total_chunks for d in self.documents.values())
        by_type = {}
        for doc in self.documents.values():
            by_type[doc.file_type] = by_type.get(doc.file_type, 0) + 1

        return {
            "total_documents": len(self.documents),
            "total_chunks": total_chunks,
            "by_type": by_type,
            "vector_db_available": self.collection is not None,
        }


document_processor = DocumentProcessor()


if __name__ == "__main__":
    async def test_document_processor():
        print("Testing Document Processor...")
        print(f"Stats: {document_processor.get_stats()}")

        print("\nListed documents:")
        for doc in document_processor.list_documents():
            print(f"  - {doc['title']} ({doc['file_type']})")

    asyncio.run(test_document_processor())
