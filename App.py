from flask import Flask, render_template_string, request
from inference_sdk import InferenceHTTPClient
import supervision as sv
import cv2

app = Flask(__name__)


def predict(image_path):
    CLIENT = InferenceHTTPClient(
        api_url="https://serverless.roboflow.com",
        api_key="Your_API_Key_Here"
    )

    result = CLIENT.infer(image_path, model_id="cmpe258-finalversion/1")
    print(result)


    labels = [item["class"] for item in result["predictions"]]

    print(labels)

    detections = sv.Detections.from_inference(result)
    label_annotator = sv.LabelAnnotator()
    bounding_box_annotator = sv.BoxAnnotator()


    image = cv2.imread(image_path)

    annotated_image = bounding_box_annotator.annotate(
        scene=image, detections=detections)
    annotated_image = label_annotator.annotate(
        scene=annotated_image, detections=detections, labels=labels)

    #matplot shit
    # newimg = sv.plot_image(image=annotated_image, size=(16, 16))


    #saving the image itself using opencv
    cv2.imwrite("uploads/Annotated.png", annotated_image)

    return "/uploads/Annotated.png"


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Basic HTML form
HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Image Upload</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f3f4f6;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-top: 40px;
        }

        h1 {
            color: #333;
            margin-bottom: 20px;
        }

        form {
            background-color: #fff;
            padding: 20px 30px;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            gap: 12px;
            align-items: center;
        }

        input[type="file"] {
            font-size: 16px;
        }

        input[type="submit"] {
            padding: 10px 20px;
            background-color: #2563eb;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
        }

        input[type="submit"]:hover {
            background-color: #1d4ed8;
        }

        .preview {
            margin-top: 30px;
            display: flex;
            gap: 20px;
            justify-content: center;
        }

        .preview img {
            border: 2px solid #ccc;
            border-radius: 8px;
            width: 300px;
        }

        p {
            margin-top: 15px;
            color: #555;
        }
    </style>
</head>
<body>

    <h1>Upload an Image</h1>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="image" required>
        <input type="submit" value="Upload">
    </form>

    {% if filename %}
        <p>Uploaded: {{ filename }}</p>
        <div class="preview">
            <div>
                <p>Original</p>
                <img src="/uploads/{{ filename }}">
            </div>
            <div>
                <p>Annotated</p>
                <img src="{{ new_img }}">
            </div>
        </div>
    {% endif %}

</body>
</html>
'''


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    filename = None
    annotatedshi = None
    if request.method == 'POST':
        image = request.files['image']
        if image:
            filename = image.filename
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            annotatedshi= predict(image_path)

    return render_template_string(HTML_FORM, filename=filename, new_img=annotatedshi)

# Serve uploaded files
from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run('0.0.0.0', port = 5000)


