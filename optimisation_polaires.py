import json
from json import JSONEncoder
import numpy as np


def polaire2_vectv2(polaires,tab_twa, tab_tws,vit_vent,angle_vent,tableau_caps):
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


def polairev2(polaires, ws, twa):
    ''' fonction extraction polaire en un seul point '''     
    '''interpolation bilineaire en utilisant np.interp 
    20 fois plus rapide que avec interpn scipy '''
    i= np.where(tabtws>ws)[0][0] 
    j= np.where(tabtwa>twa)[0][0] 
    twa_i= tabtwa[j-1]
    twa_s= tabtwa[j]
    xp=tabtws
    yp=polaires[j-1]
    yp2=polaires[j]
    a=np.interp(ws, xp, yp)
    b=np.interp(ws, xp, yp2)
    c=a+(b-a)*(twa-twa_i)/(twa_s-twa_i)
    return c

                  
def foil(ttwa,ttws,speedRatio,twaMin,twaMax,twaMerge,twsMin,twsMax,twsMerge):
    if ((ttwa>twaMin-twaMerge)and(ttwa<twaMax+twaMerge)and(ttws>twsMin-twsMerge)and(ttws<twsMax+twsMerge)):
        if (ttwa>twaMin-twaMerge) and (ttwa<(twaMin)):
            coeff1=(ttwa-twaMin+twaMerge)/twaMerge
        else :
            coeff1=1
        if (ttwa>(twaMax)) and (ttwa<(twaMax+twaMerge)):
            coeff2=(ttwa-twaMax)/twaMerge
        else :
            coeff2=1  
        if (ttws>twsMin-twsMerge) and (ttws<(twsMin)):
            coeff3=(ttws-twsMin+twsMerge)/twsMerge
        else :
            coeff3=1  
        if (ttws>(twsMax)) and (ttws<(twsMax+twsMerge)):
            coeff4=(ttws-twsMax)/twsMerge
        else :
            coeff4=1  

        # print ('coeffs',coeff1,coeff2,coeff3,coeff4)    
        coeff=1+(speedRatio-1)*coeff1*coeff2*coeff3*coeff4
    else :
        coeff=1    
    #print ('Coeff  foils : ',coeff )
    return coeff




def lecture(fichier_polaires):
    with open(fichier_polaires, 'r') as fichier:   
        polaires = json.load(fichier)
    tabtws= np.asarray(polaires['polar']['tws'])                                            
    tabtwa= np.asarray(polaires['polar']['twa'])
    print ('\ntabtws', tabtws)  
    print('\ntabtwa',tabtwa)     
    print()         
    nbtws=len(tabtws)
    nbtwa=len(tabtwa)
    nb= len(polaires['polar']['sail'])
    voile=[]
    toutespolaires=np.zeros((nbtwa,nbtws,nb))
    for i in range(nb) :
        voile.append( polaires['polar']['sail'][i]['name'])
        toutespolaires[:,:,i]= polaires['polar']['sail'][i]['speed']
    # caracteristiques foils
    speedRatio=polaires['polar']['foil']['speedRatio']
    twaMin=polaires['polar']['foil']['twaMin']
    twaMax=polaires['polar']['foil']['twaMax']
    twaMerge=polaires['polar']['foil']['twaMerge']
    twsMin=polaires['polar']['foil']['twsMin']
    twsMax=polaires['polar']['foil']['twsMax']
    twsMerge=polaires['polar']['foil']['twsMerge']
    hull=polaires['polar']['hull']['speedRatio']
    return tabtws,tabtwa,voile,speedRatio,twaMin,twaMax,twaMerge,twsMin,twsMax,twsMerge,hull,toutespolaires




 


