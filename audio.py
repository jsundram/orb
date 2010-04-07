import numpy
import math
import pyaudio # Get this from http://people.csail.mit.edu/hubert/pyaudio/
import time
import simplejson
import socket


FORMAT = pyaudio.paInt16 # if you change this, update dtype in the numpy.fromstring line.
CHANNELS = 1
RATE = 44100
CHUNK = 1024
DURATION = .25

P = pyaudio.PyAudio()


def listen(duration=DURATION):
    stream = P.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    audio = []
    for i in range(0, RATE / CHUNK * DURATION):
        try: 
            x = stream.read(CHUNK)
            audio.append(x)
        except IOError, e:
            print e 
    stream.close()
    return ''.join(audio)

# cribbed from my javascript code; if this needs fixing, so does that.
def loudness_factor(db):
    """ db is in dBFS, which has a max of 0, and a min (assuming 16-bit) of -96.
        get a number between 0 and 1 that corresponds to how loud the sound is.
        these seeems to hover around .8-.9; need more discrimination.
    """
    db += 20 # 'calibration factor'
    unit = (db + 96.0) / 96.0; # now in (0, 1)
    
    # exaggerate differences at higher end of loudness.
    return (10 ** unit) / 10.0


def calc_loudness(raw_data):
    samples = numpy.fromstring(raw_data, dtype=numpy.int16)
    max_val = float(2 ** (8 * P.get_sample_size(FORMAT) - 1))
    data = numpy.array(samples, dtype=float) / max_val
    ms = max(10e-8, math.sqrt(numpy.sum(data ** 2.0) / len(data)))
    return 10.0 * math.log(ms, 10.0)


def write_wav(raw_data, filename='test.wav'):
    import wave
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(P.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(raw_data)
    wf.close()

def send_to_orb(db):
    # convert db to a number between 0 and 1
    HOST, PORT = "192.168.1.141", 1337
    my_ip = socket.gethostbyname(socket.gethostname())
    data = simplejson.dumps({'host': my_ip, 'time':time.time(), 'loudness': loudness_factor(db)})
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data + "\n", (HOST, PORT))
    
def main():
    while True:
        raw_data = listen()
        db = calc_loudness(raw_data)
        print 'Loudness (averaged over %d seconds): %f dB -> %2.2f loudness factor' % (DURATION, db, loudness_factor(db))
        if False:
            write_wav(raw_data)
        send_to_orb(db)


if __name__ == "__main__":
    main()