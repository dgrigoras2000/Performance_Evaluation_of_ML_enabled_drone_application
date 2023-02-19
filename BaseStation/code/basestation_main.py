import fnmatch
import glob
import io
import json
import os
import os.path

import cv2
import numpy as np
import requests
from PIL import Image
from torchvision import transforms
from torchvision.io.image import read_image

from car_rec_second import VehicleCounting2
from vehicle_counting import VehicleCounting1

dir_path = "Basestation_Images"

# Environment Variables
USE_FOLDER_FOR_SAVE = bool(os.environ['USE_FOLDER_FOR_SAVE'])
FIRST_COUNTER = bool(os.environ['FIRST_COUNTER'])


class BasestationMain:

    def __init__(self):
        self.vehicle_counter_1 = VehicleCounting1()
        self.vehicle_counter_2 = VehicleCounting2()

    @staticmethod
    def find_files(directory, pattern):
        for root, dirs, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)

                    yield filename

    @staticmethod
    def save_img(pic, pic_num):
        element_formatted = f"\\pic{str(pic_num)}.jpg"
        file_path = os.path.join(dir_path, element_formatted)
        pic.save(file_path)

    @staticmethod
    def empty_dir():
        filelist = glob.glob(os.path.join(dir_path, "*.jpg"))
        for f in filelist:
            os.remove(f)

    def all_together(self, files):
        images_list = []
        save = ""
        for file in files:
            contents = file.file.read()
            image = Image.open(io.BytesIO(contents))

            if USE_FOLDER_FOR_SAVE:  # Save in folder and make a list with.
                save = "Use folder to save | "
                self.save_img(image, files.index(file))
            else:  # Don't save and make a list with numpy ndarray each image.
                save = "No use folder to save | "
                if FIRST_COUNTER:
                    image_array = np.array(image)
                    images_list.append(image_array)
                else:
                    images_list.append(transforms.ToTensor()(image))

        if USE_FOLDER_FOR_SAVE:
            # Load images from a folder
            for pic_address in self.find_files(dir_path, '*.jpg'):
                if FIRST_COUNTER:
                    images_list.append(cv2.imread(pic_address))
                else:
                    images_list.append(read_image(pic_address))
        # Choose which counter to use
        if FIRST_COUNTER:
            response = self.vehicle_counter_1.vehicle_count(images_list, None)
            counter = "and the vehicle counting (First)."
        else:
            response = self.vehicle_counter_2.vehicle_count_2(images_list, None)
            counter = "and the car recognition second (Second)."

        print("All together | " + save + counter)
        self.empty_dir()

        # cloud_response = self.send_to_cloud(response)
        # print(f"Answer from cloud: {cloud_response.text}")

        return response

    def divide_in_segments(self, files, num_pic):
        images_list = []
        save = ""
        count = 0
        for file in files:
            contents = file.file.read()
            image = Image.open(io.BytesIO(contents))

            if USE_FOLDER_FOR_SAVE:  # Save in folder and make a list with.
                save = "Use folder to save | "
                self.save_img(image, num_pic + count)
                # Load images from a folder
            else:  # Don't save and make a list with numpy ndarray each image.
                save = "No use folder to save | "
                if FIRST_COUNTER:
                    image_array = np.array(image)
                    images_list.append(image_array)
                else:
                    images_list.append(transforms.ToTensor()(image))
            count += 1

        if USE_FOLDER_FOR_SAVE:
            # Load images from a folder
            for pic_address in self.find_files(dir_path, '*.jpg'):
                if FIRST_COUNTER:
                    images_list.append(cv2.imread(pic_address))
                else:
                    images_list.append(read_image(pic_address))

            # Choose which counter to use
        if FIRST_COUNTER:
            response = self.vehicle_counter_1.vehicle_count(images_list, num_pic)
            counter = "and the vehicle counting (First)."
        else:
            response = self.vehicle_counter_2.vehicle_count_2(images_list, num_pic)
            counter = "and the car recognition second (Second)."

        print("Divided in segments | " + save + counter)
        self.empty_dir()

        # cloud_response = self.send_to_cloud(response)
        # print(f"Answer from cloud: {cloud_response.text}")

        return response

    @staticmethod
    def send_to_cloud(road_info):
        print(road_info)
        response = requests.post(
            url="http://127.0.0.1:8000/cloud/information",
            data=road_info
        )
        return response
