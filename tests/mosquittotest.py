import subprocess

subprocess.run('C:/Program Files/mosquitto/mosquitto_pub.exe -h localhost -p 1883 -t feature_store/machine1/feature_vectors -m hallo')