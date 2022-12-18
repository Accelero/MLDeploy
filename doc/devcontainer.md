# Dev Container

This project utilizes VSCode Dev Containers, which let's you use a Docker container as development environment. This is independent of the fact that the developed applications itself is designed to run in a Docker container in production. It just seems natural to use a Docker container as development and production environment. The Advantages are listed below:

1. Differences between development and production environment are minimized. 

2. Circumvention of the set up of a complicated local development environment on the developer machine. Everything needed to contribute to this project can be reduced to VSCode and Docker. The development environment is then automatically setup by VSCode inside a Docker container.

3. The Dev Container is setup inside the network of microservices and allows debugging of the component with interaction with the rest of the system. 

## Principles
The Dev Container is automatically set up by VSCode according to the devcontainer.json under ./.devcontainer/ inside the workspace directory. In this project every component of the system has it's own workspace directory under "MLDeploy/components/component_name". Inside every component's subdirectory, which is deveoped in-house, a devcontainer.json is configured to replace the component in the compose network of the system with a Dev Container variant of the component. 

Assuming the compose network is already running, the following steps are executed, when a Dev Container is opened. 

1. **The component inside the compose network is shutdown and removed.**  
This is handled by the entry `"initializeCommand": "docker compose rm component_name --stop --force"` in the devcontainer.json, which is executed at the very beginning, when a Dev Container is launched. 

2. **The Dev Container is built.**  
In the devcontainer.json the compose file is referenced and the specific service name of the container is given, that is to be launched. The default compose.yaml  is extended by a compose-override.yaml, that also resides in the ./.devcontainer folder and changes the build target of the container image used for the service to "dev". 

3. **The Dev Container is started as the respective service inside the compose network. With additional volume/bind mounts and specific entrypoint.**  
The container is then launched as the specified service as part of the compose network referenced specified by compose.yaml. The workspace directory is mounted inside the Dev Container in addition to other mounts specified and the command, which is executed on container start is replaced by `/bin/sh -c "while sleep 1000; do :; done"`, which prevents the container from immediate closing. 

For Python containers the build target "dev" does only contain python, pipenv and other build tools, aswell as environment variables to setup pipenv to use a specific folder as virtual environment. The devcontainer.json sets up a Docker Volume mount to the virtual environment folder to persist the dependencies between Dev Container rebuilds. This prevents the complete reinstallation of the dependencies in case of a change. The Python dependencies, including dev dependencies, inside the volume are installed and updated after Dev Container creation by the `"onCreateCommand": "pipenv install --dev && pipenv clean"`. This way the Dev Container always reopens with updated python dependencies. 