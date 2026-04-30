# strategy_uploader.py 
# strategy_uploader.py — Strategy file upload and validation

import os
import re
import requests
from typing import Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from strategy_rag import get_strategy_rag

STRATEGIES_FOLDER = "strategies"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = ['.txt', '.md', '.pdf']


@dataclass
class ValidationResult:
    """Result of file validation."""
    is_valid: bool
    error_message: str = ""
    sanitized_filename: str = ""
    warnings: list = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class StrategyFileInfo:
    """Information about a strategy file."""
    filename: str
    original_filename: str
    file_size: int
    content_length: int
    upload_timestamp: float
    file_type: str
    
    def to_dict(self):
        return {
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "content_length": self.content_length,
            "upload_timestamp": self.upload_timestamp,
            "file_type": self.file_type
        }
    
    def get_display_name(self) -> str:
        """Get display name with size."""
        size_kb = self.file_size / 1024
        return f"{self.filename} ({size_kb:.1f} KB)"


class FileValidator:
    """Validates uploaded files."""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent directory traversal and normalize."""
        # Remove directory components
        filename = os.path.basename(filename)
        
        # Convert to lowercase
        filename = filename.lower()
        
        # Replace spaces with underscores
        filename = filename.replace(" ", "_")
        
        # Remove any characters that aren't alphanumeric, underscore, dash, or dot
        filename = re.sub(r'[^a-z0-9_\-\.]', '', filename)
        
        return filename
    
    @staticmethod
    def validate_file(filename: str, file_size: int, content: bytes = None) -> ValidationResult:
        """Validate file extension, size, and content."""
        # Check extension
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Check size
        if file_size > MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            return ValidationResult(
                is_valid=False,
                error_message=f"File too large ({size_mb:.1f}MB). Maximum: 5MB"
            )
        
        # Check content if provided
        if content:
            if len(content) < 50:
                return ValidationResult(
                    is_valid=False,
                    error_message="File content too short (minimum 50 characters)"
                )
            
            # Check UTF-8 encoding for text files
            if ext in ['.txt', '.md']:
                try:
                    content.decode('utf-8')
                except UnicodeDecodeError:
                    return ValidationResult(
                        is_valid=False,
                        error_message="File must be valid UTF-8 encoded text"
                    )
        
        # Sanitize filename
        sanitized = FileValidator.sanitize_filename(filename)
        
        return ValidationResult(
            is_valid=True,
            sanitized_filename=sanitized
        )


class StrategyUploader:
    """Handles strategy file uploads from Telegram."""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.validator = FileValidator()
    
    def download_and_save(self, file_id: str, original_filename: str) -> Tuple[bool, str, Optional[StrategyFileInfo]]:
        """Download file from Telegram and save to strategies folder."""
        try:
            # Get file path from Telegram
            url = f"https://api.telegram.org/bot{self.bot_token}/getFile"
            response = requests.get(url, params={"file_id": file_id}, timeout=10)
            
            if response.status_code != 200:
                return False, "Failed to get file from Telegram", None
            
            file_path = response.json()["result"]["file_path"]
            file_size = response.json()["result"]["file_size"]
            
            # Validate before downloading
            validation = self.validator.validate_file(original_filename, file_size)
            if not validation.is_valid:
                return False, validation.error_message, None
            
            # Download file content
            download_url = f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
            file_response = requests.get(download_url, timeout=30)
            
            if file_response.status_code != 200:
                return False, "Failed to download file", None
            
            content = file_response.content
            
            # Validate content
            content_validation = self.validator.validate_file(original_filename, len(content), content)
            if not content_validation.is_valid:
                return False, content_validation.error_message, None
            
            # Handle duplicate filenames
            final_filename = self.handle_duplicate_filename(validation.sanitized_filename)
            
            # Save to strategies folder
            if not os.path.exists(STRATEGIES_FOLDER):
                os.makedirs(STRATEGIES_FOLDER)
            
            filepath = os.path.join(STRATEGIES_FOLDER, final_filename)
            with open(filepath, 'wb') as f:
                f.write(content)
            
            # Reload RAG system
            self.reload_rag_system()
            
            # Create file info
            file_info = StrategyFileInfo(
                filename=final_filename,
                original_filename=original_filename,
                file_size=len(content),
                content_length=len(content),
                upload_timestamp=datetime.now().timestamp(),
                file_type=os.path.splitext(final_filename)[1]
            )
            
            return True, f"✅ File uploaded successfully as {final_filename}", file_info
            
        except Exception as e:
            return False, f"Upload error: {str(e)}", None
    
    def handle_duplicate_filename(self, filename: str) -> str:
        """Append timestamp if filename already exists."""
        filepath = os.path.join(STRATEGIES_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return filename
        
        # Append timestamp
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{name}_{timestamp}{ext}"
    
    def reload_rag_system(self):
        """Reload the RAG system to pick up new strategies."""
        try:
            rag = get_strategy_rag()
            rag.load_strategies()
            print(f"  [uploader] RAG system reloaded")
        except Exception as e:
            print(f"  [uploader] Error reloading RAG: {e}")


# Global uploader instance
_strategy_uploader = None


def get_strategy_uploader(bot_token: str) -> StrategyUploader:
    """Get or create global strategy uploader instance."""
    global _strategy_uploader
    if _strategy_uploader is None:
        _strategy_uploader = StrategyUploader(bot_token)
    return _strategy_uploader
