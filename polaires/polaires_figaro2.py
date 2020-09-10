from scipy.interpolate import RegularGridInterpolator,interp2d,interpn
import  numpy  as np

# angle mini au près 36°
# angle maxi au var 160°
angle_twa_pres = 36
angle_twa_ar = 20
angle_pres = 36
angle_var = 20
x1=np.array([0,4,6,8,10,12,14,16,20,25,30,35,40,50,60,70])
y1=np.array([0,10,30,36,40,44,45,50,52,60,70,80,90,95,100,105,110,120,125,130,135,140,143,146,150,155,158,160,165,170,180])
polaires=np.array([[
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[
0,1.294,1.936,2.849,3.721,4.634,5.025,5.125,5.025,5.055,4.945,4.844,4.493,2.217,1.364,0.08],[
0,2.528,3.47,4.814,5.396,6.018,6.379,6.73,6.62,6.289,6.178,6.058,5.847,2.939,1.946,0.191],[
0,2.999,3.882,5.196,5.727,6.299,6.62,7.021,6.911,6.67,6.54,6.309,6.158,3.37,2.197,0.441],[
0,3.159,4.253,5.537,6.058,6.479,6.77,7.232,7.141,6.911,6.79,6.509,6.379,3.811,2.417,0.692],[
0,3.19,4.323,5.577,6.128,6.53,6.81,7.272,7.171,6.941,6.871,6.59,6.399,3.912,2.487,0.832],[
0,3.36,4.674,5.817,6.399,6.74,7.011,7.342,7.352,7.252,7.161,6.901,6.63,4.313,2.738,1.043],[
0,3.44,4.844,5.948,6.54,6.85,7.101,7.362,7.412,7.372,7.252,6.961,6.7,4.393,2.768,1.163],[
0,3.641,5.216,6.329,6.961,7.101,7.452,7.643,7.753,7.703,7.703,7.342,7.081,4.774,2.929,1.434],[
0,3.892,5.456,6.459,7.101,7.352,7.793,8.004,8.215,8.235,8.235,8.024,7.633,5.145,3.159,1.625],[
0,4.082,5.597,6.58,7.292,7.775,8.391,8.804,9.075,9.106,9.138,8.95,8.365,5.647,3.47,1.755],[
0,4.183,5.757,6.67,7.452,8.007,8.699,9.252,9.618,9.983,9.941,9.67,9.067,6.118,3.751,1.896],[
0,4.213,5.767,6.75,7.462,8.098,8.853,9.43,9.857,10.379,10.369,10.16,9.609,6.469,3.972,1.966],[
0,4.183,5.757,6.85,7.533,8.149,8.946,9.597,10.056,10.921,10.848,10.619,10.04,6.8,4.152,2.036],[
0,4.142,5.787,6.951,7.643,8.22,8.956,9.753,10.275,11.36,11.318,11.151,10.521,7.141,4.353,2.156],[
0,4.112,5.757,7.031,7.733,8.28,8.956,9.868,10.483,11.798,11.798,11.693,10.983,7.653,4.624,2.267],[
0,4.082,5.757,7.242,7.954,8.351,8.864,9.983,10.786,12.424,12.444,12.736,12.136,8.666,5.236,2.507],[
0,3.992,5.667,7.151,7.954,8.391,8.936,10.024,10.89,12.778,12.757,13.289,12.628,9.328,5.677,2.658],[
0,3.862,5.617,6.981,7.813,8.361,8.936,10.15,10.921,13.06,13.018,13.894,13.27,10.09,6.279,2.788],[
0,3.641,5.456,6.73,7.603,8.24,8.905,10.108,10.921,13.31,13.31,14.499,13.932,11.023,6.991,2.929],[
0,3.3,5.045,6.239,7.171,8.048,8.792,10.066,10.974,13.571,13.634,15.198,14.704,11.926,8.024,3.089],[
0,3.079,4.734,5.968,6.901,7.967,8.679,10.004,10.932,13.634,13.832,15.386,14.955,12.407,8.826,3.139],[
0,2.859,4.483,5.677,6.69,7.825,8.545,9.878,10.901,13.675,13.884,15.407,15.135,12.788,9.689,3.18],[
0,2.588,4.162,5.326,6.379,7.593,8.309,9.732,10.828,13.623,13.926,15.365,15.105,13.26,11.264,3.169],[
0,2.207,3.841,4.814,5.898,7.219,7.816,9.263,10.671,13.373,13.79,14.958,14.624,13.46,12.537,3.139],[
0,2.046,3.661,4.333,5.567,6.915,7.477,8.814,10.588,13.268,13.644,14.604,14.273,13.51,12.778,3.119],[
0,1.976,3.49,4.112,5.356,6.673,7.261,8.574,10.536,13.154,13.529,14.197,13.912,13.45,12.828,3.099],[
0,1.725,2.959,3.47,4.824,5.951,6.577,7.837,10.179,12.42,12.655,13.105,13.029,12.848,12.537,3.059],[
0,1.424,2.227,2.838,3.882,4.925,5.587,6.79,9.358,10.933,11.304,11.795,12.277,12.096,12.046,2.999],[
0,0.993,1.454,1.996,2.487,3.019,3.932,4.895,6.891,7.833,8.856,9.839,10.782,9.91,10.652,2.899]])



def twa(cap, dvent):
    twa = 180 - abs(((360 - dvent + cap) % 360) - 180)
    return twa
#
# def polaire2_vect(polaires,vit_vent,angle_vent,tableau_caps):
#     '''transformation tableau de caps en un point en tableau de donnees (twa , vit_vent)'''
#     '''Pour une valeur de vent et un angle de vent déterminés'''
#     ''' Retourne un tableau de vitesse polaires suivant le tableau de caps'''
#
#     donnees = np.zeros((len(tableau_caps),2))
#     for k in range(len(tableau_caps)):
#         twa = 180 - abs(((360 - angle_vent + tableau_caps[k]) % 360) - 180)
#         donnees[k]=[twa,vit_vent]
#     valeurs = interpn((y1, x1), polaires, donnees, method='linear')
#     return valeurs

def polaire(polaires, vit_vent, twa): # polaire simple
    donnees= [twa, vit_vent]
    valeur = interpn((y1, x1), polaires, donnees, method='linear')
    return valeur


def polaire2_vect(polaires,tws,twd,HDG):
    '''ici un seul point avec une seule tws twd
     mais plusieurs caps'''
    # on ajuste les tableaux TW et TWD à HDG
    l=len(HDG)
    TWD = (np.ones(l)*twd)
    TWA = (180 - np.abs(((360 - TWD + HDG) % 360) - 180)).reshape((-1, 1))
    TWS = (np.ones(l) * tws).reshape((-1, 1))
    donnees = np.concatenate((TWA, TWS), axis=1)
    valeurs = interpn((y1, x1), polaires, donnees, method='linear')
    return valeurs

def polaire4_vect(polaires,tws,twd,HDG):
    '''ici un seul point avec une seule tws twd
     mais plusieurs caps on retourne egalement TWAorientés'''
    # on ajuste les tableaux TW et TWD à HDG
    l=len(HDG)
    TWD = (np.ones(l)*twd)
    TWA = (180 - np.abs(((360 - TWD + HDG) % 360) - 180)).reshape((-1, 1))
    TWS = (np.ones(l) * tws).reshape((-1, 1))
    donnees = np.concatenate((TWA, TWS), axis=1)
    valeurs = interpn((y1, x1), polaires, donnees, method='linear')
    return valeurs








def polaire3_vect(polaires,TWS,TWD,HDG):
    '''Retourne un tableau de polaires en fonction des polaires bateau  de TWS TWD et HDG'''
    '''TWS true Wind speed, TWD true wind direction , HDG caps'''
    '''Les trois tableaux doivent avoir la meme dimension'''
    TWA=(180 - np.abs(((360 - TWD + HDG) % 360) - 180)).reshape((-1, 1))
    TWS2=TWS.reshape((-1, 1))
    donnees=np.concatenate((TWA,TWS2),axis=1)
    valeurs = interpn((y1, x1), polaires, donnees, method='linear')
    return valeurs





#“linear” and “nearest”, and “splinef2d”. “splinef2d” is only

if __name__ == '__main__':


    tws=12
    twd=150
    HDG = np.array([100, 101, 102])  # caps
    res4 = polaire2_vect(polaires, tws, twd, HDG)
    print('polaires calculees 4 ', res4)

    HDG=np.array([100,101,102])   #caps
    TWD=np.array([150,150,150])   #direction vent
    TWS=np.array([12,12,12])      #vitesse vent
    res=polaire3_vect(polaires, TWS, TWD, HDG)

    print('polaires calculees 3',res)

    print()




    vit_vent = 10.49
    angle_vent = 0
    #cap = 160
    caps = np.array([140.7, 140.7, 140.7])
    res = polaire2_vect(polaires, vit_vent, angle_vent, caps)

    print ('Vitesse du vent {} noeuds , angle du vent {}° ' .format(vit_vent,angle_vent))
    print ('caps :', caps)
    print('Polaires',res)


    vit1=np.array([10.49,10.49,10.49])
    ang1=np.array([0,0,0])
    caps = np.array([140.7, 140.7, 140.7])
    res2=polaire3_vect(polaires, vit1, ang1, caps)
    print('Polaires avec p3',res2)



    print ('Version simple')
    cap=140.7
    twa = 180 - abs(((360 - angle_vent + cap) % 360) - 180)
    res = polaire(polaires, vit_vent, twa)

    print ('Vitesse du vent {} noeuds , angle du vent {}° ' .format(vit_vent,angle_vent))
    print ('caps :', cap)
    print('Polaires',res)