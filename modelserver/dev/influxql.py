import requests

url = 'http://localhost:8086/query'

def post(params):
    r = requests.post(url=url, params=params)
    print(r.content)

def drop():
    params = {'q':'DROP SUBSCRIPTION modelserver ON features.autogen'}
    post(params)

def show():
    params = {'q':'SHOW SUBSCRIPTIONS'}
    post(params)

def create():
    params = {'q':'CREATE SUBSCRIPTION modelserver ON features.autogen DESTINATIONS ALL \'http://modelserver:9000/\''}
    post(params)


if __name__=='__main__':
    show()