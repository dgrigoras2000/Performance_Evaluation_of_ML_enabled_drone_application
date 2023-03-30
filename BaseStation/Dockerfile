# Pull base image of latest Python 3.10
FROM python:3.10

# Upgrade pip to the latest version
RUN pip3 install --upgrade pip


# Create a directory called 'code' in the container and set it as the working directory
RUN mkdir /code
WORKDIR /code

# Copy the requirements.txt file from the local machine to the container
ADD requirements.txt /code/

# Install the dependencies specified in requirements.txt
RUN pip install --cache-dir=./pip_cache -r requirements.txt

# Expose port 8000 to the outside world
EXPOSE 8000

# Copy the contents of the ./code directory from the local machine to the container's /code directory
ADD ./code/ /code/

# Set the default command to run when the container startss
CMD ["python", "basestation_server.py" ]
