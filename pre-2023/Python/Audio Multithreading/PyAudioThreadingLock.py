"""PyAudioThreadingLock. An naive attempt to use locks for better quality"""

import threading
import pyaudio
import wave
import sys

CHUNK = 1024

#Locking does not work in this case, because play_audio function lasts as long as the wave file.
#Thread holds lock for several seconds!
class audioThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        threadLock.acquire()
        play_audio(self.name)
        threadLock.release()
        
def play_audio(wavName):
    wf=wave.open(wavName, 'rb')

    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(CHUNK)

    while data != '':
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()
    p.terminate()
    
if (len(sys.argv)) < 2:
    print("Plays multiple wave files concurrently.\n\nUsage: %s filename1.wav filename2.wav filename3.wav..." % sys.argv[0])
    sys.exit(-1)

threads = list()
#create a single lock to be passed to different threads
threadLock = threading.Lock()

for i in range(1, len(sys.argv)):
    try:
        threads.append(audioThread(i, sys.argv[i]))
        threads[i-1].start()
    except:
        print "error: cannot start thread"

#Have all threads join to pass around lock
for t in threads:
    t.join()
