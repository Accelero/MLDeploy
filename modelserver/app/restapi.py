from flask import Flask, jsonify, request, render_template
import inference
from config import config

app = Flask(__name__.split('.')[0])

#rest functions
@app.route('/evalloss', methods=['POST'])
def evalloss():
    # Get JSON from http message body
    inputData = request.get_json(force=True)
    # Go to eval() and return result
    return jsonify(inference.eval(inputData))

@app.route('/config', methods=['GET'])
def setCfgVar():
    section = request.args.get('section')
    option = request.args.get('option')
    value = request.args.get('value')
    try:
        config.set(section, option, value)
    finally:
        return render_template('config.html', parent_dict=config.toDict())
    
@app.route('/config/save')
def saveCfg():
    try:
        config.save()
    finally:
        return 'config saved'

@app.route('/write', methods=['POST'])
def printer():
    # inputData = request.get_json(force=True)
    print(request.get_data(as_text=True))
    return 'ok'
