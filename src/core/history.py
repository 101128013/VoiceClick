"""
Manages the storage and retrieval of transcription history.

This module provides a `TranscriptionHistory` class that handles the persistence
of transcription records. It supports adding, retrieving, searching, and deleting
records, as well as exporting them to various formats.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict, field
import csv

from src.config import constants

logger = logging.getLogger(__name__)

@dataclass
class TranscriptionRecord:
    """
    Represents a single transcription event.
    
    Attributes:
        id: A unique identifier for the record, generated from the timestamp.
        timestamp: The ISO 8601 formatted timestamp of when the transcription occurred.
        text: The transcribed text.
        duration_seconds: The duration of the audio that was transcribed.
        model_used: The name of the Whisper model used for the transcription.
        language: The language of the transcribed text.
    """
    id: str = field(default_factory=lambda: datetime.now().isoformat())
    timestamp: str
    text: str
    duration_seconds: float
    model_used: str
    language: str = "en"


class TranscriptionHistory:
    """
    Manages a collection of transcription records, with persistence to a JSON file.
    
    This class provides an interface to interact with the transcription history,
    ensuring that records are saved and loaded correctly and that the history
    does not exceed a maximum size.
    """

    def __init__(self, history_file: Optional[Path] = None, max_size: int = constants.DEFAULT_HISTORY_SIZE):
        """
        Initializes the TranscriptionHistory manager.

        Args:
            history_file: Path to the JSON file for history persistence. Defaults to
                          `~/.voice_click/history.json`.
            max_size: The maximum number of records to store in the history.
        """
        self.history_file = history_file or Path.home() / ".voice_click" / constants.HISTORY_FILENAME
        self.max_size = max_size
        self.records: List[TranscriptionRecord] = []
        
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.load()

    def add_record(self, text: str, duration_seconds: float, model_used: str, language: str) -> TranscriptionRecord:
        """
        Creates a new transcription record and adds it to the history.

        Args:
            text: The transcribed text.
            duration_seconds: The duration of the recorded audio.
            model_used: The Whisper model used for transcription.
            language: The detected or specified language.

        Returns:
            The newly created TranscriptionRecord.
        """
        record = TranscriptionRecord(
            timestamp=datetime.now().isoformat(),
            text=text,
            duration_seconds=duration_seconds,
            model_used=model_used,
            language=language
        )
        
        self.records.insert(0, record)
        self._trim_history()
        self.save()
        
        logger.info(f"Added transcription record {record.id} to history.")
        return record

    def get_all(self) -> List[TranscriptionRecord]:
        """Returns a copy of all records, sorted from most to least recent."""
        return self.records.copy()

    def get_by_id(self, record_id: str) -> Optional[TranscriptionRecord]:
        """
        Retrieves a single record by its unique ID.

        Args:
            record_id: The ID of the record to find.

        Returns:
            The matching TranscriptionRecord, or None if not found.
        """
        return next((r for r in self.records if r.id == record_id), None)

    def search(self, query: str) -> List[TranscriptionRecord]:
        """
        Searches for records containing a specific text query (case-insensitive).

        Args:
            query: The text to search for within the transcription records.

        Returns:
            A list of matching records.
        """
        query_lower = query.lower()
        return [r for r in self.records if query_lower in r.text.lower()]

    def delete_record(self, record_id: str) -> bool:
        """
        Deletes a record from the history by its ID.

        Args:
            record_id: The ID of the record to delete.

        Returns:
            True if the record was found and deleted, False otherwise.
        """
        initial_len = len(self.records)
        self.records = [r for r in self.records if r.id != record_id]
        if len(self.records) < initial_len:
            self.save()
            logger.info(f"Deleted record {record_id} from history.")
            return True
        logger.warning(f"Attempted to delete non-existent record {record_id}.")
        return False

    def clear_all(self):
        """Removes all records from the history."""
        self.records = []
        self.save()
        logger.info("Transcription history has been cleared.")

    def export_to_csv(self, output_path: Path) -> bool:
        """
        Exports the entire transcription history to a CSV file.

        Args:
            output_path: The path to the destination CSV file.

        Returns:
            True on successful export, False on failure.
        """
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=list(asdict(self.records[0]).keys()) if self.records else [])
                writer.writeheader()
                for record in self.records:
                    writer.writerow(asdict(record))
            logger.info(f"Successfully exported {len(self.records)} records to {output_path}.")
            return True
        except (IOError, csv.Error) as e:
            logger.error(f"Failed to export history to CSV: {e}", exc_info=True)
            return False

    def save(self) -> bool:
        """
        Saves the current history to the JSON file.
        
        Returns:
            True on success, False on failure.
        """
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(r) for r in self.records], f, indent=4)
            return True
        except IOError as e:
            logger.error(f"Failed to save history to {self.history_file}: {e}", exc_info=True)
            return False

    def load(self) -> bool:
        """
        Loads the history from the JSON file.
        
        Returns:
            True on success, False on failure.
        """
        if not self.history_file.exists():
            return True  # Nothing to load

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.records = [TranscriptionRecord(**r) for r in data]
            self._trim_history()
            logger.info(f"Loaded {len(self.records)} records from history.")
            return True
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Failed to load or parse history file: {e}. Starting with empty history.", exc_info=True)
            self.records = []
            return False

    def _trim_history(self):
        """Ensures the history does not exceed its maximum size."""
        if len(self.records) > self.max_size:
            self.records = self.records[:self.max_size]
            logger.info(f"History trimmed to {self.max_size} records.")

    def get_stats(self) -> Dict[str, float]:
        """
        Calculates and returns statistics about the transcription history.
        """
        if not self.records:
            return {
                "total_records": 0,
                "total_duration": 0,
                "average_duration": 0,
            }
        
        total_duration = sum(r.duration_seconds for r in self.records)
        return {
            "total_records": len(self.records),
            "total_duration": total_duration,
            "average_duration": total_duration / len(self.records) if self.records else 0,
        }
