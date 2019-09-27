# Use an official Python runtime as a parent image
FROM python:3.6-alpine

LABEL maintainer="scottcho@qq.com"

RUN mkdri /app

# Copy the current directory contents into the container at /app
COPY . /app

# Set the working directory to /app/platform
WORKDIR /app/platform


# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host https://mirrors.aliyun.com/pypi/simple -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["gunicorn", "app:flask_app", "-b", "0.0.0.0:80", "-w", "3", "-D", "-p", "/tmp/app.pid", "--log-file", "/tmp/app.log"]