FROM python:3.7

EXPOSE 5000

RUN mkdir /src

COPY requirements.txt /src
RUN pip install -r src/requirements.txt

COPY app.py /src

WORKDIR src/
CMD gunicorn -b 0.0.0.0:5000 -k flask_sockets.worker app:app
