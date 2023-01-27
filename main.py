import fnmatch
import glob
import io
import os
import os.path
from typing import List

import cv2
import numpy as np
import requests
import uvicorn as uvicorn
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from torchvision import transforms
from torchvision.io.image import read_image

from BaseModels.ImageModel import VehicleCountResponse
from Microservices.BaseStation.car_rec_second import VehicleCounting2
from Microservices.BaseStation.vehicle_counting import VehicleCounting

app = FastAPI()
dir_path = "C:\\Users\\user\\PycharmProjects\\A_D_E_Origin\\Microservices\\BaseStation\\Basestation_Images\\"

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

# Environment Variables
use_folder_for_save = False
first_counter = False
send_all_together = False

if not os.path.exists(dir_path):
    os.mkdir(dir_path)
    print("Directory created.")
else:
    print("Directory already exists.")


def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)

                yield filename


def all_together(files):
    images_list = []
    save = ""
    for file in files:
        contents = file.file.read()
        image = Image.open(io.BytesIO(contents))

        if use_folder_for_save:  # Save in folder and make a list with.
            save = "Use folder to save | "
            save_img(image, files.index(file))
        else:  # Don't save and make a list with numpy ndarray each image.
            save = "No use folder to save | "
            if first_counter:
                image_array = np.array(image)
                images_list.append(image_array)
            else:
                images_list.append(transforms.ToTensor()(image))

    if use_folder_for_save:
        # Load images from a folder
        for pic_address in find_files(dir_path, '*.jpg'):
            if first_counter:
                images_list.append(cv2.imread(pic_address))
            else:
                images_list.append(read_image(pic_address))
    # Choose which counter to use
    if first_counter:
        service = VehicleCounting()
        response = service.vehicle_count(images_list, None)
        counter = "and the vehicle counting (First)."
    else:
        service = VehicleCounting2()
        response = service.vehicle_count_2(images_list, None)
        counter = "and the car recognition second (Second)."

    print("All together | " + save + counter)
    return response


def divide_in_segments(files, num_pic):
    images_list = []
    save = ""
    count = 0
    for file in files:
        contents = file.file.read()
        image = Image.open(io.BytesIO(contents))

        if use_folder_for_save:  # Save in folder and make a list with.
            save = "Use folder to save | "
            save_img(image, num_pic + count)
            # Load images from a folder
        else:  # Don't save and make a list with numpy ndarray each image.
            save = "No use folder to save | "
            if first_counter:
                image_array = np.array(image)
                images_list.append(image_array)
            else:
                images_list.append(transforms.ToTensor()(image))
        count += 1

    if use_folder_for_save:
        # Load images from a folder
        for pic_address in find_files(dir_path, '*.jpg'):
            if first_counter:
                images_list.append(cv2.imread(pic_address))
            else:
                images_list.append(read_image(pic_address))

        # Choose which counter to use
    if first_counter:
        service = VehicleCounting()
        response = service.vehicle_count(images_list, num_pic)
        counter = "and the vehicle counting (First)."
    else:
        service = VehicleCounting2()
        response = service.vehicle_count_2(images_list, num_pic)
        counter = "and the car recognition second (Second)."

    print("Divided in segments | " + save + counter)
    return response


@app.post("/import/images/{num_pic}", response_model=VehicleCountResponse)
async def import_image(num_pic: int, files: List[UploadFile] = File(...)):
    if send_all_together:
        response = all_together(files)
        empty_dir()
        # cloud_response = send_to_cloud(response)
        # print(json.loads(cloud_response.text))
    else:
        response = divide_in_segments(files, num_pic)
        empty_dir()
        # cloud_response = send_to_cloud(response)
        # print(json.loads(cloud_response.text))
        # else:
        #     pass
        # print(response)

    return VehicleCountResponse(
        cars_per_pic=response
    )


def send_to_cloud(cars_per_pic_dict):
    response = requests.post(
        url="http://127.0.0.1:8086/cars/per/picture",
        files=cars_per_pic_dict
    )
    return response


def save_img(pic, pic_num):
    element_formatted = f"pic{str(pic_num)}.jpg"
    file_path = os.path.join(dir_path, element_formatted)
    pic.save(file_path)


def empty_dir():
    filelist = glob.glob(os.path.join(dir_path, "*.jpg"))
    for f in filelist:
        os.remove(f)
