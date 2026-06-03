# research_assistant/ingestion.py
"""Multi-source ingestion for the research assistant."""

import os
from typing import List, Optional
from pathlib import Path

from llama_index.core import Document
from llama_index.readers.file import PDFReader
from llama_index.readers.web import SimpleWebPageReader
from llama_index.readers.youtube_transcript import YouTubeTranscriptReader


class ResearchIngestion:
    """Ingest research materials from multiple sources."""

    def __init__(self, data_dir: str = "./research_data") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for different sources
        (self.data_dir / "pdfs").mkdir(exist_ok=True)
        (self.data_dir / "web").mkdir(exist_ok=True)
        (self.data_dir / "youtube").mkdir(exist_ok=True)

    def ingest_pdfs(self, pdf_paths: List[str]) -> List[Document]:
        """Load PDFs and return Document objects."""
        reader = PDFReader()
        documents: List[Document] = []

        for pdf_path in pdf_paths:
            path = Path(pdf_path)
            if not path.exists():
                print(f"Warning: {pdf_path} not found, skipping")
                continue

            try:
                docs = reader.load_data(file=path)
                for doc in docs:
                    doc.metadata["source"] = str(path)
                    doc.metadata["source_type"] = "pdf"
                    doc.metadata["filename"] = path.name
                documents.extend(docs)
                print(f"✓ Loaded PDF: {path.name}")
            except Exception as e:
                print(f"✗ Failed to load {path.name}: {e}")

        return documents

    def ingest_web_pages(self, urls: List[str]) -> List[Document]:
        """Load web pages and return Document objects."""
        reader = SimpleWebPageReader(html_to_text=True)
        documents: List[Document] = []

        for url in urls:
            try:
                docs = reader.load_data([url])
                for doc in docs:
                    doc.metadata["source"] = url
                    doc.metadata["source_type"] = "web"
                documents.extend(docs)
                print(f"✓ Loaded web page: {url}")
            except Exception as e:
                print(f"✗ Failed to load {url}: {e}")

        return documents

    def ingest_youtube(self, video_ids: List[str]) -> List[Document]:
        """Load YouTube transcripts and return Document objects."""
        reader = YouTubeTranscriptReader()
        documents: List[Document] = []

        for video_id in video_ids:
            try:
                url = f"https://www.youtube.com/watch?v={video_id}"
                docs = reader.load_data([url])
                for doc in docs:
                    doc.metadata["source"] = url
                    doc.metadata["source_type"] = "youtube"
                    doc.metadata["video_id"] = video_id
                documents.extend(docs)
                print(f"✓ Loaded YouTube: {video_id}")
            except Exception as e:
                print(f"✗ Failed to load {video_id}: {e}")

        return documents

    def ingest_all(
        self,
        pdfs: Optional[List[str]] = None,
        urls: Optional[List[str]] = None,
        videos: Optional[List[str]] = None,
    ) -> List[Document]:
        """Ingest from all sources."""
        all_docs: List[Document] = []

        if pdfs:
            all_docs.extend(self.ingest_pdfs(pdfs))
        if urls:
            all_docs.extend(self.ingest_web_pages(urls))
        if videos:
            all_docs.extend(self.ingest_youtube(videos))

        print(f"\nTotal documents ingested: {len(all_docs)}")
        return all_docs
