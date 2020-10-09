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
tab_tws=np.array([0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,35,40,50,60,70])

tab_twa=np.array([0,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150,155,160,170,180])

polaires=np.array([[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[
0,2.738,5.326,7.482,8.927,9.067,10.07,10.501,10.662,10.802,10.923,11.063,11.204,11.344,11.344,11.484,11.484,11.264,10.852,9.468,8.335],[
0,3.169,6.62,9.218,10.943,11.093,12.527,12.808,13.099,13.24,13.48,13.621,13.902,14.042,14.042,14.182,14.323,14.042,13.53,11.765,10.321],[
0,4.022,8.064,11.234,13.24,13.681,15.256,15.687,15.978,16.259,16.449,16.74,16.88,17.021,17.161,17.302,17.442,17.091,16.479,14.323,12.688],[
0,4.453,8.927,12.237,14.112,14.403,15.837,16.409,16.85,17.282,17.302,17.583,17.723,18.004,18.144,18.295,18.576,18.214,17.563,15.216,13.43],[
0,4.754,9.639,12.949,14.112,14.975,16.409,17.131,17.563,17.994,18.144,18.435,18.716,18.997,19.137,19.569,20,19.599,18.897,16.369,14.554],[
0,5.045,10.361,13.681,14.403,15.546,17.131,17.563,18.285,18.716,18.856,19.137,19.709,20,20.281,20.702,21.404,20.983,20.231,17.512,15.546],[
0,5.326,10.802,14.253,14.975,15.978,17.563,18.285,18.856,19.288,19.569,20,20.421,20.842,21.404,21.835,22.828,22.377,21.575,18.666,16.549],[
0,5.577,11.023,14.594,15.446,16.309,17.883,18.736,19.308,20.03,20.471,21.123,21.695,22.257,22.828,23.4,24.814,24.323,23.45,20.331,18.034],[
0,5.847,11.404,14.824,15.677,16.68,18.525,19.097,19.96,20.662,21.494,22.116,22.979,23.54,24.383,24.955,26.941,26.409,25.456,22.116,19.528],[
0,5.988,11.545,15.105,16.239,17.101,18.881,20.047,20.932,21.945,22.794,23.653,24.298,25.167,25.894,26.763,28.932,27.803,26.8,23.27,20.521],[
0,6.128,11.825,15.246,17.101,17.392,19.25,20.726,22.083,23.116,24.138,25.004,25.859,26.693,27.58,28.602,30.97,29.187,28.134,24.413,21.645],[
0,6.128,11.825,15.386,17.392,18.094,19.533,21.158,22.677,24.013,25.317,26.328,27.497,28.498,29.197,30.084,32.139,30.301,29.207,25.316,22.397],[
0,6.128,11.825,15.386,17.532,18.666,20.119,21.743,23.262,24.899,26.349,27.664,28.967,29.833,30.678,31.408,33.328,31.414,30.281,26.339,23.26],[
0,5.988,11.545,15.246,17.392,18.947,20.402,22.174,24.159,25.786,27.392,28.55,29.718,30.574,31.127,31.554,34.068,31.133,30.02,26.088,23.009],[
0,5.847,11.404,14.824,17.101,19.097,20.544,22.472,24.753,26.537,28.279,29.447,30.595,31.158,31.575,31.992,34.214,31.133,30.02,26.088,23.009],[
0,5.557,10.973,14.684,17.252,18.947,20.686,22.616,25.045,26.829,28.728,29.593,30.595,31.304,32.013,32.597,34.506,32.246,31.083,26.981,23.881],[
0,5.286,10.692,14.684,17.392,18.666,20.686,22.76,25.494,27.424,29.166,29.739,30.595,31.304,32.305,33.328,35.55,33.5,32.297,27.994,24.754],[
0,5.186,10.662,14.624,17.101,18.666,20.544,22.904,25.494,27.278,29.02,29.885,31.043,32.045,33.056,34.193,36.718,34.614,33.36,28.886,25.627],[
0,5.186,10.361,14.403,17.131,18.967,20.402,22.904,25.494,27.132,28.874,30.188,31.481,32.785,33.933,35.08,37.751,35.576,34.303,29.789,26.369],[
0,4.895,9.789,13.972,16.7,18.716,20.605,23.284,25.494,27.132,28.874,30.334,31.627,33.088,34.381,35.675,38.794,36.559,35.245,30.561,27.001],[
0,4.754,9.358,13.24,16.118,18.285,20.605,23.294,25.744,27.403,28.874,30.48,31.919,33.526,34.819,36.269,39.67,37.392,36.048,31.193,27.613],[
0,4.313,8.495,12.377,15.256,17.422,19.584,22.4,25.15,26.808,29.082,30.762,32.368,33.818,35.257,36.707,41.026,38.786,37.382,32.467,28.736],[
0,4.022,7.924,11.514,14.403,16.7,18.714,21.23,24.555,26.193,29.197,30.824,32.597,34.068,35.55,37.01,42.768,40.311,38.856,33.751,29.859],[
0,3.45,7.192,10.361,13.099,15.546,17.561,19.751,22.604,24.701,27.434,29.792,32.295,34.36,36.134,37.897,42.476,40.04,38.585,33.5,29.609],[
0,3.169,6.329,9.358,12.237,14.543,16.54,18.724,20.967,23.355,25.953,28.905,31.992,34.506,36.718,38.94,42.184,39.749,38.325,33.239,29.358],[
0,2.879,5.757,8.355,11.093,13.24,15.529,17.542,19.611,21.707,23.741,26.401,29.197,31.846,34.068,36.572,41.579,39.197,37.783,32.728,28.987],[
0,2.598,5.045,7.633,10.07,12.377,14.518,16.505,18.568,20.351,21.676,24.336,26.986,29.499,31.992,34.36,40.849,38.505,37.111,32.216,28.485],[
0,2.307,4.754,7.192,9.498,11.514,13.38,14.975,16.7,18.285,19.569,21.835,23.962,26.379,28.505,30.762,36.439,35.717,33.6,29.919,26.369],[
0,2.166,4.614,6.76,9.067,11.093,12.808,14.403,15.978,17.422,18.716,20.842,23.119,25.235,27.502,29.498,35.165,34.473,30.14,28.194,25.496]])

print (tab_twa[19] , polaires[19])
print (tab_twa[20], polaires[20])
print (tab_twa[21], polaires[21])




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
















# #test sur polaire2 vect
#     vit_vent=10
#     angle_vent=300
#     tableau_caps=np.arange(0,360,10)
#     ws=3
#     twa=25
#     tic=time.time()
#     #print(tableau_caps)
#     print()
#     for i in range (1000):
#         res=polaire2_vect(polaires,vit_vent,angle_vent,tableau_caps)
#     tac=time.time()   
#     print('temps execution base en secondes',tac-tic)
#     print (res)

#     tic=time.time()
#     #print(tableau_caps)
#     print()
#     for i in range (1000):
#         res=polaire2_vectv2(polaires,vit_vent,angle_vent,tableau_caps)
#     tac=time.time()   
#     print('temps execution variante en secondes',tac-tic)
#     print (res)

    tws=18.7
    angle_vent=300
    tableau_caps=np.arange(0,360,10)
    twa=110

#test de polaire et polaire v2
    tic=time.time()

    for i in range (10000) :
        d=polairev2(polaires, tws, twa)
    tac=time.time()   
    print('temps execution en secondes',tac-tic)
    res= polairev2(polaires, tws, twa)
    
    print('Vitesse polaire pour vent {} et twa {} vitesse {}'.format(tws,twa, res))
















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