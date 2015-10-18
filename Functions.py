from BeautifulSoup import BeautifulSoup
from urllib import urlencode
import os
import Queue

__author__ = 'Lambasoft'
__website__ = "www.aymanabiaoun.com"


def cls():
    os.system(['clear', 'cls'][os.name == 'nt'])

def ParseFormNameText(text, name, type="input"):
    if not text: return False
    soup = BeautifulSoup(text)
    return soup.find(type, {"name": name})['value']


def ParseFormIdSrc(text, name, type="input"):
    if not text: return False
    soup = BeautifulSoup(text)
    return soup.find(type, {"id": name})['src']

def ParseContent(text, name, type="input" , tag="class"):
    if not text: return False
    soup = BeautifulSoup(text)
    value = soup.find(type, attrs={tag: name})
    if str(value) != "None": return value
    return False

def ParseAllContent(text, name, type="input" , tag="class"):
    if not text: return False
    soup = BeautifulSoup(text)
    value = soup.findAll(type, attrs={tag:name})
    return value

def ParseMD5Content(text , name="text-green"):
    if not text: return False
    text = ParseContent(text, "results" , "span" , "class")
    text = str(text).replace("<br />" , "\r\n")
    results = []
    for content in str(text).split("\n"):
        if " MD5 :" not in content: continue
        md5 = content[:content.index(" MD5 :")]
        results.append([md5[-32:], ParseContent(content, name, "span", "class").getText()])
    return results

def confirm(prompt=None, resp=False):
    if prompt is None:
        prompt = 'Confirm'

    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')

    while True:
        ans = raw_input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False

def setMD5():
    isValid = False
    while not isValid:
        answer = raw_input("Enter MD5 hash or .txt path: ")
        if ".txt" in answer:
            if os.path.isfile(answer):
                with open(answer, 'r') as f:
                    results = f.read().splitlines()
                    return results
                isValid = True
            else:
                print "[!] Please make sure the file exist"
                isValid = False
        else:
            if len(answer) >= 32:
                return [answer]
                isValid = True


def SortMD5Hashs(hashs, max=60):
    results = Queue.Queue()
    if len(hashs) < max:
        results.put(hashs)
    else:
        for i in range(0, (len(hashs) / max) + 1):
            if hashs[i*max:i*max + max*1]:
                results.put(hashs[i*max:i*max + max*1])

    return results
