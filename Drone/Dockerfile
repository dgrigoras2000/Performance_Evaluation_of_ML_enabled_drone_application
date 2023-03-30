# Pull base image of latest Python 3.10
FROM python:3.10

# Upgrade pip to the latest version
RUN pip3 install --upgrade pip

# Create a directory called 'code' in the container and set it as the working directory
RUN mkdir /code
WORKDIR /code

# Copy the requirements.txt file from the local machine to the container
ADD requirements.txt /code/

# Install all required packages using pip
RUN pip3 install -r requirements.txt

# Copy the contents of the ./code directory from the local machine to the container's /code directory
ADD ./code/ /code/

# Wait for 10 seconds before running the 'python drone_main.py' command
CMD sleep 10 && python drone_main.py