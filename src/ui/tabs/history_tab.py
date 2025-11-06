"""
The History Tab for the VoiceClick application.

This module defines the `HistoryTab` class, which provides a user interface
for viewing, searching, and managing transcription history.
"""

import logging
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QHeaderView, QFileDialog, QLineEdit, QFrame, QAbstractItemView
)
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt, QTimer, QSize

from src.core.history import TranscriptionHistory

logger = logging.getLogger(__name__)

class HistoryTab(QWidget):
    """
    The HistoryTab widget displays past transcriptions in a table and allows
    users to manage them.
    """

    def __init__(self, history_manager: TranscriptionHistory, icon_dir: Path):
        """
        Initializes the HistoryTab.

        Args:
            history_manager: An instance of TranscriptionHistory to interact with.
            icon_dir: Path to the icon directory.
        """
        super().__init__()
        self.history_manager = history_manager
        self.icon_dir = icon_dir
        
        # Cache for performance optimization
        self._cached_records = []
        self._cached_timestamps = {}
        self._last_record_count = 0
        
        self.setup_ui()
        self.connect_signals()
        self.refresh_history()
        
        # Debounce timer for search input (performance optimization)
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)

    def setup_ui(self):
        """Sets up the user interface for the history tab."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Transcription History")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #61afef; margin-bottom: 15px;")
        layout.addWidget(title)

        # Search Card
        search_card = QFrame()
        search_card.setStyleSheet("""
            QFrame {
                background-color: #21252b;
                border-radius: 8px;
                padding: 10px;
                border: 1px solid #3e4451;
            }
        """)
        search_layout = QHBoxLayout(search_card)
        search_layout.setContentsMargins(8, 8, 8, 8)
        
        search_label = QLabel("") # Removed text, will use icon
        search_label.setPixmap(QPixmap(str(self.icon_dir / 'search_icon.png')).scaled(QSize(16,16), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        search_label.setStyleSheet("color: #ABB2BF;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search transcriptions...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #282c34;
                border: 1px solid #5C6370;
                border-radius: 4px;
                padding: 8px;
                font-size: 10pt;
                color: #ABB2BF;
            }
            QLineEdit:focus {
                border-color: #61afef;
                background-color: #3e4451;
            }
        """)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addWidget(search_card)

        # History Table Card
        table_card = QFrame()
        table_card.setStyleSheet("""
            QFrame {
                background-color: #21252b;
                border: 1px solid #3e4451;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Date", "Duration (s)", "Text", "Model"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.horizontalHeader().setStretchLastSection(False)
        self.history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: #282c34;
                border: none;
                gridline-color: #3e4451;
                font-size: 9pt;
                color: #ABB2BF;
                selection-background-color: #4b5263;
                selection-color: #61afef;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #3e4451;
            }
            QTableWidget::item:selected {
                background-color: #4b5263; /* Selected row background */
                color: #61afef; /* Selected row text color */
            }
            QHeaderView::section {
                background-color: #3e4451;
                color: #ABB2BF;
                padding: 8px;
                border: 1px solid #282c34;
                font-weight: bold;
                font-size: 9pt;
            }
        """)
        table_layout.addWidget(self.history_table)
        layout.addWidget(table_card)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setIcon(QIcon(str(self.icon_dir / 'refresh_icon.png')))
        self.refresh_button.setIconSize(QSize(16, 16))
        self.refresh_button.setFont(QFont("Segoe UI", 9))
        self.refresh_button.setStyleSheet(self._get_button_style("#61afef"))
        
        self.export_button = QPushButton("Export to CSV")
        self.export_button.setIcon(QIcon(str(self.icon_dir / 'export_icon.png')))
        self.export_button.setIconSize(QSize(16, 16))
        self.export_button.setFont(QFont("Segoe UI", 9))
        self.export_button.setStyleSheet(self._get_button_style("#98C379"))
        
        self.clear_button = QPushButton("Clear History")
        self.clear_button.setIcon(QIcon(str(self.icon_dir / 'clear_icon.png')))
        self.clear_button.setIconSize(QSize(16, 16))
        self.clear_button.setFont(QFont("Segoe UI", 9))
        self.clear_button.setStyleSheet(self._get_button_style("#E06C75"))
        
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
        # Use debounced search instead of immediate filtering
        self.search_input.textChanged.connect(self._on_search_text_changed)

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
        
        # Use search method directly (more efficient than get_all + search)
        filtered_records = self.history_manager.search(search_text)
        
        # Update table with filtered results
        self.history_table.setRowCount(len(filtered_records))
        
        # Batch updates for better performance
        self.history_table.setUpdatesEnabled(False)
        self.history_table.setSortingEnabled(False)  # Disable sorting during update
        try:
            for row, record in enumerate(filtered_records):
                # Cache timestamp formatting
                if record.timestamp not in self._cached_timestamps:
                    self._cached_timestamps[record.timestamp] = datetime.fromisoformat(record.timestamp).strftime('%Y-%m-%d %H:%M:%S')
                timestamp = self._cached_timestamps[record.timestamp]
                
                # Only create items if they don't exist or need updating
                if row >= self.history_table.rowCount() or self.history_table.item(row, 0) is None:
                    self.history_table.setItem(row, 0, QTableWidgetItem(timestamp))
                    self.history_table.setItem(row, 1, QTableWidgetItem(f"{record.duration_seconds:.2f}"))
                    self.history_table.setItem(row, 2, QTableWidgetItem(record.text))
                    self.history_table.setItem(row, 3, QTableWidgetItem(record.model_used))
                else:
                    # Update existing items
                    self.history_table.item(row, 0).setText(timestamp)
                    self.history_table.item(row, 1).setText(f"{record.duration_seconds:.2f}")
                    self.history_table.item(row, 2).setText(record.text)
                    self.history_table.item(row, 3).setText(record.model_used)
        finally:
            self.history_table.setUpdatesEnabled(True)
            self.history_table.setSortingEnabled(True)
            # Defer resize to avoid blocking
            QTimer.singleShot(0, self.history_table.resizeRowsToContents)
        
        logger.info(f"Filtered history: {len(filtered_records)} records match '{search_text}'")

    def refresh_history(self):
        """
        Reloads the transcription history from the manager and updates the table.
        """
        logger.info("Refreshing history view.")
        records = self.history_manager.get_all()
        
        # Only refresh if records changed
        if len(records) == self._last_record_count and records == self._cached_records:
            return
        
        self._cached_records = records
        self._last_record_count = len(records)
        self.history_table.setRowCount(len(records))

        # Batch updates for better performance
        self.history_table.setUpdatesEnabled(False)
        self.history_table.setSortingEnabled(False)  # Disable sorting during update
        try:
            for row, record in enumerate(records):
                # Cache timestamp formatting for performance
                if record.timestamp not in self._cached_timestamps:
                    self._cached_timestamps[record.timestamp] = datetime.fromisoformat(record.timestamp).strftime('%Y-%m-%d %H:%M:%S')
                timestamp = self._cached_timestamps[record.timestamp]
                
                # Only create/update items if needed
                if row >= self.history_table.rowCount() or self.history_table.item(row, 0) is None:
                    self.history_table.setItem(row, 0, QTableWidgetItem(timestamp))
                    self.history_table.setItem(row, 1, QTableWidgetItem(f"{record.duration_seconds:.2f}"))
                    self.history_table.setItem(row, 2, QTableWidgetItem(record.text))
                    self.history_table.setItem(row, 3, QTableWidgetItem(record.model_used))
                else:
                    # Update existing items (more efficient than recreating)
                    self.history_table.item(row, 0).setText(timestamp)
                    self.history_table.item(row, 1).setText(f"{record.duration_seconds:.2f}")
                    self.history_table.item(row, 2).setText(record.text)
                    self.history_table.item(row, 3).setText(record.model_used)
        finally:
            self.history_table.setUpdatesEnabled(True)
            self.history_table.setSortingEnabled(True)
            # Defer resize to avoid blocking UI
            QTimer.singleShot(0, self.history_table.resizeRowsToContents)

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

    def _on_search_text_changed(self):
        """Debounced handler for search text changes."""
        # Restart timer - search will execute after 300ms of no typing
        self.search_timer.stop()
        self.search_timer.start(300)
    
    def _perform_search(self):
        """Performs the actual search after debounce delay."""
        self.filter_history()

    def _get_button_style(self, color: str) -> str:
        """Returns style sheet for buttons."""
        # Use simple button styling; icons handled separately per button
        return f"""
           QPushButton {{
               background-color: {color};
               color: white;
               border: none;
               border-radius: 6px;
               padding: 10px 20px;
               min-height: 36px;
               font-weight: 500;
           }}
           QPushButton:hover {{
               background-color: {self._darken_color(color, 0.1)};
           }}
           QPushButton:pressed {{
               background-color: {self._darken_color(color, 0.2)};
           }}
       """
    
    def _darken_color(self, hex_color: str, factor: float = 0.15) -> str:
        """Darkens a hex color by a factor."""
        # Simple darkening - convert hex to RGB, darken, convert back
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = max(0, min(255, int(r * (1 - factor))))
        g = max(0, min(255, int(g * (1 - factor))))
        b = max(0, min(255, int(b * (1 - factor))))
        return f"#{r:02x}{g:02x}{b:02x}"

