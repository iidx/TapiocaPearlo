FROM python:3
MAINTAINER Namjun Kim <bunseokbot@gmail.com>

WORKDIR ["/home"]

# Install Python requirements 
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy forensic tools
COPY tools .
