FROM python:3.8-alpine

WORKDIR /app

COPY app/requirements.txt /app/

RUN pip install -r requirements.txt

COPY app/app.py /app/

CMD [ "python3", "app.py"]