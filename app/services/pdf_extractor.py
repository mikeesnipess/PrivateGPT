import re
from io import BytesIO
from docx import Document
import PyPDF2

class TextVault:
    def __init__(self):
        self.texts = []

    def add_text(self, text):
        """Add text to the vault."""
        self.texts.append(text)

    def get_all_text(self):
        """Retrieve all text from the vault."""
        return "\n".join(self.texts)

    def split_text_into_chunks(self, text: str, max_chunk_size: int) -> list:
        """Split text into chunks of a maximum size."""
        text = re.sub(r'\s+', ' ', text).strip()
        sentences = re.split(r'(?<=[.!?]) +', text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= max_chunk_size:
                current_chunk += (sentence + " ").strip()
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def save_text_to_vault(self, extracted_text: str, vault_path: str = 'vault.txt'):
        """Save extracted text to a file in chunks."""
        if not extracted_text:
            print("No text extracted.")
            return

        try:
            max_chunk_size = 1500  # Maximum size of each chunk in characters
            chunks = self.split_text_into_chunks(extracted_text, max_chunk_size)
            print(f"Chunks: {chunks}")  # Debugging output

            with open(vault_path, 'a', encoding='utf-8') as vault_file:
                for chunk in chunks:
                    if chunk.strip():  # Check for non-empty chunks
                        vault_file.write(chunk.strip() + "\n\n")

            print(f'Vault.txt updated with new text. Total chunks: {len(chunks)}')
        except Exception as e:
            print(f"Error writing to vault: {e}")

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from a PDF file."""
    pdf_text = []

    try:
        reader = PyPDF2.PdfReader(pdf_file)

        for page in reader.pages:
            content = page.extract_text()
            if content:
                pdf_text.append(content)
            else:
                print("Warning: Page has no extractable text.")
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")

    return "\n".join(pdf_text)
