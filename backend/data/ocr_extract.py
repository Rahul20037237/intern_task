import re
import logging
from typing import Tuple, List
from PIL import Image
import pytesseract
import pdfplumber

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# Tesseract path — change if needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class OCRTextExtractor:
    @staticmethod
    def clean_text(text: str) -> str:
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\x0c', '', text)
        return text

    @staticmethod
    def ocr_pdf(file_path: str) -> List[Tuple[int, str]]:
        results = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    image = page.to_image(resolution=300).original.convert("RGB")
                    text = pytesseract.image_to_string(image)
                    results.append((page_num, OCRTextExtractor.clean_text(text)))
        except Exception as e:
            logger.error(f"OCR failed for PDF {file_path}: {e}")
        return results

    @staticmethod
    def ocr_image(file_path: str) -> List[Tuple[int, str]]:
        try:
            image = Image.open(file_path).convert("RGB")
            text = pytesseract.image_to_string(image)
            return [(1, OCRTextExtractor.clean_text(text))]
        except Exception as e:
            logger.error(f"OCR failed for image {file_path}: {e}")
            return []
