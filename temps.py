from datetime import datetime
import time
import os
from dateutil import tz
basedir = os.path.abspath(os.path.dirname(__file__))
#local = tz.gettz() # Local time
#ET = tz.gettz('Europe/Paris') # European time




def filename():
    ''' retourne le nom du fichier du dernier grib sous lequel le grib chargé sera sauvé ou du dernier grib disponible
       la date du grib et le tig en secondes locales '''
    t = time.localtime()
    utc = time.gmtime()
    decalage_h = t[3] - utc[3]
    heures = [0,6,12,18]
        #on bloque l'heure du grib
    heure_grib = heures[((utc[3] + 19) // 6) % 4]  #
    #si utc inferieur à 5 la date doit etre celle de la veille
    if utc[3]<5:
        utc = time.gmtime(time.time() -18000)
    dategrib =datetime(utc[0] , utc[1] , utc[2] , int(heure_grib),0, 0)
    tig=time.mktime(dategrib.timetuple())+decalage_h*3600

    date= str(dategrib)
    filename="gribs/grib_gfs_" + date + ".hdf5"
    filenamehdf5 = os.path.join(basedir,filename)
    
    #time.time()- tig correspond bien à l'ecart de temps avec le grib
    return filenamehdf5,date,tig







print()
print()

print ('filename : ' ,filename() [0] )
print ('dategrib : ' ,filename() [1] )
print ('tig : ' ,filename() [2] )


dategrib=filename() [1]
tig=filename()[2]
tic=time.time()
date=dategrib[0:10].replace("-","")
print ('date', date)
strhour=dategrib[11:13]
print('strhour',strhour)


tig_formate_utc = time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig))

print('tig_formate_utc',tig_formate_utc)
print('temps instantane',time.time())

print ('ecart', (tic-tig)/3600)



print('\n')
print('\n')
print ('Exemples')
#temps instantanés
t = time.localtime()    #retour sous forme tuple
utc = time.gmtime()     #retour sous forme tuple
# peut etre utilise par 
print ('exemple heure : t[3]',t[3])
print ('temps en s',time.time())

print ('t',t)
print('utc',utc)

#decalage horaire 
print ('\nDecalage en heures', t[3]-utc[3])

#construction d'une date
heure_grib=6
dategrib =datetime(utc[0] , utc[1] , utc[2] , int(heure_grib),0, 0)
print ('\nDategrib : ',dategrib)

# transformation de cette date en s 
t1=time.mktime(dategrib.timetuple())
print ('t1',t1 )

t3 = time.localtime(t1)##retour sous forme tuple
print ('t3',t3)   
t4 = time.gmtime(t1)##retour sous forme tuple avec deux heures en moins mais ce n'est qu'un formatage
print ('t4',t4)   



# pour mon grib 
# je constitue la presentation de l'heure du grib
dategrib =datetime(utc[0] , utc[1] , utc[2] , int(heure_grib),0, 0)
print ('\nDategrib : ',dategrib)

# je peux la transformer en secondes mais ce sont des secondes locales
tig=time.mktime(dategrib.timetuple())
print ('tig en local ',tig )

# si je les transforme en date 
t5 = time.localtime(tig)
print('tig sous forme tuple',t5)
tig_formate_utc = time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig))
print('tig_formate_utc',tig_formate_utc)


tig_formate_local = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(tig))
print('tig_formate_local',tig_formate_local)

print()

# ecart en secondes entre le tempts instantané et le temps du grib