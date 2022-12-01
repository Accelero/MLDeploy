# MLDeploy

In this branch the project was moved to VSCode Development Container. This makes the setup of the development environment easier. Only VSCode and Docker are needed on the local machine. 

## Run Demo

### 1. Build App
1. [Download](https://www.docker.com/products/docker-desktop/) and install Docker (for Linux) or Docker Desktop (for Windows and MacOS)

2. Run "start.bat" by double clicking it, or running it from a terminal

### 2. Run simulator
1. [Download](https://www.python.org/downloads/) and install Python 3.9

2. **Install pipenv:** Open terminal with privileges and run `pip install pipenv` to install system wide. Parameter `--user` can be used to install only for the current user. Make sure pipenv is added to the PATH environment variable (system or user PATH respectively).

3. **Create python virtual environment for "controllersim" subproject and install dependencies:** Open terminal at "MLDeploy/controllersim" and run `pipenv install`. 

4. **Run controller simulator:** Open terminal at "MLDeploy/controllersim" and run `pipenv shell` to use virtual environment and then run `python app/main.py` to start simulator. 

5. Open web browser at [localhost:8888](http://localhost:8888/)

6. Navigate to "Dashboards &rarr; MLOverview"

7. Set query time frame and update rate in the top right corner

![](/data/images/chronograph_dashboard.png "Chronograph Dashboard")

8. Press/hold "a" on keyboard to create anomaly (frequency change)

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