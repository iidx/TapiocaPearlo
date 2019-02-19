FROM python:3
MAINTAINER Namjun Kim <bunseokbot@gmail.com>

RUN apt-get update && \
	apt-get install -y ffmpeg && \
	rm /var/lib/apt/lists/*

WORKDIR ["/home"]

# Install Python requirements 
COPY requirements.txt .
RUN pip install -r requirements.txt
