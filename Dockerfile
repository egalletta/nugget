FROM python:3.8.6-slim-buster
RUN apt-get update
RUN apt-get -y install build-essential libffi-dev
COPY ./webservice /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 80
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:80", "app:app"]
