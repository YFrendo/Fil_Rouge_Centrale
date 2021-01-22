FROM python:3.8

ADD ./src /app/
ADD ./static /app/static/
ADD credential /.aws/
COPY requirements.txt ./

RUN pip install -r requirements.txt

WORKDIR /app

EXPOSE 5000

CMD [ "python","./serveur_flask.py"] 
