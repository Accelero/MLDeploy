# MLDeploy

## Demo
### 1. Build App
1. [Download](https://www.docker.com/products/docker-desktop/) and install Docker Desktop

2. Open terminal at project root "MLDeploy/" and run `docker-compose up`

### 2. Run simulator
1. [Download](https://www.python.org/downloads/) and install Python 3.9

2. **Install pipenv:** Open terminal with privileges and run `pip install pipenv` to install system wide. Parameter `--user` can be used to install only for the current user. Make sure pipenv is added to the PATH environment variable (system or user PATH respectively).

3. **Create python virtual environment for "controllersim" subproject and install dependencies:** Open terminal at "MLDeploy/controllersim" and run `pipenv install`. 

4. **Run controller simulator:** Open terminal at "MLDeploy/controllersim" and run `pipenv shell` to use virtual environment and then run `python app/main.py` to start simulator. 

5. Open web browser at [localhost:8888](http://localhost:8888/)

6. Navigate to "Dashboards &rarr; MLOverview"

7. Set query time frame and update rate in the top right corner

![](/docs/images/chronograph_dashboard.png "Chronograph Dashboard")

8. Press/hold "a" on keyboard to create anomaly (frequency change)

## Development

### Debug in Container
1. Install Python extension for VSCode
2. Run `docker-compose -f compose.yaml -f debug.yaml --build up`
3. Select Docker attach "run and debug" config in VSCode
4. Press F5 to run and debug