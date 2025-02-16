# Use an official Python runtime as the base image
FROM python:3.11.1

# Set the working directory inside the container
WORKDIR /app

# Copy the datasender.py file to the container
COPY docker_datasender.py /app/docker_datasender.py

# Copy the split-/*.csv file to the container
COPY split/  /app/split/

# Set environment variable FILE_PATH
# ENV FILE_PATH=/app/split/*

# Install any necessary Python dependencies (if needed)
# For example, if your datasender.py needs some libraries
# RUN pip install --no-
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "docker_datasender.py"]