import logging
import time
import datetime


class CloudMain:
    def __init__(self):
        self.txt_file = None

    def create_logs(self, txt_log):
        dt = datetime.datetime.fromtimestamp(time.time())
        # format the datetime object as a string with the hour in 24-hour format
        date_string = dt.strftime('%d-%m-%Y %H:%M:%S')
        self.txt_file.write(f"{date_string} cloud_main     | {txt_log}\n")

    # Define a static method called "road_check" that takes in an argument called "info"
    def road_check(self, info):
        self.txt_file = open('/data/cloud_logs.txt', 'a')

        # Check if the "info" argument is a dictionary
        if type(info) is dict:
            # Print the dictionary from basestation
            print(f"Dictionary from basestation with number of vehicles: \n{info}")
            logging.error(f"Dictionary from basestation with number of vehicles: \n{info}")
            self.create_logs(f"Dictionary from basestation with number of vehicles: {info}")
            # Return True if "info" is a dictionary
            return True
        # Return False if "info" is not a dictionary
        return False
