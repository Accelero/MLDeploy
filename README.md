# MLDeploy
## Introduction
*MLDeploy* is a concept for a universally applicable deployment of ML models with continual validity in machine tools. It belongs to the research project *AutoLern*. This deployment provides a simple solution to the machine learning analysis of the real-time recorded data by applying the ML module. This solution supports a profound range of data sources such as *OPCUA*, *gRPC*, *MQTT*, etc. *MLDeploy* also provides the visualization and alarm notification of the analysis results.

*MLDeploy* supports the development of components *preprocessor* and *modelserver* inside a container in *VSCode* (*Dev-Container*). It allows the developers to open any folder inside (or mounted into) a container and take advantage of Visual Studio Code's full feature set.

## Architecture of framework
The following figure shows the relationship between *Data Source* and the basic structure of *MLDeploy* consisting of *Platform* and *Hut*.

![](/data/images/mldeploy_structure.png "MLDeploy Structure")

- *Data source*

    provides input data from a server. Currently supported servers are the *Arburg-OPCUA* server, *Arburg-gRPC* server and *ControllerSim-MQTT* server.

- *Platform*

    provides the collection, sending and storing of the incoming data from *Data Source*. All of the *Platform* components run in containers, which provides an isolation environment from the operating system.

    - *Telegraf*

        is an agent, developed *InfluxData*, which collects incoming data from *Data Source* via
        
        **input-plugins** such as *opcua* (on-premise), *mqtt* (on-premise) and *arburg-grpc* (self-written)
        
        and subsequently sends data in certain data format such as *influx* via 
        
        **output-plugins** such as *influx* (on-premise) and *rabbitmq* (self-written).

        **Hint**: The input-plugin *MQTT* works only when the message broker *Mosquitto* is also running in the background. So does the output-plugin *rabbitmq* when *RabbitMQ* is running.

    - *RabbitMQ* 

        broker is a mesage broker implementing AMQP and it receives messages from *AMQP* (*RabbitMQ*) clients and routes messages to the appropriate subscribing clients. 
        
        Here, *RabbitMQ* receives messages from several clients such as *RabbitMQ* output-plugin of *Platform* with *exchanger=input* and the publisher in *Preprocessor* of *Hut* with *exchanger=preprocessor* and routes the data to the subscriber in *Preprocessor* of *Hut* and the subscriber in *Modelserver* respectively.

    - *Mosquitto* 

        broker, heart of the MQTT server, is a server that receives messages from *MQTT* clients and then routes messages to the appropriate subscribing clients. 
        
        Here, *Mosquitto* receives messages from *ControllerSim-MQTT* client and routes the data to the *MQTT* input-plugin of *Telegraf*.

    - *InfluxDB*

        is an open-source time series database developed by *InfluxData* for storage and retrieval of time series data in fields. 
        
        Here, it stores data sent by *Telegraf* output plugin *influxdb* (*databse=input*) and the *influxdb* client of in *Modelserver* (*database=predictions*). Then, the visualization tools *Chronograf* and *Grafana* retrives data from *InfluxDB*.

- *Hut*

    provides the preprocessing, prediction, visualization, alarming of the incomming data. Compared to *Grafana*, the component *Chronograf*, which is also developed by *InfluxData*,  provides similiar functions and will be removed in coming version.

    - *Preprocessor*

        is written in *python* and interpolates the time-stamped input data obtained by *RabbitMQ* subscriber (*exchanger=input*) with evenly distrubited timestamp intervals in each time frame and sends them again via *RabbitMQ* publisher (*exchanger=proprocessor*) for subsequent analysis by *Modelserver*.

    - *Modelserver*

        is written in *python* which produces the construction loss between the preprocessed input data obtained by *RabitMQ* subscriber (*exchanger=proprocessor*) and the prediction by the autoencoder and stores the data to *InfluxDB* by an *influxdb* client (*database=predictions*).

    - *Chronograf*

         is the user interface and administrative component of the InfluxDB 1. x platform, which is developed by *InfluxData*. It visualizes the input data from *Data Source* and the construction loss obtained by *Modelserver*. This component will be discarded in the future, as it contains repeated functions as *Grafana*.

    - *Grafana*

        is a multi-platform open source analytics and interactive visualization web application. It not only visualizes the input data from *Data Source* and the construction loss obtained by *Modelserver* but also send alarms via E-mails to users when the construction loss exceeds a certain value.


