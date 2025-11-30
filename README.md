# WebP Converter Studio

A modern, web-based tool to convert images to WebP format in bulk. Built with Python (Flask) and Pillow, featuring a drag-and-drop interface.

## Features

* **Bulk Conversion:** Upload multiple images at once.
* **Smart Output:** Downloads single files directly or zips multiple files automatically.
* **Modern UI:** Clean, pastel-themed interface with drag-and-drop functionality.
* **High Quality:** Converts to WebP with 90% quality retention.

## Tech Stack

* **Backend:** Python 3, Flask
* **Processing:** Pillow (PIL)
* **Frontend:** HTML5, CSS3 (Flexbox/Grid), Vanilla JS

## Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/permadisatya/image-to-webp-converter.git](https://github.com/permadisatya/image-to-webp-converter.git)
    cd image-to-webp-converter
    ```

2.  **Set up a virtual environment (Optional but recommended)**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the application**
    ```bash
    python app.py
    ```

2.  **Open in browser**
    Navigate to `http://127.0.0.1:5000`

3.  **Convert images**
    * Drag and drop images into the drop zone.
    * Click "Convert Files" to process and download.

## Project Structure

```text
/converter_app
    ├── app.py              # Main Flask application
    ├── requirements.txt    # Python dependencies
    ├── templates/
    │   └── index.html      # Frontend interface
    └── README.md