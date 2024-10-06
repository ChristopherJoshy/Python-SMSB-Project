#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import shutil
import sys
import subprocess
import string
import random
import json
import re
import time
import argparse
import zipfile
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.decorators import MessageDecorator
from utils.provider import APIProvider

try:
    import requests
    from colorama import Fore, Style
except ImportError:
    print("\tSome dependencies could not be imported (possibly not installed)")
    print("Type `pip3 install -r requirements.txt` to install all required packages")
    sys.exit(1)


def read_isd_codes():
    with open("isdcodes.json") as file:
        return json.load(file)


def get_version():
    try:
        return open(".version", "r").read().strip()
    except Exception:
        return '1.0'


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def display_banner():
    clear_console()
    logo = """
    
    CJ BomBer
"""
    if ASCII_MODE:
        logo = ""
    version = f"Version: {__VERSION__}"
    contributors = "Contributors: " + " ".join(__CONTRIBUTORS__)
    print(random.choice(ALL_COLORS) + logo + RESET_ALL)
    mesgdcrt.SuccessMessage(version)
    mesgdcrt.SectionMessage(contributors)
    print()


def check_internet_connection():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False


def format_phone_number(num):
    return ''.join(filter(str.isdigit, num)).strip()


def perform_zip_update():
    success = False
    zip_url = "https://github.com/TheSpeedX/TBomb/archive/dev.zip" if DEBUG_MODE else "https://github.com/TheSpeedX/TBomb/archive/master.zip"
    dir_name = "TBomb-dev" if DEBUG_MODE else "TBomb-master"
    
    print(ALL_COLORS[0] + "Downloading ZIP ... " + RESET_ALL)
    response = requests.get(zip_url)
    if response.status_code == 200:
        zip_content = response.content
        try:
            with zipfile.ZipFile(BytesIO(zip_content)) as zip_file:
                for member in zip_file.namelist():
                    filename = os.path.split(member)
                    if filename[1]:
                        new_filename = os.path.join(filename[0].replace(dir_name, "."), filename[1])
                        with zip_file.open(member) as source, open(new_filename, "wb") as target:
                            shutil.copyfileobj(source, target)
            success = True
        except Exception:
            mesgdcrt.FailureMessage("Error occurred while extracting!!")
    
    if success:
        mesgdcrt.SuccessMessage("CJ Bomber was updated to the latest version")
        mesgdcrt.GeneralMessage("Please run the script again to load the latest version")
    else:
        mesgdcrt.FailureMessage("Unable to update CJ Bomber.")
        mesgdcrt.WarningMessage("Grab the latest one from https://github.com/TheSpeedX/TBomb.git")

    sys.exit()


