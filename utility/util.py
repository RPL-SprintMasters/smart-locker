import math
import os
import random

def generateOTP() :
    string = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    OTP = ""
    length = len(string)
    for i in range(6):
        OTP += string[math.floor(random.random() * length)]
    return OTP

def make_dir(newpath):
    if not os.path.exists(newpath):
        os.makedirs(newpath)
        print(f"[MKDIR] Successfully created folder {newpath}")