def fullpack(fichier_polaires_raw,nomfichiersortie):
    ''' retourne le fichier correspondant a un fullpack '''

    with open(fichier_polaires, 'r') as fichier:   
        polaires = json.load(fichier)
    tabtws= polaires['polar']['tws']                                            
    tabtwa= polaires['polar']['twa']
    nbtws=len(tabtws)
    nbtwa=len(tabtwa)
    nb= len(polaires['polar']['sail'])
    toutespolaires=np.zeros((nbtwa,nbtws,nb)) # initialisation d'un numpy array
    voile=[]
    for i in range(nb) :                     # constitution du fichier global de polaires brutes
        voile.append( polaires['polar']['sail'][i]['name'])
        toutespolaires[:,:,i]= polaires['polar']['sail'][i]['speed']



    # recuperation des valeurs max     
    hull=1.003
    polairesmax=np.amax(toutespolaires,axis=2)
    # creation d'un tableau de coeff foils
    polaire=np.zeros((nbtwa,nbtws)) # initialisation d'un numpy array
    for i in range (nbtwa):
        for j in range (nbtws):    
            polaire[i,j]=np.around(polairesmax[i,j]*foil(tabtwa[i],tabtws[j],speedRatio,twaMin,twaMax,twaMerge,twsMin,twsMax,twsMerge)*hull,decimals=3)
    
    
    # calcul des vitesses degre par degre pour une force de vent
    # calcul des vitesses pour une interpolation  
    ws=11.4
    twa=52
    res1=polairev2(polaire, ws, twa) 
    
    print (res1)
    print ('La Vitesse polaire pour twa {:6.2f} et vent {:6.2f} est de {:6.3f} '.format( twa,ws, res1))    #transformation en tableau
    
    polaires_fullpack=[arr.tolist() for arr in polaire]
   
    
    #print (polaires_fullpack)
    # print()
    # i=15        #indice twa
    # j=11
    # print ('polairemax pour twa {:6.2f} et vent {:6.2f} est de {:6.3f} '.format( tabtwa[i],tabtws[j], polairesmax[i,j]))
    # resultat=polaire[i,j]
    # print ('Resultat global',resultat )
    # print()

    # constitution du fichier json  

    fullpack={"tab_tws" : tabtws, "tab_twa" :tabtwa, "polaires" :polaires_fullpack}
    filename='static/js/'+nomfichiersortie+'.json'
    with open (filename,"w") as f:
        json.dump(fullpack,f)

    return None






#  "caravelle":
#         {
#         "pres_mini" : 65,
#         "var_mini" : 20,
#         "tab_tws" :[0,6,10,14,20,24,30,35,40,55,56,70],
#         "tab_twa" :[0,50,60,65,70,80,90,100,110,120,130,140,150,160,170,180],
#         "polaires" :[[0,0,0,0,0,0,0,0,0,0,0,0],[
#                     0,0,0,0,0,0,0,0,0,0,0,0],[
#                     0,2.859,4.142,4.343,4.483,3.119,2.317,1.474,1.224,1.194,0,0],[
#                     0,3.45,5.085,5.386,5.647,4.253,3.46,2.568,2.367,2.307,0,0],[
#                     0,3.561,5.466,5.657,6.048,5.135,4.995,3.651,3.36,3.28,0,0],[
#                     0,3.551,5.958,6.275,6.801,6.593,6.488,5.143,4.253,4.142,0,0],[
#                     0,3.48,6.219,6.563,7.291,7.208,7.125,5.654,4.744,4.624,0,0],[
#                     0,3.38,6.419,6.779,7.636,7.521,7.458,5.956,4.945,4.814,0,0],[
#                     0,3.28,6.339,6.881,7.844,7.719,7.5,6.269,5.135,5.005,0,0],[
#                     0,3.109,6.098,6.748,7.844,7.928,7.396,6.373,5.236,5.105,0,0],[
#                     0,2.869,5.717,6.707,7.719,7.928,7.5,6.561,5.336,5.206,0,0],[
#                     0,2.708,5.216,6.573,7.604,8.011,7.709,6.749,5.537,5.396,0,0],[
#                     0,2.538,4.814,6.471,7.604,8.115,7.813,6.78,5.807,5.667,0,0],[
#                     0,2.357,4.213,6.183,7.5,8.011,7.813,6.78,5.827,5.687,0,0],[
#                     0,2.036,3.711,5.416,6.62,7.212,7.312,6.359,5.727,5.557,0,0],[
#                     0,1.906,3.51,5.216,6.519,7.011,7.091,6.299,5.627,5.196,0,0]]
#         },






