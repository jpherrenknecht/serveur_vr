
from scipy.interpolate import RegularGridInterpolator,interp2d,interpn
import  numpy  as np

# angle mini au près 36°
# angle maxi au var 160°
angle_twa_pres = 35
angle_twa_ar = 30
# Pour utilisation dans routage
angle_pres = 35
angle_var = 30
x1=np.array([0,6,8,10,12,14,16,20,40,50,70])
y1=np.array([0,34,35,36,38,41,47,52,60,75,90,110,120,130,135,140,143,147,150,180])


polaires=np.array([[
0,0,0,0,0,0,0,0,0,0,0],[
0,1.243,6.33,3.96,9.183,12.49,13.365,12.017,3.95,1.485,0.074],[
0,3.054,8.247,7.793,12.217,13.449,13.934,13.607,7.299,4.413,0.211],[
0,4.245,9.7,9.921,12.817,13.639,14.102,14.25,9.068,5.982,0.747],[
0,6.583,11.132,11.353,13.228,13.892,14.449,14.924,10.269,6.845,0.99],[
0,8.984,12.038,12.164,13.691,14.397,14.934,15.334,11.311,8.067,1.18],[
0,10.922,12.923,13.48,14.386,15.197,15.86,16.45,12.143,9.099,1.306],[
0,11.785,13.47,14.334,15.071,15.987,16.714,17.524,12.565,9.574,1.432],[
0,12.775,14.26,15.134,15.966,16.946,17.851,18.915,13.07,10.206,1.58],[
0,13.681,15.134,16.492,17.584,18.523,20.529,22.258,13.807,10.742,1.727],[
0,13.67,15.492,17.156,18.854,20.372,22.048,24.249,14.597,10.805,2.001],[
0,13.133,15.144,17.419,19.077,21.245,22.99,25.148,16.946,11.943,2.539],[
0,12.743,15.144,16.956,18.461,21.018,23.297,25.98,19.052,13.133,3.023],[
0,11.774,14.344,16.103,18.302,21.084,23.329,26.035,21.116,14.533,3.812],[
0,11.184,13.67,15.871,17.803,20.631,22.814,25.717,22.095,15.492,4.465],[
0,10.7,13.007,14.987,16.89,19.509,22.366,25.006,22.516,16.251,5.013],[
0,10.237,12.49,14.218,16.391,18.862,22.005,24.655,22.359,16.324,5.16],[
0,9.71,11.985,13.491,15.616,17.988,21.007,24.074,21.863,15.871,5.087],[
0,9.11,11.543,12.965,14.958,17.47,19.836,23.373,21.21,15.261,4.908],[
0,4.245,6.182,6.814,7.509,8.415,9.352,10.374,11.058,10.163,3.855]])


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
    print('tws : ',tws)
    print('twa', twa(HDG, twd))
    print('polaires calculees 4 ', res4)





    HDG=np.array([100,101,102])   #caps
    TWD=np.array([150,150,150])   #direction vent
    TWS=np.array([12,12,12])      #vitesse vent
    res=polaire3_vect(polaires, TWS, TWD, HDG)
    print('TWS : ', TWS)
    print('twa',twa(HDG,TWD))
    print('polaires calculees 3',res)

    print()




    vit_vent = 10.5
    angle_vent = 0
    #cap = 160
    caps = np.array([139, 140, 141])
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