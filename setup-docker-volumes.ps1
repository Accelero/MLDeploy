# This PowerShell script creates and sets up the Docker bind mount directories on the host machine as specified in the compose.yaml.
# The directories will be created in the folder docker-volumes/... insides this project folder and are ignored by source control (git).
# The folder "docker-volumes" and it's contents will be first deleted and then recreated, if it already exists. 

Remove-Item -Path "./docker-volumes" -Force -Recurse -ErrorAction SilentlyContinue

New-Item -Path './docker-volumes/chronograf' -ItemType Directory
New-Item -Path './docker-volumes/influxdb/config' -ItemType Directory
New-Item -Path './docker-volumes/telegraf/config' -ItemType Directory
New-Item -Path './docker-volumes/mosquitto/config/' -ItemType Directory

Copy-Item -Path './components/chronograf/chronograf-v1.db' -Destination './docker-volumes/chronograf/' -Force
Copy-Item -Path './components/influxdb/influxdb.conf' -Destination './docker-volumes/influxdb/config/' -Force
Copy-Item -Path './components/telegraf/telegraf.conf' -Destination './docker-volumes/telegraf/config/' -Force
Copy-Item -Path './external/mosquitto/mosquitto.conf' -Destination './docker-volumes/mosquitto/config/' -Force