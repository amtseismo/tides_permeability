#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  1 20:57:54 2021

A script to calculate phase angles and amplitudes from teh Xue et al. data

@author: amt
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import datetime
import matplotlib.dates as mdates
import permeability_utils
from scipy import signal

# set some options
pd.set_option("display.max_rows", None, "display.max_columns", None)

# read in Xue et al. [2013] data
df=pd.read_csv('/Users/amt/Documents/hawaii_permeability/waterlevel.csv',
                      names=['date','time','height'],skiprows=7,parse_dates=True,delim_whitespace=True)

# read tides from ertid
ertides=pd.read_csv('xue_tides_2021', names=['NN','EE'], delim_whitespace=True)
ertides['datetime']=pd.date_range("2010-01-01", periods=len(ertides), freq="2T")
ertides['dila']=-10**-9*(ertides['EE']+ertides['NN'])*(1-2*0.25)/(1-0.25) # areal strain --> dilatation

# # plot the tides
# fig1 = plt.figure(constrained_layout=True,figsize=(12,5))
# gs = fig1.add_gridspec(1, 1)
# f1_ax1 = fig1.add_subplot(gs[0])
# smalldates = mdates.date2num(ertides['datetime'].values)
# f1_ax1.plot_date(smalldates[:5040], ertides['dila'].values[:5040])
# f1_ax1.grid(True)
# f1_ax1.set_xlim((smalldates[0],smalldates[5040]))
# f1_ax1.set_xlabel('Date',fontsize=18)
# f1_ax1.set_ylabel('Dilatational Strain',fontsize=18)
# f1_ax1.set_title('Tides at WFSD-1',fontsize=22)
# fig1.savefig("wfsd_tides.png",bbow_inches='tight')

# get things into datetime format
waterdata=pd.DataFrame()
new = df["date"].str.split("-",expand=True)
waterdata['day']=new[0]
waterdata['month']=new[1]
waterdata['year']=new[2]
new = df["time"].str.split(":",expand=True)
waterdata['hour']=new[0]
waterdata['minute']=new[1]
waterdata['second']=new[2]
d = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
waterdata['month']=waterdata['month'].map(d)
df['datetime']=pd.to_datetime(waterdata)-datetime.timedelta(hours=8) # convert beijing time to UTC date time
df=df.drop(columns=['date','time'])

# original data has NaNs in some places, drop them
df=df.dropna()

# plot original data
fig2 = plt.figure(constrained_layout=True,figsize=(12,5))
gs = fig2.add_gridspec(1, 1)
f2_ax1 = fig2.add_subplot(gs[0])
smalldates = mdates.date2num(df['datetime'].values)
f2_ax1.plot_date(smalldates[:100000], df['height'].values[:100000],label='original')
f2_ax1.grid(True)
f2_ax1.set_xlim((smalldates[0],smalldates[100000]))
f2_ax1.set_xlabel('Date',fontsize=18)
f2_ax1.set_ylabel('Water level data (m)',fontsize=18)
f2_ax1.set_title('Water levels at WFSD-1',fontsize=22)

# resample to 2 minute intervals 
df=df.resample('2T', on='datetime').mean()

# for some reason the resampling deletes the index so add it back
df=df.reset_index()

# also sampling to 2 minute intervals reintroduces NaNs so interpolate individual NaNs and cull the rest
print(df['height'].isna().sum())
df=df.interpolate(limit=2)
print(df['height'].isna().sum())
df=df.dropna()
print(df['height'].isna().sum())

# # plot resampled timeseries
# smalldates = mdates.date2num(df['datetime'].values)
# plt.plot_date(smalldates[:100000], df['height'].values[:100000], fmt='o',label='resampled')
# f2_ax1.set_ylim((520.4,520.8))
# f2_ax1.legend()
# fig2.savefig("wfsd_water_level.png",bbow_inches='tight')

# initialize output arrays
starttime=[]
ftphasevalues=[]
ccphasevalues=[]
sdphasevalues=[]
ampvalues=[]
meanccampvalues=[]

# windowlength in days
winlen=29.6

# filter timeseries
# xue filtered from 0.8-2.2 cycles per day 
fs=720 # Samples per day
lowcut=0.8 # cycles/day
highcut=2.2 # cycles/day
sos = signal.butter(4, [lowcut, highcut], 'bandpass', fs=fs, output='sos') # make a filter

