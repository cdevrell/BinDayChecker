FROM python:3.10-alpine

COPY src/GetBinDay.py /opt/
COPY src/requirements.txt /opt/

RUN pip3 install -r /opt/requirements.txt

CMD [ "python3", "/opt/GetBinDay.py"]