#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database management module for Child Safety Protection App
Handles data storage, retrieval, and matching logic
"""

import json
import os
import time
import shutil
from typing import Dict, List, Any, Optional, Tuple
import difflib

class DatabaseManager:
    """Class for managing application data and storage"""
    
    def __init__(self, data_file: str = "data/users.json"):
        """
        Initialize the database manager
        
        Args:
            data_file: Path to the JSON data file
        """
        self.data_file = data_file
        self._ensure_data_file_exists()
    
    def _ensure_data_file_exists(self):
        """Ensure that the data file exists, create if it doesn't"""
        if not os.path.exists(os.path.dirname(self.data_file)):
            os.makedirs(os.path.dirname(self.data_file))
        
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump({"children": []}, f)
    
    def _load_data(self) -> Dict:
        """Load data from the JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # Return empty data structure if file is corrupt or missing
            return {"children": []}
    
    def _save_data(self, data: Dict):
        """Save data to the JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_child(self, child_data: Dict, child_image_path: str) -> str:
        """
        Add a new child to the database
        
        Args:
            child_data: Dictionary containing child's details
            child_image_path: Path to the child's image
        
        Returns:
            Child ID (used for folder name)
        """
        data = self._load_data()
        
        # Generate unique ID for the child
        child_id = f"{int(time.time())}_{child_data['name'].replace(' ', '_')}"
        
        # Create directory for this child
        child_dir = f"images/{child_id}"
        os.makedirs(child_dir, exist_ok=True)
        
        # Copy child image to the directory
        image_ext = os.path.splitext(child_image_path)[1]
        child_image_dest = f"{child_dir}/child{image_ext}"
        shutil.copy(child_image_path, child_image_dest)
        
        # Add child to database
        child_entry = {
            "id": child_id,
            "name": child_data["name"],
            "age": child_data["age"],
            "school": child_data["school"],
            "class": child_data["class"],
            "section": child_data["section"],
            "image_path": child_image_dest,
            "parents": []
        }
        
        data["children"].append(child_entry)
        self._save_data(data)
        
        return child_id
    
    def add_parent(self, child_id: str, parent_data: Dict, parent_image_path: str, id_proof_path: str, ocr_text: str) -> None:
        """
        Add a parent to a child's record
        
        Args:
            child_id: ID of the child
            parent_data: Dictionary containing parent's details
            parent_image_path: Path to the parent's image
            id_proof_path: Path to the parent's ID proof
            ocr_text: Extracted text from the ID proof
        """
        data = self._load_data()
        
        # Find the child by ID
        for child in data["children"]:
            if child["id"] == child_id:
                child_dir = f"images/{child_id}"
                
                # Copy parent image to the child's directory
                parent_image_ext = os.path.splitext(parent_image_path)[1]
                parent_image_dest = f"{child_dir}/parent_{parent_data['name'].replace(' ', '_')}{parent_image_ext}"
                shutil.copy(parent_image_path, parent_image_dest)
                
                # Copy ID proof to the child's directory
                id_proof_ext = os.path.splitext(id_proof_path)[1]
                id_proof_dest = f"{child_dir}/id_proof_{parent_data['name'].replace(' ', '_')}{id_proof_ext}"
                shutil.copy(id_proof_path, id_proof_dest)
                
                # Add parent to child's record
                parent_entry = {
                    "name": parent_data["name"],
                    "age": parent_data["age"],
                    "relationship": parent_data["relationship"],
                    "image_path": parent_image_dest,
                    "id_proof_path": id_proof_dest,
                    "ocr_text": ocr_text
                }
                
                child["parents"].append(parent_entry)
                self._save_data(data)
                break
    
    def find_parent_by_ocr_text(self, ocr_text: str, similarity_threshold: float = 0.5) -> Optional[Tuple[Dict, Dict]]:
        """
        Find a parent based on OCR text from an ID
        
        Args:
            ocr_text: The extracted text from the ID
            similarity_threshold: Minimum similarity ratio to consider a match
        
        Returns:
            Tuple of (child_data, parent_data) if match found, None otherwise
        """
        data = self._load_data()
        
        for child in data["children"]:
            for parent in child["parents"]:
                stored_ocr_text = parent["ocr_text"]
                
                # Calculate similarity ratio
                similarity = difflib.SequenceMatcher(None, ocr_text, stored_ocr_text).ratio()
                
                if similarity >= similarity_threshold:
                    return (child, parent)
        
        return None
    
    def get_all_children(self) -> List[Dict]:
        """
        Get all children from the database
        
        Returns:
            List of all children records
        """
        data = self._load_data()
        return data["children"]
