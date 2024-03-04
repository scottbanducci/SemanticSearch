from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, session
from dotenv import load_dotenv
import pathlib
import os
import glob
from werkzeug.utils import secure_filename
from pdf_to_text import convert_pdf_folder_to_text
from text_to_vec import generate_embeddings
from find_similarity import find_similar_embeddings



# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = r"data\pdfs"
app.secret_key = os.environ.get('SECRET_KEY', 'default_key_as_fallback')  # Needed for flash messages

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Pass `success=True` to the template to show the success message and "OK" button
            return render_template('upload.html', success=True)
    # Pass `success=False` explicitly if needed, or simply don't pass it as Flask templates treat non-existent variables as falsy
    return render_template('upload.html', success=False)


@app.route('/convert-pdfs', methods=['GET'])
def convert_pdfs():
    pdfs_path = r'data\pdfs'
    text_files_path = r'data\text_files'
    
    # List all PDFs in the pdfs_path
    pdf_files = [f for f in os.listdir(pdfs_path) if f.endswith('.pdf')]
    
    # List all directories in the text_files_path
    directories = [d for d in os.listdir(text_files_path) if os.path.isdir(os.path.join(text_files_path, d))]
    
    return render_template('convert_pdfs.html', pdf_files=pdf_files, directories=directories)

@app.route("/convert-pdfs-action", methods=['POST'])
def convert_pdfs_action():
    selected_pdfs = request.form.getlist('pdfs[]')  # Get selected PDFs from the form
    pdfs_path = r"data\pdfs"
    text_files_path = r"data\text_files"

    try:
        # Pass the selected PDFs and paths to the conversion function
        converted_files, skipped_files = convert_pdf_folder_to_text(text_files_path, pdfs_path, selected_pdfs)
        session['converted_files'] = converted_files
        session['skipped_files'] = skipped_files  # Store skipped files in session
        print(session['skipped_files'])
        flash('PDFs conversion process completed.')
    except Exception as e:
        flash(f'Error: {e}')
    return redirect(url_for('convert_pdfs_results'))

@app.route("/convert-pdfs-results")
def convert_pdfs_results():
    converted_files = session.get('converted_files', [])
    skipped_files = session.get('skipped_files', [])  # Retrieve skipped files from session
    return render_template('convert_pdfs_results.html', files=converted_files, skipped_files=skipped_files)

@app.route("/generate-embeddings", methods=['GET'])
def generate_embeddings_route():
    try:
        generate_embeddings()
        flash('Embeddings generated successfully.')
        return render_template('message.html', redirect_url=url_for('home'))
    except Exception as e:
        flash(f'Error: {e}')
        return render_template('message.html', redirect_url=url_for('home'))
    return redirect(url_for('home'))

@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        num_results = int(request.form.get('num_results', 5))
        results = find_similar_embeddings(query, num_results)
        return render_template('search_results.html', query=query, results=results)
    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True)