from flask import request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from app import app
from app.services.image_reader import ImageReader
from app.services.pdf_extractor import extract_text_from_pdf, TextVault
from app.services.word_extractor import get_data_from_word
from app.services.OllamaChatService import OllamaChatService
from app.forms import UploadFileForm
from app.enums_local import OS

# Initialize OllamaChatService
service = OllamaChatService()

@app.route('/', methods=['GET', 'POST'])
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadFileForm()
    if form.validate_on_submit():
        files = request.files.getlist('file')  # Get all uploaded files
        text_vault = TextVault()

        for file in files:
            if file:
                filename = secure_filename(file.filename)
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    ir = ImageReader(OS.WINDOWS)  # Ensure OS setting is correct
                    text = ir.extract_text(file, lang='ron')
                    text_vault.add_text(text)
                elif filename.lower().endswith('.pdf'):
                    extracted_text = extract_text_from_pdf(file)
                    text_vault.add_text(extracted_text)
                elif filename.lower().endswith('.docx'):
                    extracted_text = get_data_from_word(file)
                    text_vault.add_text(extracted_text)
                else:
                    print(f"Unsupported file type: {filename}")

        # Save the vault content to a file
        text_vault.save_text_to_vault(text_vault.get_all_text())

        # Redirect to chat interface
        return redirect(url_for('chat'))

    return render_template('upload.html', form=form)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    response = ""

    if request.method == 'POST':
        user_input = request.form.get('query', '').strip()
        if user_input.lower() == 'quit':
            return redirect(url_for('upload'))
        if user_input:
            response = service.chat(user_input)
        return render_template('chat.html', response=response)

    return render_template('chat.html', response=response)
