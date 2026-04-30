# strategy_rag.py — Load trading strategy PDFs and include in AI analysis

import os
import json
from typing import List
from pathlib import Path


class StrategyRAG:
    """
    Retrieval-Augmented Generation for trading strategies.
    Load PDF strategy documents and inject into AI prompts.
    """
    
    def __init__(self, strategies_folder: str = "strategies"):
        self.strategies_folder = strategies_folder
        self.strategies = {}
        self.create_folder()
        self.load_strategies()
    
    def create_folder(self):
        """Create strategies folder if it doesn't exist."""
        if not os.path.exists(self.strategies_folder):
            os.makedirs(self.strategies_folder)
            print(f"  [RAG] Created {self.strategies_folder}/ folder for strategy documents")
            
            # Create example file
            example_file = os.path.join(self.strategies_folder, "README.txt")
            with open(example_file, "w") as f:
                f.write("""STRATEGY DOCUMENTS FOLDER

Place your trading strategy documents here:
- ICT_strategy.txt
- SMC_price_action.txt
- supply_demand_zones.txt
- risk_management_rules.txt
- entry_exit_rules.txt

Supported formats:
- .txt (plain text)
- .md (markdown)
- .pdf (will extract text if PyPDF2 installed)

The AI will read all documents and apply your rules to trading decisions.
""")
            print(f"  [RAG] Created README in {self.strategies_folder}/")
    
    def load_strategies(self):
        """Load all strategy documents from folder."""
        self.strategies = {}
        supported_extensions = ['.txt', '.md']
        
        if not os.path.exists(self.strategies_folder):
            print(f"  [RAG] No strategies folder found")
            return
        
        for filename in os.listdir(self.strategies_folder):
            filepath = os.path.join(self.strategies_folder, filename)
            
            if not os.path.isfile(filepath):
                continue
            
            ext = os.path.splitext(filename)[1].lower()
            
            # Handle text files
            if ext in supported_extensions:
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Skip if file too small
                    if len(content) > 50:
                        self.strategies[filename] = content
                        print(f"  [RAG] ✅ Loaded: {filename} ({len(content)} chars)")
                except Exception as e:
                    print(f"  [RAG] ❌ Error loading {filename}: {e}")
            
            # Handle PDF files (if PyPDF2 available)
            elif ext == '.pdf':
                try:
                    import PyPDF2
                    content = self.extract_pdf(filepath)
                    
                    if len(content) > 50:
                        self.strategies[filename] = content
                        print(f"  [RAG] ✅ Loaded PDF: {filename} ({len(content)} chars)")
                except ImportError:
                    print(f"  [RAG] ⚠️  PyPDF2 not installed. Skipping {filename}")
                except Exception as e:
                    print(f"  [RAG] ❌ Error loading {filename}: {e}")
    
    def extract_pdf(self, filepath: str) -> str:
        """Extract text from PDF file."""
        try:
            import PyPDF2
            text = ""
            with open(filepath, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"  [RAG] PDF extraction error: {e}")
            return ""
    
    def get_strategy_context(self) -> str:
        """Get all loaded strategies as formatted context for AI."""
        if not self.strategies:
            return "No trading strategy documents loaded."
        
        context = "=== YOUR TRADING STRATEGY RULES ===\n\n"
        
        for filename, content in self.strategies.items():
            context += f"--- {filename} ---\n"
            context += content[:1000]  # Limit to first 1000 chars per file
            context += "\n...\n\n"
        
        context += "=== END STRATEGY RULES ===\n"
        
        return context
    
    def has_strategies(self) -> bool:
        """Check if any strategies are loaded."""
        return len(self.strategies) > 0
    
    def get_strategy_summary(self) -> dict:
        """Get summary of loaded strategies."""
        return {
            "strategies_loaded": len(self.strategies),
            "total_chars": sum(len(c) for c in self.strategies.values()),
            "files": list(self.strategies.keys())
        }
    
    def format_for_display(self) -> str:
        """Format strategies for Telegram display."""
        summary = self.get_strategy_summary()
        
        if summary["strategies_loaded"] == 0:
            msg = "📚 <b>STRATEGY DOCUMENTS</b>\n\n"
            msg += "No strategy documents loaded.\n\n"
            msg += "To enable RAG:\n"
            msg += "1. Create <code>strategies/</code> folder\n"
            msg += "2. Add .txt or .md files with your trading rules\n"
            msg += "3. Restart bot\n"
            return msg
        
        msg = f"📚 <b>STRATEGY DOCUMENTS ({summary['strategies_loaded']})</b>\n\n"
        msg += f"Total content: {summary['total_chars']:,} characters\n\n"
        msg += "<b>Loaded files:</b>\n"
        for fname in summary["files"]:
            msg += f"✅ {fname}\n"
        
        msg += "\nAI will follow these rules for all trading decisions."
        
        return msg


# Global RAG instance
_strategy_rag = None


def get_strategy_rag() -> StrategyRAG:
    """Get or create global strategy RAG instance."""
    global _strategy_rag
    if _strategy_rag is None:
        _strategy_rag = StrategyRAG()
    return _strategy_rag


def get_strategy_context() -> str:
    """Get strategy context for AI analysis."""
    rag = get_strategy_rag()
    return rag.get_strategy_context()
