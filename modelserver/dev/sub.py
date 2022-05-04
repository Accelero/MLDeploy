import requests

url = 'http://localhost:8086/query'
# params = {'q':'CREATE SUBSCRIPTION modelserver ON input.autogen DESTINATIONS ALL \'http://host.docker.internal:9000/\''}
params = {'q':'SHOW SUBSCRIPTIONS'}
# params = {'q':'DROP SUBSCRIPTION modelserver ON input.autogen'}

r = requests.post(url=url, params=params)
print(r.content)