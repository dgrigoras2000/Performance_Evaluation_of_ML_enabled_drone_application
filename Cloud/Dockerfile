# Pull base image of latest Python 3.10.x
FROM python:3.10

## Set environment variables
#ENV PYTHONUNBUFFERED=1
#ENV USE_FOLDER_FOR_SAVE=True
#ENV SEND_ALL_TOGETHER=True
#ENV FIRST_COUNTER=True

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/

RUN pip3 install -r requirements.txt

EXPOSE 8000
# cron tab
ADD ./code/ /code/

#RUN chmod +x /code/entrypoint.sh
#CMD ["uvicorn", "basestation_server:app1", "--reload", "--host", "127.0.0.1", "--port", "8000"]
CMD ["python3", "cloud_server.py" ]
