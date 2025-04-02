#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR Processing module for Child Safety Protection App
Handles OCR processing of ID documents
"""

import os
import pytesseract
import cv2
from PIL import Image
from typing import Optional

class OCRProcessor:
    """Class for handling OCR operations"""
    
    def __init__(self):
        """Initialize the OCR processor"""
        # Ensure Tesseract is available
        try:
            pytesseract.get_tesseract_version()
        except pytesseract.TesseractNotFoundError:
            print("ERROR: Tesseract OCR is not installed or not in PATH")
            print("Please install Tesseract OCR and ensure it's in your system PATH")
    
    def process_image(self, image_path: str) -> str:
        """
        Process an image and extract text using OCR
        
        Args:
            image_path: Path to the image file
        
        Returns:
            Extracted text from the image
        """
        try:
            # Load image
            image = Image.open(image_path)
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(image)
            
            return text.strip()
        except Exception as e:
            print(f"Error during OCR processing: {e}")
            return ""
    
    def process_image_from_cv(self, cv_image) -> str:
        """
        Process an OpenCV image and extract text using OCR
        
        Args:
            cv_image: OpenCV image (numpy array)
        
        Returns:
            Extracted text from the image
        """
        try:
            # Convert the OpenCV image to PIL format
            pil_image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(pil_image)
            
            return text.strip()
        except Exception as e:
            print(f"Error during OCR processing: {e}")
            return ""
    
    def preprocess_image(self, image_path: str) -> Optional[str]:
        """
        Preprocess an image to improve OCR accuracy
        
        Args:
            image_path: Path to the image file
        
        Returns:
            Path to the preprocessed image
        """
        try:
            # Read the image
            img = cv2.imread(image_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding to get a binary image
            _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Save the preprocessed image
            preprocessed_path = f"{os.path.splitext(image_path)[0]}_preprocessed.jpg"
            cv2.imwrite(preprocessed_path, binary)
            
            return preprocessed_path
        except Exception as e:
            print(f"Error during image preprocessing: {e}")
            return None