## Structure of repository
```
project
|   start.bat
|   compose.yaml
|   .env
|   ...
└───docker-volumes
|   |   ...
└───components
|   |   chronograf
|   |   grafana
|   |   influxdb
|   |   modelserver
|   |   preprocessor
|   |   rabbitmq
|   |   telegraf
└───external
|   |   controllersim
|   |   mosquitto
└───lib
    |...
```

## Run Demo

### 1. Run simulator (Option 1)
1. [Download](https://www.python.org/downloads/) and install Python 3.9.

2. **Install pipenv:** Open terminal with privileges and run `pip install pipenv` to install system wide. Parameter `--user` can be used to install only for the current user. Make sure pipenv is added to the PATH environment variable (system or user PATH respectively).

3. **Create python virtual environment for "controllersim" subproject and install dependencies:** Open terminal at "MLDeploy/controllersim" and run `pipenv install`. 

4. Press/hold "a" on keyboard to create anomaly (frequency change).

5. **Run controller simulator:** Open terminal at "MLDeploy/controllersim" and run `pipenv shell` to use virtual environment and then run `python app/main.py` to start simulator.

### 2. Run Arburg Freeformer Simulator (Option 2)
1. Open the executable file for Arburg Freeformer Simulator (Windows: *GesticaGrpcSimulatorUI.exe*).

2. Click *Server Starten* in Tab *gRPC*.

3. Load an *.afprotocol* file in Tab *ProcessLog* tab and click *Simulation Starten*.

### 3. Build App
1. [Download](https://www.docker.com/products/docker-desktop/) and install Docker (for Linux) or Docker Desktop (for Windows and MacOS).

2. Run "start.bat" by double clicking it, or running it from a terminal.

### 4. Visualization
1. Open web browser at [localhost:8888](http://localhost:8888/).

2. Navigate to "Dashboards &rarr; MLOverview".

    ![](/data/images/chronograph_main.png "Chronograph Main Page")

3. Set query time frame to 5s and update rate in the top right corner.

    ![](/data/images/chronograph_dashboard.png "Chronograph Dashboard")
4. Then you can see the panels in *Chronograf*.
    ![](/data/images/chronograph_panel.png "Chronograph Panels")


4. For the visualization in Grafana, open web browser at [localhost:3000](http://localhost:3000/) and enter "admin" for both the username and the password. Then you can click "skip" to skip setting the new password.

5. Navigate to "Search dashboards &rarr; General &rarr; Arburg Freeformer / Sinus Simulator".
    ![](/data/images/grafana_dashboard.png "Grafan Dashboard")

6. Then you can see the panels in *Grafana*.
    ![](/data/images/grafana_panel.png "Grafan Panels")

7. To check the status of *RabbitMQ* clients, open web browswer at [localhost:15672](http://localhost:15672) and enter "guest" for both the username and the password.

8. Click Tab *Connections* and you can see the states of all connections
    ![](/data/images/rabbitmq.png "RabbitMQ Connections")

9. If one of the connections has no bytes, please restart the corresponding containers.

## Development

This project utilizes Dev Containers from Visual Studio Code (VSCode). Dev Containers provide an encapsulated development environment inside of a Docker Container, that can be automatically setup by VSCode from definitions specified inside of a "dev-container.json" file. 
Since the entire application is divided into individual services, Dev Containers provide individual environments for the development of every service, which mimics the production environemnt of a Docker Container closely. Every Dev Container is set up to connect to the rest of the application and allow development and testing in conjunction with the other services. 

### Setup
1. [Download](https://code.visualstudio.com/) and install Visual Studio Code

2. **Install the "Dev Containers"-extension for VSCode:** Install the extension manually or install the workspace recommended extensions

### Develop in Container
1. Launch VSCode

2. Run "start.bat" by double clicking it, or running it from a terminal

4. To start development of an existing service, open the component's subdirectory in a Dev Container. Press F1 to open the command palette and call "Dev Containers: Open Folder in Container..." and select a folder of an existing service (e.g. "MLDeploy/components/modelserver/").
The Dev Container should be built and replace the service in the active compose network.\
Issues with launching the Dev Container can be caused by VSCode not correctly replacing the container in the compose network. Forcing a rebuild of the Dev Container can often fix these issues. Choose "Dev Containers: Rebuild and Reopen in Container" from the command palette to force a rebuild of the Dev Container. 