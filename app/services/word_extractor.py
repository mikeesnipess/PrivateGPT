from io import BytesIO
from docx import Document
import re

class TextVault:
    def __init__(self):
        pass

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
                    if chunk.strip():  # Check for non-empty chunks
                        vault_file.write(chunk.strip() + "\n\n")

            print(f'Vault.txt updated with new text. Total chunks: {len(chunks)}')
        except Exception as e:
            print(f"Error writing to vault: {e}")

def get_data_from_word(file_storage):
    # Use BytesIO to handle the FileStorage object
    doc_object = BytesIO(file_storage.read())
    doc_reader = Document(doc_object)
    data = ""

    for p in doc_reader.paragraphs:
        data += p.text + "\n"

    return data
