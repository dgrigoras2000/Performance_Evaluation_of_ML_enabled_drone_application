import glob

import cv2

from vehicle_detector import VehicleDetector

# Set the path of the images directory
IMG_DIR = "Basestation_Images\\*.jpg"


class VehicleCounting1:

    def __init__(self):
        # Load the VehicleDetector object for detecting vehicles in images
        self.vd = VehicleDetector()

        # Load images from a folder
        self.images_folder = glob.glob(IMG_DIR)

        # Initialize the total count of vehicles detected in the folder
        self.vehicles_folder_count = 0

    @staticmethod
    def count_vehicles(vehicle_boxes, img, vehicle_count):
        # Draw a bounding box around each detected vehicle and display the total count
        for box in vehicle_boxes:
            x, y, w, h = box

            # Draw a rectangle around the vehicle
            cv2.rectangle(img, (x, y), (x + w, y + h), (25, 0, 180), 3)

            # Display the total vehicle count on the image
            cv2.putText(img, "Vehicles: " + str(vehicle_count), (20, 50), 0, 2, (100, 200, 0), 3)

    def vehicle_count(self, images_details, img_number):
        # Count the number of vehicles in each image in the list of image arrays
        vehicle_count_dict = {}  # Initialize an empty dictionary to store the vehicle count for each image
        counter = 0

        for image_arr in images_details:
            # Generate a unique name for the image
            if not img_number:
                img_name = f"pic{counter}"
            else:
                img_name = f"pic{img_number + counter}"

            # Detect the vehicles in the image and count them
            vehicle_boxes = self.vd.detect_vehicles(image_arr)
            vehicle_count = len(vehicle_boxes)

            # Update total count
            vehicle_count_dict[img_name] = vehicle_count

            # Display the bounding boxes and count on the image
            self.count_vehicles(vehicle_boxes, image_arr, vehicle_count)

            counter += 1

        return vehicle_count_dict
