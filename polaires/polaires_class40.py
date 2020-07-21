
# Source
# # # http://toxcct.free.fr/polars/generator.htm
# # # http://toxcct.free.fr/polars/help/csvgen_input.htm
# # # pour obtenir les donnees brutes dans vr dashboard raw values reperer la ligne et la copier
# copies des donnees brutes - retirer tWA TWS le replacer par 0, remplacer les , par des , - ajouter   : ],[ à la fin de chaque ligne, polaires=np.array([[ au debut et ]])

from scipy.interpolate import RegularGridInterpolator,interp2d,interpn
import  numpy  as np
# angle mini au près 36°
# angle maxi au var 160°
angle_twa_pres = 40    # angle mini de remontee au vent
angle_twa_ar = 20       # angle mini par rappport au vent arriere
angle_pres = 36
angle_var = 20

#definition des graduations sur les axes x y
x1=np.array([0,4,6,8,10,12,14,16,18,20,22,24,26,28,30,40,50,70])   #les vents
y1=np.array([0,30,33,36,39,42,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150,155,160,180])  # les twa




polaires=np.array([[

0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[
0,2.507,3.912,5.015,5.717,5.928,6.118,6.219,6.319,6.319,6.299,6.409,6.519,6.519,6.309,6.128,5.928,4.875],[
0,2.808,4.313,5.416,6.018,6.219,6.419,6.519,6.62,6.72,6.72,6.82,6.931,6.941,6.77,6.66,6.409,5.266],[
0,3.109,4.614,5.717,6.219,6.519,6.72,6.82,7.021,7.011,7.111,7.312,7.412,7.412,7.222,7.111,6.8,5.757],[
0,3.31,4.915,5.918,6.419,6.72,6.921,7.121,7.322,7.412,7.603,7.703,7.853,7.803,7.703,7.512,7.202,6.239],[
0,3.51,5.155,6.118,6.62,7.021,7.222,7.522,7.623,7.703,8.004,8.205,8.235,8.205,8.205,8.004,7.573,6.61],[
0,3.711,5.416,6.319,6.82,7.222,7.522,7.823,8.024,8.104,8.395,8.656,8.696,8.596,8.696,8.395,7.944,6.941],[
0,4.112,5.717,6.519,7.121,7.623,8.024,8.325,8.626,8.796,9.087,9.288,9.288,9.187,9.388,9.087,8.646,7.533],[
0,4.413,5.918,6.82,7.422,8.024,8.525,8.826,9.228,9.348,9.759,9.98,10.08,9.97,10.271,9.98,9.518,8.094],[
0,4.614,6.068,6.921,7.623,8.225,8.826,9.228,9.709,9.98,10.572,10.772,10.873,10.873,11.264,10.963,10.391,8.666],[
0,4.784,6.178,7.081,7.874,8.576,9.167,9.669,10.271,10.702,11.264,11.464,11.555,11.555,11.956,11.555,11.073,9.198],[
0,4.824,6.259,7.252,8.044,8.836,9.528,10.231,10.822,11.314,11.755,12.056,12.247,12.247,12.548,12.156,11.655,9.739],[
0,4.865,6.359,7.352,8.345,9.174,10.049,10.937,11.55,12.041,12.635,12.798,13.003,13.003,13.402,12.748,12.146,10.05],[
0,4.865,6.349,7.402,8.536,9.514,10.579,11.673,12.288,12.695,13.3,13.383,13.769,13.769,14.176,13.139,12.527,10.461],[
0,4.965,6.459,7.643,8.616,9.766,10.877,12.079,12.705,13.102,13.571,13.832,14.301,14.385,14.698,13.631,13.119,10.772],[
0,4.965,6.459,7.703,8.736,10.009,11.288,12.225,12.883,13.415,13.873,14.207,14.718,14.896,15.417,14.323,13.5,11.033],[
0,4.965,6.459,7.743,8.836,10.11,11.493,12.465,12.914,13.634,14.332,14.729,15.23,15.522,15.928,14.854,13.992,11.444],[
0,4.885,6.459,7.843,8.887,10.211,11.698,12.59,13.321,13.884,14.635,15.021,15.532,15.939,16.335,15.216,14.574,11.896],[
0,4.855,6.359,7.843,8.937,10.211,11.698,12.81,13.529,14.239,14.771,15.344,15.949,16.346,16.753,15.607,14.965,12.377],[
0,4.774,6.259,7.743,8.937,10.211,11.698,13.008,13.842,14.552,15.157,15.459,16.147,16.857,17.358,16.198,15.446,12.979],[
0,4.714,6.189,7.543,8.836,10.12,11.596,13.008,13.947,14.656,15.344,15.845,16.221,16.961,17.764,16.6,15.837,13.51],[
0,4.534,6.118,7.422,8.706,9.807,11.39,12.914,13.842,14.666,15.261,16.001,16.565,16.846,18.077,16.65,16.128,13.882],[
0,4.313,6.018,7.222,8.525,9.605,11.288,12.81,13.738,14.656,15.355,16.064,16.773,16.961,17.869,16.7,15.928,14.092],[
0,4.012,5.817,7.121,8.225,9.473,11.092,12.517,13.769,14.552,15.355,16.168,16.878,16.857,17.67,16.6,15.637,14.202],[
0,3.711,5.416,6.921,7.723,8.998,10.579,11.683,13.352,14.197,15.25,16.064,16.878,16.753,17.566,16.499,15.546,14.112],[
0,3.31,4.915,6.72,7.222,8.493,9.952,11.057,12.622,13.362,14.698,15.616,16.44,16.648,17.566,16.499,15.546,13.851],[
0,3.009,4.513,6.379,6.82,8.038,9.346,10.536,11.579,12.538,13.978,15,16.022,16.648,17.472,16.299,15.546,13.591],[
0,2.608,4.112,5.918,6.319,7.279,8.525,9.805,10.848,11.819,13.154,14.176,15.355,16.231,17.264,16.108,15.346,12.879],[
0,2.207,3.51,5.336,5.717,6.572,7.6,8.762,9.805,10.483,11.714,12.841,14.385,15.417,16.335,15.216,14.574,11.825],[
0,1.906,3.109,4.724,5.115,6.066,6.881,7.928,8.95,9.346,10.17,11.203,12.736,13.665,14.698,13.731,13.119,10.501],[
0,1.304,2.006,2.909,3.31,3.912,4.413,5.015,5.516,6.028,6.419,7.011,7.703,8.295,9.187,8.897,7.753,6.65]])





# ************************************************Fonctions   **********************************************************

def twa(cap, dvent):
    twa = 180 - abs(((360 - dvent + cap) % 360) - 180)
    return twa


def polaire(polaires, vit_vent, twa): # polaire simple
    donnees= [twa, vit_vent]
    valeur = interpn((y1, x1), polaires, donnees, method='linear')
    return valeur



def polaire2_vect(polaires,vit_vent,angle_vent,tableau_caps):
    #transformation tableau de caps en un point en tableau de donnees (twa , vit_vent)
    donnees = np.zeros((len(tableau_caps),2))
    for k in range(len(tableau_caps)):
        twa = 180 - abs(((360 - angle_vent + tableau_caps[k]) % 360) - 180)
        donnees[k]=[twa,vit_vent]
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

if __name__ == '__main__':
    print(x1.shape)
    print(y1.shape)
    print(polaires.shape)

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




    vit_vent = 10.5
    angle_vent = 0
    #cap = 160
    caps = np.array([140, 141, 142,143])
    res = polaire2_vect(polaires, vit_vent, angle_vent, caps)

    print ('Vitesse du vent {} noeuds , angle du vent {}° ' .format(vit_vent,angle_vent))
    print ('caps :', caps)
    print('Polaires',res)


    vit1=np.array([10.49,10.49,10.49])
    ang1=np.array([0,0,0])
    caps = np.array([140.7, 140.7, 140.7])
    res2=polaire3_vect(polaires, vit1, ang1, caps)
    print('Polaires avec p3',res2)



    print ('\nVersion simple')
    cap=142
    twa = 180 - abs(((360 - angle_vent + cap) % 360) - 180)
    res = polaire(polaires, vit_vent, twa)

    print ('Vitesse du vent {} noeuds , angle du vent {}° ' .format(vit_vent,angle_vent))
    print ('caps :', cap)
    print('Polaire',res)













