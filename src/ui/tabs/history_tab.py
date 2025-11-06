"""
The History Tab for the VoiceClick application.

This module defines the `HistoryTab` class, which provides a user interface
for viewing, searching, and managing transcription history.
"""

import logging
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QHeaderView, QFileDialog, QLineEdit
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from src.core.history import TranscriptionHistory

logger = logging.getLogger(__name__)

class HistoryTab(QWidget):
    """
    The HistoryTab widget displays past transcriptions in a table and allows
    users to manage them.
    """

    def __init__(self, history_manager: TranscriptionHistory):
        """
        Initializes the HistoryTab.

        Args:
            history_manager: An instance of TranscriptionHistory to interact with.
        """
        super().__init__()
        self.history_manager = history_manager
        self.setup_ui()
        self.connect_signals()
        self.refresh_history()

    def setup_ui(self):
        """Sets up the user interface for the history tab."""
        layout = QVBoxLayout(self)

        title = QLabel("Transcription History")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search transcriptions...")
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Date", "Duration (s)", "Text", "Model"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.horizontalHeader().setStretchLastSection(False)
        self.history_table.setColumnWidth(0, 160)
        self.history_table.setColumnWidth(1, 80)
        self.history_table.setColumnWidth(3, 100)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.history_table)

        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.export_button = QPushButton("Export to CSV")
        self.clear_button = QPushButton("Clear History")
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.export_button)
        button_layout.addStretch()
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)

    def connect_signals(self):
        """Connects UI element signals to their respective slots."""
        self.refresh_button.clicked.connect(self.refresh_history)
        self.export_button.clicked.connect(self.export_history)
        self.clear_button.clicked.connect(self.clear_history)
        self.search_input.textChanged.connect(self.filter_history)

    def filter_history(self, search_text: str = None):
        """
        Filters the history table based on the search text.
        
        Args:
            search_text: Optional search text. If None, uses the search input field.
        """
        if search_text is None:
            search_text = self.search_input.text()
        
        if not search_text.strip():
            # Show all records if search is empty
            self.refresh_history()
            return
        
        # Get all records and filter
        all_records = self.history_manager.get_all()
        filtered_records = self.history_manager.search(search_text)
        
        # Update table with filtered results
        self.history_table.setRowCount(len(filtered_records))
        
        for row, record in enumerate(filtered_records):
            timestamp = datetime.fromisoformat(record.timestamp).strftime('%Y-%m-%d %H:%M:%S')
            
            self.history_table.setItem(row, 0, QTableWidgetItem(timestamp))
            self.history_table.setItem(row, 1, QTableWidgetItem(f"{record.duration_seconds:.2f}"))
            self.history_table.setItem(row, 2, QTableWidgetItem(record.text))
            self.history_table.setItem(row, 3, QTableWidgetItem(record.model_used))
        
        self.history_table.resizeRowsToContents()
        logger.info(f"Filtered history: {len(filtered_records)} records match '{search_text}'")

    def refresh_history(self):
        """
        Reloads the transcription history from the manager and updates the table.
        """
        logger.info("Refreshing history view.")
        records = self.history_manager.get_all()
        self.history_table.setRowCount(len(records))

        for row, record in enumerate(records):
            timestamp = datetime.fromisoformat(record.timestamp).strftime('%Y-%m-%d %H:%M:%S')
            
            self.history_table.setItem(row, 0, QTableWidgetItem(timestamp))
            self.history_table.setItem(row, 1, QTableWidgetItem(f"{record.duration_seconds:.2f}"))
            self.history_table.setItem(row, 2, QTableWidgetItem(record.text))
            self.history_table.setItem(row, 3, QTableWidgetItem(record.model_used))
        
        self.history_table.resizeRowsToContents()

    def export_history(self):
        """Opens a dialog to export the history to a CSV file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export History", "", "CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            if self.history_manager.export_to_csv(file_path):
                logger.info(f"History exported successfully to {file_path}")
            else:
                logger.error("Failed to export history.")

    def clear_history(self):
        """Clears all records from the history."""
        self.history_manager.clear_all()
        self.refresh_history()
        logger.info("History cleared by user.")