# calcul des vitesses polaires pour une voile pour toutes les twa et une vitesse de vent
def polaires_detail(nvoile,toutespolaires,tws):
    tabtwa=np.array(range(181))
    polaires_voile=toutespolaires[:,:,nvoile]



    return None




def interpolpolairesimple (nvoile,toutespolaires,ws,wa):
    #calcul de la vitesse polaire par interpolation pouur une vitesse et un vent
    # recuperation du tableau pour une voile
    polaires_voile=toutespolaires[:,:,nvoile]
    # recuperation des indices
    i= np.where(tabtws>ws)[0][0] 
    j= np.where(tabtwa>wa)[0][0] 
    twa_i= tabtwa[j-1]
    twa_s= tabtwa[j]
    xp=tabtws
    yp=polaires_voile[j-1]
    yp2=polaires_voile[j]
    a=np.interp(ws, xp, yp)
    b=np.interp(ws, xp, yp2)
    c=a+(b-a)*(wa-twa_i)/(twa_s-twa_i)
    return c





if __name__ == "__main__" :

    fichier_polaires='static/js/rawpolars_imoca40.json'  # nom du fichier entree toutes voiles recupere sur vr
    bateau='class_40'                                    # nom du fichier de sortie polaires fullpack 
    tabtws,tabtwa,voile,speedRatio,twaMin,twaMax,twaMerge,twsMin,twsMax,twsMerge,hull,toutespolaires=lecture(fichier_polaires)

    print (tabtws,tabtwa,voile,speedRatio,twaMin,twaMax,twaMerge,twsMin,twsMax,twsMerge,hull)
    
    fullpack(fichier_polaires,bateau)

    ws=12
    wa=90
    nvoile=4

#"foil":{"speedRatio":1.04,"twaMin":80,"twaMax":160,"twaMerge":10,"twsMin":16,"twsMax":35,"twsMerge":5},
    
    coeff_foil=foil(wa,ws,speedRatio,twaMin,twaMax,twaMerge,twsMin,twsMax,twsMerge)
    res=interpolpolairesimple (nvoile,toutespolaires,ws,wa)

    print ('Liste des voiles',voile)
    print('Voile choisie : ', voile[nvoile] )
    print('Speedratio ',speedRatio)
    print('tws : ',ws,' twa : ',wa)
    print('Resultat brut: ', res )
    res=res*1.003*coeff_foil         #ajout du polish et des foils
    print('Resultat avec polish et foils: ', res )




                # console.log('Nom de la Voile : '+voile)
                # j=i+1
                # eval("polairesj"+j +"=polaires['polar']['sail'][i]['speed']")




# with open('static/js/barriere.json', 'r') as fichier:                      # change dans fichier courants
#         data1 = json.load(fichier)
#         points  = data1['coords']        # on passe par numpy provisoirement
        
#         print(points)
        
        
#         nppoints=np.array(points)

#         lngs=nppoints[:,0].reshape(-1,1)/1000
#         lats=nppoints[:,1].reshape(-1,1)/1000
#         poly=np.concatenate((lats,lngs),1)
#         polyline=[arr.tolist() for arr in poly]
    
#         # on cree un dictionnaire qui sera transforme en json 
#         poly_json={'barrieretest': polyline}


# on le sauvegarde sous forme de json
# with open("static/js/barriereglaces.json","w") as f :
#      json.dump(poly_json,f)

# # on peut 

# # le recharge eventuellement 
# with open('static/js/barriereglaces.json', 'r') as fichier:                      # change dans fichier courants
#      data2 = json.load(fichier)



# print('\n Premier Point \n',data2['barrieretest'][1])



# with open ("static/js/barriere2.json","w") as f:
#     json.dump(polyline,f)


# with open ("static/js/barriere2.json","r") as f:
#     data2 = json.load(f)


#     print (data2)
#         #print(polyline)
       