FROM python:3.8.19

ENV HOME /app
WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8080

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD /wait && gunicorn -k eventlet --bind 0.0.0.0:8080 server:app