# Project Structure

The structure of the project directory is based on the structure of the distributed system. In addition to files regarding the system itself, come files like documentation etc. The basic structure is outlined and explained in the following sections. 

    MLDeploy
    |-- .vscode
    |-- components
    |   |-- modelserver
    |   |-- preprocessor
    |   `-- ...
    |-- doc
    |-- external
    |   |-- controllersim
    |   `-- ...
    |-- lib
    |-- .gitignore
    |-- compose.yaml
    |-- README.md
    |-- start.bat
    `-- TODO.md

## The System
The system is defined by the components and the compose file.  
The relevant files in the project directory are the following:

    MLDeploy
    |-- components
    |   |-- component1
    |   |-- component2
    |   `-- ...
    |-- compose.yaml
    `-- ...

### components
The Source Code of the system components is located here. Every subdirectory represents a component of the distributed system and is a small subproject itself. 

### compose.yaml
The docker compose file orchestrates the build of the component containers and sets up the container network.

## Additional Files and Directories

    MLDeploy
    |-- .vscode
    |-- doc
    |-- external
    |   |-- controllersim
    |   `-- ...
    |-- lib
    |-- .gitignore
    |-- README.md
    |-- start.bat
    `-- TODO.md

### .vscode
In the .vscode directory at the root level of the project are recommended VSCode extensions for the project specified. 

### doc
Here is the project documentation located, like this file regarding the project structure. Component level documentation like code documentation should be placed in the subdirectory of the component under "MLDeploy/components/component_name/doc". 

### external
External components and applications for testing and special use cases are currently located here. 

### lib
The lib directory on the root level of the project is intended for custom libraries that are being used by multiple components.

### README.md
The Readme should give a short Overview of the project and serves as a frontpage/entry for the project on git. 

### TODO.md
In this simple todo list you can specify pending tasks or missing features that should be tracked.

### start.bat
This script sets up the necessary docker volumes under "MLDeploy/docker-volumes", copies the preconfigured config files and runs docker compose up.

### .gitignore
The gitignore list lists subdirectories and files that are excluded from source control and therefore don't get syncronized with the remote repository. It is currently st up to ignore .env files for local environment configuration, python cache files and the docker-volumes created by "start.bat".  

## Component Subdirectories
The subdirectory structure of the in-house developed components, that are not based on third party applications should conform to a similar layout. The component subdirectory is meant to be opened as it's own workspace in VSCode. For generic compiled programming languages this could look something like this:

    MLDeploy
    |-- components
    |   |-- component_name
    |   |   |-- .devcontainer
    |   |   |-- .vscode
    |   |   |-- src
    |   |   |-- ext
    |   |   |-- bin
    |   |   |-- test
    |   |   |-- doc
    |   |   |-- Dockerfile
    |   `-- ...
    `-- ...

There is currently no container that is not based on Python, so this layout is just an idea. For Python Docker containers, a layout similar to this should be used:

    MLDeploy
    |-- components
    |   |-- component_name
    |   |   |-- .devcontainer
    |   |   |-- .vscode
    |   |   |-- app
    |   |   |   |-- main.py
    |   |   |   `-- ...
    |   |   |-- test
    |   |   |-- doc
    |   |   |-- Pipfile
    |   |   |-- Pipfile.lock
    |   |   |-- Dockerfile
    |   `-- ...
    `-- ...

The exisitng Python containers are based on this layout and can be used as a reference or template to develop new Python based components. The component subdirectory's folders and files are explained in the following sections. Additional folders can be added as needed.

### .devcontainer
Since this project is based on in-container Development via VSCode Dev Containers, every component needs a devcontainer.json under "component_name/.devcontainer/devcontainer.json", that specifies the automatic devcontainer setup for VSCode. 

### .vscode
VSCode workspace settings are located under .vscode/ in the workspace directory which is in this case the component subdirectory. More about workspace settings under https://code.visualstudio.com/docs/getstarted/settings. 

### app
This is where the source code of the component is located. It should contain the entrypoint of the program as an Python file named "main.py". This folder should contain only the files to run the program and gets copied into the container image on build. 

### test
This folder contains tests.

### doc
Component specific documentation like code/api documentation goes here. 

### Pipfile*
Python dependency management is handled by pipenv, which uses these two Pipfiles to list the dependencies. The Pipfile contains direct dependencies of the source code and is meant for manual editing and designed for readablity. The Pipfile.lock lists all dependencies of the solved dependency graph and specifies the exact versions, including package hashes. The Pipfile.lock should never be manually edited. More about pipenv under https://docs.pipenv.org/. 

### Dockerfile
In the Dockerfile the build of the container image is described. Docker builds the image by executing the commands from the Dockerfile. Multiple build targets can be specified in the Dockerfile and can be understood as "variants" of the image. The build target "dev" is used for the Dev Container and contains necessary build tools etc. The build target "release" is configured for deployment. 