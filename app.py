import os
import io
import zipfile
from flask import Flask, render_template, request, send_file
from PIL import Image

app = Flask(__name__)

def convert_to_webp(file_storage):
    """Converts a single FileStorage object to WebP bytes."""
    image = Image.open(file_storage)
    # Convert to RGB if image is RGBA/P to ensure compatibility
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

@app.route('/convert', methods=['POST'])
def convert():
    if 'images' not in request.files:
        return "No files uploaded", 400

    files = request.files.getlist('images')
    if not files or files[0].filename == '':
        return "No selected files", 400

    # Single File Case
    if len(files) == 1:
        file = files[0]
        webp_data = convert_to_webp(file)
        filename = os.path.splitext(file.filename)[0] + ".webp"
        return send_file(webp_data, mimetype='image/webp', as_attachment=True, download_name=filename)

    # Bulk Case (ZIP)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file in files:
            webp_data = convert_to_webp(file)
            filename = os.path.splitext(file.filename)[0] + ".webp"
            zip_file.writestr(filename, webp_data.read())
    
    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name="converted_images.zip")

if __name__ == '__main__':
    app.run(debug=True, port=5000)