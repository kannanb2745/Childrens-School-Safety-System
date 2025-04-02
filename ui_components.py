#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI Components for Child Safety Protection App
Contains the different screens and widgets used in the application
"""

import os
import sys
import cv2
import time
import re
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QLineEdit, QFormLayout, QFileDialog, QScrollArea, 
                            QMessageBox, QGroupBox, QComboBox, QSpinBox, QGridLayout,
                            QSplitter, QFrame)
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer

from ocr_processor import OCRProcessor
from utils import save_temp_file, crop_image_to_fit
import json
import shutil
from typing import Dict, List, Any, Optional, Tuple
import difflib


class HomeScreen(QWidget):
    """Home screen widget"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Welcome message and instructions
        welcome_label = QLabel("Welcome to Child Safety Protection System")
        welcome_label.setFont(QFont("Arial", 24, QFont.Bold))
        welcome_label.setAlignment(Qt.AlignCenter)
        
        instructions_label = QLabel(
            "This system helps secure children by verifying authorized individuals for pickup.\n\n"
            "• Register new children and parents/guardians using the 'New User' button\n"
            "• Verify visitors by scanning their ID using the 'Scan Card' button\n"
            "• Return to this screen anytime by clicking the 'Home' button"
        )
        instructions_label.setFont(QFont("Arial", 14))
        instructions_label.setAlignment(Qt.AlignCenter)
        instructions_label.setWordWrap(True)
        
        # Application logo or icon
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Add widgets to layout
        layout.addStretch(1)
        layout.addWidget(welcome_label)
        layout.addSpacing(20)
        layout.addWidget(instructions_label)
        layout.addSpacing(40)
        layout.addWidget(logo_label)
        layout.addStretch(1)
        
        self.setLayout(layout)


