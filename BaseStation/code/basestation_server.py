# Import necessary modules and libraries
import ast  # Library to convert strings to Python objects
import csv
import datetime
import json  # Library to encode and decode JSON data
import logging  # Library to log messages
import os.path  # Library to work with file and directory paths
import time
from typing import List  # Library for typed list of elements

import requests  # Library to make HTTP requests
from fastapi import FastAPI  # Web framework for building APIs
from fastapi import File  # FastAPI file object type
from fastapi import UploadFile  # FastAPI upload file object type
from pydantic import BaseModel  # Library for data validation and settings management

from basestation_main import BasestationMain  # Import a custom class from another module

# Get an environment variable and convert it to a boolean
USE_FOLDER_FOR_SAVE = ast.literal_eval(os.getenv("USE_FOLDER_FOR_SAVE", "True"))
# Get another environment variable and convert it to a boolean
ALL_TOGETHER = ast.literal_eval(os.getenv("ALL_TOGETHER", "True"))
CLOUD_URL = os.getenv('CLOUD_URL')

# Set a directory path as a string
dir_path = "Basestation_Images"

# Define a global variable to store data
response_cloud = {}

# Create a new instance of the FastAPI framework
app = FastAPI()


# Define a data model for the response of the API endpoint
class VehicleCountResponse(BaseModel):
    success: bool
    message: str


def create_logs(txt_file, txt_log):
    dt = datetime.datetime.fromtimestamp(time.time())
    # format the datetime object as a string with the hour in 24-hour format
    date_string = dt.strftime('%d-%m-%Y %H:%M:%S')
    txt_file.write(f"{date_string} basestation_server  | {txt_log}\n")


def create_data(t_id, desc, start, end):
    row = [t_id, desc, start, end, end - start]
    return row


def save_csv(csv_file, csv_data):
    # open a new CSV file in write mode
    writer = csv.writer(csv_file)

    # write each row to the CSV file
    writer.writerow(csv_data)


# Endpoint to check connection between drone-basestation
@app.get("/check/connection/basestation")
async def check_conn():
    return "Connection established"


async def send_to_cloud(service, data):
    # Print message to indicate that the function is waiting for a connection with the cloud
    print("Waiting for connection establishment with Cloud...")

    # Send a GET request to check the connection with the cloud
    try:
        response = requests.get(
            url=f"http://{CLOUD_URL}/check/connection/cloud",
            timeout=10
        )
        # Check if the response status code is 200
        if response.status_code == 200:  # Raise an exception if the response status code is not 200
            # Log that the request was successful
            logging.error("Request was successful for cloud")
        else:
            # Raise a SystemExit exception with the response status code if it is not 200
            raise SystemExit(f"Request failed with status code: {response.status_code}")
    # Handle request timeouts
    except requests.exceptions.Timeout:
        raise SystemExit("Request timed out")
    # Handle other request exceptions
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        raise SystemExit(f"An error occurred: {e}")

    # Print message to indicate that the function is waiting for a response from the cloud
    print(json.loads(response.text) + "\n\n" + "Waiting for cloud response...\n")

    # Send the data to the cloud using the BasestationMain service's send_to_cloud method and store the response
    response = service.send_to_cloud(data)

    # Return the response from the cloud
    return response


@app.post("/import/images/{num_pic}/{num_of_repeats}", response_model=VehicleCountResponse)
async def drone(num_pic: int, num_of_repeats: int, files: List[UploadFile] = File(...)):
    send_end_time = 0
    send_start_time = 0
    start_time = time.time()  # get the current time in seconds
    # Set a default value for cloud response
    cloud_response = True

    # Check if log and CSV files exist.
    if os.path.exists('/data_basestation/basestation_logs.txt'):
        # Open existing text file in 'append' mode
        txt_file = open('/data_basestation/basestation_logs.txt', 'a')
        # Open existing CSV file in 'append' mode
        csv_file = open('/data_basestation/basestation_times.csv', "a", newline="")
    else:
        # Create new text file and open in 'write' mode
        txt_file = open('/data_basestation/basestation_logs.txt', 'w')
        # Create new CSV file and open in 'write' mode
        csv_file = open('/data_basestation/basestation_times.csv', "w", newline="")
        # Define header for CSV file
        header = ["ID", "Description", "Start Time", "End Time", "Total Time"]
        # Write header to CSV file
        (csv.writer(csv_file)).writerow(header)

    # Create an instance of BasestationMain
    service = BasestationMain()

    # Divide images in segments and process each segment separately
    response = service.divide_in_segments(files, num_pic)
    # Update response_cloud dictionary with response
    response_cloud.update(response)

    # If response is not a dictionary, return an error response
    if type(response) is not dict:
        return VehicleCountResponse(
            success=False,
            message="Process in vehicle count didn't complete successfully"
        )

    # If all images have been processed, send the updated response_cloud dictionary to cloud
    # and update cloud_response variable
    if num_pic + len(files) is num_of_repeats:
        send_start_time = time.time()  # get the current time in seconds
        cloud_response = await send_to_cloud(service, response_cloud)
        send_end_time = time.time()  # get the current time again
        print(f"Cloud response: {cloud_response}")
        create_logs(txt_file, f"Cloud response: {cloud_response}")

    # calculate the elapsed time
    send_elapsed_time = send_end_time - send_start_time
    # get the end time
    end_time = time.time()
    # calculate the elapsed time
    elapsed_time = end_time - start_time - send_elapsed_time
    save_csv(csv_file, create_data(num_pic, "StartEndTime", start_time, end_time))

    print(f"Latency time for BaseStation: {elapsed_time} seconds")
    create_logs(txt_file, f"Latency time for BaseStation: {elapsed_time} seconds")
    # If cloud response is successful, return a success response. Otherwise, return an error response.
    if cloud_response:
        return VehicleCountResponse(
            success=True,
            message="Process completed successfully"
        )
    else:
        return VehicleCountResponse(
            success=False,
            message="Process in cloud didn't complete successfully"
        )


if __name__ == "__main__":
    import uvicorn
    import shutil

    # Check if the flag USE_FOLDER_FOR_SAVE is set to True
    if USE_FOLDER_FOR_SAVE:
        # Check if the specified directory already exists
        if os.path.exists(dir_path):
            logging.error("Directory already exists.")
        else:
            # Create the directory if it does not exist
            os.mkdir(dir_path)
            logging.error("Directory created.")

    try:
        # Start the server using Uvicorn
        # Listen on all network interfaces on port 8000
        # Automatically reload the server on code changes
        uvicorn.run(f"basestation_server:app", host="0.0.0.0", port=8000, reload=True)

    except KeyboardInterrupt:
        # Remove the directory if it was created earlier
        shutil.rmtree(dir_path)
        print("Server has stopped")
