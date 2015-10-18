import requests
import cStringIO
import PIL
from Functions import *
from PIL import ImageTk
import Tkinter as TK
from Tkinter import *
import threading

__author__ = 'Lambasoft'
__website__ = "www.aymanabiaoun.com"

threadLock = threading.Lock()


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

isFirstPop = 0


class PopCaptcha(Frame):
    def __init__(self, img):

        def onok(event=None):
            self.captchaText = self.entry1.get()
            self.captchaThread = 1
            self.master.destroy()

        global isFirstPop

        self.captchaThread = 0
        self.captchaText = ""
        TK.Frame.__init__(self)

        isFirstPop += 1
        self.pack()
        self.master.title("Enter Captcha")

        image1 = PIL.Image.open(img)
        tkpi = ImageTk.PhotoImage(image1)

        self.picture1 = Label(self, image=tkpi)
        self.picture1.image = tkpi
        self.picture1.grid(row=1)

        self.entry1 = Entry(self, font=('Helvetica', '14'))
        self.entry1.grid(row=2)

        self.button1 = Button(self, text="SUBMIT", width=25, command=onok)
        self.button1.grid(row=3)

        self.master.bind('<Return>', onok)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.captchaThread = 1
        self.master.destroy()


class HashKiller:
    def __init__(self, hashs):
        self.hashs = hashs
        self.hashQueue = Queue.Queue
        self.error = ""
        self.status = ""
        self.captchaTries = 0
        self.Session = {'view_state': '', 'event_validation': '', 'Captcha': ''}

    def CheckMD5(self):
        pattern = re.compile(r"([a-fA-F\d]{32})")
        m = pattern.match(self.hash)
        if m:
            return True
        return False

    def CrackMd5(self, WorkingHashs, captchaObj, SaveTo, DeathByCaptchaClient = None):
        self.status = ""
        self.error = ""

        hr = requests.get('http://hashkiller.co.uk/md5-decrypter.aspx')
        self.Session['view_state'] = ParseFormNameText(hr.text, "__VIEWSTATE")
        self.Session['event_validation'] = ParseFormNameText(hr.text, "__EVENTVALIDATION")
        self.Session['Cookies'] = hr.cookies


        captchaurl = ParseFormIdSrc(hr.text, "content1_imgCaptcha", "img")
        captchaurl = "http://hashkiller.co.uk" + str(captchaurl)


        hr = requests.get(captchaurl, cookies=self.Session['Cookies'])
        captchafile = cStringIO.StringIO(hr.content)

        while self.status is not "OK" or self.error == "WrongCaptcha":

            if not DeathByCaptchaClient == None:
                hr = requests.get(captchaurl, cookies=self.Session['Cookies'])
                captchafile = cStringIO.StringIO(hr.content)
                captcha = DeathByCaptchaClient.decode(captchafile, 100)
                if captcha:
                    # The CAPTCHA was solved; captcha["captcha"] item holds its
                    # numeric ID, and captcha["text"] item its text.
                    self.Session['Captcha'] = captcha["text"]

            else:
                self.captchaTries += 1
                if (self.captchaTries > 3):
                    hr = requests.get(captchaurl, cookies=self.Session['Cookies'])
                    captchafile = cStringIO.StringIO(hr.content)
                    self.captchaTries = 0

                threadLock.acquire()
                # captcha = PopCaptcha(captchafile)

                captcha = captchaObj(captchafile)
                print "Enter the Captcha..."
                captcha.mainloop()
                threadLock.release()

                while captcha.captchaThread == 0:
                    pass
                self.Session['Captcha'] = captcha.captchaText

            PostData = {
                'ctl00$ScriptMan1' : 'ctl00$content1$updDecrypt|ctl00$content1$btnSubmit',
                'ctl00$content1$txtInput' : "\r\n".join(self.hashs),
                '__EVENTTARGET' : '',
                '__EVENTARGUMENT' : '',
                '__VIEWSTATE' : self.Session['view_state'],
                '__EVENTVALIDATION' :  self.Session['event_validation'],
                '__ASYNCPOST' : 'true',
                'ctl00$content1$btnSubmit' : 'Submit',
                'ctl00$content1$txtCaptcha' : self.Session['Captcha']
            }

            headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
                'X-Requested-With': 'XMLHttpRequest',
                'X-MicrosoftAjax' : 'Delta=true',
                'Pragma' : 'no-cache',
                'content-type': 'application/x-www-form-urlencoded; charset=utf-8',
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Charset' : 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                'Accept-Language' : 'en-US,en;q=0.5'
            }

            r = requests.post("http://hashkiller.co.uk/md5-decrypter.aspx", data=PostData, headers=headers, cookies=self.Session['Cookies'])

            self.status = ParseContent(r.text, 'content1_lblStatus', 'span' ,'id').getText()

            if self.status and not "Please find them below..." in self.status and not "Failed to find any hashes!" in self.status:
                print ("Error: " + BColors.FAIL + "{0}" + BColors.ENDC).format(self.status)
                if "The CAPTCHA code you specifed is wrong" in self.status:
                    self.error = "WrongCaptcha"
            else:
                result = ParseAllContent(r.text , 'text-green', "span" , "class")
                if result:
                    for hashed in ParseMD5Content(r.text ):
                        WorkingHashs.append(hashed[0] + ":" + hashed[1])
                        with open(SaveTo, "a") as myfile:
                            myfile.write("%s\n" % (hashed[0] + ":" + hashed[1]))
                        print ("Hash [{0}] found: " + BColors.OKGREEN + hashed[1] + BColors.ENDC).format(hashed[0])
                else:
                    print ("Hash " + BColors.WARNING + "not found" + BColors.ENDC).format("TODO")

                self.error = "NoError"
                self.status = "OK"






