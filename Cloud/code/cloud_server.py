# Importing the FastAPI framework and the CloudMain class from another module
import time
import datetime
from fastapi import Body
from fastapi import FastAPI

from cloud_main import CloudMain

# Creating a new FastAPI app instance
app = FastAPI()

txt_file = open('/data/logs.txt', 'a')


def create_logs(txt_log):
    dt = datetime.datetime.fromtimestamp(time.time())
    # format the datetime object as a string with the hour in 24-hour format
    date_string = dt.strftime('%d-%m-%Y %H:%M:%S')
    txt_file.write(f"{date_string} cloud_server   | {txt_log}\n")


# Defining a route for checking the connection to the Cloud Server
@app.get("/check/connection/cloud")
async def check_connection():
    return "Connection established to Cloud Server"


# Defining a route for handling incoming requests to the '/cloud/information' endpoint
@app.post("/cloud/information")
async def cloud1(road_info: dict = Body(...)):
    start_time = time.time()  # get the current time in seconds

    # Printing the received information for debugging purposes
    print(f"road_info: {road_info}")
    create_logs(f"road_info: {road_info}")
    # Creating an instance of the CloudMain class
    service = CloudMain()
    # Calling the 'road_check' method of the CloudMain instance with the received information
    response = service.road_check(road_info)
    end_time = time.time()  # get the current time again

    elapsed_time = end_time - start_time  # calculate the elapsed time

    print(f"Elapsed time for cloud: {elapsed_time} seconds")
    str_time = f"Elapsed time for cloud: {elapsed_time} seconds"
    create_logs(str_time)

    # Returning the response from the 'road_check' method
    return response


# Starting the FastAPI app using the Uvicorn server
if __name__ == "__main__":
    import uvicorn

    try:
        # Starting the server on 'localhost:8080' and enabling hot reloading
        uvicorn.run(f"cloud_server:app", host="0.0.0.0", port=8080, reload=True)

    except KeyboardInterrupt:
        print("Server has stopped")
