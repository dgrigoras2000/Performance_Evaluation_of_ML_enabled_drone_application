# Import necessary modules
import ast  # For literal evaluation of strings to Python objects
import csv
import datetime
import fnmatch  # For pattern matching of filenames
import logging  # For logging error messages
import os  # For interacting with the file system
import time
import pytz

import requests  # For making HTTP requests
import simplejson as json  # For parsing JSON data

# Set the path to the directory containing the images to be sent
img_dir_path = "Pics_drones"

# Set the value of the environment variable 'ALL_TOGETHER' to True or False
ALL_TOGETHER = ast.literal_eval(os.getenv('ALL_TOGETHER', "False"))

# Set the value of the environment variable 'ALL_TOGETHER'
NUMBER_OF_IMAGES = int(os.getenv('NUMBER_OF_IMAGES', '2'))

# Set the value of the environment variable 'BASESTATION_URL'
BASESTATION_URL = os.getenv('BASESTATION_URL')


# Define a class for sending images to the basestation
class DroneMain:
    def __init__(self):
        # Initialize an empty list to store the images
        self.images_list = []
        # Initialize the image array as None
        self.image_arr = None
        # Initialize send time to zero
        self.send_elapsed_time = 0

    # Define a function for finding files in a directory that match a given pattern
    @staticmethod
    def find_files(directory, pattern):
        for root, dirs, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    yield filename

    @staticmethod
    def create_data(t_id, desc, start, end):
        # Create a row of data to be saved to the CSV file
        row = [t_id, desc, start, end, end - start]
        return row

    @staticmethod
    def save_csv(csv_file, csv_data):
        # Open the CSV file in write mode and create a writer object
        writer = csv.writer(csv_file)

        # Write the data to the CSV file
        writer.writerow(csv_data)

    @staticmethod
    def create_logs(txt_file, txt_log):
        # Set the timezone to Europe/Nicosia
        tz = pytz.timezone('Europe/Nicosia')

        # Get the current datetime with the timezone set to Europe/Nicosia
        dt = datetime.datetime.now(tz)
        # Format the datetime object as a string with the hour in 24-hour format
        date_string = dt.strftime('%d-%m-%Y %H:%M:%S')

        # Write the log message to the text file with the current date and time
        txt_file.write(f"{date_string} drone  | {txt_log}\n")

    # Define a function for loading the images from the specified directory
    def load_images(self):
        # Check if log and CSV files exist.
        if os.path.exists('/data_drone/drone_logs.txt'):
            # Open existing text file in 'append' mode
            txt_file = open('/data_drone/drone_logs.txt', 'a')
            # Open existing CSV file in 'append' mode
            csv_file = open('/data_drone/drone_times.csv', "a", newline="")
        else:
            # Create new text file and open in 'write' mode
            txt_file = open('/data_drone/drone_logs.txt', 'w')
            # Create new CSV file and open in 'write' mode
            csv_file = open('/data_drone/drone_times.csv', "w", newline="")
            # Define header for CSV file
            header = ["ID", "Description", "Start Time", "End Time", "Total Time"]
            # Write header to CSV file
            (csv.writer(csv_file)).writerow(header)

        while True:
            # Get the current time as the starting time
            start_time = time.time()

            # Load images from a folder
            for filename in self.find_files(img_dir_path, '*.jpg'):
                # Open the image file and add it to the list of images to be sent
                img_tuple = ('files', open(filename, 'rb'))
                self.images_list.append(img_tuple)

            # Get the total number of images
            total_num_of_imgs = len(self.images_list)

            # Send the images to the basestation
            response = self.send_images(total_num_of_imgs, txt_file, csv_file)

            # Log an error message indicating the response from the basestation
            logging.error(f"Basestation response: {response}")
            # Write the response to the drone logs text file
            self.create_logs(txt_file, f"Basestation response: {response}")
            # Print a message indicating that a response has been received from the basestation
            print("Received from BaseStation")

            # Get the current time as the ending time
            end_time = time.time()
            # Calculate the elapsed time
            elapsed_time = end_time - start_time

            # Write the start time, end time, and total time to the CSV file
            self.save_csv(csv_file, self.create_data(10, "StartEndTime", start_time, end_time))

            # Print the latency time to the console
            print(f"Latency time for drone: {elapsed_time} seconds")
            # Write the latency time to the drone logs text file
            self.create_logs(txt_file, f"Latency time for drone: {elapsed_time} seconds")

            # Clear the list of images to be sent
            self.images_list = []

    ############################################################################################

    # Define a function for sending the images to the basestation
    def send_images(self, total_num_of_imgs, txt_file, csv_file):

        # If the flag ALL_TOGETHER is set to False, group pictures by a defined number of images
        if ALL_TOGETHER:
            imgs_in_segments = total_num_of_imgs
        else:
            imgs_in_segments = NUMBER_OF_IMAGES

        # Print a message indicating that the code is waiting for the connection to be established
        print("Waiting for connection establishment with BaseStation...")

        try:
            # Make an HTTP GET request to check if the connection to the basestation has been established
            response = requests.get(url=f"http://{BASESTATION_URL}/check/connection/basestation", timeout=10)
            if response.status_code == 200:
                # If the response status code is 200, log a message indicating that the request was successful
                logging.error("Request was successful")
                self.create_logs(txt_file, "Request was successful")

            else:
                # If the response status code is not 200, raise a SystemExit exception with an error message
                raise SystemExit(f"Request failed with status code: {response.status_code}")
        except requests.exceptions.Timeout:
            # If the request times out, raise a SystemExit exception with an error message
            raise SystemExit("Request timed out")
        except requests.exceptions.RequestException as e:
            # If an exception occurs, raise a SystemExit exception with an error message
            raise SystemExit(f"An error occurred: {e}")

        print(f"Request was successful with code: {response.status_code} and text: {json.loads(response.text)}")
        logging.error(
            f"Request was successful with code: {response.status_code} and text: {json.loads(response.text)}")
        self.create_logs(txt_file,
                         f"Request was successful with code: {response.status_code} and text: {json.loads(response.text)}\n")

        print(json.loads(response.text) + "\n\n" + "Waiting for basestation response...\n")

        way_of_send = f"Use segments to send pictures in list with number of pics to group: {imgs_in_segments}."
        list_num_elements = []
        response = {}

        # Iterate over the list of images and group them in segments
        for num_pic in range(0, total_num_of_imgs, imgs_in_segments):
            send_start_time = time.time()  # get the current time in seconds
            # Loop over the range of the segment and add images to the list_num_elements
            for x in range(0, imgs_in_segments):
                if num_pic + x < total_num_of_imgs:
                    list_num_elements.append(self.images_list[num_pic + x])

            try:
                response = requests.post(
                    # Endpoint URL to send images
                    url=f"http://{BASESTATION_URL}/import/images/{num_pic}/{total_num_of_imgs}",
                    files=list_num_elements,  # Images to be sent
                    timeout=60
                )
                if response.status_code == 200:
                    # If the status code is 200,
                    # log that the request was successful along with the current segment number
                    logging.error(f"Request was successful {num_pic}")
                else:
                    # If the status code is different from 200, raise an exception with the status code
                    raise SystemExit(f"Request failed with status code: {response.status_code}")
            except requests.exceptions.Timeout:
                # If the request times out, raise an exception
                raise SystemExit("Request timed out")
            except requests.exceptions.RequestException as e:
                # If any other exception occurs, raise an exception with the error message
                raise SystemExit(f"An error occurred: {e}")

            # If the 'success' key in the JSON response is False,
            # raise an exception with error message from response
            if not json.loads(response.text)["success"]:
                raise SystemExit(f"Something went wrong with the process in BaseStation\n"
                                 f"{json.loads(response.text)['message']}"
                                 )
            # Reset list of images for next segment
            list_num_elements = []
            send_end_time = time.time()

            # Create a row in the csv_file with start and end time
            csv_data = self.create_data(num_pic, "Time to send images", send_start_time, send_end_time)
            # Save row in the file
            self.save_csv(csv_file, csv_data)

            # Sleeps for 5 seconds until send the next group of images
            print('Sleeping for 5 seconds...')
            time.sleep(5)

        # Log way of sending images
        logging.error(way_of_send)
        self.create_logs(txt_file, way_of_send)

        # Return success message from response
        return json.loads(response.text)["message"]


# Main program entry point
# This block of code is executed only if this file is run as the main program.
# It creates an instance of the DroneMain class and calls the load_images method to start the process.
if __name__ == "__main__":
    run = DroneMain()
    run.load_images()
