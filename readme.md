# Motor Controller

you will need to install socketio client

```
pip3 install "python-socketio[client]"
```

## Running the app

Now run where:

-S is the ip address of the main websocket server
-M is the minimum speed needed to start the motor, ie 50%

```bash
python3 ./app.py -S "192.168.55.13" -M 40
```

## Docker

This is experimental and not up to date at the moment

docker build -t philstenning/motor-server .
docker run --rm -it philstenning/motor-server -W 192.168.55.12
