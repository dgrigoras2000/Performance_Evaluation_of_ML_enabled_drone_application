# Pull base image of latest Python 3.7.x
FROM python:3.10

# Set environment variables
#ENV PYTHONUNBUFFERED=1
#ENV ALL_TOGETHER=True
#ENV NUMBER_OF_IMAGES=2

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/

RUN pip3 install -r requirements.txt

EXPOSE 8000
# cron tab
ADD ./code/ /code/

#RUN chmod +x /code/entrypoint.sh
CMD ["python3", "drone_main.py"]