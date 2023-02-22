FROM --platform=linux/amd64 python:3.9-slim

COPY ./app /app
COPY ./entrypoint.sh /entrypoint.sh
COPY ./requirements.txt /requirements.txt

RUN apt-get update && \
    apt-get install -y libsm6 libxext6 libxrender-dev libglib2.0-0 \
        build-essential \
        python3-dev \
        python3-setuptools \
        tesseract-ocr \
        make \
        gcc \
        dos2unix \
    && dos2unix /entrypoint.sh \
    && chmod +x /entrypoint.sh \
    && python3 -m pip install -r requirements.txt \
    && apt-get remove -y --purge make gcc build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000 2222


CMD [ "./entrypoint.sh" ]
