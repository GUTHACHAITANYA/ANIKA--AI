import os
from PIL import Image, ImageEnhance

def preprocess_receipt_image(input_path: str, max_dimension: int = 2400) -> str:
    """
    Preprocesses uploaded receipt/bill image:
    - Scales down if image exceeds max_dimension to preserve memory.
    - Enhances contrast slightly for clearer OCR character segmentation.
    """
    try:
        with Image.open(input_path) as img:
            # Check dimensions
            width, height = img.size
            if max(width, height) > max_dimension:
                scale = max_dimension / float(max(width, height))
                new_size = (int(width * scale), int(height * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Enhance contrast slightly
            enhancer = ImageEnhance.Contrast(img)
            enhanced_img = enhancer.enhance(1.2)

            enhanced_img.save(input_path, quality=92, optimize=True)
            return input_path
    except Exception:
        # If PIL fails on PDF or unusual format, keep original file
        return input_path
