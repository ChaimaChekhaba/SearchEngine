import os

import lucene

from utils.Evaluation import *

lucene.initVM(vmargs=['-Djava.awt.headless=true'])

directory = "AP/"

def check_file(term, file):
    with open(file, encoding='latin-1') as f:
        if term.lower() in f.read().lower():
            return True
        else:
            return False


OOV = True
for file in os.listdir(directory):
    if check_file("OS ", "AP/" + file):
        OOV = False
        print(file)

if OOV is True:
    print("word ", "OS")
