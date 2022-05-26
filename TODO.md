# TODOs
- slim down and optimize docker-builts
- create IOWrapper Python package
- Logging

## Modelserver
- Flask Server Production setup (Gunicorn)
- Train sliding window autoencoder
- Setup Subscriptions
- cleanup
- optimize dockerfile

## Preprocessor
- make code more reusable
- startup routine
- auto create db if not existing
- optimize dockerfile

## Telegraf
- Build Docker container with custom config

## Influxdb
- Define how dbs are automatically created and setup
- Build Docker container with custom config

## Configs
- Vars defined in code, so linter recognizes them   x
- Vars declared in one place    x
- Vars are thread and multiprocessing safe  x
- Functionality decoupled and maximum reusability of code
- save, set methods x
- read, load methods    x
- check on load / fallback x
- environment variable load