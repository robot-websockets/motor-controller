# Motor Controller

you will need to install socketio

```
pip3 install "python-socketio[client]"
```

run the server with:

```
python3 ./app.py
```

If it crashes and needs to be restarted during development
use.

```
 py .\forever.py
```

# docker

docker build -t philstenning/motor-server .
docker run --rm -it philstenning/motor-server -W 192.168.55.12
