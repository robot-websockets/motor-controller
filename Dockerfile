FROM python:3

ADD . /code

WORKDIR /code

RUN pip install -r requirements.txt

EXPOSE 5001

ENTRYPOINT [ "python", "main.py" ]

# CMD [ "python", "main.py" ]