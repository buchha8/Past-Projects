"""PyAudioThreading. Use Multithreading to play multiple wave files concurrently"""

import threading
import pyaudio
import wave
import sys

CHUNK = 1024

#Define Objects to be used for sound threads
class audioThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        play_audio(self.name)

#Function for audio playback, taken from PyAudio Example        
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

#Store wave files that were passed as arguments into a list of threads, and try to play audio on each thread
threads = list()
for i in range(1, len(sys.argv)):
    try:
        threads.append(audioThread(i, sys.argv[i]))
        threads[i-1].start()
    except:
        print "error: cannot start thread"
