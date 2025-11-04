"""RAG Manager Agent.
Handles document retrieval from GitHub and vector database operations.
"""
import os
import json
import logging
import requests
import re
from io import BytesIO
from typing import List, Dict, Any, Optional
from src.agents.base_agent import BaseAgent
from src.core import config

try:
    from langchain.schema import Document
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import Chroma
    from langchain_openai import OpenAIEmbeddings
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"PyPDF2 not installed: {e}")
    PYPDF2_AVAILABLE = False

# Try alternative PDF libraries
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

# Check if any PDF library is available
PDF_LIBRARY_AVAILABLE = PYPDF2_AVAILABLE or PYPDF_AVAILABLE or PDFPLUMBER_AVAILABLE

if not PDF_LIBRARY_AVAILABLE:
    logger = logging.getLogger(__name__)
    logger.warning("No PDF library available. Install PyPDF2, pypdf, or pdfplumber")

logger = logging.getLogger(__name__)


class RAGManager(BaseAgent):
    """
    Manages Retrieval-Augmented Generation system.
    Loads travel guides from GitHub and creates vector database.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize RAG manager."""
        super().__init__(api_key)
        self.github_token = config.GITHUB_TOKEN
        self.chunk_size = config.CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP
        self.top_k = config.RAG_TOP_K
        self.max_context_chars = getattr(config, "RAG_CONTEXT_MAX_CHARS", 2800)
        self.max_doc_chars = getattr(config, "RAG_CONTEXT_MAX_DOC_CHARS", 650)
        self.vector_db = None
    
    def get_travel_context(
        self, 
        travel_info: Dict[str, Any],
        force_reload: bool = False
    ) -> str:
        """
        Get relevant travel context from documents.
        
        Args:
            travel_info: Parsed travel information
            force_reload: Force reload documents from GitHub
        
        Returns:
            Formatted context string
        """
        destination = travel_info.get("destination", "")
        country = travel_info.get("country", "")
        interests = travel_info.get("interests", [])
        
        logger.info(f"Retrieving travel context for {destination}, {country}")
        
        # Load documents
        documents = self._load_travel_documents(destination, force_reload)
        
        if not documents:
            logger.warning(f"No documents loaded for {destination}")
            return f"No specific travel guides available for {destination}. Using general knowledge to create travel plan."
        
        # Create or load vector database
        if force_reload or not self.vector_db:
            self.vector_db = self._create_vector_db(documents)
        
        # Query vector database
        query = self._build_rag_query(destination, country, interests)
        relevant_docs = self._query_vector_db(query)
        
        # Format context
        context = self._format_context(relevant_docs)
        
        logger.info(f"Retrieved context with {len(relevant_docs)} documents")
        return context
    
    def _load_travel_documents(
        self, 
        destination: str, 
        force_reload: bool = False
    ) -> List[Any]:
        """
        Load travel documents from GitHub repository.
        
        Args:
            destination: Destination city
            force_reload: Force reload from GitHub
        
        Returns:
            List of Document objects
        """
        if not Document or not RecursiveCharacterTextSplitter:
            logger.error("LangChain dependencies not available")
            return []
        
        if not PDF_LIBRARY_AVAILABLE:
            logger.error("No PDF library available. Install PyPDF2, pypdf, or pdfplumber")
            return []
        
        documents = []
        
        try:
            # Parse GitHub repo URL
            repo_url = config.GITHUB_REPO_URL
            owner, repo = self._parse_github_url(repo_url)
            
            # Get files from GitHub
            files = self._get_github_files(owner, repo)
            
            # Filter for PDFs (exclude very small files that are likely corrupted)
            pdf_files = [
                f for f in files 
                if f.get("name", "").endswith(".pdf") and f.get("size", 0) > 1000
            ]
            
            logger.info(f"Found {len(pdf_files)} valid PDF files (excluding corrupted)")
            
            # Filter by destination if possible
            destination_files = []
            if destination and destination.lower() != "any":
                # Try various name formats
                dest_variations = [
                    destination.lower().replace(" ", "_"),
                    destination.lower().replace(" ", "-"),
                    destination.lower().replace(" ", " "),
                    destination.lower()
                ]
                
                for f in pdf_files:
                    name_lower = f.get("name", "").lower()
                    if any(var in name_lower for var in dest_variations):
                        destination_files.append(f)
                
                if destination_files:
                    pdf_files = destination_files
                    logger.info(f"Found {len(pdf_files)} PDFs for {destination}")
                else:
                    logger.warning(f"No PDFs found for {destination}, using general guides")
                    # Use a few random PDFs as general context
                    pdf_files = pdf_files[:3]
            
            # Limit number of files
            pdf_files = pdf_files[:5]
            
            logger.info(f"Selected {len(pdf_files)} PDF files to process")
            
            # Download and parse PDFs
            for file_info in pdf_files:
                try:
                    file_name = file_info["name"]
                    file_size = file_info.get("size", 0)
                    
                    logger.info(f"Processing {file_name} ({file_size:,} bytes)")
                    
                    text = self._download_and_extract_pdf(file_info["download_url"])
                    if text and len(text.strip()) > 100:
                        doc = Document(
                            page_content=text,
                            metadata={
                                "source": file_name,
                                "type": "travel_guide",
                                "size": file_size
                            }
                        )
                        documents.append(doc)
                        logger.info(f"✅ Successfully loaded {file_name} ({len(text):,} chars)")
                    else:
                        logger.warning(f"⚠️  Skipped {file_name} - no text extracted")
                except Exception as e:
                    logger.warning(f"❌ Failed to process {file_info['name']}: {e}")
            
            logger.info(f"Loaded {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to load travel documents: {e}")
        
        return documents
    
    def _create_vector_db(self, documents: List[Any]) -> Any:
        """
        Create vector database from documents.
        
        Args:
            documents: List of Document objects
        
        Returns:
            Chroma vector store
        """
        if not Chroma or not OpenAIEmbeddings or not RecursiveCharacterTextSplitter:
            logger.error("Required dependencies not available")
            return None
        
        try:
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            chunks = text_splitter.split_documents(documents)
            
            logger.info(f"Created {len(chunks)} chunks from documents")
            
            # Create embeddings
            embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_key=self.api_key
            )
            
            # Create vector store
            vector_db = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=config.VECTOR_DB_DIR
            )
            
            logger.info("Vector database created successfully")
            return vector_db
            
        except Exception as e:
            logger.error(f"Failed to create vector database: {e}")
            return None
    
    def _query_vector_db(self, query: str) -> List[Any]:
        """
        Query vector database for relevant documents.
        
        Args:
            query: Search query
        
        Returns:
            List of relevant Document objects
        """
        if not self.vector_db:
            logger.warning("Vector database not initialized")
            return []
        
        try:
            results = self.vector_db.similarity_search(query, k=self.top_k)
            logger.info(f"Found {len(results)} relevant documents")
            return results
        except Exception as e:
            logger.error(f"Vector database query failed: {e}")
            return []
    
    def _build_rag_query(
        self, 
        destination: str, 
        country: str, 
        interests: List[str]
    ) -> str:
        """
        Build query for RAG system.
        
        Args:
            destination: Destination city
            country: Destination country
            interests: List of interests
        
        Returns:
            Query string
        """
        interests_str = ", ".join(interests) if interests else "tourism"
        query = f"Travel guide for {destination}, {country}. Interests: {interests_str}. "
        query += "Looking for practical tips, attractions, local culture, and recommendations."
        return query
    
    def _format_context(self, documents: List[Any]) -> str:
        """
        Format retrieved documents into context string.
        
        Args:
            documents: List of Document objects
        
        Returns:
            Formatted context string
        """
        if not documents:
            return "No additional information available from travel guides."
        
        max_total = max(500, int(self.max_context_chars))
        remaining = max_total
        header = "=== TRAVEL GUIDE INFORMATION ===\n"
        parts = [header]
        remaining -= len(header)

        for idx, doc in enumerate(documents, 1):
            if remaining <= 0:
                break
            snippet = self._build_snippet(doc, min(self.max_doc_chars, remaining))
            if not snippet:
                continue
            source = doc.metadata.get("source", "Unknown")
            block = f"\n[Source {idx}: {source}]\n{snippet}"
            if len(block) > remaining:
                block = block[:remaining].rstrip()
            parts.append(block)
            remaining -= len(block)

        context = "\n".join(parts)
        if len(context) > max_total:
            context = context[:max_total].rstrip()
        return context

    def _build_snippet(self, doc: Any, max_chars: int) -> str:
        """Condense a document chunk into a compact snippet."""
        if not doc or max_chars <= 0:
            return ""

        text = getattr(doc, "page_content", "") or ""
        text = self._normalize_whitespace(text)
        if not text:
            return ""

        if len(text) <= max_chars:
            return text

        sentences = re.split(r"(?<=[.!?])\s+", text)
        selected: List[str] = []
        current_len = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # If first sentence is too long, truncate it directly
            if not selected and len(sentence) >= max_chars:
                return sentence[:max_chars].rstrip()

            projected = current_len + len(sentence) + (2 if selected else 0)
            if projected > max_chars:
                break

            selected.append(sentence)
            current_len = projected

            if current_len >= max_chars:
                break

        if not selected:
            return text[:max_chars].rstrip()

        snippet = "\n".join(f"- {sentence}" for sentence in selected)
        if len(snippet) > max_chars:
            snippet = snippet[:max_chars].rstrip()
        return snippet

    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        """Collapse repeated whitespace while preserving paragraph breaks."""
        if not text:
            return ""

        # Preserve double newlines for paragraph separation, collapse others
        text = text.replace("\r", "")
        paragraphs = [re.sub(r"\s+", " ", para).strip() for para in text.split("\n\n")]
        paragraphs = [para for para in paragraphs if para]
        if not paragraphs:
            return ""
        return "\n".join(paragraphs)
    
    def _get_github_files(
        self, 
        owner: str, 
        repo: str, 
        path: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Get files from GitHub repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: Path within repository
        
        Returns:
            List of file information dictionaries
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        headers = {"Accept": "application/vnd.github.v3+json"}
        
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        
        try:
            response = requests.get(url, headers=headers, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get GitHub files: {e}")
            return []
    
    def _download_and_extract_pdf(self, url: str) -> str:
        """
        Download and extract text from PDF using multiple fallback methods.
        
        Args:
            url: PDF download URL
        
        Returns:
            Extracted text
        """
        if not PDF_LIBRARY_AVAILABLE:
            logger.error("No PDF library available")
            return ""
        
        try:
            logger.info(f"Downloading PDF from {url}")
            response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            pdf_content = response.content
            content_size = len(pdf_content)
            logger.info(f"Downloaded {content_size} bytes")
            
            # Check if file is too small (likely corrupted or empty)
            if content_size < 1000:
                logger.error(f"PDF file too small ({content_size} bytes) - likely corrupted or empty")
                return ""
            
            # Check if it's actually a PDF
            if not pdf_content.startswith(b'%PDF'):
                logger.error("Downloaded file is not a valid PDF (missing PDF header)")
                return ""
            
            # Try multiple PDF extraction methods
            text = None
            
            # Method 1: Try pdfplumber first (most robust)
            if PDFPLUMBER_AVAILABLE and not text:
                try:
                    logger.info("Attempting extraction with pdfplumber")
                    text = self._extract_with_pdfplumber(pdf_content)
                    if text and len(text.strip()) > 100:
                        logger.info(f"Successfully extracted {len(text)} chars with pdfplumber")
                        return text
                except Exception as e:
                    logger.warning(f"pdfplumber extraction failed: {e}")
            
            # Method 2: Try pypdf
            if PYPDF_AVAILABLE and not text:
                try:
                    logger.info("Attempting extraction with pypdf")
                    text = self._extract_with_pypdf(pdf_content)
                    if text and len(text.strip()) > 100:
                        logger.info(f"Successfully extracted {len(text)} chars with pypdf")
                        return text
                except Exception as e:
                    logger.warning(f"pypdf extraction failed: {e}")
            
            # Method 3: Try PyPDF2 with error recovery
            if PYPDF2_AVAILABLE and not text:
                try:
                    logger.info("Attempting extraction with PyPDF2")
                    text = self._extract_with_pypdf2(pdf_content)
                    if text and len(text.strip()) > 100:
                        logger.info(f"Successfully extracted {len(text)} chars with PyPDF2")
                        return text
                except Exception as e:
                    logger.warning(f"PyPDF2 extraction failed: {e}")
            
            # If we got some text but it's short, still return it
            if text and len(text.strip()) > 0:
                logger.warning(f"Extracted only {len(text)} chars, but returning it")
                return text
            
            logger.error("All PDF extraction methods failed")
            return ""
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download PDF: {e}")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error in PDF extraction: {e}")
            return ""
    
    def _extract_with_pypdf2(self, pdf_content: bytes) -> str:
        """Extract text using PyPDF2 with strict=False for error recovery."""
        if not PYPDF2_AVAILABLE:
            return ""
        
        pdf_file = BytesIO(pdf_content)
        # Use strict=False to be more lenient with PDF errors
        reader = PyPDF2.PdfReader(pdf_file, strict=False)
        
        text = ""
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            except Exception as e:
                logger.warning(f"Failed to extract page {i}: {e}")
                continue
        
        return text
    
    def _extract_with_pypdf(self, pdf_content: bytes) -> str:
        """Extract text using pypdf library."""
        if not PYPDF_AVAILABLE:
            return ""
        
        pdf_file = BytesIO(pdf_content)
        reader = pypdf.PdfReader(pdf_file)
        
        text = ""
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            except Exception as e:
                logger.warning(f"Failed to extract page {i}: {e}")
                continue
        
        return text
    
    def _extract_with_pdfplumber(self, pdf_content: bytes) -> str:
        """Extract text using pdfplumber (most robust)."""
        if not PDFPLUMBER_AVAILABLE:
            return ""
        
        pdf_file = BytesIO(pdf_content)
        text = ""
        
        with pdfplumber.open(pdf_file) as pdf:
            for i, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception as e:
                    logger.warning(f"Failed to extract page {i}: {e}")
                    continue
        
        return text
    
    def _parse_github_url(self, url: str) -> tuple:
        """
        Parse GitHub repository URL.
        
        Args:
            url: GitHub repository URL
        
        Returns:
            Tuple of (owner, repo)
        """
        # Example: https://github.com/owner/repo
        parts = url.rstrip("/").split("/")
        if len(parts) >= 2:
            return parts[-2], parts[-1]
        raise ValueError(f"Invalid GitHub URL: {url}")
