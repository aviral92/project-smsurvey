import argparse

import smsurvey.interface.interfaces_master as li

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", action="store_true", dest="local")
    args = parser.parse_args()

    li.initiate_interface()

