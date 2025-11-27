#!/usr/bin/env python3
"""
Media Processor
Image compression, thumbnail generation, responsive image sizes
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class MediaProcessor:
    """
    Media Processor
    Handles image compression, thumbnail generation, and responsive sizes
    """
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize media processor
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir or Path(".")
        self.media_dir = self.base_dir / "data" / "media"
        self.media_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnails_dir = self.media_dir / "thumbnails"
        self.thumbnails_dir.mkdir(parents=True, exist_ok=True)
    
    def process_image(
        self,
        image_path: Path,
        max_width: int = 1920,
        max_height: int = 1080,
        quality: int = 85
    ) -> Dict[str, Any]:
        """
        Process and compress an image
        
        Args:
            image_path: Path to source image
            max_width: Maximum width
            max_height: Maximum height
            quality: JPEG quality (1-100)
            
        Returns:
            Dictionary with processed image info
        """
        # Check if PIL/Pillow is available
        try:
            from PIL import Image
        except ImportError:
            # If PIL not available, return original file info
            return {
                "original_path": str(image_path),
                "processed_path": str(image_path),
                "width": 0,
                "height": 0,
                "size": image_path.stat().st_size if image_path.exists() else 0,
                "format": image_path.suffix.lower(),
                "compressed": False
            }
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            # Open and process image
            with Image.open(image_path) as img:
                original_size = image_path.stat().st_size
                original_format = img.format or 'JPEG'
                
                # Resize if needed
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Convert to RGB if needed (for JPEG)
                if original_format == 'JPEG' and img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save processed image
                processed_path = self.media_dir / f"processed_{image_path.name}"
                
                if original_format == 'JPEG' or original_format == 'JPG':
                    img.save(processed_path, 'JPEG', quality=quality, optimize=True)
                elif original_format == 'PNG':
                    img.save(processed_path, 'PNG', optimize=True)
                else:
                    # Convert to JPEG
                    img = img.convert('RGB')
                    processed_path = processed_path.with_suffix('.jpg')
                    img.save(processed_path, 'JPEG', quality=quality, optimize=True)
                
                processed_size = processed_path.stat().st_size
                
                return {
                    "original_path": str(image_path),
                    "processed_path": str(processed_path),
                    "width": img.width,
                    "height": img.height,
                    "size": processed_size,
                    "original_size": original_size,
                    "compression_ratio": round((1 - processed_size / original_size) * 100, 2) if original_size > 0 else 0,
                    "format": processed_path.suffix.lower(),
                    "compressed": processed_size < original_size
                }
        except Exception as e:
            # If processing fails, return original
            return {
                "original_path": str(image_path),
                "processed_path": str(image_path),
                "width": 0,
                "height": 0,
                "size": image_path.stat().st_size if image_path.exists() else 0,
                "format": image_path.suffix.lower(),
                "compressed": False,
                "error": str(e)
            }
    
    def generate_thumbnail(
        self,
        image_path: Path,
        size: Tuple[int, int] = (200, 200),
        quality: int = 75
    ) -> Optional[Path]:
        """
        Generate thumbnail for an image
        
        Args:
            image_path: Path to source image
            size: Thumbnail size (width, height)
            quality: JPEG quality
            
        Returns:
            Path to thumbnail or None
        """
        try:
            from PIL import Image
        except ImportError:
            return None
        
        if not image_path.exists():
            return None
        
        try:
            with Image.open(image_path) as img:
                # Create thumbnail
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save thumbnail
                thumbnail_name = f"thumb_{image_path.stem}.jpg"
                thumbnail_path = self.thumbnails_dir / thumbnail_name
                img.save(thumbnail_path, 'JPEG', quality=quality, optimize=True)
                
                return thumbnail_path
        except Exception:
            return None
    
    def get_responsive_sizes(
        self,
        image_path: Path,
        sizes: list = None
    ) -> Dict[str, Any]:
        """
        Generate responsive image sizes
        
        Args:
            image_path: Path to source image
            sizes: List of (width, height) tuples
            
        Returns:
            Dictionary with responsive image info
        """
        if sizes is None:
            sizes = [(320, 240), (640, 480), (1280, 960), (1920, 1080)]
        
        responsive_images = {}
        
        for width, height in sizes:
            try:
                processed = self.process_image(image_path, max_width=width, max_height=height)
                responsive_images[f"{width}x{height}"] = processed
            except Exception:
                pass
        
        return {
            "original": str(image_path),
            "responsive": responsive_images
        }
    
    def validate_media_file(
        self,
        file_path: Path,
        max_size_mb: int = 10,
        allowed_types: list = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate media file
        
        Args:
            file_path: Path to file
            max_size_mb: Maximum file size in MB
            allowed_types: List of allowed file extensions
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if allowed_types is None:
            allowed_types = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.mov', '.webm']
        
        if not file_path.exists():
            return False, "File not found"
        
        # Check file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return False, f"File size ({file_size_mb:.2f}MB) exceeds maximum ({max_size_mb}MB)"
        
        # Check file type
        file_ext = file_path.suffix.lower()
        if file_ext not in allowed_types:
            return False, f"File type {file_ext} not allowed. Allowed types: {', '.join(allowed_types)}"
        
        return True, None

