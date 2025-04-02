#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility functions for Child Safety Protection App
"""

import os
import cv2
import time
import tempfile
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QRect, QSize

def save_temp_file(cv_image):
    """
    Save a temporary file from an OpenCV image
    
    Args:
        cv_image: OpenCV image (numpy array)
    
    Returns:
        Path to the temporary file
    """
    # Create a temporary file
    temp_dir = tempfile.gettempdir()
    temp_file = os.path.join(temp_dir, f"ocr_image_{int(time.time())}.jpg")
    
    # Save the image to the temporary file
    cv2.imwrite(temp_file, cv_image)
    
    return temp_file

def crop_image_to_fit(pixmap, target_size):
    """
    Crop and scale an image to fit a target size while maintaining aspect ratio
    
    Args:
        pixmap: QPixmap to crop and scale
        target_size: QSize target dimensions
    
    Returns:
        Cropped and scaled QPixmap
    """
    if pixmap.isNull():
        return pixmap
    
    # Scale the pixmap while maintaining aspect ratio
    scaled_pixmap = pixmap.scaled(
        target_size,
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation
    )
    
    # If the scaled pixmap is smaller than the target size,
    # we can just return it without cropping
    if scaled_pixmap.width() <= target_size.width() and scaled_pixmap.height() <= target_size.height():
        return scaled_pixmap
    
    # Otherwise, create a new pixmap of the target size and center the scaled pixmap
    result = QPixmap(target_size)
    result.fill(Qt.transparent)
    
    painter = QPainter(result)
    
    # Calculate position to center the scaled pixmap
    x = (target_size.width() - scaled_pixmap.width()) // 2
    y = (target_size.height() - scaled_pixmap.height()) // 2
    
    # Draw the scaled pixmap at the calculated position
    painter.drawPixmap(x, y, scaled_pixmap)
    painter.end()
    
    return result

def ensure_directory_exists(directory):
    """
    Ensure that a directory exists, create it if it doesn't
    
    Args:
        directory: Path to the directory
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
