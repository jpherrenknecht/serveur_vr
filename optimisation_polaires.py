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
    i= np.where(tab_tws>ws)[0][0] 
    j= np.where(tab_twa>twa)[0][0] 
    twa_i= tab_twa[j-1]
    twa_s= tab_twa[j]
    xp=tab_tws
    yp=polaires[j-1]
    yp2=polaires[j]
    a=np.interp(ws, xp, yp)
    b=np.interp(ws, xp, yp2)
    c=a+(b-a)*(twa-twa_i)/(twa_s-twa_i)
    return c

print('test0')







with open('static/js/fullpolarsvg.json', 'r') as fichier:   
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


print('Speedratio ',speedRatio)                   # la transition se fait entre twamin -twaMerge et twamin
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

        print ('coeffs',coeff1,coeff2,coeff3,coeff4)    
        coeff=1+(speedRatio-1)*coeff1*coeff2*coeff3*coeff4
    else :
        coeff=1    
    print ('Coeff :',coeff )
    return coeff







print (voile)
# tabtwa=np.array(range(181))
# print(tabtwa)

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

    ws=13.5
    wa=79
    nvoile=4
#"foil":{"speedRatio":1.04,"twaMin":80,"twaMax":160,"twaMerge":10,"twsMin":16,"twsMax":35,"twsMerge":5},
    
    coeff_foil=foil(wa,ws,speedRatio,twaMin,twaMax,twaMerge,twsMin,twsMax,twsMerge)

    res=interpolpolairesimple (nvoile,toutespolaires,ws,wa)
    print('Voile : ', voile[nvoile] )
    print('tws : ',ws,' twa : ',wa)
    print('Resultat brut: ', res )
    res=res*1.003*coeff_foil#ajout du polish


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
       