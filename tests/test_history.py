"""
Unit tests for VoiceClick History module
"""
import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from src.core.history import TranscriptionHistory, TranscriptionRecord


class TestTranscriptionRecord:
    """Test TranscriptionRecord class"""
    
    def test_record_creation(self):
        """Test creating a transcription record"""
        record = TranscriptionRecord(
            timestamp=datetime.now().isoformat(),
            text="Hello world",
            duration_seconds=5.0,
            model_used="large-v3"
        )
        
        assert record.text == "Hello world"
        assert record.duration_seconds == 5.0
        assert record.model_used == "large-v3"
        assert record.timestamp is not None


class TestTranscriptionHistory:
    """Test TranscriptionHistory class"""
    
    def test_history_initialization(self):
        """Test history initializes correctly"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            history = TranscriptionHistory(history_file=temp_path)
            assert len(history.records) == 0
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def test_add_record(self):
        """Test adding records to history"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            history = TranscriptionHistory(history_file=temp_path)
            
            # Add records
            history.add_record("First transcription", 2.5, "large-v3", "en")
            history.add_record("Second transcription", 3.0, "large-v3", "en")
            
            assert len(history.records) == 2
            assert history.records[0].text == "Second transcription"  # Most recent first
            assert history.records[1].text == "First transcription"
            
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def test_search_records(self):
        """Test searching history records"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            history = TranscriptionHistory(history_file=temp_path)
            
            # Add test records
            history.add_record("Hello world", 1.0, "tiny", "en")
            history.add_record("Python programming", 2.0, "tiny", "en")
            history.add_record("Hello Python", 3.0, "tiny", "en")
            
            # Search for "Hello"
            results = history.search("Hello")
            assert len(results) == 2
            
            # Search for "Python"
            results = history.search("Python")
            assert len(results) == 2
            
            # Search for non-existent term
            results = history.search("JavaScript")
            assert len(results) == 0
            
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def test_save_and_load(self):
        """Test saving and loading history"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            # Create and save history
            history1 = TranscriptionHistory(history_file=temp_path)
            history1.add_record("Test entry 1", 1.5, "tiny", "en")
            history1.add_record("Test entry 2", 2.5, "tiny", "en")
            history1.save()
            
            # Load in new instance
            history2 = TranscriptionHistory(history_file=temp_path)
            history2.load()
            
            assert len(history2.records) == 2
            
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def test_delete_record(self):
        """Test deleting history records"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            history = TranscriptionHistory(history_file=temp_path)
            
            # Add records
            rec1 = history.add_record("Entry 1", 1.0, "tiny", "en")
            rec2 = history.add_record("Entry 2", 2.0, "tiny", "en")
            rec3 = history.add_record("Entry 3", 3.0, "tiny", "en")
            
            assert len(history.records) == 3
            
            # Delete middle record
            result = history.delete_record(rec2.id)
            
            assert result == True
            assert len(history.records) == 2
            
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def test_export_to_csv(self):
        """Test exporting history to CSV"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            json_path = Path(f.name)
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            csv_path = Path(f.name)
        
        try:
            history = TranscriptionHistory(history_file=json_path)
            history.add_record("Test 1", 1.0, "tiny", "en")
            history.add_record("Test 2", 2.0, "tiny", "en")
            
            # Export to CSV
            result = history.export_to_csv(csv_path)
            
            # Verify export succeeded
            assert result == True
            assert csv_path.exists()
            content = csv_path.read_text()
            assert "Test 1" in content or "Test 2" in content
            
        finally:
            if json_path.exists():
                json_path.unlink()
            if csv_path.exists():
                csv_path.unlink()
    
    def test_get_stats(self):
        """Test get_stats method"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            history = TranscriptionHistory(history_file=temp_path)
            
            # Empty history
            stats = history.get_stats()
            assert stats['total_records'] == 0
            assert stats['total_duration'] == 0
            assert stats['average_duration'] == 0
            
            # Add records
            history.add_record("Test 1", 2.0, "tiny", "en")
            history.add_record("Test 2", 4.0, "tiny", "en")
            
            stats = history.get_stats()
            assert stats['total_records'] == 2
            assert stats['total_duration'] == 6.0
            assert stats['average_duration'] == 3.0
            
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def test_trim_history(self):
        """Test _trim_history with max_size"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            history = TranscriptionHistory(history_file=temp_path, max_size=3)
            
            # Add more records than max_size
            history.add_record("Record 1", 1.0, "tiny", "en")
            history.add_record("Record 2", 2.0, "tiny", "en")
            history.add_record("Record 3", 3.0, "tiny", "en")
            history.add_record("Record 4", 4.0, "tiny", "en")
            history.add_record("Record 5", 5.0, "tiny", "en")
            
            # Should be trimmed to max_size
            assert len(history.records) == 3
            assert history.records[0].text == "Record 5"  # Most recent
            
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def test_load_invalid_json(self):
        """Test loading invalid JSON"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as f:
            temp_path = Path(f.name)
            f.write("invalid json content {")
        
        try:
            history = TranscriptionHistory(history_file=temp_path)
            # Should start with empty history
            assert len(history.records) == 0
            
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def test_get_by_id(self):
        """Test get_by_id method"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            history = TranscriptionHistory(history_file=temp_path)
            
            rec1 = history.add_record("Record 1", 1.0, "tiny", "en")
            rec2 = history.add_record("Record 2", 2.0, "tiny", "en")
            
            found = history.get_by_id(rec1.id)
            assert found is not None
            assert found.text == "Record 1"
            
            not_found = history.get_by_id("nonexistent")
            assert not_found is None
            
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def test_clear_all(self):
        """Test clear_all method"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            history = TranscriptionHistory(history_file=temp_path)
            history.add_record("Record 1", 1.0, "tiny", "en")
            history.add_record("Record 2", 2.0, "tiny", "en")
            
            assert len(history.records) == 2
            
            history.clear_all()
            
            assert len(history.records) == 0
            
        finally:
            if temp_path.exists():
                temp_path.unlink()
