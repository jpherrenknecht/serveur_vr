# Source
# # # http://toxcct.free.fr/polars/generator.htm
# # # http://toxcct.free.fr/polars/help/csvgen_input.htm
# # # pour obtenir les donnees brutes dans vr dashboard raw values reperer la ligne et la copier
# copies des donnees brutes - retirer tWA TWS le replacer par 0, remplacer les , par des , 
# - ajouter   : ],[ à la fin de chaque ligne, polaires=np.array([[ au debut et ]])
#prendre la premiere ligne et la transformer en x1=np.array([ 0, tws ...]) ne garder qu'un zero 
# reconstituer y1 avec les premiers chiffres de chaque ligne
# supprimer les premiers chiffres de chaque ligne y compris le premier zero

#rajouter les fonctions et tester

from scipy.interpolate import RegularGridInterpolator,interp2d,interpn
import  numpy  as np
# angle mini au près 36°
# angle maxi au var 160°
angle_twa_pres = 40    # angle mini de remontee au vent
angle_twa_ar = 20       # angle mini par rappport au vent arriere
angle_pres = 36
angle_var = 20

#definition des graduations sur les axes x y

x1=np.array([0,2,4,5,6,7,8,9,10,12,14,16,18,20,22,24,25,26,28,30,32,34,35,36,37,38,39,40,41,42,44,46,48,50,60,70])   #les vents
y1=np.array([0,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150,155,160,165,170,175,180])

