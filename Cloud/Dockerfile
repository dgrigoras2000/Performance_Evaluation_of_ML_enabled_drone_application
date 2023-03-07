# Pull base image of latest Python 3.10.x
FROM python:3.10

# Upgrade pip to the latest version
RUN pip3 install --upgrade pip

# Create a directory for the code and set it as the working directory
RUN mkdir /code
WORKDIR /code

# Copy the requirements file and install the dependencies
ADD requirements.txt /code/
RUN pip3 install -r requirements.txt

# Expose port 8080 to the outside world
EXPOSE 8080

# Copy the contents of the ./code directory from the local machine to the container's /code directory
ADD ./code/ /code/

# Set the default command to run when the container starts
#CMD sleep 10 && python cloud_server.py
CMD ["python", "cloud_server.py" ]
