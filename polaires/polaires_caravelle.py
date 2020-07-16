from scipy.interpolate import RegularGridInterpolator,interp2d,interpn
import  numpy  as np

# angle mini au près 65°
# angle maxi au var 160°

angle_twa_pres = 65
angle_twa_ar = 20

x1=np.array([0,6,10,14,20,24,30,35,40,55,56,70])
y1=np.array([0,50,60,65,70,80,90,100,110,120,130,140,150,160,170,180])

polaires=np.array([[
0,0,0,0,0,0,0,0,0,0,0,0],[
0,0,0,0,0,0,0,0,0,0,0,0],[
0,2.859,4.142,4.343,4.483,3.119,2.317,1.474,1.224,1.194,0,0],[
0,3.45,5.085,5.386,5.647,4.253,3.46,2.568,2.367,2.307,0,0],[
0,3.561,5.466,5.657,6.048,5.135,4.995,3.651,3.36,3.28,0,0],[
0,3.551,5.958,6.275,6.801,6.593,6.488,5.143,4.253,4.142,0,0],[
0,3.48,6.219,6.563,7.291,7.208,7.125,5.654,4.744,4.624,0,0],[
0,3.38,6.419,6.779,7.636,7.521,7.458,5.956,4.945,4.814,0,0],[
0,3.28,6.339,6.881,7.844,7.719,7.5,6.269,5.135,5.005,0,0],[
0,3.109,6.098,6.748,7.844,7.928,7.396,6.373,5.236,5.105,0,0],[
0,2.869,5.717,6.707,7.719,7.928,7.5,6.561,5.336,5.206,0,0],[
0,2.708,5.216,6.573,7.604,8.011,7.709,6.749,5.537,5.396,0,0],[
0,2.538,4.814,6.471,7.604,8.115,7.813,6.78,5.807,5.667,0,0],[
0,2.357,4.213,6.183,7.5,8.011,7.813,6.78,5.827,5.687,0,0],[
0,2.036,3.711,5.416,6.62,7.212,7.312,6.359,5.727,5.557,0,0],[
0,1.906,3.51,5.216,6.519,7.011,7.091,6.299,5.627,5.196,0,0]])






def twa(cap, dvent):
    twa = 180 - abs(((360 - dvent + cap) % 360) - 180)
    return twa

def polaire2_vect(polaires,vit_vent,angle_vent,tableau_caps):
    '''transformation tableau de caps en un point en tableau de donnees (twa , vit_vent)'''
    '''Pour une valeur de vent et un angle de vent déterminés'''
    ''' Retourne un tableau de vitesse polaires suivant le tableau de caps'''

    donnees = np.zeros((len(tableau_caps),2))
    for k in range(len(tableau_caps)):
        twa = 180 - abs(((360 - angle_vent + tableau_caps[k]) % 360) - 180)
        donnees[k]=[twa,vit_vent]
    valeurs = interpn((y1, x1), polaires, donnees, method='linear')
    return valeurs

def polaire(polaires, vit_vent, twa): # polaire simple
    donnees= [twa, vit_vent]
    valeur = interpn((y1, x1), polaires, donnees, method='linear')

    return valeur



if __name__ == '__main__':
    vit_vent = 19
    angle_vent = 100
    #cap = 160
    caps = np.array([165, 170, 180])



    res = polaire2_vect(polaires, vit_vent, angle_vent, caps)

    print ('Vitesse du vent {} noeuds , angle du vent {}° ' .format(vit_vent,angle_vent))
    print ('caps :', caps)
    print('Polaires',res)


    print ('Version simple')
    cap=165
    twa = 180 - abs(((360 - angle_vent + cap) % 360) - 180)
    res = polaire(polaires, vit_vent, twa)

    print ('Vitesse du vent {} noeuds , angle du vent {}° ' .format(vit_vent,angle_vent))
    print ('caps :', cap)
    print('Polaires',res)