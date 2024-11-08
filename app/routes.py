import base64
from flask import Blueprint,Flask, redirect, url_for, send_file, request, jsonify, flash, render_template, current_app
import requests
from werkzeug.utils import secure_filename
import os
from app.optimalPath import ImageSeg, OptimalPathing
import cv2
from urllib.parse import quote

# Initialize the Blueprint
main = Blueprint('main', __name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app','static', 'UPLOADS') ## Create uploads folder inside static directory
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# Example route
@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html')


@main.route('/object_detection')
def object_detection():
    return render_template('tree_count.html')


@main.route('/object_segmentation')
def object_segmentation():
    return render_template('object_segmentation.html')



@main.route('/tree_species')
def tree_species():
    return render_template('tree_species.html')


@main.route('/optimal_path')
def optimal_path():
    return render_template('optimal_path.html')


@main.route('/historical_data')
def historical_data():
    return render_template('weather.html')


@main.route('/predict')
def predict():
    return render_template('predict.html')


@main.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return render_template('optimal_path.html')

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return render_template('optimal_path.html')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)


        # Initialize ImageSeg and process the image
        image_processor = ImageSeg(file_path)
        thresholded_image = image_processor.IsoGrayThresh()

        # Initialize OptimalPathing and compute the path
        optimal_path_processor = OptimalPathing(thresholded_image, file_path)
        processed_image = optimal_path_processor.ComputeAStar()

        # Save the processed image
        processed_image_path = os.path.join(upload_folder, 'processed_image.png')
        cv2.imwrite(processed_image_path, processed_image)

        # Convert the processed image to a base64 string
        with open(processed_image_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode('utf-8')

        # Return the processed image as a base64 string
        return jsonify({'processed_image': base64_image})

    return jsonify({'error': 'File processing failed'}), 400


@main.route('/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    if not city or len(city) < 3:
        return jsonify({'error': 'City parameter is required'}), 400

    # Use f-string to include the city parameter
    from urllib.parse import quote
    encoded_city = quote(city)
    api_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{encoded_city}?unitGroup=metric&key=VK8AZQ82WD8X8RZKZ9DBJEGVQ&contentType=json"

    print(f"Constructed API URL: {api_url}")  # Debugging line

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch data: {str(e)}'}), 500
