from PIL import Image
from pytesseract import pytesseract
import re
import os
from app.enums_local  import OS


class ImageReader:
    def __init__(self, os: OS):
        if os == OS.WINDOWS:
            windows_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            pytesseract.tesseract_cmd = windows_path
            print('Running on Windows\n')

    def extract_text(self, image_path: str, lang: str = 'ron') -> str:
        try:
            img = Image.open(image_path)
            extracted_text = pytesseract.image_to_string(img, lang=lang)
            print(f"Extracted text: {extracted_text}")  # Add this line for debugging
            return extracted_text
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""

    def add_text_to_vault(self, extracted_text: str, vault_path: str = 'vault.txt'):
        if not extracted_text:
            print("No text extracted.")
            return

        try:
            max_chunk_size = 1000  # Maximum size of each chunk in characters
            chunks = self.split_text_into_chunks(extracted_text, max_chunk_size)
            print(f"Chunks: {chunks}")  # Add this line for debugging

            with open(vault_path, 'a', encoding='utf-8') as vault_file:
                for chunk in chunks:
                    vault_file.write(chunk.strip() + "\n\n")

            print(f'Vault.txt updated with new text. Total chunks: {len(chunks)}')
        except Exception as e:
            print(f"Error writing to vault: {e}")

    def split_text_into_chunks(self, text: str, max_chunk_size: int) -> list:
        text = re.sub(r'\s+', ' ', text).strip()
        sentences = re.split(r'(?<=[.!?]) +', text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 < max_chunk_size:
                current_chunk += (sentence + " ").strip()
            else:
                chunks.append(current_chunk)
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk)

        return chunks