polaires=np.array([[
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[
0,0.993,1.434,1.876,1.655,2.207,3.2,1.966,4.965,6.62,6.62,6.289,7.723,8.054,8.054,6.951,7.723,6.399,5.075,5.075,5.627,5.406,5.095,4.895,4.313,4.122,3.852,3.761,3.591,3.51,3.26,3.089,2.849,2.618,1.735,0.943],[
0,1.324,1.876,2.317,2.096,3.2,3.972,3.4,6.068,8.164,7.723,7.833,9.047,9.488,9.488,8.275,8.937,7.723,7.171,7.282,6.901,6.63,6.299,6.068,5.276,5.065,4.764,4.664,4.463,4.273,4.072,3.862,3.51,3.24,2.177,1.163],[
0,1.545,2.317,2.869,2.979,4.193,4.855,5.908,7.392,9.599,9.047,9.488,10.04,10.702,10.702,9.488,10.371,9.047,9.268,9.268,8.385,8.164,7.703,7.934,7.192,6.941,6.509,6.279,6.128,5.898,5.537,5.256,4.824,4.413,2.949,1.605],[
0,1.765,2.869,3.42,3.862,5.847,6.951,7.492,9.268,10.812,10.371,10.371,11.033,11.695,11.695,10.923,11.695,10.481,10.702,10.812,9.769,9.488,8.897,8.907,8.435,8.064,7.613,7.352,7.091,6.931,6.509,6.098,5.627,5.175,3.48,1.846],[
0,1.986,3.2,4.082,5.075,6.84,7.833,8.235,9.93,11.254,11.033,11.033,11.585,12.136,12.247,12.688,12.909,12.247,11.916,12.026,11.153,10.822,10.201,10.281,9.87,9.468,9.077,8.786,8.495,8.205,7.733,7.262,6.72,6.138,4.102,2.207],[
0,2.317,3.531,4.634,5.627,7.282,8.164,8.676,10.592,11.585,11.254,11.585,12.136,12.798,13.129,13.571,14.233,13.571,12.688,12.798,11.996,11.635,10.903,11.163,10.642,10.13,9.91,9.589,9.288,8.977,8.465,7.954,7.382,6.76,4.493,2.427],[
0,2.317,3.751,5.075,5.958,7.613,8.385,9.177,10.923,11.805,11.695,12.357,13.129,13.571,14.233,14.564,14.895,14.453,13.46,13.571,13.059,12.658,11.896,12.337,11.695,11.163,10.642,10.311,9.98,9.659,9.117,8.495,7.894,7.242,4.824,2.598],[
0,2.317,3.751,5.296,6.178,7.723,8.716,9.458,11.143,12.026,12.247,13.019,14.122,14.233,14.895,15.226,15.557,15.115,14.674,14.784,14.543,14.082,13.3,13.119,12.939,12.377,11.645,11.294,10.862,10.521,9.93,9.348,8.696,7.934,5.266,2.838],[
0,2.317,3.862,5.516,6.399,7.944,9.047,9.749,11.364,12.357,12.798,13.681,14.895,15.005,15.667,16.108,16.439,16.329,15.667,15.888,16.138,15.617,14.694,14.202,13.902,13.32,12.477,12.106,11.735,11.284,10.662,10.04,9.288,8.556,5.697,3.059],[
0,2.317,3.972,5.737,6.62,8.054,9.268,9.97,11.474,12.517,13.622,14.742,15.868,15.98,16.655,17.556,17.443,17.781,17.106,17.331,17.658,17.177,16.113,15.714,14.941,14.276,13.353,12.909,12.437,12.056,11.314,10.662,9.87,9.037,6.038,3.26],[
0,2.317,4.082,5.958,6.951,8.164,9.378,10.241,11.585,12.789,14.348,15.605,16.867,16.992,17.556,19.047,18.588,19.277,18.703,18.818,18.776,18.255,17.159,17.079,15.899,15.153,14.144,13.631,13.139,12.738,11.966,11.274,10.451,9.518,6.369,3.42],[
0,2.317,4.082,6.289,7.171,8.385,9.488,10.481,11.585,13.123,14.687,16.179,17.67,17.639,18.474,19.736,19.506,20.195,19.851,19.965,19.548,18.995,17.89,17.679,16.782,16.009,14.882,14.253,13.841,13.34,12.608,11.815,10.963,10.07,6.71,3.611],[
0,2.317,4.193,6.399,7.502,8.495,9.819,10.592,11.585,13.234,15.026,16.638,18.244,18.536,19.277,20.31,20.424,20.883,20.769,20.998,20.216,19.632,18.505,18.187,17.368,16.58,15.438,14.794,14.363,13.851,13.019,12.277,11.404,10.411,6.951,3.751],[
0,2.317,4.303,6.62,7.613,8.716,9.93,10.592,11.364,13.346,15.139,17.211,18.818,19.465,19.903,20.539,21.227,21.457,21.572,21.801,20.873,20.268,19.027,18.497,17.666,16.774,15.711,15.065,14.533,14.112,13.26,12.437,11.545,10.622,7.051,3.811],[
0,2.317,4.303,6.73,7.502,8.716,9.93,10.592,11.474,13.457,15.365,17.785,19.162,20.278,20.351,21.227,21.686,21.916,22.145,22.375,21.759,21.123,19.861,18.797,17.963,17.059,15.903,15.326,14.804,14.283,13.43,12.668,11.765,10.762,7.141,3.862],[
0,2.317,4.303,6.84,7.613,8.716,9.819,10.592,11.254,13.457,15.478,17.9,19.392,20.852,20.81,21.457,21.916,22.145,22.375,22.604,22.198,21.551,20.278,19.098,18.251,17.344,16.176,15.506,14.975,14.533,13.671,12.818,11.916,10.893,7.242,3.922],[
0,2.317,4.413,6.951,7.613,8.385,9.709,10.481,11.254,13.234,15.591,18.015,19.736,20.967,21.269,21.697,21.916,22.375,22.49,22.719,22.417,21.759,20.487,19.305,18.251,17.436,16.267,15.597,15.065,14.533,13.751,12.899,11.986,10.963,7.292,3.922],[
0,2.207,4.413,6.84,7.613,8.275,9.488,10.371,11.364,13.234,15.591,17.785,19.965,20.852,21.269,21.801,21.655,22.604,22.375,22.604,22.531,21.864,20.591,19.305,18.456,17.528,16.358,15.687,15.155,14.704,13.831,12.979,12.056,11.033,7.342,3.972],[
0,2.096,4.413,6.469,7.502,8.164,9.268,10.15,11.033,13.234,15.704,17.211,19.851,20.967,20.925,22.145,21.676,22.834,22.375,22.604,22.312,21.655,20.383,19.201,18.456,17.528,16.358,15.687,15.236,14.704,13.831,13.049,12.056,11.033,7.382,3.972],[
0,1.765,4.413,6.038,7.282,7.944,9.047,10.04,11.033,13.346,15.591,16.753,19.392,20.737,20.581,21.916,21.791,22.928,22.145,22.375,22.093,21.436,20.174,19.098,18.456,17.528,16.358,15.687,15.155,14.704,13.831,12.979,12.056,11.033,7.342,3.972],[
0,1.545,4.303,5.587,7.171,7.723,8.937,9.709,11.033,13.012,15.478,16.523,18.818,20.622,20.466,21.697,21.791,23.136,21.801,22.26,21.864,21.227,19.965,18.901,18.456,17.528,16.358,15.687,15.236,14.704,13.831,13.049,12.056,11.033,7.382,3.972],[
0,1.324,3.862,5.095,6.509,7.282,8.385,9.268,10.923,12.122,14.913,16.179,18.421,19.976,20.195,21.457,21.895,22.97,21.457,21.916,21.645,21.019,19.757,18.694,18.456,17.528,16.358,15.687,15.155,14.704,13.831,12.979,12.056,11.033,7.342,3.972],[
0,0.993,2.979,4.704,5.847,6.178,7.282,8.606,10.261,11.344,14.348,15.72,17.733,18.88,19.527,20.539,21.686,21.916,22.031,22.031,21.426,20.8,19.548,18.497,18.456,17.528,16.358,15.687,15.155,14.704,13.831,12.979,12.056,11.033,7.342,3.972],[
0,0.772,2.317,4.303,5.296,5.516,6.84,7.944,9.488,10.232,13.444,15.031,16.784,17.775,18.474,19.621,20.769,21.436,21.457,21.572,20.988,20.383,19.131,18.083,17.861,16.957,15.812,15.236,14.714,14.192,13.43,12.588,11.695,10.692,7.141,3.831],[
0,0.662,1.545,3.862,4.744,4.965,6.178,6.951,8.716,9.008,12.654,13.884,15.678,16.44,17.159,18.359,19.736,20.602,20.998,21.113,20.539,19.955,18.714,17.886,17.368,16.488,15.347,14.794,14.273,13.851,13.019,12.207,11.334,10.411,6.901,3.721],[
0,0.552,0.993,3.531,4.082,4.634,5.516,5.958,8.054,8.23,11.976,12.851,14.468,15.146,15.991,17.326,18.474,19.047,19.809,20.195,19.767,19.214,18.098,16.976,16.289,15.439,14.417,13.801,13.4,12.999,12.207,11.504,10.672,9.719,6.469,3.5],[
0,0.441,0.772,3.089,3.641,4.303,5.075,4.965,7.282,7.562,11.298,11.933,11.36,14.155,14.948,16.294,16.481,16.179,18.171,17.9,18.223,17.618,16.638,15.961,15.314,14.583,13.588,12.999,12.608,12.227,11.474,10.812,10.01,9.167,6.078,3.28],[
0,0.441,0.662,2.758,3.2,3.531,4.634,4.303,6.509,6.757,10.161,10.466,9.791,13.249,13.31,14.967,14.405,14.067,15.643,15.755,16.901,16.338,15.397,14.43,13.774,13.143,12.245,11.835,11.474,11.033,10.411,9.809,9.067,8.345,5.547,2.979],[
0,0.331,0.552,2.427,2.758,3.31,3.972,3.531,5.847,6.289,8.937,8.937,8.495,11.976,12.207,13.129,12.357,12.247,13.46,13.571,14.443,13.982,13.199,12.828,12.176,11.725,11.003,10.672,10.331,9.92,9.358,8.806,8.184,7.512,4.975,2.678],[
0,0.221,0.441,1.876,2.207,2.869,3.42,2.648,5.075,5.516,7.171,7.723,7.282,10.592,11.254,11.585,10.592,10.371,11.143,11.254,11.785,11.434,10.802,10.672,10.16,9.749,9.167,8.877,8.586,8.295,7.813,7.342,6.8,6.209,4.152,2.237],[
0,0.221,0.331,1.214,1.655,1.765,1.986,1.876,2.869,3.972,4.524,5.627,4.744,5.516,5.406,7.061,7.171,6.399,7.833,7.944,6.269,6.128,5.797,5.386,5.747,5.436,5.135,5.025,4.814,4.704,4.393,4.092,3.801,3.521,2.317,1.264]])




# ************************************************Fonctions   **********************************************************

def ftwa(cap, dvent):
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
    print()
    print ('polaire simple exemple 1')
    tws=10
    twa=45
    res=polaire(polaires, tws, twa)
    print('Pour TWA = {} et TWS ={} polaire= {}'.format(twa,tws,res))

    print()
    print ('polaire simple exemple 2')
    tws=15.2
    twa=147
    res=polaire(polaires, tws, twa)
    print('Pour TWA = {} et TWS ={} polaire= {}'.format(twa,tws,res))


    print()
    print('Avec tableau de caps fonction polaire2vect ')
    tws=10
    twd=0
    HDG = np.array([99,100, 101])  # caps
    res = polaire2_vect(polaires, tws, twd, HDG)
    print('polaires calculees pour twa{} et tws {}  res {}'.format(HDG,tws,res))

    print()
    print('Avec tableau de caps fonction polaire3vect ')
    print('tableaux de points avec tws,twdet hdg differents')
    HDG=np.array([102,101,100])   #caps
    TWD=np.array([150,150,150])   #direction vent
    TWS=np.array([12,12,12])      #vitesse vent
    TWA=ftwa(HDG,TWD)
    res=polaire3_vect(polaires, TWS, TWD, HDG)
    print('Polaires calculees 3 twd{} hdg {} twa {} tws{} res{}'.format(TWD,HDG,TWA,TWS,res))



    print()



