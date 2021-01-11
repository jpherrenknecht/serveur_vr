import json
from json import JSONEncoder
import numpy as np


with open('static/js/barriere.json', 'r') as fichier:                      # change dans fichier courants
        data1 = json.load(fichier)
        points  = data1['coords']        # on passe par numpy provisoirement
        
        print(points)
        
        
        nppoints=np.array(points)

        lngs=nppoints[:,0].reshape(-1,1)/1000
        lats=nppoints[:,1].reshape(-1,1)/1000
        poly=np.concatenate((lats,lngs),1)
        polyline=[arr.tolist() for arr in poly]
    
        # on cree un dictionnaire qui sera transforme en json 
        poly_json={'barrieretest': polyline}



# on peut 

# le recharge eventuellement 
with open('static/js/barriereglaces.json', 'r') as fichier:                      # change dans fichier courants
     data2 = json.load(fichier)



print('\n Premier Point \n',data2['barrieretest'][1])



# with open ("static/js/barriere2.json","w") as f:
#     json.dump(polyline,f)


# with open ("static/js/barriere2.json","r") as f:
#     data2 = json.load(f)


#     print (data2)
#         #print(polyline)
       