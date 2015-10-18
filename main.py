import hashkiller
import time
import os
import threading
import Functions
import deathbycaptcha
import sys

from colorama import init
init(strip=not sys.stdout.isatty()) # strip colors if stdout is redirected
from termcolor import cprint
from pyfiglet import figlet_format


__author__ = 'Lambasoft'
__website__ = "www.aymanabiaoun.com"
__version__ = "0.9"
__revision__ = "Beta"
WorkingHashs = []
TotalMd5count = 0


if __name__ == "__main__":

    CurrDir = os.path.dirname(os.path.realpath(__file__))  # Get the current run directory path
    SaveTo = str(time.time()).translate(None, '.') + ".txt"  # Location where the dehashed MD5 will be saved

    Functions.cls()
    print "\n\r"
    cprint(figlet_format('   MD5HashKill', font='big'),
           'yellow', attrs=['bold'])

    print " " * 9 + "-" * 42
    print " " * 10 + "Author: {0} | {1}".format(__author__ , __website__)
    print " " * 10 + "Version: {0} {1}".format(__version__, __revision__)
    print " " * 9 + "-" * 42
    print "\n\r"

    md5 = Functions.setMD5()  # Call setMD5() Function to input the hashs
    TotalMd5count = len(md5)  # Count the hashs before sorting
    md5 = Functions.SortMD5Hashs(md5, 60)  # Sort the hashs by group in a multi-dimensional list
    DBC_Logged = False  # DeathByCaptcha account logged in boolean

    DBC = True  # Are we goint to use DeathByCaptcha ?
    client = None  # DeathByCaptcha socket client

    while not DBC_Logged and DBC is True:
        DBC = Functions.confirm("Would you like to use your DeathByCaptcha account ?")
        if DBC:
            DBC_Username = raw_input("Enter your DBC Username: ")
            DBC_Password = raw_input("Enter your DBC Password: ")
            try:
                # Attempt to log to DBC account with given credentials
                client = deathbycaptcha.SocketClient(DBC_Username, DBC_Password)
                # Print the balance in the DBC account
                print client.get_balance()
                # Successfully Logged in
                DBC_Logged = True
            except Exception, e:
                print "[!] " + e.message

    # Manually pop the cpatcha to be solved
    captchaObj = hashkiller.PopCaptcha

    # Work to be called by the threads
    def ThreadWork(md5, captchaObj, SaveTo, DeathByCaptchaClient):
        while not md5.empty():
            try:
                # Declare HashKiller class and set md5 hashs
                hk = hashkiller.HashKiller(md5.get())
                # Attempt to crack the hashs using HashKiller
                hk.CrackMd5(WorkingHashs, captchaObj, SaveTo, DeathByCaptchaClient)
                # Show number of deHashed cracked out of the Total hashs
                print "{0} working out of {1} ...".format(len(WorkingHashs), TotalMd5count)
            except KeyboardInterrupt:
                # Break if CTRL + C is pressed
                break

    # List to store the running threads
    threads = []

    # IF not using DBC only 1 thread can be ran, due to tkinter not being thread safe
    if DBC_Logged:
        # Input the thread number to be ran
        threadNum = raw_input("How many threads would you like to run ? ")

    # Check all threads will have a job to do
    threadNum = 1 if not DBC_Logged else (md5.qsize() - 1 if md5.qsize() < int(threadNum) else int(threadNum))

    # Append the threads to threads list
    for i in range(threadNum):
        print "Starting Thread-{0}".format(i+1)
        t = threading.Thread(target=ThreadWork, args=(md5, captchaObj, SaveTo, client,))
        threads.append(t)

    print "DeHashing Started! Hashes will be saved to: " + CurrDir + "\\" + SaveTo

    # Start the threads
    for x in threads:
        x.start()

    # Join the threads
    for x in threads:
        x.join()
