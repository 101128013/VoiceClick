#!/usr/bin/env python3
"""
VoiceClick - History Tab
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class HistoryTab(QWidget):
    """History tab - view transcription history"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Setup history display UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Transcription History")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Create table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([
            "Timestamp", "Duration (s)", "Text", "Model"
        ])
        self.history_table.setColumnWidth(0, 180)
        self.history_table.setColumnWidth(1, 100)
        self.history_table.setColumnWidth(2, 300)
        self.history_table.setColumnWidth(3, 80)
        
        layout.addWidget(self.history_table)

        # Buttons
        button_layout = QVBoxLayout()
        self.refresh_button = QPushButton("Refresh History")
        self.export_button = QPushButton("Export History")
        self.clear_button = QPushButton("Clear History")
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_history(self):
        """Load and display history from file"""
        # This is a placeholder. Integration with history manager is needed.
        self.history_table.setRowCount(0) # Clear table
        # Example row
        self.history_table.insertRow(0)
        self.history_table.setItem(0, 0, QTableWidgetItem("2025-11-05 10:00:00"))
        self.history_table.setItem(0, 1, QTableWidgetItem("5.2"))
        self.history_table.setItem(0, 2, QTableWidgetItem("Hello world, this is a test."))
        self.history_table.setItem(0, 3, QTableWidgetItem("base"))
