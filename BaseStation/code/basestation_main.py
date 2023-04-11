# Import necessary modules and libraries
import ast  # for parsing strings into Python objects
import fnmatch  # for file name pattern matching
import glob  # for searching file path-names
import io  # for working with I/O streams
import json  # for working with JSON data
import logging  # for logging messages
import os  # for working with the operating system
import os.path  # for working with file paths
import time
import datetime

import cv2  # for working with images using OpenCV library
import numpy as np  # for working with numerical arrays
import requests  # for making HTTP requests
from PIL import Image  # for working with images using PIL library
from torchvision import transforms  # for applying image transforms using PyTorch
from torchvision.io.image import read_image  # for reading images using PyTorch

# Import custom modules
from car_rec_second import VehicleCounting2
from vehicle_counting import VehicleCounting1

# Define the directory path for saving images
dir_path = "Basestation_Images"

# Get values of environment variables and convert them to bool
ALL_TOGETHER = ast.literal_eval(os.getenv("ALL_TOGETHER", "True"))
FIRST_COUNTER = ast.literal_eval(os.getenv("FIRST_COUNTER", "True"))
USE_FOLDER_FOR_SAVE = ast.literal_eval(os.getenv("USE_FOLDER_FOR_SAVE", "True"))
CLOUD_URL = os.getenv('CLOUD_URL')


class BasestationMain:

    def __init__(self):
        # Initialize vehicle counters
        self.vehicle_counter_1 = VehicleCounting1()
        self.vehicle_counter_2 = VehicleCounting2()
        self.txt_file = None

    @staticmethod
    def find_files(directory, pattern):
        # Recursively search for files matching a given pattern in a directory and its subdirectories.
        for root, dirs, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)

                    yield filename

    # Save an image to disk with a given filename.
    @staticmethod
    def save_img(pic, pic_num):
        element_formatted = f"\\pic{str(pic_num)}.jpg"
        file_path = os.path.join(dir_path, element_formatted)
        pic.save(file_path)

    # Remove all image files in the Basestation_Images directory.
    @staticmethod
    def empty_dir():
        filelist = glob.glob(os.path.join(dir_path, "*.jpg"))
        for f in filelist:
            os.remove(f)

    def create_logs(self, txt_log):
        dt = datetime.datetime.fromtimestamp(time.time())
        # format the datetime object as a string with the hour in 24-hour format
        date_string = dt.strftime('%d-%m-%Y %H:%M:%S')
        self.txt_file.write(f"{date_string} basestation_main  | {txt_log}\n")

    # Process all images in a list at once and return a response
    def all_together(self, files):
        # Initialize empty list to store processed images
        images_list = []
        # Initialize save variable for logging purposes
        save = ""
        for file in files:
            contents = file.file.read()
            # Open image from file contents
            image = Image.open(io.BytesIO(contents))

            if USE_FOLDER_FOR_SAVE:  # Save in folder and make a list with.
                save = "Use folder to save | "
                self.save_img(image, files.index(file))
            else:  # Don't save and make a list with numpy ndarray each image.
                save = "No use folder to save | "
                if FIRST_COUNTER:
                    # Convert image to a numpy array and append to the list
                    image_array = np.array(image)
                    images_list.append(image_array)
                else:
                    # Apply the ToTensor transform to convert the image to a PyTorch tensor and append to the list
                    images_list.append(transforms.ToTensor()(image))

        if USE_FOLDER_FOR_SAVE:
            # Load images from a folder
            for pic_address in self.find_files(dir_path, '*.jpg'):
                # Check if it's the first counter being selected
                if FIRST_COUNTER:
                    # Load image with OpenCV and append to images list
                    images_list.append(cv2.imread(pic_address))
                else:
                    # Load image with custom read_image function and append to images list
                    images_list.append(read_image(pic_address))

        # Choose which vehicle counting method to use based on the value of the FIRST_COUNTER variable
        if FIRST_COUNTER:
            # vehicle_counter_1 object's vehicle_count method is called on the list of images (images_list)
            response = self.vehicle_counter_1.vehicle_count(images_list, None)
            counter = "and the vehicle counting (First)."
        else:
            # vehicle_counter_2 object's vehicle_count_2 method is called on the list of images (images_list)
            response = self.vehicle_counter_2.vehicle_count_2(images_list, None)
            counter = "and the car recognition second (Second)."

        # Log message with save and counter info
        print("All together | " + save + counter)
        # Empty saved images folder
        self.empty_dir()

        return response

    def divide_in_segments(self, files, num_pic):
        images_list = []
        save = ""
        count = 0

        self.txt_file = open('/data/logs.txt', 'a')

        # Loop through all the files
        for file in files:
            contents = file.file.read()
            image = Image.open(io.BytesIO(contents))

            # If using a folder for saving
            if USE_FOLDER_FOR_SAVE:  # Save in folder and make a list with.
                save = "Use folder to save | "
                # Save the image to a folder and append its file path to the images_list
                self.save_img(image, num_pic + count)

            # Otherwise
            else:  # Don't save and make a list with numpy ndarray each image.
                save = "No use folder to save | "
                if FIRST_COUNTER:
                    # Convert the image to a numpy array and append it to the images_list
                    image_array = np.array(image)
                    images_list.append(image_array)
                else:
                    # Apply the ToTensor transform to convert the image to a PyTorch tensor
                    # and append it to the images_list
                    images_list.append(transforms.ToTensor()(image))
            count += 1

        # If using a folder for loading
        if USE_FOLDER_FOR_SAVE:
            # Load images from a folder
            for pic_address in self.find_files(dir_path, '*.jpg'):
                if FIRST_COUNTER:
                    # Load the image with OpenCV and append it to the images_list
                    images_list.append(cv2.imread(pic_address))
                else:
                    # Load the image with custom read_image function and append it to the images_list
                    images_list.append(read_image(pic_address))

        # Choose which counter to use
        if FIRST_COUNTER:
            # Call the vehicle_counter_1's vehicle_count method with the images_list
            # and the number of the first image in the segment
            response = self.vehicle_counter_1.vehicle_count(images_list, num_pic)
            counter = "and the vehicle counting (First)."
        else:
            # Call the vehicle_counter_2's vehicle_count_2 method with the images_list
            # and the number of the first image in the segment
            response = self.vehicle_counter_2.vehicle_count_2(images_list, num_pic)
            counter = "and the car recognition second (Second)."

        # Log the information and empty the folder used for saving
        logging.error(f"Divided in segments ({count}) | " + save + counter)
        self.create_logs(f"Divided in segments ({count}) | " + save + counter)
        self.empty_dir()

        # Return response from selected counter for cars in images
        return response

    def send_to_cloud(self, road_info):
        try:
            # Send a POST request to the cloud service with road_info data as the payload
            response = requests.post(
                url=f"http://{CLOUD_URL}/cloud/information",
                data=json.dumps(road_info),
                timeout=60
            )

            # Check if the response status code is 200 (success)
            if response.status_code == 200:  # Raise an exception if the response status code is not 200
                logging.error("Request was successful")
                self.create_logs("Request was successful from cloud")
            else:
                # Raise a SystemExit exception if the response status code is not 200
                raise SystemExit(f"Request failed with status code: {response.status_code}")
        except requests.exceptions.Timeout:
            # Raise a SystemExit exception if the request times out
            raise SystemExit("Request timed out")
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            # Raise a SystemExit exception if any other exception occurs during the request
            raise SystemExit(f"An error occurred: {e}")

        # Return the response data as a JSON object
        return json.loads(response.text)
