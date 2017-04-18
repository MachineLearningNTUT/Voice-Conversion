import numpy  as np
import pysptk
import math
import scipy.io.wavfile
import linecache
import matplotlib
import matplotlib.pyplot as plt
from dtw import dtw
import matplotlib.cm as cm
import librosa
import sklearn.neural_network
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import pyrenn
import cmath
from scipy.io import wavfile
from IPython.display import Audio
import pysas
import os
from scipy.io import wavfile
from os import listdir
from os.path import isfile, join
import dspUtil



sourcepath='source/'
source=[]
target=[]
for i in range(10,51):
    if(os.path.exists(sourcepath+'arctic_a00'+str(i)+'.wav')):
        source.append(sourcepath+'arctic_a00'+str(i)+'.wav')
targetpath='target/'  
for i in range(10,51):
    if(os.path.exists(targetpath+'arctic_a00'+str(i)+'.wav')):
        target.append(targetpath+'arctic_a00'+str(i)+'.wav')

frameLength = 1024
overlap = 0.25
hop_length=256
subFrameLength = frameLength * overlap
net=pyrenn.CreateNN([26,30,30,26])
order = 25
alpha = 0.41
gamma = -0.35
count=0
for sourcefile,targetfile in zip(source,target) :
    print(sourcefile,targetfile)
    sr, sx = wavfile.read(sourcefile)
    sourceframes = librosa.util.frame(sx, frame_length=frameLength,
    hop_length=hop_length).astype(np.float64).T
    sourceframes *= pysptk.blackman(frameLength)
    sourcemcepvectors = np.apply_along_axis(pysptk.mcep, 1, sourceframes, order, alpha)
    sr, tx = wavfile.read(targetfile)
    targetframes = librosa.util.frame(tx, frame_length=frameLength,
    hop_length=hop_length).astype(np.float64).T
    targetframes *= pysptk.blackman(frameLength)
    targetmcepvectors = np.apply_along_axis(pysptk.mcep, 1, targetframes, order, alpha)
    reslen=min(len(sourcemcepvectors),len(targetmcepvectors))
    transsourcemcepvectorsmod=np.empty([26,reslen])
    transtargetmcepvectorsmod=np.empty([26,reslen])
    transsourcemcepvectorsmod=np.transpose(sourcemcepvectors[0:reslen])
    transtargetmcepvectorsmod=np.transpose(targetmcepvectors[0:reslen])
    print(len(sourcemcepvectors),len(targetmcepvectors))
    for i in range(len(sourcemcepvectors)):
        for j in range(len(sourcemcepvectors[i])):
            if np.isnan(sourcemcepvectors[i][j]):
                print("yes")
    for i in range(len(targetmcepvectors)):
        for j in range(len(targetmcepvectors[i])):
            if np.isnan(targetmcepvectors[i][j]):
                print("no")
    print("Before",net["w"])
    net=pyrenn.train_LM(transsourcemcepvectorsmod,transtargetmcepvectorsmod,net,k_max=1000,verbose=True,E_stop=5)
    print("After",net["w"])
    count=count+1


sourcepath='source'
sourcefile='arctic_a0018.wav'    
sr, sx = wavfile.read(sourcepath+'/'+sourcefile)
l=len(sx)

sourceframes = librosa.util.frame(sx, frame_length=frameLength,
hop_length=hop_length).astype(np.float64).T

# Windowing
sourceframes*= pysptk.blackman(frameLength)

sourcemcepvectors = np.apply_along_axis(pysptk.mcep, 1, sourceframes, order, alpha) 
mgc=np.empty([len(sourcemcepvectors),26])
mgc=pyrenn.NNOut(sourcemcepvectors.transpose(),net).transpose()
mgc=mgc.copy(order="C")
logHmgc = np.apply_along_axis(pysptk.mgc2sp, 1, mgc, 0.41, 0.0, frameLength)
rawHmgc=np.exp(logHmgc).T
mgcRecover = librosa.core.istft(rawHmgc, hop_length, frameLength,
                                    pysptk.blackman(frameLength))
Audio(mgcRecover, rate=sr)
