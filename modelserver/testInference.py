import inference
import json

if __name__ == '__main__':
    f = open('tests/oneECG.json')
    JSONdata = json.load(f)
    print(inference.predict(JSONdata))
