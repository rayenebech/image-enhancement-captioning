import cv2
import numpy as np
import webcolors
import math
from PIL import Image
import logging
from typing import Tuple, Optional

logger = logging.getLogger('ColorUtils')

class ColorDetector:
    def __init__(self, n_clusters: int = 5, quant_size: int = 16):
        self.n_clusters = n_clusters
        self.quant_size = quant_size
        
    def get_dominant_color(self, image: Image.Image) -> Optional[Tuple[int, int, int]]:
        """Extract dominant color from PIL Image."""
        try:
            # Convert to RGB and resize for faster processing
            image = image.convert('RGB').resize((150, 150))
            pixels = np.float32(list(image.getdata()))
            
            # Use k-means clustering to find dominant colors
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
            _, labels, palette = cv2.kmeans(
                pixels, 
                self.n_clusters, 
                None, 
                criteria, 
                10, 
                cv2.KMEANS_RANDOM_CENTERS
            )
            
            # Get the most dominant color
            dominant_color = tuple(map(int, palette[np.argmax(np.unique(labels, return_counts=True)[1])]))
            logger.info(f"Successfully extracted dominant color: {dominant_color}")
            return dominant_color
            
        except Exception as e:
            logger.error(f"Error extracting dominant color: {e}")
            return None
    
    def quantize_color(self, rgb_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Quantize RGB color values."""
        try:
            return tuple(int(round(c/(256/self.quant_size))*(256/self.quant_size)) 
                        for c in rgb_color)
        except Exception as e:
            logger.error(f"Error quantizing color: {e}")
            return rgb_color
    
    def rgb_to_color_name(self, rgb_color: Tuple[int, int, int]) -> str:
        """Convert RGB color to nearest CSS3 color name."""
        try:
            color_distances = {}
            for color_name in webcolors.names("css3"):
                r, g, b = webcolors.name_to_rgb(color_name)
                # Use weighted Euclidean distance for better human perception
                distance = math.sqrt(2*(r-rgb_color[0])**2 + 
                                  4*(g-rgb_color[1])**2 + 
                                  (b-rgb_color[2])**2)
                color_distances[distance] = color_name
            
            nearest_color = min(color_distances.items())[1]
            logger.info(f"Found nearest color name: {nearest_color}")
            return nearest_color
            
        except Exception as e:
            logger.error(f"Error converting RGB to color name: {e}")
            return "white"  # Safe fallback
    
    def get_color_name(self, image: Image.Image) -> str:
        """Get color name from image with fallback handling."""
        try:
            dominant_color = self.get_dominant_color(image)
            if dominant_color is None:
                logger.warning("Failed to get dominant color, using fallback")
                return "white"
                
            quantized_color = self.quantize_color(dominant_color)
            color_name = self.rgb_to_color_name(quantized_color)
            
            return color_name
            
        except Exception as e:
            logger.error(f"Error in get_color_name: {e}")
            return "white"  # Safe fallback