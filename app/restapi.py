from flask import Flask, jsonify, request
import inference

app = Flask(__name__)

#rest functions
@app.route('/evalloss', methods=['POST'])
def evalloss():
    # Get JSON from http message body
    inputData = request.get_json(force=True)
    # Go to eval() and return result
    return jsonify(inference.eval(inputData))