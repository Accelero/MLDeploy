from flask import Flask, jsonify, request
import inference

app = Flask(__name__)

#rest functions
@app.route('/predict', methods=['POST'])
def dataIO():
    # Get JSON from http message body
    inputData = request.get_json(force=True)
    # Go to predict() and return result message
    return jsonify(inference.predict(inputData))