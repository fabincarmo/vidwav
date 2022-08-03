# -*- coding: utf-8 -*-
"""
@author: fabincarmo@gmail.com
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Uncomment if you want to use TeX
#from matplotlib import rc
#rc('text', usetex=True)
#rc('font', **{'family':'serif', 'serif':['Computer Modern Roman'], 
#        'monospace': ['Computer Modern Typewriter'], 'size':14})

import matplotlib.animation as manimation
import wave

from matplotlib.ticker import FuncFormatter
def kilo(x, pos):
    return '%1.fk' % (x*1e-3)

def vidwav(wavfile, fps=25):

    FFMpegWriter = manimation.writers['ffmpeg']
    metadata = dict(title='Wav Spectrogram', artist='Matplotlib',
            comment='')
    writer = FFMpegWriter(fps=fps, metadata=metadata, bitrate=3500)
    
    wf = wave.open(wavfile, 'rb')
    
    fs = wf.getframerate()
    N = wf.getnframes()
    duration = N/float(fs)
    bytes_per_sample = wf.getsampwidth()
    bits_per_sample  = bytes_per_sample * 8
    dtype = 'int{0}'.format(bits_per_sample)
    channels = wf.getnchannels()
    
    audio = np.frombuffer(wf.readframes(int(duration*fs*bytes_per_sample/channels)), dtype=dtype)
    audio.shape = (int(audio.shape[0]/channels), channels)
    freqs = np.fft.fftfreq(audio[:,0].shape[0], 1.0/fs) / 1000.0
    max_freq_kHz = freqs.max()
    times = np.arange(audio.shape[0]) / float(fs)
    
    fig = plt.figure(figsize=(6.4, 4.8))
    
    plt.subplot(211)
    plt.plot(times, (audio[:,0]).astype(float)/np.max(np.abs(audio[:,0])), c='k', lw=.3)

    plt.xlim(0,duration)
    plt.ylim(-1,1)
    
    l1, = plt.plot([], [], '#333333', lw=2)
    
    plt.subplot(212)
    plt.specgram(audio[:,0], Fs=fs, cmap=plt.get_cmap('jet'))
    plt.xlim(0,duration)
    plt.ylim(0,max_freq_kHz*1000.0)
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    formatter = FuncFormatter(kilo)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(formatter)
    
    l2, = plt.plot([], [], '#333333', lw=2)
    
#    plt.tight_layout()
    plt.subplots_adjust(bottom=0.09, 
                                 right=0.98, 
                                 top=0.98, 
                                 left=0.08, 
                                 hspace=0.14)
    
    x = np.array([0., 0.])
    y0 = np.array([-1, 1])
    y1 = np.array([0, max_freq_kHz*1000.0])
    
    with writer.saving(fig, "temp.mp4", 100):
        for i in range((int(duration)+1)*fps):
            x += 1.0/float(fps)
            l1.set_data(x,y0)
            l2.set_data(x,y1)
            writer.grab_frame()
    
    import os
    os.system('ffmpeg -y -i "'+wavfile+'" -i temp.mp4 -c:v copy -strict -2 "'+wavfile.split('.')[0]+'.mp4"')
    os.remove("temp.mp4")

def main():
    vidwav("data.wav")

if __name__ == "__main__":
    main()
