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
x1=np.array([0,2,4,5,8,10,12,14,16,18,20,22,24,25,26,28,30,32,35,40,50,60,70])   #les vents
y1=np.array([0,20,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150,155,160,165,170,175,180])  # les twa

polaires=np.array([[
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[
0,0.802,1.224,1.434,1.284,0.943,1.043,0.732,0.512,0.331,0.341,0.231,0.14,0.15,0.09,0.09,0.05,0.03,0.01,0,0,0,0],[
0,1.725,3.41,4.052,5.216,5.777,6.479,6.68,6.79,6.891,6.981,7.081,7.181,7.181,7.282,7.282,7.382,6.644,5.906,4.429,3.265,2.311,0.942],[
0,2.177,4.293,5.196,6.459,7.212,8.174,8.686,8.806,8.836,8.816,9.097,8.887,9.147,9.218,8.977,9.358,8.169,7.262,5.663,4.062,2.873,1.249],[
0,2.528,5.165,6.178,7.563,8.495,9.488,10.03,10.231,10.431,10.471,10.682,10.782,10.873,10.873,10.973,11.073,9.92,8.867,6.554,4.759,3.394,1.468],[
0,2.838,5.727,6.79,8.546,9.218,10.13,10.531,10.923,11.123,11.143,11.274,11.374,11.474,11.474,11.565,11.855,10.712,9.609,7.204,5.251,3.719,1.619],[
0,3.039,6.178,7.272,9.017,9.619,10.531,10.943,11.344,11.545,11.565,11.775,11.976,12.076,12.176,12.267,12.467,11.311,10.201,7.667,5.647,4,1.739],[
0,3.24,6.58,7.703,9.428,9.93,10.943,11.244,11.645,11.956,12.076,12.267,12.568,12.678,12.778,12.969,13.27,12.033,10.848,8.197,6.048,4.281,1.863],[
0,3.44,6.891,8.004,9.729,10.231,11.244,11.645,12.056,12.357,12.467,12.778,13.31,13.27,13.43,13.671,13.972,12.838,11.571,8.81,6.525,4.594,2.004],[
0,3.571,7.081,8.255,9.93,10.471,11.474,11.986,12.377,12.788,13.109,13.47,13.942,14.072,14.263,14.564,14.965,13.829,12.606,9.52,7.021,4.971,2.16],[
0,3.711,7.322,8.425,10.15,10.702,11.835,12.237,12.738,13.24,13.731,14.162,14.664,14.864,15.065,15.476,15.968,14.644,13.569,10.285,7.573,5.356,2.335],[
0,3.811,7.422,8.515,10.431,10.933,12.084,12.779,13.402,14.006,14.609,15.111,15.571,15.868,16.072,16.584,17.106,15.724,14.577,10.893,8.034,5.689,2.476],[
0,3.912,7.512,8.616,10.632,11.274,12.334,13.249,14.072,14.812,15.428,16.033,16.742,17.003,17.295,17.785,18.255,16.523,15.334,11.434,8.43,5.966,2.6],[
0,3.912,7.512,8.616,10.913,11.524,12.527,13.557,14.499,15.323,16.147,16.867,17.577,17.879,18.098,18.682,19.068,17.003,15.563,11.855,8.741,6.191,2.693],[
0,3.912,7.512,8.606,11.083,11.835,12.84,13.855,14.917,15.96,16.878,17.702,18.515,18.839,19.006,19.506,19.725,17.577,15.949,12.207,9.047,6.379,2.789],[
0,3.811,7.422,8.515,11.133,12.046,13.042,14.174,15.438,16.481,17.514,18.213,19.037,19.329,19.527,19.934,20.278,18.307,16.387,12.437,9.198,6.495,2.84],[
0,3.711,7.272,8.425,11.163,12.166,13.143,14.379,15.855,17.003,18.129,18.839,19.569,19.861,20.049,20.33,20.622,18.891,16.846,12.517,9.363,6.62,2.892],[
0,3.591,7.091,8.325,11.224,12.136,13.244,14.482,16.054,17.264,18.338,19.225,19.851,20.09,20.341,20.685,21.029,19.396,17.493,12.758,9.508,6.74,2.946],[
0,3.46,6.881,8.124,11.133,12.116,13.244,14.584,16.262,17.524,18.651,19.371,19.934,20.278,20.508,20.977,21.457,19.781,17.925,13.029,9.664,6.871,2.991],[
0,3.39,6.79,8.074,11.033,12.036,13.143,14.687,16.262,17.493,18.547,19.444,20.101,20.476,20.706,21.353,21.885,20.259,18.509,13.46,9.975,7.065,3.075],[
0,3.28,6.58,7.884,10.943,12.136,13.153,14.687,16.262,17.483,18.442,19.548,20.174,20.581,20.988,21.697,22.396,20.795,19.093,13.892,10.286,7.282,3.168],[
0,3.139,6.279,7.593,10.632,11.956,13.174,14.923,16.262,17.399,18.442,19.538,20.278,20.789,21.196,22.01,22.823,21.264,19.502,14.311,10.552,7.466,3.25],[
0,3.019,5.978,7.292,10.331,11.645,13.083,14.769,16.429,17.483,18.536,19.611,20.466,20.894,21.405,22.323,23.23,21.64,20.003,14.666,10.817,7.651,3.331],[
0,2.788,5.527,6.79,9.719,11.143,12.557,14.317,16.116,17.17,18.599,19.663,20.685,21.207,21.718,22.521,23.439,22.1,20.62,15.207,11.214,7.936,3.454],[
0,2.528,5.065,6.279,9.077,10.632,11.95,13.588,15.459,16.753,18.348,19.632,20.862,21.374,21.999,22.73,23.971,22.597,21.33,15.671,11.519,8.225,3.545],[
0,2.267,4.564,5.567,8.405,9.93,11.232,12.654,14.426,15.803,17.535,19.214,20.654,21.478,22.177,23.136,24.284,22.691,21.163,15.683,11.565,8.184,3.563],[
0,2.026,4.052,5.065,7.803,9.318,10.616,11.924,13.383,14.958,16.606,18.348,20.08,21.186,22.104,23.043,24.253,22.785,21.004,15.569,11.479,8.124,3.536],[
0,1.825,3.681,4.503,7.091,8.505,9.898,11.205,12.538,13.905,15.146,16.909,18.776,19.986,20.758,21.885,23.345,22.222,20.662,15.322,11.304,8,3.481],[
0,1.625,3.38,4.142,6.479,7.904,9.291,10.579,11.902,13.06,13.905,15.657,17.462,18.515,19.35,20.612,21.999,21.574,20.337,15.087,11.123,7.872,3.415],[
0,1.525,3.149,3.852,6.178,7.593,8.852,10.049,11.264,12.246,13.044,14.65,16.185,17.228,18.016,19.234,20.758,20.33,19.209,14.485,10.617,7.559,3.289],[
0,1.444,3.009,3.691,5.978,7.392,8.525,9.619,10.632,11.645,12.357,13.831,15.366,16.158,16.86,18.255,19.649,19.3,18.19,14.01,10.085,7.31,3.181],[
0,1.424,2.939,3.651,5.837,7.192,8.305,9.388,10.431,11.344,12.146,13.561,15.065,15.767,16.459,17.863,19.157,18.857,17.797,13.709,9.569,7.113,3.114],[
0,1.414,2.929,3.651,5.777,7.091,8.205,9.218,10.231,11.143,11.976,13.37,14.764,15.466,16.158,17.552,18.856,18.587,17.484,13.468,9.007,6.861,3.06]])


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




    vit_vent = 10
    angle_vent = 0
    #cap = 160
    caps = np.array([140, 141, 142,143,144,145])
    res = polaire2_vect(polaires, vit_vent, angle_vent, caps)

    print ('Vitesse du vent {} noeuds , angle du vent {}° ' .format(vit_vent,angle_vent))
    print ('caps :', caps)
    print('Polaires',res)


    vit1=np.array([10.49,10.49,10.49])
    ang1=np.array([0,0,0])
    caps = np.array([140.7, 140.7, 140.7])
    res2=polaire3_vect(polaires, vit1, ang1, caps)
    print('Polaires avec p3',res2)  # ne marche pas



    print ('\nVersion simple')
    cap=142
    twa = 180 - abs(((360 - angle_vent + cap) % 360) - 180)
    res = polaire(polaires, vit_vent, twa)

    print ('Vitesse du vent {} noeuds , angle du vent {}° ' .format(vit_vent,angle_vent))
    print ('caps :', cap)
    print('Polaire',res)

