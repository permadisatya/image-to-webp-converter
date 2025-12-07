import os
import io
import zipfile
import logging
from flask import Flask, render_template, request, send_file
from PIL import Image
from PIL import Image, UnidentifiedImageError

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Limit upload size to 4MB (Vercel Limit)
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

# Allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_webp(file_storage):
    """Converts a single FileStorage object to WebP bytes."""
    # Reset file pointer to start
    file_storage.seek(0)
    
    try:
        image = Image.open(file_storage)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")
            
        output = io.BytesIO()
        image.save(output, format="WEBP", quality=90)
        output.seek(0)
        return output
    except Exception as e:
        logging.error(f"Error in convert_to_webp: {str(e)}")
        raise

# Global Error Handlers
@app.errorhandler(403)
def forbidden(e):
    logging.error(f"403 Forbidden: {e}")
    return render_template('index.html', error="Error: Access Forbidden (403). Check file permissions or CORS settings."), 403

@app.errorhandler(404)
def not_found(e):
    logging.error(f"404 Not Found: {e}")
    return render_template('index.html', error="Error: Page not found (404)."), 404

@app.errorhandler(405)
def method_not_allowed(e):
    logging.error(f"405 Method Not Allowed: {e}")
    return render_template('index.html', error="Error: Method not allowed. Use POST for /convert."), 405

@app.errorhandler(413)
def too_large(e):
    logging.error(f"413 Payload Too Large: {e}")
    return render_template('index.html', error="Error: File too large. Maximum 4MB allowed."), 413

@app.errorhandler(500)
def server_error(e):
    logging.exception(f"500 Server Error: {e}")
    return render_template('index.html', error="Error: Server error occurred."), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None

    if request.method == 'POST':
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

            # --- Conversion Logic ---
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
            
            # ... inside the index() function, at the bottom ...

            zip_buffer.seek(0)
            return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name="converted_images.zip")
        
        # --- NEW: Specific PIL Error Handling ---
        except UnidentifiedImageError:
            return render_template('index.html', error="Error: One or more files are corrupted or unreadable.")
            
        # --- EXISTING: Generic Error Handling ---
        except Exception as e:
            print(e) # Optional: prints error to Vercel logs for debugging
            return render_template('index.html', error="Error: Unable to process files. Please try again.")

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)