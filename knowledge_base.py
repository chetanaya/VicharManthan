import logging
import os
import uuid
from typing import Any, Optional


class PDFKnowledgeBase:
    def __init__(self, base_dir: str = None):
        """
        Initialize a PDF knowledge base

        Args:
            base_dir: Base directory for PDF files
        """
        self.base_dir = base_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "uploads"
        )
        self.path = None
        self.document = None

    def load(self, recreate: bool = False) -> bool:
        """
        Load the PDF file into the knowledge base

        Args:
            recreate: Whether to recreate the knowledge base

        Returns:
            True if successful, False otherwise
        """
        try:
            # Only import these libraries when needed
            from langchain_community.document_loaders import PyPDFLoader

            if not self.path or not os.path.exists(self.path):
                logging.error(f"PDF file not found: {self.path}")
                return False

            # Load the PDF file
            loader = PyPDFLoader(self.path)
            self.document = loader.load()
            return True

        except Exception as e:
            logging.error(f"Error loading PDF: {e}")
            return False

    def search(self, query: str) -> list:
        """
        Search the knowledge base for the given query

        Args:
            query: The query to search for

        Returns:
            List of relevant document sections
        """
        if not self.document:
            return []

        # Implement basic search functionality
        # This could be improved with embeddings and vector search
        results = []
        for page in self.document:
            if query.lower() in page.page_content.lower():
                results.append(page)

        return results


class KnowledgeManager:
    def __init__(self):
        """Initialize the knowledge manager"""
        # Create directories if they don't exist
        self.upload_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "uploads"
        )
        os.makedirs(self.upload_dir, exist_ok=True)

        # Initialize knowledge bases
        self._pdf_knowledge_base = None

    def save_uploaded_pdf(self, uploaded_file) -> Optional[str]:
        """
        Save an uploaded PDF file to the uploads directory

        Args:
            uploaded_file: The uploaded file from Streamlit

        Returns:
            The path to the saved file, or None if no file was uploaded
        """
        if uploaded_file is None:
            return None

        # Generate a unique filename
        file_extension = os.path.splitext(uploaded_file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(self.upload_dir, unique_filename)

        # Save the file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return file_path

    def get_pdf_knowledge_base(self, recreate: bool = False) -> Any:
        """
        Get the PDF knowledge base

        Args:
            recreate: Whether to recreate the knowledge base

        Returns:
            The PDF knowledge base
        """
        if self._pdf_knowledge_base is None or recreate:
            self._pdf_knowledge_base = PDFKnowledgeBase(self.upload_dir)

        return self._pdf_knowledge_base
