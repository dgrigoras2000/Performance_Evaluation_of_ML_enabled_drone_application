# Import necessary modules
import ast  # For literal evaluation of strings to Python objects
import fnmatch  # For pattern matching of filenames
import logging  # For logging error messages
import os  # For interacting with the file system

import requests  # For making HTTP requests
import simplejson as json  # For parsing JSON data

# Set the path to the directory containing the images to be sent
img_dir_path = "Pics_drones"

# Set the value of the environment variable 'ALL_TOGETHER' to True or False
ALL_TOGETHER = ast.literal_eval(os.getenv('ALL_TOGETHER', "False"))

# Set the value of the environment variable 'ALL_TOGETHER' to True or False
NUMBER_OF_IMAGES = int(os.getenv('NUMBER_OF_IMAGES', '2'))


# Define a class for sending images to the basestation
class DroneMain:
    def __init__(self):
        # Initialize an empty list to store the images
        self.images_list = []
        # Initialize the image array as None
        self.image_arr = None

    # Define a function for finding files in a directory that match a given pattern
    @staticmethod
    def find_files(directory, pattern):
        for root, dirs, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)

                    yield filename

    # Define a function for loading the images from the specified directory
    def load_images(self):
        # Load images from a folder
        for filename in self.find_files(img_dir_path, '*.jpg'):
            # Open the image file and add it to the list of images to be sent
            img_tuple = ('files', open(filename, 'rb'))
            self.images_list.append(img_tuple)

        # Get the total number of images
        total_num_of_imgs = len(self.images_list)

        # Send the images to the basestation
        response = self.send_images(total_num_of_imgs)

        # Log an error message indicating the response from the basestation
        logging.error(f"Basestation response: {response}")
        # Print a message indicating that a response has been received from the basestation
        print("Received from BaseStation")
        return

    ############################################################################################

    # Define a function for sending the images to the basestation
    def send_images(self, total_num_of_imgs):

        # Print a message indicating that the code is waiting for the connection to be established
        print("Waiting for connection establishment with BaseStation...")

        try:
            # Make an HTTP GET request to check if the connection to the basestation has been established
            response = requests.get(url="http://172.20.0.2:8000/check/connection/basestation", timeout=10)
            if response.status_code == 200:
                # If the response status code is 200, log a message indicating that the request was successful
                logging.error("Request was successful")
            else:
                # If the response status code is not 200, raise a SystemExit exception with an error message
                raise SystemExit(f"Request failed with status code: {response.status_code}")
        except requests.exceptions.Timeout:
            # If the request times out, raise a SystemExit exception with an error message
            raise SystemExit("Request timed out")
        except requests.exceptions.RequestException as e:
            # If an exception occurs, raise a SystemExit exception with an error message
            raise SystemExit(f"An error occurred: {e}")

        print(json.loads(response.text) + "\n\n" + "Waiting for basestation response...\n")

        # If the flag ALL_TOGETHER is set to True, send all pictures together
        if ALL_TOGETHER:
            way_of_send = "Use list to send all pictures together "
            try:
                response = requests.post(
                    url=f"http://172.20.0.2:8000/import/images/0/0",  # Endpoint URL to send images
                    files=self.images_list,  # Images to be sent
                    timeout=60
                )
                if response.status_code == 200:  # Raise an exception if the response status code is not 200
                    # If the status code is 200, log that the request was successful
                    logging.error("Request was successful")
                else:
                    # If the status code is different from 200, raise an exception with the status code
                    raise SystemExit(f"Request failed with status code: {response.status_code}")
            except requests.exceptions.Timeout:
                # If the request times out, raise an exception
                raise SystemExit("Request timed out")
            except requests.exceptions.RequestException as e:
                # If any other exception occurs, raise an exception with the error message
                raise SystemExit(f"An error occurred: {e}")

            # If the 'success' key in the JSON response is False, raise an exception
            if not json.loads(response.text)["success"]:
                raise SystemExit("Something went wrong with the process in BaseStation")

        else:
            # If the flag ALL_TOGETHER is set to False, group pictures by a defined number of images
            imgs_in_segments = NUMBER_OF_IMAGES
            way_of_send = f"Use segments to send pictures in list with number of pics to group: {imgs_in_segments}."
            list_num_elements = []
            response = {}

            # Iterate over the list of images and group them in segments
            for num_pic in range(0, total_num_of_imgs, imgs_in_segments):
                # Loop over the range of the segment and add images to the list_num_elements
                for x in range(0, imgs_in_segments):
                    if num_pic + x < total_num_of_imgs:
                        list_num_elements.append(self.images_list[num_pic + x])

                try:
                    response = requests.post(
                        # Endpoint URL to send images
                        url=f"http://172.20.0.2:8000/import/images/{num_pic}/{total_num_of_imgs}",
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

        # Log way of sending images
        logging.error(way_of_send)
        # Return success message from response
        return json.loads(response.text)["message"]


# Main program entry point
# This block of code is executed only if this file is run as the main program.
# It creates an instance of the DroneMain class and calls the load_images method to start the process.
if __name__ == "__main__":
    run = DroneMain()
    run.load_images()