def perform_git_update():
    success = False
    try:
        print(ALL_COLORS[0] + "UPDATING " + RESET_ALL, end='')
        process = subprocess.Popen("git checkout . && git pull", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        while process:
            print(ALL_COLORS[0] + '.' + RESET_ALL, end='')
            time.sleep(1)
            if process.poll() is not None:
                break
        success = not process.returncode
    except Exception:
        success = False
    print("\n")

    if success:
        mesgdcrt.SuccessMessage("CJ Bomber was updated to the latest version")
        mesgdcrt.GeneralMessage("Please run the script again to load the latest version")
    else:
        mesgdcrt.FailureMessage("Unable to update CJ Bomber.")
        mesgdcrt.WarningMessage("Make sure to install 'git'")
        mesgdcrt.GeneralMessage("Then run command:")
        print("git checkout . && git pull https://github.com/TheSpeedX/TBomb.git")

    sys.exit()


def update():
    if shutil.which('git'):
        perform_git_update()
    else:
        perform_zip_update()


def check_for_updates():
    if DEBUG_MODE:
        mesgdcrt.WarningMessage("DEBUG MODE Enabled! Auto-Update check is disabled.")
        return
    mesgdcrt.SectionMessage("Checking for updates")
    fver = requests.get("https://raw.githubusercontent.com/TheSpeedX/TBomb/master/.version").text.strip()
    
    if fver != __VERSION__:
        mesgdcrt.WarningMessage("An update is available")
        mesgdcrt.GeneralMessage("Starting update...")
        update()
    else:
        mesgdcrt.SuccessMessage("CJ Bomber is up-to-date")
        mesgdcrt.GeneralMessage("Starting CJ Bomber")


def notify():
    try:
        noti = "Ellam Working Annu Enthelum Kuzapam Undel Enne Villiku"
        mesgdcrt.SectionMessage("NOTIFICATION: " + noti)
    except Exception:
        pass


def get_phone_info():
    while True:
        cc = input(mesgdcrt.CommandMessage("Enter your country code (Without +): "))
        cc = format_phone_number(cc)
        if not country_codes.get(cc, False):
            mesgdcrt.WarningMessage(f"The country code ({cc}) that you have entered is invalid or unsupported")
            continue
        
        target = input(mesgdcrt.CommandMessage(f"Enter the target number: +{cc} "))
        target = format_phone_number(target)
        
        if len(target) < 7 or len(target) > 11:
            mesgdcrt.WarningMessage(f"The phone number ({target}) that you have entered is invalid")
            continue
        
        return cc, target


def get_email_info():
    mail_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    
    while True:
        target = input(mesgdcrt.CommandMessage("Enter target mail: "))
        if not re.search(mail_regex, target, re.IGNORECASE):
            mesgdcrt.WarningMessage(f"The mail ({target}) that you have entered is invalid")
            continue
        
        return target


def pretty_print(cc, target, success, failed):
    requested = success + failed
    mesgdcrt.SectionMessage("Bombing is in progress - Please be patient")
    mesgdcrt.GeneralMessage("Please stay connected to the internet")
    mesgdcrt.GeneralMessage(f"Target       : {cc} {target}")
    mesgdcrt.GeneralMessage(f"Sent         : {requested}")
    mesgdcrt.GeneralMessage(f"Successful   : {success}")
    mesgdcrt.GeneralMessage(f"Failed       : {failed}")
    mesgdcrt.WarningMessage("Ethu kondu Nigal enthu chyithalum ente Uthravadithyam alla")
    mesgdcrt.SuccessMessage("CJ Bomber was created by CJ")


def worker_node(mode, cc, target, count, delay, max_threads):
    api = APIProvider(cc, target, mode, delay=delay)
    clear_console()
    mesgdcrt.SectionMessage("Gearing up the Bomber - Please be patient")
    mesgdcrt.GeneralMessage("Please stay connected to the internet")
    mesgdcrt.GeneralMessage("API Version   : " + api.api_version)
    mesgdcrt.GeneralMessage("Target        : " + cc + target)
    mesgdcrt.GeneralMessage("Amount        : " + str(count))
    mesgdcrt.GeneralMessage("Threads       : " + str(max_threads) + " threads")
    mesgdcrt.GeneralMessage("Delay         : " + str(delay) + " seconds")
    mesgdcrt.WarningMessage("Ethu verum bomb alla edivettu Bomb")
    print()
    input(mesgdcrt.CommandMessage("Press [CTRL+Z] to suspend the bomber or [ENTER] to resume it"))

    if len(APIProvider.api_providers) == 0:
        mesgdcrt.FailureMessage("Your country/target is not supported yet")
        mesgdcrt.GeneralMessage("Feel free to reach out to us")
        input(mesgdcrt.CommandMessage("Press [ENTER] to exit"))
        display_banner()
        sys.exit()

    success, failed = 0, 0
    while success < count:
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            jobs = [executor.submit(api.hit) for _ in range(count - success)]

            for job in as_completed(jobs):
                result = job.result()
                if result:
                    success += 1
                else:
                    failed += 1
                pretty_print(cc, target, success, failed)

    print()
    mesgdcrt.SuccessMessage("Target bombing completed")


def parse_arguments():
    parser = argparse.ArgumentParser(description="CJ Bomber - A simple tool for bombarding")
    parser.add_argument("-c", "--count", type=int, default=20, help="Number of messages to send")
    parser.add_argument("-m", "--mode", choices=["sms", "mail"], required=True, help="Mode of bombing (sms/mail)")
    parser.add_argument("-t", "--delay", type=float, default=1, help="Delay between messages in seconds")
    parser.add_argument("-th", "--threads", type=int, default=10, help="Number of threads to use")
    return parser.parse_args()


def main():
    global __VERSION__, ASCII_MODE, __CONTRIBUTORS__, RESET_ALL, ALL_COLORS, DEBUG_MODE, country_codes, mesgdcrt

    __VERSION__ = get_version()
    country_codes = read_isd_codes()
    ASCII_MODE = False
    DEBUG_MODE = False
    ALL_COLORS = [Fore.GREEN, Fore.RED, Fore.BLUE, Fore.YELLOW, Fore.CYAN]
    RESET_ALL = Style.RESET_ALL
    mesgdcrt = MessageDecorator()

    display_banner()
    check_internet_connection()
    check_for_updates()
    notify()

    args = parse_arguments()

    if args.mode == 'sms':
        cc, target = get_phone_info()
    else:
        target = get_email_info()
        cc = None

    worker_node(args.mode, cc, target, args.count, args.delay, args.threads)

if __name__ == "__main__":
    main()
