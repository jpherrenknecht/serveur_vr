import numpy as np
import math
import time
import datetime
import os
import folium
tic = time.time()
basedir = os.path.abspath(os.path.dirname(__file__))
import numba
from numba import jit


def previsionv2(tig, GR, tp, latitude, longitude):
    ''' donne les previsions de vent en un point'''
    ''' calcul optimise 1/20eme du temps initial !! '''
    itemp      = (tp - tig) / 3600 / 3
    ilati      = (latitude + 90)
    ilong      = (longitude) % 360
    iitemp     = math.floor(itemp)
    iilati     = math.floor(ilati)
    iilong     = math.floor(ilong)
    ditemp     = itemp%1
    dilati     = ilati%1
    dilong     = ilong%1
    v000       = GR[iitemp][iilati][iilong]
    v010       = GR[iitemp][iilati+1][iilong]
    v001       = GR[iitemp][iilati][iilong+1]
    v011       = GR[iitemp][iilati+1][iilong+1]
    v0x0       = v000+dilati*(v010-v000)
    v0x1       = v001+dilati*(v011-v001)
    v0xx       = v0x0+dilong*(v0x1-v0x0)
    v100       = GR[iitemp+1][iilati][iilong]
    v110       = GR[iitemp+1][iilati+1][iilong]
    v101       = GR[iitemp+1][iilati][iilong+1]
    v111       = GR[iitemp+1][iilati+1][iilong+1]
    v1x0       = v100+dilati*(v110-v100)
    v1x1       = v101+dilati*(v111-v101)
    v1xx       = v1x0+dilong*(v1x1-v1x0)
    vxxx       = v0xx+ditemp*(v1xx-v0xx)   
    vit_vent_n = np.abs(vxxx) * 1.94384
    angle_vent = (270 - np.angle(vxxx, deg = True)) % 360
    
    return vit_vent_n, angle_vent


def polairev2(polaires, ws, twa):
''' fonction extraction polaire en un seul point '''     
    '''interpolation bilineaire en utilisant np.interp 
    20 fois plus rapide que avec interpn scipy '''
    i= np.where(tab_tws>ws)[0][0] 
    j= np.where(tab_twa>twa)[0][0] 
    twa_i= tab_twa[j-1]
    twa_s= tab_twa[j]
    xp=tab_tws
    yp=polaires[j-1]
    yp2=polaires[j]
    a=np.interp(ws, xp, yp)
    b=np.interp(ws, xp, yp2)
    c=a+(b-a)*(twa-twa_i)/(twa_s-twa_i)
    return c



def polaire2_vectv2(polaires,vit_vent,angle_vent,tableau_caps):
    '''il n'y a qu'une vitesse et un angle de vent mais plusieurs caps '''
    ''' 20% plus performant que la fonction de base'''
    #transformation tableau de caps en un point en tableau de donnees (twa , vit_vent)
    l=len(tableau_caps)
    twax = 180 - abs(((360 - angle_vent + tableau_caps) % 360) - 180)  # broadcasting
    twa  = twax.reshape(-1,1)
    vvent = (np.ones(l)*vit_vent).reshape(-1,1)
    donnees= np.concatenate((twa,vvent), axis = 1) 
    valeurs = interpn((tab_twa, tab_tws), polaires, donnees, method='linear')
    return valeurs



@jit(nopython=True)
def deplacement_x_y_v2(x0,y0,d_t,HDG,VT):
    ''' fonction donnant le tuple point d arrivée en fonction des coordonnées du point de depart ''' 
    '''HDG et VT sont des np.array  acceleration 30% avec numba @jit'''
    HDG_R = HDG * math.pi / 180     # cap en radians
    x= x0+ d_t / 3600 / 60 * VT * (np.sin(HDG_R) / math.cos(y0 * math.pi / 180)) 
    y= y0- d_t / 3600 / 60 * VT * np.cos(HDG_R)
    return x,y


@jit(nopython=True)
def ftwaov2( HDG,TWD):
'''retourne une twa orientee babord<0 tribord>0 à partir de ndarray '''
''' le temps est divise par 4 avec @jit'''
    A=np.mod((HDG-TWD+360),360)
return np.where(A<180,-A,360-A)    


@jit(nopython=True)
def deplacement2(x0,y0,d_t,HDG,TWD,VT,A,twa,penalite):
    ''' fonction donnant le tuple point d arrivée en fonction des coordonnées du point de depart ''' 
    ''' c'est cette fonction qui sert dans le calcul des isochrones '''
    ''' ameliore deplacement de 30% '''
    # integre une penalite si la nouvelle twa est de signe inverse de la nouvelle
    if penalite !=0 :   
        TWAO=ftwaov2( HDG,TWD)
        Virement=np.where(TWAO*twa>0,False,True)
        DT=np.ones(len(VT))*d_t-Virement*penalite
        HDG_R = HDG * math.pi / 180     # cap en radians
        X= x0+ DT / 3600 / 60 * VT * (np.sin(HDG_R) / math.cos(y0 * math.pi / 180)) 
        Y= y0- DT / 3600 / 60 * VT * np.cos(HDG_R)
    else :
        HDG_R = HDG * math.pi / 180     # cap en radians
        X= x0+ d_t / 3600 / 60 * VT * (np.sin(HDG_R) / math.cos(y0 * math.pi / 180)) 
        Y= y0- d_t / 3600 / 60 * VT * np.cos(HDG_R)

    #Pointscpx=X+Y*1j
    #Di,Ca=dist_cap(X+Y*1j, A)
    return X,Y