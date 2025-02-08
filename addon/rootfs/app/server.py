#!/usr/bin/env python
import traceback
from os import path, environ
import cv2
from flask import Flask, request, jsonify
import base64
import numpy as np
import requests
from auth import token_required
from lib.detection_model import load_net, detect

THRESH = 0.08  # The threshold for a box to be considered a positive detection ## TO-DO: allow user input/setting for this
SESSION_TTL_SECONDS = 60 * 2

app = Flask(__name__)

status = dict()

# SECURITY WARNING: don't run with debug turned on in production!
app.config['DEBUG'] = environ.get('DEBUG') == 'True'

model_dir = path.join(path.dirname(path.realpath(__file__)), 'model')
net_main = load_net(path.join(model_dir, 'model.cfg'), path.join(model_dir, 'model.meta'))

# draw_bounding_boxes function - inspired from Obico ML HA Addon
def draw_bounding_boxes(image, detections, rectangleColor=(0, 0, 255), rectangleThickness=5, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.5, textColor=(0, 0, 255), textThickness=2): # <--- Corrected fontFace
    for detection in detections:
        label, confidence, bbox = detection
        x, y, w, h = [int(v) for v in bbox]
        cv2.rectangle(image, (x, y), (x + w, y + h), rectangleColor, rectangleThickness)
        text = f"{label}: {confidence:.2f}"
        cv2.putText(image, text, (x, y - 5), fontFace, fontScale, textColor, textThickness)  # <--- Corrected fontFace
    return image

# /p/ endpoint
# example request: http://localhost:3333/p/?img=https://www.example.com/image.jpg
# example response: {"detections": [["failure", 0.627044320106506, [[314.500637054443, 594.114170074463, 175.366888046265, 293.919010162354]], ["failure", 0.351168990135193, [177.455763816834, 361.810432434082, 233.478097915649, 292.509155273438]]]}
@app.route('/p/', methods=['GET'])
@token_required
def get_p():
    if 'img' in request.args:
        try:
            resp = requests.get(request.args['img'], stream=True, timeout=(0.1, 5))
            resp.raise_for_status()
            img_array = np.array(bytearray(resp.content), dtype=np.uint8)
            img = cv2.imdecode(img_array, -1)
            detections = detect(net_main, img, thresh=THRESH)
            return jsonify({'detections': detections})
        except:
            print(traceback.print_exc())
    else:
        app.logger.warn("Invalid request params: {}".format(request.args))

    return jsonify({'detections': []})

# /hc/ endpoint - for testing. Returns 'ok' if the server is running and the model is loaded
@app.route('/hc/', methods=['GET'])
def health_check():
    return 'ok' if net_main is not None else 'error'

# /detect/ endpoint - added from Obico ML HA Addon (with fixes)
# example request data:
# {
#     "img": "base64_encoded_image_as_string",
#     "threshold": 0.08,
#     "rectangleColor": [0, 0, 255],
#     "rectangleThickness": 5,
#     "fontFace": "FONT_HERSHEY_SIMPLEX",
#     "fontScale": 1.5,
#     "textColor": [0, 0, 255],
#     "textThickness": 2
# }
# example response data:
# {
#     "detections": [["failure", 0.627044320106506, [[314.500637054443, 594.114170074463, 175.366888046265, 293.919010162354]], ["failure", 0.351168990135193, [177.455763816834, 361.810432434082, 233.478097915649, 292.509155273438]]],
#     "image_with_detections": "base64_encoded_image_as_string"
# }
@app.route('/detect/', methods=['POST'])
# @token_required # might add for final version after testing...
def failure_detect():
    try:
        data = request.get_json(force=True)  # <-- Force JSON parsing

        img_base64 = data.get("img", None)
        if img_base64 is None:
            return jsonify({"error": "No image provided"}), 400

        img_bytes = base64.b64decode(img_base64)
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_array, -1)

        threshold = float(data.get("threshold", THRESH))

        detections = detect(net_main, img, thresh=threshold)

        rectangleColor = tuple(data.get("rectangleColor", (0, 0, 255)))
        rectangleThickness = data.get("rectangleThickness", 5)
        fontFace = getattr(cv2, data.get("fontFace", "FONT_HERSHEY_SIMPLEX"))
        fontScale = data.get("fontScale", 1.5)
        textColor = tuple(data.get("textColor", (0, 0, 255)))
        textThickness = data.get("textThickness", 2)

        img_with_boxes = draw_bounding_boxes(img, detections, rectangleColor, rectangleThickness, fontFace, fontScale, textColor, textThickness)

        _, buffer = cv2.imencode('.jpg', img_with_boxes)
        img_with_boxes_base64 = base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            "detections": detections,
            "image_with_detections": img_with_boxes_base64
        }), 200

    except Exception as e:
        app.logger.error(f"Error processing image: {str(e)}")
        return jsonify({"error": f"Failed to process image - {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3333, threaded=False)
