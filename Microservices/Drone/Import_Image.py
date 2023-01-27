import fnmatch
import os
from distutils.util import strtobool

import requests
import simplejson as json

img_dir_path = "C:\\Users\\user\\PycharmProjects\\A_D_E_Origin\\Microservices\\Drone\\images"


class ImportImage:
    def __init__(self):
        # list to store files
        self.images_list = []
        self.image_arr = None

    @staticmethod
    def find_files(directory, pattern):
        for root, dirs, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)

                    yield filename

    def load_images(self):
        # Load images from a folder
        for filename in self.find_files(img_dir_path, '*.jpg'):
            img_tuple = ('files', open(filename, 'rb'))
            self.images_list.append(img_tuple)

        num_of_pics = len(self.images_list)

        response = self.send_images(num_of_pics)

        print(response)
        return

    ############################################################################################

    def send_images(self, num_of_pics):
        res = {}
        response = {}
        if strtobool(os.environ['all_together']):
            way_of_send = "Use list to send all pictures together "
            response = requests.post(
                url=f"http://127.0.0.1:8000/import/images/0",
                files=self.images_list
            )
            response = json.loads(response.text)["cars_per_pic"]
        else:
            num_pics = int(os.environ['num_pics'])
            way_of_send = f"Use segments to send pictures in list with number of pics to group: {num_pics}."
            list_num_elements = []
            for num_pic in range(0, num_of_pics, num_pics):
                for x in range(0, num_pics):
                    if num_pic + x < num_of_pics:
                        list_num_elements.append(self.images_list[num_pic + x])
                half_response = requests.post(
                    url=f"http://127.0.0.1:8000/import/images/{num_pic}",
                    files=list_num_elements
                )
                response.update(json.loads(half_response.text)["cars_per_pic"])
                list_num_elements = []

        res["cars_per_pic"] = response
        print(way_of_send)
        return res


def main():
    run = ImportImage()
    run.load_images()


if __name__ == "__main__":
    main()
