import requests
import json

url = 'http://localhost:9000/predict'
f = open('oneECG.json')
JSONdata = json.load(f)
JSONdata = json.dumps(JSONdata)
r = requests.post(url, JSONdata)
print("Result:")
message = r.text
print(message)
print("end")


