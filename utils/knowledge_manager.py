from pathlib import Path
from typing import Optional, Union

from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.vectordb.pgvector import PgVector

from utils.config_manager import ConfigManager


class KnowledgeManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self._knowledge_bases = {}
        self._ensure_data_dirs()
        # Track the currently loaded PDF path (file or directory)
        self.current_pdf_path = None

    def _ensure_data_dirs(self):
        """Ensure data directories exist."""
        data_dir = Path("data")
        pdf_dir = data_dir / "pdfs"

        data_dir.mkdir(exist_ok=True)
        pdf_dir.mkdir(exist_ok=True)

    def get_pdf_knowledge_base(
        self, recreate: bool = False, pdf_path: Optional[Union[str, Path]] = None
    ) -> Optional[PDFKnowledgeBase]:
        """
        Get or create a PDF knowledge base with current configuration.

        Args:
            recreate: Whether to recreate the knowledge base
            pdf_path: Optional specific PDF file path to use instead of config
        """
        config = self.config_manager.get_config()
        knowledge_config = config.get("knowledge", {})
        pgvector_config = config.get("pgvector", {})

        # Skip if PDF knowledge is disabled
        if not knowledge_config.get("pdf", {}).get("enabled", False):
            return None

        # Determine the PDF path to use
        path_to_use = None
        if pdf_path:
            # Use explicitly provided path
            path_to_use = pdf_path
            # Update current path for tracking
            self.current_pdf_path = pdf_path
        elif self.current_pdf_path:
            # Use previously set path if available
            path_to_use = self.current_pdf_path
        else:
            # Fall back to config path
            path_to_use = knowledge_config.get("pdf", {}).get("path", "data/pdfs")
            self.current_pdf_path = path_to_use

        if "pdf" not in self._knowledge_bases or recreate:
            # Create DB URL from pgvector settings
            db_url = f"postgresql+psycopg://{pgvector_config.get('db_user', 'ai')}:{pgvector_config.get('db_password', 'ai')}@{pgvector_config.get('host', 'localhost')}:{pgvector_config.get('port', 5532)}/{pgvector_config.get('db_name', 'ai')}"

            pdf_config = knowledge_config.get("pdf", {})
            table_name = pdf_config.get("table_name", "pdf_documents")
            chunk = pdf_config.get("chunk", True)

            # Create PDF knowledge base with the determined path - simplified initialization
            pdf_knowledge_base = PDFKnowledgeBase(
                path=path_to_use,
                vector_db=PgVector(
                    table_name=table_name,
                    db_url=db_url,
                ),
                reader=PDFReader(chunk=chunk),
            )

            self._knowledge_bases["pdf"] = pdf_knowledge_base

        return self._knowledge_bases.get("pdf")

    def save_uploaded_pdf(self, uploaded_file) -> str:
        """Save an uploaded PDF file to the data directory."""
        pdf_dir = Path("data") / "pdfs"
        pdf_dir.mkdir(exist_ok=True)

        # Create file path
        file_path = pdf_dir / uploaded_file.name

        # Write the file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Update current path to point directly to this specific file
        self.current_pdf_path = str(file_path)

        return str(file_path)

    def get_current_pdf_info(self) -> dict:
        """
        Get information about the currently loaded PDF path.

        Returns:
            dict with information about the current PDF path
        """
        if not self.current_pdf_path:
            return {
                "is_loaded": False,
                "path": None,
                "is_file": False,
                "is_directory": False,
                "file_name": None,
            }

        path_obj = Path(self.current_pdf_path)

        return {
            "is_loaded": True,
            "path": str(path_obj),
            "is_file": path_obj.is_file(),
            "is_directory": path_obj.is_dir(),
            "file_name": path_obj.name if path_obj.is_file() else None,
        }

    def set_pdf_path(self, path: Union[str, Path]) -> bool:
        """
        Set the current PDF path and validate it exists.

        Args:
            path: Path to PDF file or directory of PDFs

        Returns:
            bool: True if path exists and is valid, False otherwise
        """
        path_obj = Path(path)
        if not path_obj.exists():
            return False

        # Check if it's a PDF file
        if path_obj.is_file() and path_obj.suffix.lower() != ".pdf":
            return False

        self.current_pdf_path = str(path_obj)
        return True
