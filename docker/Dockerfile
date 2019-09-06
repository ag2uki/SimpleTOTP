FROM alpine:3.10.2

WORKDIR /run
COPY ../Source /run

RUN apk add python3 
RUN pip3 install tinydb --trusted-host pypi.python.org

EXPOSE 8000

CMD ["python3", "Service.py"]