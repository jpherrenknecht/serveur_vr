
# Source
# # # http://toxcct.free.fr/polars/generator.htm
# # # http://toxcct.free.fr/polars/help/csvgen_input.htm
# # # pour obtenir les donnees brutes dans vr dashboard raw values reperer la ligne et la copier
# copies des donnees brutes - retirer tWA TWS le replacer par 0, remplacer les ; par des , - ajouter   : ],[ à la fin de chaque ligne, polaires=np.array([[ au debut et ]])







import numpy as np
import math



polaires=np.array([[
0,0,4,6,8,10,12,14,16,20,25,30,35,40,50,60,70],[
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[
10,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[
30,0,1.294,1.936,2.849,3.721,4.634,5.025,5.125,5.025,5.055,4.945,4.844,4.493,2.217,1.364,0.08],[
36,0,2.528,3.47,4.814,5.396,6.018,6.379,6.73,6.62,6.289,6.178,6.058,5.847,2.939,1.946,0.191],[
40,0,2.999,3.882,5.196,5.727,6.299,6.62,7.021,6.911,6.67,6.54,6.309,6.158,3.37,2.197,0.441],[
44,0,3.159,4.253,5.537,6.058,6.479,6.77,7.232,7.141,6.911,6.79,6.509,6.379,3.811,2.417,0.692],[
45,0,3.19,4.323,5.577,6.128,6.53,6.81,7.272,7.171,6.941,6.871,6.59,6.399,3.912,2.487,0.832],[
50,0,3.36,4.674,5.817,6.399,6.74,7.011,7.342,7.352,7.252,7.161,6.901,6.63,4.313,2.738,1.043],[
52,0,3.44,4.844,5.948,6.54,6.85,7.101,7.362,7.412,7.372,7.252,6.961,6.7,4.393,2.768,1.163],[
60,0,3.641,5.216,6.329,6.961,7.101,7.452,7.643,7.753,7.703,7.703,7.342,7.081,4.774,2.929,1.434],[
70,0,3.892,5.456,6.459,7.101,7.352,7.793,8.004,8.215,8.235,8.235,8.024,7.633,5.145,3.159,1.625],[
80,0,4.082,5.597,6.58,7.292,7.775,8.391,8.804,9.075,9.106,9.138,8.95,8.365,5.647,3.47,1.755],[
90,0,4.183,5.757,6.67,7.452,8.007,8.699,9.252,9.618,9.983,9.941,9.67,9.067,6.118,3.751,1.896],[
95,0,4.213,5.767,6.75,7.462,8.098,8.853,9.43,9.857,10.379,10.369,10.16,9.609,6.469,3.972,1.966],[
100,0,4.183,5.757,6.85,7.533,8.149,8.946,9.597,10.056,10.921,10.848,10.619,10.04,6.8,4.152,2.036],[
105,0,4.142,5.787,6.951,7.643,8.22,8.956,9.753,10.275,11.36,11.318,11.151,10.521,7.141,4.353,2.156],[
110,0,4.112,5.757,7.031,7.733,8.28,8.956,9.868,10.483,11.798,11.798,11.693,10.983,7.653,4.624,2.267],[
120,0,4.082,5.757,7.242,7.954,8.351,8.864,9.983,10.786,12.424,12.444,12.736,12.136,8.666,5.236,2.507],[
125,0,3.992,5.667,7.151,7.954,8.391,8.936,10.024,10.89,12.778,12.757,13.289,12.628,9.328,5.677,2.658],[
130,0,3.862,5.617,6.981,7.813,8.361,8.936,10.15,10.921,13.06,13.018,13.894,13.27,10.09,6.279,2.788],[
135,0,3.641,5.456,6.73,7.603,8.24,8.905,10.108,10.921,13.31,13.31,14.499,13.932,11.023,6.991,2.929],[
140,0,3.3,5.045,6.239,7.171,8.048,8.792,10.066,10.974,13.571,13.634,15.198,14.704,11.926,8.024,3.089],[
143,0,3.079,4.734,5.968,6.901,7.967,8.679,10.004,10.932,13.634,13.832,15.386,14.955,12.407,8.826,3.139],[
146,0,2.859,4.483,5.677,6.69,7.825,8.545,9.878,10.901,13.675,13.884,15.407,15.135,12.788,9.689,3.18],[
150,0,2.588,4.162,5.326,6.379,7.593,8.309,9.732,10.828,13.623,13.926,15.365,15.105,13.26,11.264,3.169],[
155,0,2.207,3.841,4.814,5.898,7.219,7.816,9.263,10.671,13.373,13.79,14.958,14.624,13.46,12.537,3.139],[
158,0,2.046,3.661,4.333,5.567,6.915,7.477,8.814,10.588,13.268,13.644,14.604,14.273,13.51,12.778,3.119],[
160,0,1.976,3.49,4.112,5.356,6.673,7.261,8.574,10.536,13.154,13.529,14.197,13.912,13.45,12.828,3.099],[
165,0,1.725,2.959,3.47,4.824,5.951,6.577,7.837,10.179,12.42,12.655,13.105,13.029,12.848,12.537,3.059],[
170,0,1.424,2.227,2.838,3.882,4.925,5.587,6.79,9.358,10.933,11.304,11.795,12.277,12.096,12.046,2.999],[
180,0,0.993,1.454,1.996,2.487,3.019,3.932,4.895,6.891,7.833,8.856,9.839,10.782,9.91,10.652,2.899]])

# ************************************************Fonctions   **********************************************************

def twa(cap, dvent):
    twa = 180 - abs(((360 - dvent + cap) % 360) - 180)
    return twa

def polaire (polaires,vent,twa):
    # Recherche des indices
    i,j=0,0
    while i < np.size(polaires[0]):
        if vent < polaires[0][i]:
            break
        i+= 1
    while j < np.size(polaires[:,0]):
        if twa < polaires[j][0]:
            break
        j+= 1


    dx=vent-polaires[0][i-1]
    dy=twa-polaires[j-1][0]
    deltax=polaires[0][i]-polaires[0][i-1]
    deltay=polaires[j][0]-polaires[j-1][0]

    # print('dx',dx)
    # print('dy',dy)
    # print('deltax',deltax)
    # print('deltay',deltay)


    fx1y1=polaires[j-1][i-1]
    fx1y2=polaires[j][i-1]
    fx2y1=polaires[j-1][i]
    fx2y2=polaires[j][i]

    # print ('fx1y1',fx1y1)
    # print ('fx1y2',fx1y2)
    # print ('fx2y1',fx2y1)
    # print ('fx2y2',fx2y2)


    deltafx=fx2y1-fx1y1
    deltafy=fx1y2-fx1y1
    deltafxy=fx1y1+fx2y2-fx2y1-fx1y2

    # print ('deltafx',deltafx)
    # print ('deltafy',deltafy)
    # print ('deltafxy',deltafxy)

    resultat=(deltafx*dx/deltax)+(deltafy*dy/deltay)+(deltafxy*dx*dy/deltax/deltay)+fx1y1

    return resultat


def polaire2(polaires,vit_vent,angle_vent,cap):
    twa = 180 - abs(((360 - angle_vent + cap) % 360) - 180)
    # Recherche des indices
    i,j=0,0
    while i < np.size(polaires[0]):
        if vit_vent < polaires[0][i]:
            break
        i+= 1
    while j < np.size(polaires[:,0]):
        if twa < polaires[j][0]:
            break
        j+= 1

    dx = vit_vent - polaires[0][i - 1]
    dy = twa - polaires[j - 1][0]
    deltax = polaires[0][i] - polaires[0][i - 1]
    deltay = polaires[j][0] - polaires[j - 1][0]
    fx1y1 = polaires[j - 1][i - 1]
    fx1y2 = polaires[j][i - 1]
    fx2y1 = polaires[j - 1][i]
    fx2y2 = polaires[j][i]
    deltafx = fx2y1 - fx1y1
    deltafy = fx1y2 - fx1y1
    deltafxy = fx1y1 + fx2y2 - fx2y1 - fx1y2

    resultat = (deltafx * dx / deltax) + (deltafy * dy / deltay) + (deltafxy * dx * dy / deltax / deltay) + fx1y1

    return resultat

def polaire2_vect(polaires,vit_vent,angle_vent,tableau_caps):
    polaires2=np.zeros(len(tableau_caps))
    for k in range(len(tableau_caps)):
        twa = 180 - abs(((360 - angle_vent + tableau_caps[k]) % 360) - 180)
        #print(twa)
        # Recherche des indices
        i,j=0,0
        while i < np.size(polaires[0]):
            if vit_vent < polaires[0][i]:
                break
            i+= 1
        while j < np.size(polaires[:,0]):
            if twa < polaires[j][0]:
                break
            j+= 1
        dx = vit_vent - polaires[0][i - 1]
        dy = twa - polaires[j - 1][0]
        deltax = polaires[0][i] - polaires[0][i - 1]
        deltay = polaires[j][0] - polaires[j - 1][0]
        fx1y1 = polaires[j - 1][i - 1]
        fx1y2 = polaires[j][i - 1]
        fx2y1 = polaires[j - 1][i]
        fx2y2 = polaires[j][i]
        deltafx = fx2y1 - fx1y1
        deltafy = fx1y2 - fx1y1
        deltafxy = fx1y1 + fx2y2 - fx2y1 - fx1y2

        polaires2[k] = (deltafx * dx / deltax) + (deltafy * dy / deltay) + (deltafxy * dx * dy / deltax / deltay) + fx1y1

    return polaires2

#pol_vect=np.vectorize (polaire2)



if __name__=='__main__':
    vit_vent = 25
    angle_vent = 100
    cap=140
    tableau_caps = np.array([140, 141, 142])
    twa = 180 - abs(((360 - angle_vent + cap) % 360) - 180)

# premiere fonction
    resultat=polaire(polaires,vit_vent,twa)
    print('\n\tPolaire pour un Vent de {} Noeuds  et une twa de {}° = {:6.3f} Noeuds '.format(vit_vent,twa, resultat))

# deuxieme fonction
    res=polaire2(polaires,vit_vent,angle_vent,cap)
    print ('\tPour un vent de {} Noeuds avec une twa de {}° la polaire est {}'.format(vit_vent,twa,res))

#troisieme fonction
    res=polaire2_vect(polaires,vit_vent,angle_vent,tableau_caps)
    print(res)

# quatrieme fonction ne marche pas
#     res = pol_vect(polaires, vit_vent, angle_vent, tableau_caps)


