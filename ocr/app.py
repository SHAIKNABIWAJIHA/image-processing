from flask import Flask, request, render_template, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import os
import pytesseract
from PIL import Image
from collections import Counter
import matplotlib.pyplot as plt
import io
# Initializing Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
def perform_ocr(image_path):
    # Using pytesseract to do OCR on the image
    text = pytesseract.image_to_string(Image.open(image_path))
    words = text.split()
    return Counter(words)
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Checking if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return redirect(url_for('report', filename=filename))
    return render_template('upload.html')
@app.route('/report/<filename>')
def report(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    word_counts = perform_ocr(filepath)
    # Creating the bar chart with matplotlib
    fig, ax = plt.subplots()
    words, counts = zip(*word_counts.items())
    ax.barh(words, counts, color='skyblue')
    ax.set_xlabel('Counts')
    ax.set_ylabel('Words')
    ax.set_title('Word Count Report')
    # Setting the background color of the plot
    fig.patch.set_facecolor('lightgrey')
    ax.set_facecolor('whitesmoke')
    plt.tight_layout()
    # Save the plot to a BytesIO object
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png', facecolor=fig.get_facecolor())
    img_io.seek(0)
    # Save the plot as a PNG file
    plot_path = os.path.join(app.config['UPLOAD_FOLDER'], 'plot.png')
    plt.savefig(plot_path, format='png', facecolor=fig.get_facecolor())
    # Render the HTML template with the report details
    return render_template('report.html', word_counts=word_counts, plot_path=url_for('static', filename=f'uploads/plot.png'))
if __name__ == '__main__':
    app.run(debug=True)