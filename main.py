#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Child Safety Protection Application
Main application entry point
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QStackedWidget)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QSize

from ui_components import HomeScreen, NewUserScreen, ScanCardScreen
import utils
from database import DatabaseManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create necessary directories if they don't exist
        os.makedirs("data", exist_ok=True)
        os.makedirs("images", exist_ok=True)
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle("Child Safety Protection App")
        self.setGeometry(100, 100, 1000, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create navigation bar
        nav_bar = QWidget()
        nav_bar.setStyleSheet("background-color: #2c3e50; color: white;")
        nav_bar.setFixedHeight(60)
        nav_layout = QHBoxLayout(nav_bar)
        
        # App logo and title
        logo_layout = QHBoxLayout()
        app_title = QLabel("Child Safety App")
        app_title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        logo_layout.addWidget(app_title)
        logo_layout.addStretch()
        
        # Navigation buttons
        self.new_user_btn = QPushButton("New User")
        self.scan_card_btn = QPushButton("Scan Card")
        self.home_btn = QPushButton("Home")
        
        # Style buttons
        for btn in [self.new_user_btn, self.scan_card_btn, self.home_btn]:
            btn.setFixedSize(120, 40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
        
        # Add buttons to navigation layout
        nav_layout.addLayout(logo_layout)
        nav_layout.addStretch()
        nav_layout.addWidget(self.new_user_btn)
        nav_layout.addWidget(self.scan_card_btn)
        nav_layout.addWidget(self.home_btn)
        nav_layout.addStretch()
        
        # Create stacked widget for different screens
        self.stacked_widget = QStackedWidget()
        
        # Create screens
        self.home_screen = HomeScreen()
        self.new_user_screen = NewUserScreen(self.db_manager)
        self.scan_card_screen = ScanCardScreen(self.db_manager)
        
        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.home_screen)
        self.stacked_widget.addWidget(self.new_user_screen)
        self.stacked_widget.addWidget(self.scan_card_screen)
        
        # Add navigation bar and stacked widget to main layout
        main_layout.addWidget(nav_bar)
        main_layout.addWidget(self.stacked_widget)
        
        # Connect signals
        self.home_btn.clicked.connect(self.show_home_screen)
        self.new_user_btn.clicked.connect(self.show_new_user_screen)
        self.scan_card_btn.clicked.connect(self.show_scan_card_screen)
        
        # Set initial screen
        self.show_home_screen()
    
    def show_home_screen(self):
        """Show the home screen"""
        self.stacked_widget.setCurrentWidget(self.home_screen)
    
    def show_new_user_screen(self):
        """Show the new user registration screen"""
        self.new_user_screen.reset_form()
        self.stacked_widget.setCurrentWidget(self.new_user_screen)
    
    def show_scan_card_screen(self):
        """Show the scan card screen"""
        self.stacked_widget.setCurrentWidget(self.scan_card_screen)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show the main window
    main_window = MainWindow()
    main_window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())
