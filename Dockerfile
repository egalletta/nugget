FROM python:3.8.6-slim-buster
COPY ./webservice /app
WORKDIR /app
RUN apt-get update
RUN apt-get -y install build-essential libffi-dev
RUN pip install -r requirements.txt
EXPOSE 8700
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8700", "app:app"]
