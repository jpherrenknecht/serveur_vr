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
x1=np.array([0,6,8,10,12,14,16,20,24,28,30,40,50])   #les vents
y1=np.array([0,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150,155,160,180])  # les twa


polaires=np.array([[
0,0,0,0,0,0,0,0,0,0,0,0,0],[
0,4.513,5.316,5.717,6.018,6.118,6.319,6.419,6.419,6.419,6.419,6.419,6.219],[
0,4.714,5.516,6.018,6.419,6.519,6.85,6.921,7.011,7.111,7.111,7.111,6.901],[
0,4.915,5.717,6.319,6.74,6.921,7.322,7.412,7.603,7.703,7.703,7.703,7.482],[
0,5.115,5.918,6.55,7.021,7.322,7.753,7.904,8.104,8.295,8.295,8.295,8.064],[
0,5.186,6.078,6.78,7.382,7.673,8.074,8.465,8.596,8.897,8.987,8.987,8.746],[
0,5.266,6.158,7.061,7.643,8.044,8.385,9.007,9.187,9.468,9.679,9.779,9.518],[
0,5.266,6.209,7.252,7.976,8.516,8.911,9.719,9.975,10.22,10.384,10.371,10.1],[
0,5.276,6.189,7.352,8.351,8.925,9.492,10.316,10.755,10.859,11.099,10.943,10.712],[
0,5.466,6.229,7.452,8.523,9.213,9.784,10.65,11.224,11.339,11.631,11.364,11.173],[
0,5.516,6.459,7.402,8.503,9.336,10.014,10.89,11.735,11.62,11.965,11.655,11.464],[
0,5.557,6.55,7.543,8.584,9.654,10.337,11.109,12.152,11.923,12.476,12.056,11.855],[
0,5.597,6.64,7.663,8.755,9.839,10.713,11.276,12.392,12.298,12.778,12.427,12.267],[
0,5.557,6.67,7.743,8.806,9.963,10.932,11.652,12.528,12.653,13.133,12.949,12.758],[
0,5.537,6.62,7.643,8.907,10.055,11.078,12.142,12.58,12.997,13.55,13.25,13.119],[
0,5.496,6.57,7.452,8.806,9.963,11.203,12.695,13.185,13.237,13.832,13.38,13.189],[
0,5.567,6.62,7.392,8.543,9.839,11.151,12.997,13.8,13.55,13.957,13.46,13.31],[
0,5.607,6.62,7.352,8.614,9.922,11.182,13.102,14.009,13.947,13.957,13.581,13.45],[
0,5.516,6.519,7.322,8.584,9.86,11.36,13.049,13.8,13.905,13.853,13.761,13.54],[
0,5.316,6.319,7.272,8.493,9.829,11.161,12.663,13.508,13.634,13.853,13.33,13.089],[
0,5.015,6.018,7.061,8.23,9.449,10.838,12.215,12.914,13.164,13.394,12.868,12.658],[
0,4.684,5.617,6.72,8.078,9.141,10.556,11.923,12.434,12.601,12.851,12.347,12.247],[
0,4.383,5.206,6.399,7.765,8.833,10.223,11.735,12.027,12.225,12.392,11.976,11.906],[
0,4.012,4.814,6.038,7.259,8.535,9.91,11.401,11.631,11.704,11.756,11.344,11.274],[
0,3.611,4.443,5.587,6.572,7.703,9.294,10.421,10.556,10.682,10.88,10.401,10.401],[
0,2.608,3.109,3.912,4.513,5.115,5.717,6.901,6.931,7.011,7.151,7.222,6.77]])





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

