# MLDeploy

To run scripts from the /dev directory:
1. create an .env file in the project root and add the line PYTHONPATH=app
2. run pipenv shell

This adds the /app directory to the PYTHONPATH environment variable of your python virtual environment. Absolute imports can now find modules in /app.