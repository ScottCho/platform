# Use an official Python runtime as a parent image
FROM python:3.6-slim

LABEL maintainer="scottcho@qq.com"

# Set the working directory to /code
WORKDIR /code

# Define environment variable
ENV FLASK_RUN_HOST 0.0.0.0

# Copy the current directory contents into the container at /app
COPY . /code

# Install any needed packages specified in requirements.txt
RUN pip --no-cache-dir install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com -r requirements.txt

# db init
RUN flask db init && flask db migrate

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
CMD ["gunicorn", "app:flask_app", "-b", "0.0.0.0:80"]