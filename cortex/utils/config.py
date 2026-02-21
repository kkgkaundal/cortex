"""
Configuration management for Cortex.
"""
import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration manager for Cortex system."""
    
    def __init__(self):
        """Initialize configuration."""
        # Base directory for Cortex data
        self.cortex_home = Path(os.getenv('CORTEX_HOME', Path.home() / '.cortex'))
        self.cortex_home.mkdir(parents=True, exist_ok=True)
        
        # Database path
        self.db_path = self.cortex_home / 'cortex.db'
        
        # Archive directory for cold storage
        self.archive_dir = self.cortex_home / 'archive'
        self.archive_dir.mkdir(exist_ok=True)
        
        # Sandbox configuration
        self.sandbox_timeout = int(os.getenv('CORTEX_SANDBOX_TIMEOUT', '60'))
        
        # Learning thresholds
        self.pattern_min_occurrences = int(os.getenv('CORTEX_PATTERN_MIN', '3'))
        self.confidence_threshold = float(os.getenv('CORTEX_CONFIDENCE_MIN', '0.5'))
        
        # Memory consolidation
        self.consolidation_days = int(os.getenv('CORTEX_CONSOLIDATION_DAYS', '7'))
        
    def get_db_path(self) -> str:
        """Get database path."""
        return str(self.db_path)
        
    def get_archive_dir(self) -> str:
        """Get archive directory."""
        return str(self.archive_dir)


# Global config instance
config = Config()
