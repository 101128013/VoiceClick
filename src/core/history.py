"""
VoiceClick History - Manages transcription history persistence
Stores, retrieves, searches, and exports transcription records
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict, field

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionRecord:
    """Single transcription history record."""
    timestamp: str
    text: str
    duration_seconds: float
    model_used: str
    language: str = "en"
    confidence: float = 0.0
    id: str = field(default_factory=lambda: datetime.now().isoformat())


class TranscriptionHistory:
    """
    Manages transcription history with persistence to JSON.
    Provides search, filtering, and export functionality.
    """

    def __init__(self, history_file: Optional[Path] = None, max_size: int = 50):
        """
        Initialize history manager.
        
        Args:
            history_file: Path to JSON history file (defaults to ~/.voice_click/history.json)
            max_size: Maximum number of records to keep
        """
        if history_file is None:
            history_file = Path.home() / ".voice_click" / "history.json"
        
        self.history_file = history_file
        self.max_size = max_size
        self.records: List[TranscriptionRecord] = []
        
        # Create directory if needed
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing history
        self.load()

    def add_record(self, text: str, duration_seconds: float, model_used: str) -> TranscriptionRecord:
        """
        Add a new transcription record to history.
        
        Args:
            text: Transcribed text
            duration_seconds: Recording duration in seconds
            model_used: Whisper model name used
            
        Returns:
            TranscriptionRecord: The created record
        """
        record = TranscriptionRecord(
            timestamp=datetime.now().isoformat(),
            text=text,
            duration_seconds=duration_seconds,
            model_used=model_used
        )
        
        # Add to beginning of list (most recent first)
        self.records.insert(0, record)
        
        # Trim if exceeds max size
        if len(self.records) > self.max_size:
            self.records = self.records[:self.max_size]
        
        # Save to file
        self.save()
        
        logger.info(f"Added transcription record: {record.id[:8]}... ({len(text)} chars)")
        return record

    def get_all(self) -> List[TranscriptionRecord]:
        """
        Get all history records.
        
        Returns:
            List of TranscriptionRecord objects (most recent first)
        """
        return self.records.copy()

    def get_by_id(self, record_id: str) -> Optional[TranscriptionRecord]:
        """
        Get a specific record by ID.
        
        Args:
            record_id: Record ID
            
        Returns:
            TranscriptionRecord or None if not found
        """
        for record in self.records:
            if record.id == record_id:
                return record
        return None

    def search(self, query: str) -> List[TranscriptionRecord]:
        """
        Search history by text content.
        
        Args:
            query: Search query (case-insensitive)
            
        Returns:
            List of matching records
        """
        query_lower = query.lower()
        return [r for r in self.records if query_lower in r.text.lower()]

    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[TranscriptionRecord]:
        """
        Get records within a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of records in date range
        """
        results = []
        for record in self.records:
            record_date = datetime.fromisoformat(record.timestamp)
            if start_date <= record_date <= end_date:
                results.append(record)
        return results

    def delete_record(self, record_id: str) -> bool:
        """
        Delete a record by ID.
        
        Args:
            record_id: Record ID to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        for i, record in enumerate(self.records):
            if record.id == record_id:
                del self.records[i]
                self.save()
                logger.info(f"Deleted record: {record_id[:8]}...")
                return True
        return False

    def clear_all(self):
        """Clear all history records."""
        self.records = []
        self.save()
        logger.info("History cleared")

    def export_to_csv(self, output_path: Path) -> bool:
        """
        Export history to CSV file.
        
        Args:
            output_path: Path to output CSV file
            
        Returns:
            bool: True if successful
        """
        try:
            import csv
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['timestamp', 'text', 'duration_seconds', 'model_used', 'language']
                )
                writer.writeheader()
                
                for record in self.records:
                    writer.writerow({
                        'timestamp': record.timestamp,
                        'text': record.text,
                        'duration_seconds': record.duration_seconds,
                        'model_used': record.model_used,
                        'language': record.language
                    })
            
            logger.info(f"Exported {len(self.records)} records to {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            return False

    def export_to_txt(self, output_path: Path) -> bool:
        """
        Export history to plain text file.
        
        Args:
            output_path: Path to output text file
            
        Returns:
            bool: True if successful
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("VoiceClick Transcription History\n")
                f.write("=" * 50 + "\n\n")
                
                for i, record in enumerate(self.records, 1):
                    f.write(f"[{i}] {record.timestamp}\n")
                    f.write(f"Duration: {record.duration_seconds:.1f}s | Model: {record.model_used}\n")
                    f.write(f"Text: {record.text}\n")
                    f.write("-" * 50 + "\n\n")
            
            logger.info(f"Exported {len(self.records)} records to {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Text export failed: {e}")
            return False

    def save(self) -> bool:
        """
        Save history to JSON file.
        
        Returns:
            bool: True if successful
        """
        try:
            data = [asdict(record) for record in self.records]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
            return False

    def load(self) -> bool:
        """
        Load history from JSON file.
        
        Returns:
            bool: True if successful
        """
        try:
            if not self.history_file.exists():
                self.records = []
                return True
            
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.records = [TranscriptionRecord(**record) for record in data]
            
            # Keep only max_size records
            if len(self.records) > self.max_size:
                self.records = self.records[:self.max_size]
                self.save()
            
            logger.info(f"Loaded {len(self.records)} history records")
            return True
        
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            self.records = []
            return False

    def get_stats(self) -> Dict:
        """
        Get statistics about transcription history.
        
        Returns:
            Dictionary with statistics
        """
        if not self.records:
            return {
                "total_records": 0,
                "total_characters": 0,
                "total_duration": 0,
                "average_duration": 0
            }
        
        total_duration = sum(r.duration_seconds for r in self.records)
        total_chars = sum(len(r.text) for r in self.records)
        
        return {
            "total_records": len(self.records),
            "total_characters": total_chars,
            "total_duration": total_duration,
            "average_duration": total_duration / len(self.records),
            "average_chars_per_transcription": total_chars / len(self.records)
        }
