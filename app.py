import os
import io
import zipfile
from flask import Flask, render_template, request, send_file
from PIL import Image

app = Flask(__name__)

# Limit upload size to 4MB (Vercel Limit)
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

# Allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_webp(file_storage):
    """Converts a single FileStorage object to WebP bytes."""
    image = Image.open(file_storage)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGBA")
    else:
        image = image.convert("RGB")
        
    output = io.BytesIO()
    image.save(output, format="WEBP", quality=90)
    output.seek(0)
    return output

@app.route('/')
def index():
    return render_template('index.html')

# --- REPLACE THE '/convert' ROUTE ---
@app.route('/convert', methods=['POST'])
def convert():
    try:
        # 1. Check if file part exists
        if 'images' not in request.files:
            return render_template('index.html', error="Error: No file part found.")

        files = request.files.getlist('images')

        # 2. Check if files were selected
        if not files or files[0].filename == '':
            return render_template('index.html', error="Error: No files selected.")

        # 3. Validate File Types
        for file in files:
            if not allowed_file(file.filename):
                return render_template('index.html', error="Error: Invalid file format. Only JPG and PNG are allowed.")

        # --- Conversion Logic (Same as before) ---
        if len(files) == 1:
            file = files[0]
            webp_data = convert_to_webp(file)
            filename = os.path.splitext(file.filename)[0] + ".webp"
            return send_file(webp_data, mimetype='image/webp', as_attachment=True, download_name=filename)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file in files:
                webp_data = convert_to_webp(file)
                filename = os.path.splitext(file.filename)[0] + ".webp"
                zip_file.writestr(filename, webp_data.read())
        
        zip_buffer.seek(0)
        return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name="converted_images.zip")
    
    except Exception as e:
        # Catch-all for processing errors
        return render_template('index.html', error="Error: Unable to process files. Please try again.")

if __name__ == '__main__':
    app.run(debug=True)