class NewUserScreen(QWidget):
    """Screen for registering new users"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_child_id = None
        self.child_image_path = None
        self.parent_image_path = None
        self.id_proof_path = None
        self.ocr_processor = OCRProcessor()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Register New User")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        layout.addSpacing(10)
        
        # Child Information Form
        child_group = QGroupBox("Child Information")
        child_form = QFormLayout()
        
        # Child details fields
        self.child_name_input = QLineEdit()
        self.child_age_input = QSpinBox()
        self.child_age_input.setRange(1, 18)
        self.child_school_input = QLineEdit()
        self.child_class_input = QLineEdit()
        self.child_section_input = QLineEdit()
        
        child_form.addRow("Name:", self.child_name_input)
        child_form.addRow("Age:", self.child_age_input)
        child_form.addRow("School:", self.child_school_input)
        child_form.addRow("Class:", self.child_class_input)
        child_form.addRow("Section:", self.child_section_input)
        
        # Child photo upload button
        self.child_photo_btn = QPushButton("Upload Child Photo")
        self.child_photo_label = QLabel("No photo selected")
        child_photo_layout = QHBoxLayout()
        child_photo_layout.addWidget(self.child_photo_btn)
        child_photo_layout.addWidget(self.child_photo_label)
        child_form.addRow("Photo:", child_photo_layout)
        
        child_group.setLayout(child_form)
        layout.addWidget(child_group)
        
        # Button to register child
        self.register_child_btn = QPushButton("Register Child")
        self.register_child_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        layout.addWidget(self.register_child_btn)
        layout.addSpacing(20)
        
        # Parent Information Form
        self.parent_group = QGroupBox("Parent/Guardian Information")
        self.parent_group.setEnabled(False)  # Disabled until child is registered
        parent_form = QFormLayout()
        
        # Parent details fields
        self.parent_name_input = QLineEdit()
        self.parent_age_input = QSpinBox()
        self.parent_age_input.setRange(18, 100)
        self.parent_age_input.setValue(30)
        self.parent_relationship_input = QComboBox()
        self.parent_relationship_input.addItems(["Father", "Mother", "Guardian", "Relative"])
        
        parent_form.addRow("Name:", self.parent_name_input)
        parent_form.addRow("Age:", self.parent_age_input)
        parent_form.addRow("Relationship:", self.parent_relationship_input)
        
        # Parent photo upload button
        self.parent_photo_btn = QPushButton("Upload Parent Photo")
        self.parent_photo_label = QLabel("No photo selected")
        parent_photo_layout = QHBoxLayout()
        parent_photo_layout.addWidget(self.parent_photo_btn)
        parent_photo_layout.addWidget(self.parent_photo_label)
        parent_form.addRow("Photo:", parent_photo_layout)
        
        # ID Proof upload button
        self.id_proof_btn = QPushButton("Upload ID Proof")
        self.id_proof_label = QLabel("No ID proof selected")
        id_proof_layout = QHBoxLayout()
        id_proof_layout.addWidget(self.id_proof_btn)
        id_proof_layout.addWidget(self.id_proof_label)
        parent_form.addRow("ID Proof:", id_proof_layout)
        
        # OCR Text display
        self.ocr_text_label = QLabel("OCR Text will appear here")
        self.ocr_text_label.setWordWrap(True)
        # parent_form.addRow("Extracted Text:", self.ocr_text_label)
        
        self.parent_group.setLayout(parent_form)
        layout.addWidget(self.parent_group)
        
        # Button to register parent
        self.register_parent_btn = QPushButton("Register Parent/Guardian")
        self.register_parent_btn.setEnabled(False)
        self.register_parent_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        layout.addWidget(self.register_parent_btn)
        
        # Status message
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Connect signals
        self.child_photo_btn.clicked.connect(self.upload_child_photo)
        self.parent_photo_btn.clicked.connect(self.upload_parent_photo)
        self.id_proof_btn.clicked.connect(self.upload_id_proof)
        self.register_child_btn.clicked.connect(self.register_child)
        self.register_parent_btn.clicked.connect(self.register_parent)
    
    def upload_child_photo(self):
        """Handle child photo upload"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Child Photo", "", "Images (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.child_image_path = file_path
            self.child_photo_label.setText(os.path.basename(file_path))
    
    def upload_parent_photo(self):
        """Handle parent photo upload"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Parent Photo", "", "Images (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.parent_image_path = file_path
            self.parent_photo_label.setText(os.path.basename(file_path))
    
    def upload_id_proof(self):
        """Handle ID proof upload"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select ID Proof", "", "Images (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.id_proof_path = file_path
            self.id_proof_label.setText(os.path.basename(file_path))
            
            # Process the ID proof image with OCR
            self.process_id_proof()
    
    def process_id_proof(self):
        """Process ID proof image with OCR"""
        if not self.id_proof_path:
            return
        
        # Preprocess the image for better OCR accuracy
        preprocessed_path = self.ocr_processor.preprocess_image(self.id_proof_path)
        
        if preprocessed_path:
            # Extract text using OCR
            ocr_text = self.ocr_processor.process_image(preprocessed_path)
            
            # Display extracted text
            self.ocr_text_label.setText(ocr_text)
            
            # Enable register parent button if all required fields are filled
            self.check_parent_form()
    
    def register_child(self):
        """Register a new child"""
        # Validate inputs
        if not self.validate_child_form():
            return
        
        # Collect child data
        child_data = {
            "name": self.child_name_input.text(),
            "age": self.child_age_input.value(),
            "school": self.child_school_input.text(),
            "class": self.child_class_input.text(),
            "section": self.child_section_input.text()
        }
        
        # Add child to database
        self.current_child_id = self.db_manager.add_child(child_data, self.child_image_path)
        
        # Enable parent registration form
        self.parent_group.setEnabled(True)
        
        # Update status
        self.status_label.setText(f"Child {child_data['name']} registered successfully! Now add parent/guardian details.")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        
        # Disable child registration form and button
        self.register_child_btn.setEnabled(False)
        for i in range(child_form.rowCount()):
            child_form.itemAt(i, QFormLayout.FieldRole).widget().setEnabled(False)
    
    def register_parent(self):
        """Register a parent for the current child"""
        # Validate inputs
        if not self.validate_parent_form():
            return
        
        # Collect parent data
        parent_data = {
            "name": self.parent_name_input.text(),
            "age": self.parent_age_input.value(),
            "relationship": self.parent_relationship_input.currentText()
        }
        
        # Get OCR text
        ocr_text = self.ocr_text_label.text()
        
        # Add parent to child's record
        self.db_manager.add_parent(
            self.current_child_id, 
            parent_data, 
            self.parent_image_path, 
            self.id_proof_path,
            ocr_text
        )
        
        # Update status
        self.status_label.setText(f"Parent {parent_data['name']} registered successfully!")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        
        # Reset parent form for additional parents
        self.reset_parent_form()
    
    def validate_child_form(self):
        """Validate the child registration form"""
        if not self.child_name_input.text():
            QMessageBox.warning(self, "Validation Error", "Child name is required!")
            return False
        
        if not self.child_school_input.text():
            QMessageBox.warning(self, "Validation Error", "School name is required!")
            return False
        
        if not self.child_class_input.text():
            QMessageBox.warning(self, "Validation Error", "Class is required!")
            return False
        
        if not self.child_section_input.text():
            QMessageBox.warning(self, "Validation Error", "Section is required!")
            return False
        
        if not self.child_image_path:
            QMessageBox.warning(self, "Validation Error", "Child photo is required!")
            return False
        
        return True
    
    def validate_parent_form(self):
        """Validate the parent registration form"""
        if not self.parent_name_input.text():
            QMessageBox.warning(self, "Validation Error", "Parent name is required!")
            return False
        
        if not self.parent_image_path:
            QMessageBox.warning(self, "Validation Error", "Parent photo is required!")
            return False
        
        if not self.id_proof_path:
            QMessageBox.warning(self, "Validation Error", "ID proof is required!")
            return False
        
        return True
    
    def check_parent_form(self):
        """Check if parent form has all required fields filled"""
        if (self.parent_name_input.text() and 
            self.parent_image_path and 
            self.id_proof_path):
            self.register_parent_btn.setEnabled(True)
        else:
            self.register_parent_btn.setEnabled(False)
    
    def reset_parent_form(self):
        """Reset the parent form for registering another parent"""
        self.parent_name_input.clear()
        self.parent_age_input.setValue(30)
        self.parent_relationship_input.setCurrentIndex(0)
        self.parent_image_path = None
        self.id_proof_path = None
        self.parent_photo_label.setText("No photo selected")
        self.id_proof_label.setText("No ID proof selected")
        self.ocr_text_label.setText("OCR Text will appear here")
        self.register_parent_btn.setEnabled(False)


