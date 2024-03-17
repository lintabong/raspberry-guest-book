import os
import re
from datetime import datetime
from scipy.io import wavfile

parrent = "result"

if not os.path.exists(parrent):
    os.mkdir(parrent)

def saveSound(rec, freq=44100):
    now = datetime.now().date()
    now = re.sub(r"-", "", str(now))

    if not os.path.exists(f'{parrent}/{now}'):
        os.mkdir(f'{parrent}/{now}')

    num = len(os.listdir(os.path.join(parrent, now))) + 1

    if num < 10:
        num = f'000{num}'
    elif num >= 10 and num < 100:
        num = f'00{num}'
    elif num >= 100 and num < 1000:
        num = f'0{num}'
    else:
        num = f'{num}'

    filename = datetime.now().replace(microsecond=0).time()
    filename = f'{num}_{re.sub(r":", "", str(filename))}'

    wavfile.write(f'{parrent}/{now}/{filename}.wav', freq, rec)

def getSound(path=None):
    return wavfile.read(path)[1]
