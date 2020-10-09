from scipy.interpolate import RegularGridInterpolator,interp2d,interpn
import  numpy  as np
import numba
import time
from numba import jit
print(numba.__version__)



# angle mini au près 36°
# angle maxi au var 160°
angle_twa_pres = 36
angle_twa_ar = 20
angle_pres = 36
angle_var = 20

#definition des graduations sur les axes x y
tab_tws=np.array([0,2,4,5,8,10,12,14,16,18,20,22,24,25,26,28,30,32,35,40,50,60,70])   #les vents
tab_twa=np.array([0,20,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150,155,160,165,170,175,180])

polaires=np.array([[
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[
0,0.802,1.224,1.434,1.284,0.943,1.043,0.732,0.512,0.331,0.341,0.231,0.14,0.15,0.09,0.09,0.05,0.03,0.01,0,0,0,0],[
0,1.725,3.41,4.052,5.216,5.777,6.479,6.68,6.79,6.891,6.981,7.081,7.181,7.181,7.282,7.282,7.382,7.382,7.382,7.382,6.53,5.777,3.139],[
0,2.177,4.293,5.196,6.459,7.212,8.174,8.686,8.806,8.836,8.816,9.097,8.887,9.147,9.218,8.977,9.358,9.077,9.077,9.438,8.124,7.181,4.162],[
0,2.528,5.165,6.178,7.563,8.495,9.488,10.03,10.231,10.431,10.471,10.682,10.782,10.873,10.873,10.973,11.073,11.073,11.173,10.923,9.518,8.485,4.895],[
0,2.838,5.727,6.79,8.546,9.218,10.13,10.531,10.923,11.123,11.143,11.274,11.374,11.474,11.474,11.565,11.855,11.775,11.876,12.006,10.501,9.298,5.396],[
0,3.039,6.178,7.272,9.017,9.619,10.531,10.943,11.344,11.545,11.565,11.775,11.976,12.076,12.176,12.267,12.467,12.568,12.668,12.778,11.294,10,5.797],[
0,3.24,6.58,7.703,9.428,9.93,10.943,11.244,11.645,11.956,12.076,12.267,12.568,12.678,12.778,12.969,13.27,13.37,13.561,13.661,12.096,10.702,6.209],[
0,3.44,6.891,8.004,9.729,10.231,11.244,11.645,12.056,12.357,12.467,12.778,13.31,13.27,13.43,13.671,13.972,14.162,14.463,14.684,13.049,11.484,6.68],[
0,3.571,7.081,8.255,9.93,10.471,11.474,11.986,12.377,12.788,13.109,13.47,13.942,14.072,14.263,14.564,14.965,15.366,15.757,15.867,14.042,12.427,7.202],[
0,3.711,7.322,8.425,10.15,10.702,11.835,12.237,12.738,13.24,13.731,14.162,14.664,14.864,15.065,15.476,15.968,16.459,16.961,17.141,15.145,13.51,7.783],[
0,3.811,7.422,8.515,10.431,10.933,12.084,12.779,13.402,14.006,14.609,15.111,15.571,15.868,16.072,16.584,17.106,17.709,18.221,18.154,16.068,14.223,8.255],[
0,3.912,7.512,8.616,10.632,11.274,12.334,13.249,14.072,14.812,15.428,16.033,16.742,17.003,17.295,17.785,18.255,18.015,19.517,19.057,16.86,14.915,8.666],[
0,3.912,7.512,8.616,10.913,11.524,12.527,13.557,14.499,15.323,16.147,16.867,17.577,17.879,17.67,18.682,19.193,17.879,19.454,19.759,17.482,15.476,8.977],[
0,3.912,7.512,8.606,11.083,11.835,12.84,13.855,14.917,15.96,16.878,17.702,18.515,18.839,19.006,19.506,19.131,18.161,19.287,20.451,18.094,16.008,9.298],[
0,3.811,7.422,8.515,11.133,12.046,13.042,14.174,15.438,16.481,17.514,18.213,19.037,19.329,19.527,19.934,20.424,19.809,19.027,20.762,18.395,16.239,9.468],[
0,3.711,7.272,8.425,11.163,12.166,13.143,14.379,15.855,17.003,18.129,18.839,19.569,19.861,20.049,20.33,20.622,21.165,20.654,20.672,18.726,16.549,9.639],[
0,3.591,7.091,8.325,11.224,12.136,13.244,14.482,16.054,17.264,18.338,19.225,19.851,20.09,20.341,20.685,21.029,21.551,22.02,20.421,19.017,16.85,9.819],[
0,3.46,6.881,8.124,11.133,12.116,13.244,14.584,16.262,17.524,18.651,19.371,19.934,20.278,20.508,20.977,21.457,21.979,22.406,21.244,19.328,17.111,9.97],[
0,3.39,6.79,8.074,11.033,12.036,13.143,14.687,16.262,17.493,18.547,19.444,20.101,20.476,20.706,21.353,21.885,22.511,23.136,22.547,19.95,17.663,10.251],[
0,3.28,6.58,7.884,10.943,12.136,13.153,14.687,16.262,17.483,18.442,19.548,20.174,20.581,20.988,21.697,22.396,23.105,23.867,23.25,20.572,18.204,10.562],[
0,3.139,6.279,7.593,10.632,11.956,13.174,14.923,16.262,17.399,18.442,19.538,20.278,20.789,21.196,22.01,22.823,23.627,24.378,23.851,21.103,18.666,10.832],[
0,3.019,5.978,7.292,10.331,11.645,13.083,14.769,16.429,17.483,18.536,19.611,20.466,20.894,21.405,22.323,23.23,24.044,25.004,24.443,21.635,19.127,11.103],[
0,2.788,5.527,6.79,9.719,11.143,12.557,14.317,16.116,17.17,18.599,19.663,20.685,21.207,21.718,22.521,23.439,24.555,25.775,25.346,22.427,19.839,11.514],[
0,2.528,5.065,6.279,9.077,10.632,11.95,13.588,15.459,16.753,18.348,19.632,20.862,21.374,21.999,22.73,23.971,25.108,26.662,26.118,23.039,20.561,11.815],[
0,2.267,4.564,5.567,8.405,9.93,11.232,12.654,14.426,15.803,17.535,19.214,20.654,21.478,22.177,23.136,24.284,25.212,26.454,26.138,23.129,20.461,11.876],[
0,2.026,4.052,5.065,7.803,9.318,10.616,11.924,13.383,14.958,16.606,18.348,20.08,21.186,22.104,23.043,24.253,25.317,26.255,25.948,22.959,20.311,11.785],[
0,1.825,3.681,4.503,7.091,8.505,9.898,11.205,12.538,13.905,15.146,16.909,18.776,19.986,20.758,21.885,23.345,24.691,25.828,25.536,22.608,20,11.605],[
0,1.625,3.38,4.142,6.479,7.904,9.291,10.579,11.902,13.06,13.905,15.657,17.462,18.515,19.35,20.612,21.999,23.971,25.421,25.145,22.247,19.679,11.384],[
0,1.525,3.149,3.852,6.178,7.593,8.852,10.049,11.264,12.246,13.044,14.65,16.185,17.228,18.016,19.234,20.758,22.589,24.011,24.142,21.234,18.897,10.963],[
0,1.444,3.009,3.691,5.978,7.392,8.525,9.619,10.632,11.645,12.357,13.831,15.366,16.158,16.86,18.255,19.649,21.444,22.738,23.35,20.17,18.275,10.602],[
0,1.424,2.939,3.651,5.837,7.192,8.305,9.388,10.431,11.344,12.146,13.561,15.065,15.767,16.459,17.863,19.157,20.953,22.247,22.848,19.137,17.783,10.381],[
0,1.414,2.929,3.651,5.777,7.091,8.205,9.218,10.231,11.143,11.976,13.37,14.764,15.466,16.158,17.552,18.856,20.652,21.855,22.447,18.014,17.151,10.201]])








def twa(cap, dvent):
    ''' marche avec des np.array '''
    twa = 180 - abs(((360 - dvent + cap) % 360) - 180)
    return twa

def twa2(cap, dvent):
    ''' marche avec des np.array '''
    twa = 180 - abs(((360 - dvent + cap) % 360) - 180)
    return twa


def polaire(polaires, vit_vent, twa): # polaire simple
    donnees= [twa, vit_vent]
    valeur = interpn((tab_twa, tab_tws), polaires, donnees, method='linear')
    return valeur



def polaire2_vect(polaires,vit_vent,angle_vent,tableau_caps):
    #transformation tableau de caps en un point en tableau de donnees (twa , vit_vent)
    donnees = np.zeros((len(tableau_caps),2))
    for k in range(len(tableau_caps)):
        twa = 180 - abs(((360 - angle_vent + tableau_caps[k]) % 360) - 180)
        donnees[k]=[twa,vit_vent]
    valeurs = interpn((tab_twa, tab_tws), polaires, donnees, method='linear')
    return valeurs


def polaire2_vectv2(polaires,vit_vent,angle_vent,tableau_caps):
    '''il n'y a qu'une vitesse et un angle mais plusieurs caps '''
    ''' 20% plus performant que la fonction de base'''
    #transformation tableau de caps en un point en tableau de donnees (twa , vit_vent)
    l=len(tableau_caps)
    twax = 180 - np.abs(((360 - angle_vent + tableau_caps) % 360) - 180)  # broadcasting
    twa  = twax.reshape(-1,1)
    vvent = (np.ones(l)*vit_vent).reshape(-1,1)
    donnees= np.concatenate((twa,vvent), axis = 1) 
    valeurs = interpn((tab_twa, tab_tws), polaires, donnees, method='linear')
    return valeurs





def polaire3_vect(polaires,TWS,TWD,HDG):
    '''Retourne un tableau de polaires en fonction des polaires bateau  de TWS TWD et HDG'''
    '''TWS true Wind speed, TWD true wind direction , HDG caps'''
    '''Les trois tableaux doivent avoir la meme dimension'''
    TWA=(180 - np.abs(((360 - TWD + HDG) % 360) - 180)).reshape((-1, 1))
    TWS2=TWS.reshape((-1, 1))
    donnees=np.concatenate((TWA,TWS2),axis=1)
    valeurs = interpn((tab_twa, tab_tws), polaires, donnees, method='linear')
    return valeurs




def polairev2(polaires, ws, twa):
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
    


if __name__ == '__main__':
















#test sur polaire2 vect
    vit_vent=10
    angle_vent=300
    tableau_caps=np.arange(0,360,10)
    ws=3
    twa=25
    tic=time.time()
    #print(tableau_caps)
    print()
    for i in range (1000):
        res=polaire2_vect(polaires,vit_vent,angle_vent,tableau_caps)
    tac=time.time()   
    print('temps execution base en secondes',tac-tic)
    print (res)

    tic=time.time()
    #print(tableau_caps)
    print()
    for i in range (1000):
        res=polaire2_vectv2(polaires,vit_vent,angle_vent,tableau_caps)
    tac=time.time()   
    print('temps execution variante en secondes',tac-tic)
    print (res)



#test de polaire et polaire v2
    # for i in range (10000) :
    #     d=polairev2(polaires, ws, twa)
    # tac=time.time()   
    # print('temps execution en secondes',tac-tic)
    # e= polairev2(polaires, ws, twa)
    # #print('Par methode variante fonction',e)
















    # print('tab_tws', tab_tws)
    # l=list(tab_tws)
    # print(l)


    # print('tab_twa', tab_twa)
    # l2=list(tab_twa)
    # print(l2)

    # print()
    # polairesjs=[arr.tolist() for arr in polaires]
    # print (polairesjs)


# # transformation de polaire en tableau 2 dimensions





#     print(tab_tws.shape)
#     print(tab_twa.shape)
#     print(polaires.shape)




#     tws=12
#     twd=150
#     HDG = np.array([100, 101, 102])  # caps
#     res4 = polaire2_vect(polaires, tws, twd, HDG)
#     print('polaires calculees 4 ', res4)




#     HDG=np.array([100,101,102])   #caps
#     TWD=np.array([190,190,190])   #direction vent
#     TWS=np.array([20,20,20])      #vitesse vent
#     res=polaire3_vect(polaires, TWS, TWD, HDG)

#     print('polaires calculees 3',res)

#     print()




#     vit_vent = 20
#     angle_vent = 0
#     #cap = 160
#     caps = np.array([90, 90, 90])
#     res = polaire2_vect(polaires, vit_vent, angle_vent, caps)

#     print ('Vitesse du vent {} noeuds , angle du vent {}° ' .format(vit_vent,angle_vent))
#     print ('caps :', caps)
#     print('Polaires',res)


#     vit1=np.array([20,20,20])
#     ang1=np.array([0,0,0])
#     caps = np.array([90,-90,90])
#     res2=polaire3_vect(polaires, vit1, ang1, caps)
#     print('Polaires avec p3',res2)



#     print ('Version simple')
#     cap=140.7
#     twa = 180 - abs(((360 - angle_vent + cap) % 360) - 180)
#     res = polaire(polaires, vit_vent, twa)

#     print ('Vitesse du vent {} noeuds , angle du vent {}° ' .format(vit_vent,angle_vent))
#     print ('caps :', cap)
#     print('Polaires',res)