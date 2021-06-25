#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 19:36:34 2021

Permeability estimates

@author: amt
"""

import numpy as np
import matplotlib.pyplot as plt
import permeability_utils

# ---------------- Xue measured amp and phase ----------------

# I opted to try to reproduce the earliest point on Figure 4, which has permeability of ~1.1e-15 and S of 2.34e-4
measured_phase=-25.5 # earliest point on Figure 3
measured_amp=7e-7 #  earliest point on Figure 3 1/m

# ---------------- constants we need to specify ----------

rho= 1000 # density [kg/m^3]
g= 9.81 # gravity [m/s^2]
mu= 10**-3 # viscosity [Pa*s]
porosity= 0.1 # porosity [dimensionless]
K_solid= 1/(4e-10) # bulk modulus of rock [Pa] reciprocal of compressibility
K_fluid= 1/(1e-9) # buld modulus of fluid [Pa] reciprocal of compressibility
# SS= rho*g*((1/K_solid)+(porosity/K_fluid)) # specific storage in [1/m] this comes from Hsieh88
rc= 0.08 # radius of well casing [m] from Xue -- (for later 4.55/2*0.0254 -- 4.55 inches diameter from Don T. email, converted to radius and meters)
rw= 0.09 # radius of open portion of the well [m] from Xue -- (for later # 3.825/2*0.0254) 3.825 inches diameter from Don T. email, converted to radius and meters
tau= 12.4206*3600 #12.4206*3600 # period of disturbance [s]
omega= 2*np.pi/tau # angular frequency [rad/s]
d= 400 # thickness of the open interval of the well [m]

# -------------------- do the calculation -----------
S=np.logspace(-7,-2,num=1000)
T=np.logspace(-7,-2,num=1000)
AR=np.zeros((len(S),len(T)))
eta=np.zeros((len(S),len(T)))
for ii in range(len(S)):
    for jj in range(len(T)):
        alphaw=np.sqrt(omega*S[ii]/T[jj])*rw # [dimensionless] -- this is Hsieh eq. 10
        Ker0, Kei0 = permeability_utils.kelvink(int(0), alphaw)
        Ker1, Kei1 = permeability_utils.kelvink(int(1), alphaw);
        phi=-(Ker1+Kei1)/(np.sqrt(2)*alphaw*(Ker1**2+Kei1**2)) # [dimensionless] -- this is Hsieh eq. 8, note the mistake in the paper--the Kei1 is not squared and should be
        psi=-(Ker1-Kei1)/(np.sqrt(2)*alphaw*(Ker1**2+Kei1**2)) # [dimensionless] -- this is Hsieh eq. 9
        E=1-omega*rc**2/(2*T[jj])*(psi*Ker0+phi*Kei0)  # -- [dimensionless] this is Hsieh87 eq. 13      
        F=omega*rc**2/(2*T[jj])*(phi*Ker0+psi*Kei0) # -- [dimensionless] this is Hsieh87 eq. 14
        eta[ii,jj]=-1*np.arctan(F/E)*180/np.pi
        AH=1/np.sqrt(E**2+F**2) # this is the dimensionless amplitude of Hsieh -- complex amplitude of water level/complex amplitude of pressure head [dimensionless]          
        A=1/AH # now complex amplitude of pressure head/complex amplitude of water level [dimensionless] 
        AR[ii,jj]=A*S[ii]/d # this converts to measured amplitude, strain/water level, in [1/m] 

# --------------- make figure -----------------------
X,Y=np.meshgrid(T,S)
fig=plt.figure(constrained_layout=True,figsize=(20,10))
gs = fig.add_gridspec(1, 2)
ax0 = fig.add_subplot(gs[0])
ax1 = fig.add_subplot(gs[1])
cmap0=ax0.contourf(X, Y, np.log10(AR), cmap='viridis') # np.arange(-8,-2,.5), cmap='viridis')
CS=ax0.contour(cmap0,colors='w')
ax0.set_yscale('log')
ax0.set_xscale('log')
ax0.set_ylabel('S',fontsize=14)
ax0.set_xlabel('T',fontsize=14)
plt.colorbar(cmap0, ax=ax0)
ax0.set_title('Amplitude Response',fontsize=16)
cmap1=ax1.contourf(X, Y, eta, np.arange(-90,10,10), cmap='viridis')
ax1.contour(cmap1,colors='w')
ax1.set_title('eta (degrees)')
ax1.set_yscale('log')
ax1.set_xscale('log')
ax1.set_ylabel('S',fontsize=14)
ax1.set_xlabel('T',fontsize=14)
plt.colorbar(cmap1, ax=ax1)
ax1.set_title('Phase Response',fontsize=16)

# --------------- find optimal T and S and calculate permeability and diffusivity -----------------------
phasetol=20
amptol=1
indx=[]
flag=0
while len(indx)!=1:
    print(len(indx))
    if len(indx)==0:
        if flag==1:
            phasetol*=1.1
            amptol*=1.1
        else:
            phasetol*=2
            amptol*=2
    else:
        phasetol/=2  
        amptol/=2
        flag=1
    aindx,aindy=np.where((np.abs(np.log10(AR)-np.log10(measured_amp))<amptol*np.abs(np.log10(measured_amp))))
    pindx,pindy=np.where(np.abs(eta-measured_phase)<phasetol)
    indx,indy=np.where((np.abs(np.log10(AR)-np.log10(measured_amp))<amptol*np.abs(np.log10(measured_amp))) & (np.abs(eta-measured_phase)<phasetol))
    
for ii in range(len(aindx)):
    ax0.plot(X[aindx[ii],aindy[ii]],Y[aindx[ii],aindy[ii]],'k+')  
for ii in range(len(indx)):
    ax0.plot(X[indx[ii],indy[ii]],Y[indx[ii],indy[ii]],'ro')
for ii in range(len(pindx)):
    ax1.plot(X[pindx[ii],pindy[ii]],Y[pindx[ii],pindy[ii]],'k+')     
for ii in range(len(indx)):  
    ax1.plot(X[indx[ii],indy[ii]],Y[indx[ii],indy[ii]],'ro')
    
if len(indx)==1:
    Tbest=X[indx[0],indy[0]]
    Sbest=Y[indx[0],indy[0]]
    print("Estimated phase = "+str(eta[indx[0],indy[0]]))
    print("Measured phase = "+str(measured_phase))
    print("Estimated Amp = "+str(AR[indx[0],indy[0]]))
    print("Measured phase = "+str(measured_phase))
    print("T is "+str(Tbest))
    print("S is "+str(Sbest))
    print("Hydraulic diffusivity is "+str(Tbest/Sbest))
    print("Permeability is " +str(mu/(rho*g*d)*Tbest))

fig.savefig("s_and_t.png",bbow_inches='tight')  