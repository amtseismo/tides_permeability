#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 12:36:36 2021

some utilities for permeability calculations

@author: amt
"""

import numpy as np
import scipy.special

# fft 
def TF(series, sampling_rate):
    delta_time= 1./sampling_rate
    freq = np.fft.rfftfreq(len(series),delta_time)
    freq = freq[1:]
    fourier= np.fft.rfft(series)
    amplitud= np.abs(fourier)
    phase=np.angle(fourier,deg=True)
    tf_amp=amplitud[1:]
    tf_phase=phase[1:]
    return freq, tf_amp, tf_phase, fourier

def kelvink(n,x):
    a=np.exp(np.pi*1j/4)
    b=np.exp(-n*np.pi*1j/2)
    ke = b*scipy.special.kv(n,x*a)
    ker = np.real(ke)
    kei = np.imag(ke)
    return ker, kei