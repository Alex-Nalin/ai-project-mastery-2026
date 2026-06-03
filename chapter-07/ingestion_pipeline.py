# ingestion_pipeline.py
"""Multi-source document ingestion for RAG 2.0 systems."""

import os
from typing import List, Optional
from pathlib import Path

from llama_index.core import SimpleDirectoryReader, Document
from llama_index.readers.web import SimpleWebPageReader
from llama_index.readers.youtube_transcript import YouTubeTranscriptReader
from llama_index.readers.file import PDFReader


class MultiSourceIngestor:
    """Ingest documents from PDFs, web pages, and YouTube transcripts."""

    def __init__(self, data_dir: str = "./data") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def ingest_pdfs(self, pdf_dir: Optional[str] = None) -> List[Document]:
        """Load all PDFs from a directory."""
        source_dir = pdf_dir or str(self.data_dir / "pdfs")
        reader = SimpleDirectoryReader(
            input_dir=source_dir,
            file_extensions=[".pdf"],
            file_extractor={".pdf": PDFReader()},
        )
        documents = reader.load_data()
        print(f"Loaded {len(documents)} PDF documents")
        return documents

    def ingest_web_pages(self, urls: List[str]) -> List[Document]:
        """Load content from web pages."""
        reader = SimpleWebPageReader(html_to_text=True)
        documents: List[Document] = []
        for url in urls:
            try:
                docs = reader.load_data([url])
                documents.extend(docs)
                print(f"Loaded: {url}")
            except Exception as e:
                print(f"Failed to load {url}: {e}")
        return documents

    def ingest_youtube_transcripts(self, video_ids: List[str]) -> List[Document]:
        """Load YouTube video transcripts."""
        reader = YouTubeTranscriptReader()
        # YouTubeTranscriptReader expects full URLs
        urls = [f"https://www.youtube.com/watch?v={vid}" for vid in video_ids]
        documents = reader.load_data(urls)
        print(f"Loaded {len(documents)} YouTube transcripts")
        return documents

    def ingest_all(
        self,
        urls: Optional[List[str]] = None,
        video_ids: Optional[List[str]] = None,
        pdf_dir: Optional[str] = None,
    ) -> List[Document]:
        """Ingest from all sources and return combined documents."""
        all_docs: List[Document] = []

        if pdf_dir or (self.data_dir / "pdfs").exists():
            all_docs.extend(self.ingest_pdfs(pdf_dir))

        if urls:
            all_docs.extend(self.ingest_web_pages(urls))

        if video_ids:
            all_docs.extend(self.ingest_youtube_transcripts(video_ids))

        print(f"Total documents ingested: {len(all_docs)}")
        return all_docs
