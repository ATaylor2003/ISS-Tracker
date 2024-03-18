FROM python:3.9

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python3 && \
    apt-get install -y python3-pip

RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY iss_tracker.py /app/iss_tracker.py
COPY test/test_iss_tracker.py /app/test_iss_tracker.py

ENTRYPOINT [ "python" ]
CMD ["iss_tracker.py"]