from __future__ import print_function

import os
import time
import logging
import datetime
import argparse
import subprocess
from distutils.spawn import find_executable

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--interval", type=int, default=15, help="Interval for taking a picture (expressed in minutes)")
    parser.add_argument("--length", type=int, default=8 * 60, help="The timelapse will be running for that much time (expressed in minutes)")
    parser.add_argument("--image-name", type=str, default="pi_timelapse", required=False, help="Name (without extension) of the output images")
    parser.add_argument("output_dir", type=str, help="Where to save the images")

    args = parser.parse_args()
    return args

def run_timelapse(log, args):
    current_time = datetime.datetime.now()
    end_time = current_time + datetime.timedelta(minutes=args.length)

    log.info("Hello! We're about to start a new timelapse..")

    original_dir = os.getcwd()
    output_dir = os.path.abspath(args.output_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        if not os.path.isdir(output_dir):
            raise IOError("Output dir exists but is not a directory! %s" % output_dir)

    if not find_executable("raspistill"):
        log.error("'raspistill' was not found in the $PATH !")
        return

    os.chdir(output_dir)
    current_frame = 1001

    try:
        while current_time < end_time:
            current_time = datetime.datetime.now()
            output_file_name = "{name}.{frame}.jpg".format(name=args.image_name, frame=current_frame)
            log.info("Taking picture: %s", output_file_name)

            command = ["raspistill", "--timeout", "1", "-o", output_file_name]
            p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()

            if p.returncode != 0:
                log.error("Error while running raspistill: %s", err)
                log.error("Stopping executing of timelapse")
                break
            else:
                time.sleep(args.interval * 60)
                current_frame += 1

    except KeyboardInterrupt:
        os.chdir(original_dir)
        log.info("User pressed CTRL+C, exiting..")

    except Exception:
        os.chdir(original_dir)
        raise

    current_time = datetime.datetime.now()
    log.info("Timelapse finished at %s.", current_time)

def main():

    log = logging.getLogger("timelapse")

    logging.root.handlers = []

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    log.addHandler(console_handler)
    log.setLevel(logging.DEBUG)

    args = parse_args()
    run_timelapse(log, args)

if __name__ == "__main__":
    main()