class CameraThread(QThread):
    """Thread for camera capture to avoid UI blocking"""
    frame_captured = pyqtSignal(object)
    
    def __init__(self, camera_id=0):
        super().__init__()
        self.camera_id = camera_id
        self.running = False
    
    def run(self):
        """Main thread method"""
        cap = cv2.VideoCapture(self.camera_id)
        self.running = True
        
        while self.running:
            ret, frame = cap.read()
            if ret:
                self.frame_captured.emit(frame)
            
            # Small delay to reduce CPU usage
            self.msleep(30)
        
        cap.release()
    
    def stop(self):
        """Stop the camera thread"""
        self.running = False
        self.wait()


class ScanCardScreen(QWidget):
    """Screen for scanning and verifying ID cards"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.ocr_processor = OCRProcessor()
        self.camera_thread = None
        self.current_frame = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Scan ID Card for Verification")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        layout.addSpacing(10)
        
        # Instructions
        instructions = QLabel(
            "Place the ID card in front of the camera and click 'Capture' to verify the visitor."
        )
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        layout.addSpacing(10)
        
        # Camera preview and results in a split view
        splitter = QSplitter(Qt.Horizontal)
        
        # Camera preview area
        camera_container = QWidget()
        camera_layout = QVBoxLayout(camera_container)
        
        self.camera_label = QLabel("Camera feed will appear here")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumSize(400, 300)
        self.camera_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        camera_layout.addWidget(self.camera_label)
        
        # Camera control buttons
        button_layout = QHBoxLayout()
        self.start_camera_btn = QPushButton("Start Camera")
        self.capture_btn = QPushButton("Capture ID")
        self.capture_btn.setEnabled(False)
        
        button_layout.addWidget(self.start_camera_btn)
        button_layout.addWidget(self.capture_btn)
        camera_layout.addLayout(button_layout)
        
        # OCR Text display
        self.ocr_text_label = QLabel("Extracted text will appear here")
        self.ocr_text_label.setWordWrap(True)
        self.ocr_text_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.ocr_text_label.setStyleSheet("background-color: #f9f9f9; padding: 10px; border: 1px solid #ddd;")
        self.ocr_text_label.setMinimumHeight(100)
        camera_layout.addWidget(QLabel("Extracted Text:"))
        camera_layout.addWidget(self.ocr_text_label)
        
        # Results area
        results_container = QWidget()
        results_layout = QVBoxLayout(results_container)
        
        results_title = QLabel("Verification Results")
        results_title.setFont(QFont("Arial", 14, QFont.Bold))
        results_title.setAlignment(Qt.AlignCenter)
        results_layout.addWidget(results_title)
        
        # Status indicator
        self.status_indicator = QLabel("Awaiting ID scan")
        self.status_indicator.setAlignment(Qt.AlignCenter)
        self.status_indicator.setStyleSheet("font-weight: bold; color: #7f8c8d;")
        results_layout.addWidget(self.status_indicator)
        
        # Child and parent information display
        self.info_container = QWidget()
        info_layout = QGridLayout(self.info_container)
        
        # Child information
        child_info_group = QGroupBox("Child Information")
        child_info_layout = QFormLayout()
        self.child_name_label = QLabel("—")
        self.child_age_label = QLabel("—")
        self.child_school_label = QLabel("—")
        self.child_class_label = QLabel("—")
        self.child_section_label = QLabel("—")
        self.child_image_label = QLabel()
        self.child_image_label.setAlignment(Qt.AlignCenter)
        self.child_image_label.setMinimumSize(150, 150)
        self.child_image_label.setStyleSheet("border: 1px solid #ccc;")
        
        child_info_layout.addRow("Name:", self.child_name_label)
        child_info_layout.addRow("Age:", self.child_age_label)
        child_info_layout.addRow("School:", self.child_school_label)
        child_info_layout.addRow("Class:", self.child_class_label)
        child_info_layout.addRow("Section:", self.child_section_label)
        child_info_layout.addRow("Photo:", self.child_image_label)
        child_info_group.setLayout(child_info_layout)
        
        # Parent information
        parent_info_group = QGroupBox("Parent Information")
        parent_info_layout = QFormLayout()
        self.parent_name_label = QLabel("—")
        self.parent_age_label = QLabel("—")
        self.parent_relationship_label = QLabel("—")
        self.parent_image_label = QLabel()
        self.parent_image_label.setAlignment(Qt.AlignCenter)
        self.parent_image_label.setMinimumSize(150, 150)
        self.parent_image_label.setStyleSheet("border: 1px solid #ccc;")
        
        parent_info_layout.addRow("Name:", self.parent_name_label)
        parent_info_layout.addRow("Age:", self.parent_age_label)
        parent_info_layout.addRow("Relationship:", self.parent_relationship_label)
        parent_info_layout.addRow("Photo:", self.parent_image_label)
        parent_info_group.setLayout(parent_info_layout)
        
        # Add child and parent info to grid layout
        info_layout.addWidget(child_info_group, 0, 0)
        info_layout.addWidget(parent_info_group, 0, 1)
        
        # Initially hide the info container
        self.info_container.setVisible(False)
        results_layout.addWidget(self.info_container)
        
        # Add camera and results to splitter
        splitter.addWidget(camera_container)
        splitter.addWidget(results_container)
        
        layout.addWidget(splitter, 1)  # 1 is the stretch factor
        
        self.setLayout(layout)
        
        # Connect signals
        self.start_camera_btn.clicked.connect(self.toggle_camera)
        self.capture_btn.clicked.connect(self.capture_id)
    
    def toggle_camera(self):
        """Start or stop the camera"""
        if self.camera_thread and self.camera_thread.running:
            # Stop the camera
            self.camera_thread.stop()
            self.start_camera_btn.setText("Start Camera")
            self.capture_btn.setEnabled(False)
            self.camera_label.setText("Camera feed will appear here")
        else:
            # Start the camera
            self.camera_thread = CameraThread()
            self.camera_thread.frame_captured.connect(self.update_frame)
            self.camera_thread.start()
            self.start_camera_btn.setText("Stop Camera")
            self.capture_btn.setEnabled(True)
    
    def update_frame(self, frame):
        """Update the camera preview with the current frame"""
        self.current_frame = frame
        
        # Convert frame to QImage for display
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        q_img = QImage(rgb_frame.data, w, h, ch * w, QImage.Format_RGB888)
        
        # Scale to fit the label while maintaining aspect ratio
        pixmap = QPixmap.fromImage(q_img)
        self.camera_label.setPixmap(pixmap.scaled(
            self.camera_label.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        ))
    
    def capture_id(self):
        """Capture the current frame and process it as ID"""
        if self.current_frame is None:
            QMessageBox.warning(self, "Error", "No camera feed available!")
            return
        
        # Save the current frame to a temporary file
        temp_file = save_temp_file(self.current_frame)
        
        # Process the image with OCR
        ocr_text = self.ocr_processor.process_image(temp_file)
        self.ocr_text_label.setText(ocr_text)
        
        # Find matching parent in database
        #TODO: function to find parent by OCR text
        # match = self.db_manager.find_parent_by_ocr_text(ocr_text)
        # def ocrrr(ocr_text):
        # def ocrrr(self, ocr_text: str, similarity_threshold: float = 0.5) -> Optional[Tuple[Dict, Dict]]:
        #     # data = self ._load_data()
        #     data = self.db_manager.get_all_children()
        
        #     for child in data:
        #         for parent in child["parents"]:
        #             stored_ocr_text = parent["ocr_text"]
                
        #             # Calculate similarity ratio
        #             similarity = difflib.SequenceMatcher(None, ocr_text, stored_ocr_text).ratio()
                
        #             if similarity >= similarity_threshold:
        #                 return (child, parent)
        
        #     return None
        # match = ocrrr(ocr_text)
        match = None
                
        #         # Calculate similarity ratio
        #         similarity = difflib.SequenceMatcher(None, ocr_text, stored_ocr_text).ratio()
        #         # print(f"Comparing {ocr_text} with {stored_ocr_text}: {similarity}")
        #         print(f"Similarity: {similarity}")
        #         if similarity >= 0.5:
        #             match = (child, parent)
        #             break
        def preprocess_text(text: str) -> str:
            """Preprocess text by removing extra spaces, special characters, and normalizing text."""
            text = text.lower()  # Convert to lowercase
            text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
            text = re.sub(r'[^a-z0-9]', '', text)  # Remove non-alphanumeric characters
            return text
        def check_similarity(ocr_text: str, stored_text: str, threshold: float = 0.3) -> bool:
            """Checks if the similarity between OCR text and stored text meets the threshold."""
            processed_ocr_text = preprocess_text(ocr_text)
            processed_stored_text = preprocess_text(stored_text)
            
            similarity = difflib.SequenceMatcher(None, processed_ocr_text, processed_stored_text).ratio()
            
            print(f"Similarity: {similarity:.2f}")  # Debugging output
            
            return similarity >= threshold
        
        data = self.db_manager.get_all_children()
        # print(data)
        for child in data:
            for parent in child["parents"]:
                stored_ocr_text = parent["ocr_text"]
                # print(stored_ocr_text)
                print(f"Comparing {ocr_text} with {stored_ocr_text}")
                if check_similarity(ocr_text, stored_ocr_text):
                    match = (child, parent)
                    break
                
        if match:
            child, parent = match
            self.display_match_info(child, parent)
            self.status_indicator.setText("VERIFICATION SUCCESSFUL")
            self.status_indicator.setStyleSheet("font-weight: bold; color: green; font-size: 16px;")
        else:
            self.clear_match_info()
            self.status_indicator.setText("NO MATCH FOUND")
            self.status_indicator.setStyleSheet("font-weight: bold; color: red; font-size: 16px;")
            self.info_container.setVisible(False)
            QMessageBox.warning(self, "Verification Failed", "No registered user found for this ID")
    
    def display_match_info(self, child, parent):
        """Display the matched child and parent information"""
        # Update child information
        self.child_name_label.setText(child["name"])
        self.child_age_label.setText(str(child["age"]))
        self.child_school_label.setText(child["school"])
        self.child_class_label.setText(child["class"])
        self.child_section_label.setText(child["section"])
        
        # Update parent information
        self.parent_name_label.setText(parent["name"])
        self.parent_age_label.setText(str(parent["age"]))
        self.parent_relationship_label.setText(parent["relationship"])
        
        # Load images
        if os.path.exists(child["image_path"]):
            child_pixmap = QPixmap(child["image_path"])
            self.child_image_label.setPixmap(crop_image_to_fit(child_pixmap, self.child_image_label.size()))
        
        if os.path.exists(parent["image_path"]):
            parent_pixmap = QPixmap(parent["image_path"])
            self.parent_image_label.setPixmap(crop_image_to_fit(parent_pixmap, self.parent_image_label.size()))
        
        # Show the info container
        self.info_container.setVisible(True)
    
    def clear_match_info(self):
        """Clear the match information display"""
        # Clear child information
        self.child_name_label.setText("—")
        self.child_age_label.setText("—")
        self.child_school_label.setText("—")
        self.child_class_label.setText("—")
        self.child_section_label.setText("—")
        self.child_image_label.clear()
        
        # Clear parent information
        self.parent_name_label.setText("—")
        self.parent_age_label.setText("—")
        self.parent_relationship_label.setText("—")
        self.parent_image_label.clear()
    
    def closeEvent(self, event):
        """Handle close event to ensure camera thread is stopped"""
        if self.camera_thread and self.camera_thread.running:
            self.camera_thread.stop()
        event.accept()
