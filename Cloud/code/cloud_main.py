import logging


class CloudMain:
    # Define a static method called "road_check" that takes in an argument called "info"
    @staticmethod
    def road_check(info):
        # Check if the "info" argument is a dictionary
        if type(info) is dict:
            # Print the dictionary from basestation
            print(f"Dictionary from basestation with number of vehicles: \n{info}")
            logging.error(f"Dictionary from basestation with number of vehicles: \n{info}")
            # Return True if "info" is a dictionary
            return True
        # Return False if "info" is not a dictionary
        return False
