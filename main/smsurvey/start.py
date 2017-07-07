import argparse

import smsurvey.interface.launch_interfaces as li

from smsurvey import config

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", action="store_true", dest="local")
    args = parser.parse_args()

    li.initiate_interface()

