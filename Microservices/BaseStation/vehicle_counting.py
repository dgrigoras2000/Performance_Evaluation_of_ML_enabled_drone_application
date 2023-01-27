import glob

import cv2

from Microservices.BaseStation.vehicle_detector import VehicleDetector

IMG_DIR = "C:\\Users\\user\\PycharmProjects\\A_D_E_Origin\\Microservices\\BaseStation\\Basestation_Images\\*.jpg"


class VehicleCounting:

    def __init__(self):
        # Load Vehicle Detector
        self.vd = VehicleDetector()

        # Load images from a folder
        self.images_folder = glob.glob(IMG_DIR)

        self.vehicles_folder_count = 0

    @staticmethod
    def get_pic_name(img_path):
        path_list = img_path.split("\\")
        name_pic = path_list[len(path_list) - 1][:-4]
        return str(name_pic)

    @staticmethod
    def count_vehicles(vehicle_boxes, img, vehicle_count):
        # count = 0
        for box in vehicle_boxes:
            x, y, w, h = box

            cv2.rectangle(img, (x, y), (x + w, y + h), (25, 0, 180), 3)
            cv2.putText(img, "Vehicles: " + str(vehicle_count), (20, 50), 0, 2, (100, 200, 0), 3)

        # cv2.imshow(f"Cars{count}", img)
        # count += 1
        cv2.waitKey(1)

    def vehicle_count(self, images_details, img_number):
        vehicle_count_dict = {}
        counter = 0

        for image_arr in images_details:
            if not img_number:
                img_name = f"pic{counter}"
            else:
                img_name = f"pic{img_number + counter}"

            vehicle_boxes = self.vd.detect_vehicles(image_arr)
            vehicle_count = len(vehicle_boxes)

            # Update total count
            vehicle_count_dict[img_name] = vehicle_count

            self.count_vehicles(vehicle_boxes, image_arr, vehicle_count)

            counter += 1

        return vehicle_count_dict
