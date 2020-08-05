import numpy as np
import math
import os
import sys


# maximum sur une colonne np decommenter pour tester
# a = np.random .random_integers(10,50,size=(3,4))
# print(a)
# print()
# # maximum sur la troisieme colonne
# # numero de la ligne ou la valeur est maximum pour la troiseme colonne 
# # le o correspond à l'axe des colonnes
# n= np.argmax(a,0)
# print (n)
# # d'ou la valeur maxi de la colonne indice 2 
# colonne=3
# max2=a[np.argmax(a,0)[colonne],colonne]
# print( max2 )



def deplacement_x_y(x0,y0,d_t,HDG,VT):
    ''' fonction donnalnt le tuple point d arrivée en fonction des coordonnées du point de depart ''' 
    HDG_R = HDG * math.pi / 180     # cap en radians
    x= x0+ d_t / 3600 / 60 * VT * (np.sin(HDG_R) / math.cos(y0 * math.pi / 180)) 
    y= y0- d_t / 3600 / 60 * VT * np.cos(HDG_R)
    return x,y

 # fonction inverse trouver le cap et la distance connaissant le depart et l'arrivee 
    # avec des complexes
def dist_cap(D, A):
    '''retourne la distance et l'angle du deplacement entre le depart et l'arrivee'''
    C = A - D
    return np.abs(C), (450 + np.angle(C, deg=True)) % 360

def dist_cap2(x0,y0,x1,y1):

    coslat= math.cos(y0 * math.pi / 180)
    C=(x-x0)*coslat +(y-y0)*1j
    return np.abs(C), (450 + np.angle(C, deg=True)) % 360

def dist_cap3(D,A):

    coslat= np.cos(D.imag * math.pi / 180)
    C=(A.real-D.real)*coslat +(A.imag-D.imag)*1j
    return np.abs(C), (450 + np.angle(C, deg=True)) % 360


if __name__ == '__main__':
    from sys import platform as _platform
    print ('\n platform',_platform)    
    
    print('\nos.name',os.name)

    #print(platform.system())
    # test deplacement_x_y

    x0=-5.811
    y0=-46.0594
    d_t=300

    cap=260
    VT=6.87
    x,y=deplacement_x_y(x0,y0, d_t, cap, VT)


    print('Resultat du calcul ')
    print (x,y)
    print()   

    D= x0+y0*1j
    A= x+y*1j

    

    # cos de la latitude
    cos=math.cos(y0 * math.pi / 180)
    print ('cos',cos)
   # on corrige le point d'arrivee
    m=(x-x0)/(y-y0)
    a =math.atan(m*cos)
    print (180-a*180/math.pi)  # cette valeur la est bonne

    print('dist_cap2',dist_cap2(x0,y0,x,y))

    print (180-math.atan(m)*180/math.pi)

    D1=x0*cos +y0*1j
    A1=x*cos +y*1j
    print(dist_cap(D1, A1))

    print ('cap_dist3')
    print(dist_cap3(D, A))