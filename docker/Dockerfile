FROM python:3.10-slim

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

RUN mkdir /acc_api
WORKDIR /acc_api
COPY . ./
RUN pip install .

EXPOSE 9002
ENTRYPOINT ["python", "-u", "/acc_api/scripts/apifast.py"]