for ii in range(80):
    # clip to time period of interest
    start=datetime.datetime(2010,1,1,0,0,0)+datetime.timedelta(days=winlen*ii*0.2)
    finish=start+datetime.timedelta(days=winlen)
    print('-------------------START TIME:'+str(start)+'-------------------')
    dfsmall=df[(df['datetime']>=start) & (df['datetime']<finish)].copy()
    
    # # plot time period
    # plt.figure()
    # smalldates = mdates.date2num(dfsmall['datetime'].values)
    # plt.plot_date(smalldates, dfsmall['height'].values)
    
    # find largest section of contiguous data
    dt = dfsmall['datetime']
    tm = pd.Timedelta('2T')
    in_block = ((dt - dt.shift(-1)).abs() == tm) | (dt.diff() == tm)
    filt = dfsmall.loc[in_block]
    breaks = filt['datetime'].diff() != tm
    dfsmall['groups'] = breaks.cumsum()
    dfsmall=dfsmall[dfsmall['groups']==dfsmall['groups'].mode()[0]]
    
    # clip to time period of interest
    ertidessmall=ertides[(ertides['datetime']>=dfsmall.iloc[0]['datetime']) & (ertides['datetime']<=dfsmall.iloc[-1]['datetime'])].copy()

    # plt.figure()
    # smalldates = mdates.date2num(ertidessmall['datetime'].values)
    # plt.plot_date(smalldates, ertidessmall['dila'].values)   
    
    # check timeseries
    if len(ertidessmall)<30*24*14:
        continue
    elif ertidessmall.iloc[0]['datetime'] != dfsmall.iloc[0]['datetime']:
        #raise NameError('start times arent the same')
        print('start times arent the same')
        continue
    elif ertidessmall.iloc[-1]['datetime'] != dfsmall.iloc[-1]['datetime']:
        # raise NameError('end times arent the same')
        print('end times arent the same')
        continue
    elif len(ertidessmall) != len(dfsmall):
        #raise NameError('end times arent the same')
        print('end times arent the same')
        continue
        
    # filter the data
    dfsmall['heightfilt'] = signal.sosfiltfilt(sos, dfsmall['height'].values) # apply the filter
    # dont think Xue filitered but I am unsure
    ertidessmall['dilafilt'] = ertidessmall['dila'] #signal.sosfiltfilt(sos, ertidessmall['dila'].values) 
    
    # calculate spectra
    # water_freq, water_amp, water_phase, water_spec=TF(dfsmall['height'].values, 1/2)
    water_freq, water_amp, water_phase, water_spec=permeability_utils.TF(dfsmall['heightfilt'].values, 1/2)
    tid_freq, tid_amp, tid_phase, tid_spec=permeability_utils.TF(ertidessmall['dilafilt'].values, 1/2)
    divspec=water_spec/tid_spec
    
    # change frequencies to hours
    tid_freq=1/(tid_freq*60)
    water_freq=1/(water_freq*60)
    
    # cross correlate timeseries
    cc=np.correlate(dfsmall['heightfilt'].values,ertidessmall['dilafilt'].values,mode='full')
    lag=np.where(cc==np.max(cc))[0][0]-len(ertidessmall)+1
    ccphaselag=lag*2/(12.421*60)*360
    
