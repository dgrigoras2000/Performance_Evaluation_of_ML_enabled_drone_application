import fnmatch
import os

import requests
import simplejson as json

img_dir_path = "Pics_drones"
ALL_TOGETHER = bool(os.environ['ALL_TOGETHER'])
NUMBER_OF_IMAGES = int(os.environ['NUMBER_OF_IMAGES'])

class DroneMain:
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

        print(f"Basestation response: {response}")
        return

    ############################################################################################

    def send_images(self, num_of_pics):
        res = {}
        response = {}

        print("Waiting for connection establishment...")

        try:
            response = requests.get(url="http://172.20.0.2:8000/check/connection")
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            raise SystemExit(e)

        print(json.loads(response.text) + "\n\n" + "Waiting for basestation response...\n")

        if ALL_TOGETHER:
            way_of_send = "Use list to send all pictures together "
            try:
                response = requests.post(
                    url=f"http://172.20.0.2:8000/import/images/0",
                    files=self.images_list
                )
            except requests.exceptions.RequestException as e:  # This is the correct syntax
                raise SystemExit(e)

            response = json.loads(response.text)["cars_per_pic"]
        else:
            num_pics = NUMBER_OF_IMAGES
            way_of_send = f"Use segments to send pictures in list with number of pics to group: {num_pics}."
            list_num_elements = []
            for num_pic in range(0, num_of_pics, num_pics):
                for x in range(0, num_pics):
                    if num_pic + x < num_of_pics:
                        list_num_elements.append(self.images_list[num_pic + x])

                try:
                    half_response = requests.post(
                        url=f"http://172.20.0.2:8000/import/images/{num_pic}",
                        files=list_num_elements
                    )
                except requests.exceptions.RequestException as e:  # This is the correct syntax
                    raise SystemExit(e)

                response.update(json.loads(half_response.text)["cars_per_pic"])
                list_num_elements = []

        res["cars_per_pic"] = response
        print(way_of_send)
        return res


if __name__ == "__main__":
    run = DroneMain()
    run.load_images()
