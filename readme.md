# Motor Controller

you will need to install socketio client

```
pip3 install "python-socketio[client]"
```

## Running the app

Now run where:

-W is the ip of the main websocket server

```bash
python3 ./app.py -W "192.168.55.13:5001"
```

## Docker

This is experimental and not up to date at the moment

docker build -t philstenning/motor-server .
docker run --rm -it philstenning/motor-server -W 192.168.55.12