#     # check cc shift
#     # fig, ax=plt.subplots()
#     # ax.plot(dfsmall['heightfilt'].values,label='height',color='r')
#     # ax.legend()
#     # axb=ax.twinx()
#     # axb.plot(ertidessmall['dilafilt'].values,label='tides',color='b')
#     # axb.plot(np.roll(ertidessmall['dilafilt'].values,lag),label='tides shifted',color='k')
#     # axb.legend()
    
    if ii==0:
        # make a plot
        fig = plt.figure(figsize=(16,6))
        spec = gridspec.GridSpec(ncols=2, nrows=1, width_ratios=[2, 1])
        ax0 = fig.add_subplot(spec[0])
        #ax0.plot(dfsmall['datetime'].values,dfsmall['height'].values, label='water level')
        #ax0.plot(dfsmall['datetime'].values,dfsmall['height'].values, label='unfiltered water level')
        ax0.plot(dfsmall['datetime'].values,dfsmall['heightfilt'].values, label='filtered water level')
        #ax0.plot(dfsmall['datetime'].values,dfsmall['height'].values-dfsmall['hourly'].values, label='water level')
        ax0.set_xlabel('Time',fontsize=18)
        ax0.set_ylabel('Water level (m)',fontsize=18)
        ax0.legend()
        ax0.set_xlim((dfsmall['datetime'].values[0],dfsmall['datetime'].values[-1]))
        ax0.grid(True)
        ax0b=ax0.twinx()
        #ax0b.plot(ertidessmall['datetime'].values, ertidessmall['dila'].values,'r', label='tidal strain (load only)')
        ax0b.plot(ertidessmall['datetime'].values, ertidessmall['dilafilt'].values,'r', label='filtered tidal strain (load only)')
        ax0b.set_ylabel('Tidal strain',fontsize=18)
        ax0b.legend(loc="lower right")
        ax1 = fig.add_subplot(spec[1])
        ax1.plot(water_freq,water_amp)
        ax1.set_xlim((0,26))
        ax1.set_xlabel('Frequency (hours)',fontsize=18)
        ax1.set_ylabel('Water level amplitude',fontsize=18)
        ax1b=ax1.twinx()
        ax1b.plot(tid_freq,tid_amp,'g')
        ax1b.set_ylabel('Tidal strain amplitude',fontsize=18)
        fig.savefig("tides_wl_example.png",bbox_inches='tight')
    
    print('Phase lags estimates are:')
    print('Cross correlation: '+str(ccphaselag))
    
    # print phase angles
    cp=12.421 # M2 hourly period
    # get water index
    water_ind=np.argmin(np.abs(water_freq-cp))
    #ax1.plot(water_freq[water_ind],water_amp[water_ind],'ko')
    
    # get tide index
    tid_ind=np.argmin(np.abs(tid_freq-cp))
    #ax1b.plot(tid_freq[tid_ind],tid_amp[tid_ind],'ko')
    
    if tid_ind != water_ind:
        raise NameError('Inds arent the same')
    
    print('FT difference: '+str(tid_phase[tid_ind]-water_phase[tid_ind]))
    print('Spectral Division (unstable): '+str(-1*np.angle(divspec[tid_ind],deg=True)))
    print('Amplitude estimate is '+str(tid_amp[tid_ind]/water_amp[tid_ind]))
    ftphasevalues.append(-1*(tid_phase[tid_ind]-water_phase[tid_ind]))
    ccphasevalues.append(-1*ccphaselag)
    sdphasevalues.append(np.angle(divspec[tid_ind],deg=True))
    ampvalues.append(tid_amp[tid_ind]/water_amp[tid_ind])
    starttime.append(start)
    meanccampvalues.append(np.median(np.abs(np.roll(ertidessmall['dilafilt'].values,lag))/np.abs(dfsmall['heightfilt'].values)))
    
dates = mdates.date2num(starttime)
fig4=plt.figure(constrained_layout=True,figsize=(10,4))
gs = fig4.add_gridspec(1, 1)
f4_ax1 = fig4.add_subplot(gs[0])
f4_ax1.plot_date(dates, ftphasevalues, label='FT phase')
f4_ax1.plot_date(dates, ccphasevalues, label='CC phase')
f4_ax1.plot_date(dates, sdphasevalues, label='SD phase')
f4_ax1.grid(True)
f4_ax1.set_ylim((-45,-15))
f4_ax1.set_xlabel('Date',fontsize=18)
f4_ax1.set_ylabel('Phase',fontsize=18)
f4_ax1.legend()
fig4.savefig("wfsd_phases.png",bbow_inches='tight')

fig5=plt.figure(constrained_layout=True,figsize=(10,4))
gs = fig5.add_gridspec(1, 1)
f5_ax1 = fig5.add_subplot(gs[0])
f5_ax1.plot_date(dates, ampvalues, label='FT Amplitude Ratio')
f5_ax1.plot_date(dates, meanccampvalues, label='CC Amplitude Ratio')
f5_ax1.grid(True)
#f5_ax1.set_ylim((11e-6))
f5_ax1.set_xlabel('Date',fontsize=18)
f5_ax1.set_ylabel('Amplitude',fontsize=18)
f5_ax1.legend()
fig5.savefig("wfsd_amps.png",bbow_inches='tight')