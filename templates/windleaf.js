<html>
    <head>
        <meta name="viewport"content="width=device-width, initial-scale=1.0, shrink-to-fit=no" />             
        <script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
        <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js"></script>
        <script src="https://unpkg.com/leaflet@1.4.0/dist/leaflet.js"></script>
        <script src="https://api.windy.com/assets/map-forecast/libBoot.js"></script>
        <link rel="stylesheet" href="https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/themes/smoothness/jquery-ui.css">
        <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='css/base.css') }}">
    </head>


    <script>
            function arrondi(a,n)
            {return(Math.round(a*10**n)/10**n);}


            function h_mn(sec)
			{   sec=sec+15
				h=Math.floor(sec/3600)	
				mn=Math.ceil((sec-3600*h)/60)
				s=sec-3600*h-60*mn 
				res=h+'h '+mn+'mn'
				return res
			}
        
            function deg_mn_(sec)
			{   sec=sec+15
				h=Math.floor(sec/3600)	
				mn=Math.ceil((sec-3600*h)/60)
				s=sec-3600*h-60*mn 
				res=h+'h '+mn+'mn'
				return res
			}

            function pos_dec_mn(pos)
			{  // transforme les degres decimaux en mn sec
			 	abs=Math.abs(pos)
				deg=Math.floor(abs)
				min=Math.floor((abs-deg)*60)
				sec=Math.round(((abs-deg)*60-min)*60)
				return deg+'°'+min+'mn'+sec+'s'
            }  
            
            function numero_point(sec)
            {var nbiso_dixmn=72;
                if (sec<nbiso_dixmn*600)
                    {npt=Math.floor (sec/600)}
                else
                    {npt=Math.floor(sec/3600)+72}
                return npt;
            }


            function cap(x0,y0,x1,y1)
                {capi=90-(Math.atan((y1-y0)/(x1-x0+0.0000001))*180/3.1416);
                    if ((x1-x0)>0)
                        {capi=capi+180}
                return capi }   
                function pos_dec_mn(pos)
                    {   abs=Math.abs(pos)
                        deg=Math.floor(abs)
                        min=Math.floor((abs-deg)*60)
                        sec=Math.round(((abs-deg)*60-min)*60)
                        return deg+'°'+min+'mn'+sec+'s'
                    }    

           		deltay=tws_sup-tws_inf
				fx1y1   = bateau[i_sup-1][j_sup-1]
				fx2y1   = bateau[i_sup][j_sup-1]			
				fx1y2   = bateau[i_sup-1][j_sup]			
				fx2y2   = bateau[i_sup][j_sup]			
				dfx     = fx2y1-fx1y1			
				dfy     = fx1y2-fx1y1			
				dfxy    = fx1y1+fx2y2-fx2y1-fx1y2				
				fxy     = dfx*dx/deltax  + dfy*dy/deltay + dfxy*dx*dy/deltax/deltay + fx1y1
				return fxy
			}
            function cvent(u,v) //retourne la vitesse du vent et sa force a partir de u et v
			{
				vit = Math.sqrt(u*u + v*v)
				angle= Math.acos(v/vit)*180/Math.PI+180;
				if (u<0)
				{angle=360-angle}
				vit*= 1.94384     // Vitesse en noeuds
				return [vit,angle]				
			} 

			function interpol2d(XX,t0,i_lat,i_lng)
			{			
				lat0    = Math.floor(i_lat)       // partie entiere
				lng0    = Math.floor(i_lng)
				//t0    = Math.floor(i_t)       // t0 est censé être un indice entier
				dec_lat = i_lat%1    				// partie decimale
				dec_lng = i_lng%1
                console.log( 'lat0 '+ lat0 +' Lng0 '+lng0 +' t0 ' + t0) 
				fx1y1   = XX[t0][lat0][lng0]
				fx2y1   = XX[t0][lat0+1][lng0]
				fx1y2   = XX[t0][lat0][lng0+1]
				fx2y2   = XX[t0][lat0+1][lng0+1]
				dfx     = fx2y1-fx1y1
				dfy     = fx1y2-fx1y1
				dfxy    = fx1y1+fx2y2-fx2y1-fx1y2
				fxy     = dfx*dec_lat  + dfy*dec_lng + dfxy*dec_lat*dec_lng + fx1y1
				return fxy
			}

			function interpol3d(XX,i_t,i_lat,i_lng)
			{
				lat0    = Math.floor(i_lat)       // partie entiere
				lng0    = Math.floor(i_lng)
				t0      = Math.floor(i_t)
				dec_t   = i_t%1						// partie decimale				
				dec_lat = i_lat%1
				dec_lng = i_lng%1
				r1      = interpol2d(XX,t0,i_lat,i_lng)
				r2      = interpol2d(XX,t0+1,i_lat,i_lng)
				r       = r1+(r2-r1)*dec_t
				return r
			}

            function gvent (lat,lng ,t)
			{
			i_lat=lat-latini       // ecart avec la latitude du grib chargé
			i_lng=lng-lngini
			console.log(' ')	
			console.log ('************* Latitude  '+lat+' i_lat : '+i_lat)
			console.log ('************* Longitude ' +lng+' i_lng : '+i_lng)
			console.log(' ')
			i_t=(t-tig)/3600/3     // Ecart en heures avec le tig  modulo 3h
			u10=interpol3d(U10,i_t,i_lat,i_lng)	
			v10=interpol3d(V10,i_t,i_lat,i_lng)	
			res=cvent(u10,v10) 		// vitesse=res[0], angle=res[1] 
			console.log('resultat'+ res)
			return res	

			}

            function ftwa(cap,dvent)
			{//twa en valeur absolue
			return 180-Math.abs(((cap-dvent+360)%360)-180)
			}

			function ftwao(cap,dvent)
			{ // twa orientée
			twa1=(cap-dvent+360)%360
			if (twa1<180)
			{twao=twa1}
			else{twao=twa1-360}
			return twao	
			}

			function pos_dec_mn(pos)
			{  // transforme les degres decimaux en mn sec
			 	abs=Math.abs(pos)
				deg=Math.floor(abs)
				min=Math.floor((abs-deg)*60)
				sec=Math.round(((abs-deg)*60-min)*60)
				return deg+'°'+min+'mn'+sec+'s'
			}  

			function h_mn(sec)
			{
				h=Math.floor(sec/3600)	
				mn=Math.floor((sec-3600*h)/60)
				s=sec-3600*h-60*mn
				res=h+'h '+mn+'mn '+s+'s'
				return res
			}


			function polinterpol2d(bateau,twa,tws)
			{	// parametres : polaires du bateau twa et tws
				twa=Math.abs(twa)
			    var i_sup=l2.findIndex(element => element > twa);

				var j_sup=l1.findIndex(element => element > tws);				
				var twa_inf=l2[i_sup-1]
				var twa_sup=l2[i_sup]
				var tws_inf=l1[j_sup-1]
				var tws_sup=l1[j_sup]
				console.log('isup : '+ i_sup)
                dx = twa-twa_inf 				// Ecart avec la valeur d'indice mini
				dy = tws-tws_inf

				deltax=twa_sup-twa_inf
				deltay=tws_sup-tws_inf
				fx1y1   = bateau[i_sup-1][j_sup-1]
				fx2y1   = bateau[i_sup][j_sup-1]			
				fx1y2   = bateau[i_sup-1][j_sup]			
				fx2y2   = bateau[i_sup][j_sup]			
				dfx     = fx2y1-fx1y1			
				dfy     = fx1y2-fx1y1			
				dfxy    = fx1y1+fx2y2-fx2y1-fx1y2				
				fxy     = dfx*dx/deltax  + dfy*dy/deltay + dfxy*dx*dy/deltax/deltay + fx1y1
				return fxy
			}


			function vit_angle_vent (lat,lng ,t)
			{
			i_lat=-lat-latini       // ecart avec la latitude du grib chargé
			i_lng=360+lng-lngini
			i_t=(t-tig)/3600/3     // Ecart en heures avec le tig  modulo 3h
				
			// console.log ('**** Temps depuis le grib en h '+i_t*3+ ' Indice '+i_t)
			// console.log ('**** latini : '+latini+' ********* Latitude  '+lat+' i_lat : '+i_lat)
			// console.log ('**** lngini : '+lngini+' ********* Longitude ' +lng+' i_lng : '+i_lng)
					
			u10=interpol3d(U10,i_t,i_lat,i_lng)	
			v10=interpol3d(V10,i_t,i_lat,i_lng)	
			res=cvent(u10,v10) 		// vitesse=res[0], angle=res[1] 
			// console.log('resultat'+ res)
			return res	

			}

			function cvent(u,v) //retourne la vitesse du vent et sa force a partir de u et v
			{
				vit = Math.sqrt(u*u + v*v)
				angle= Math.acos(v/vit)*180/Math.PI+180;
				if (u<0)
				{angle=360-angle}
				vit*= 1.94384     // Vitesse en noeuds
				return [vit,angle]				
			} 

			

            
			function dist_cap_ortho(lati,lngi,latfi,lngfi)
			{// latitude origine equateur positive vers le nord
			//longitude greenwich positive vers l'est 
			latirad = lati*Math.PI/180
			latfrad = latfi*Math.PI/180
			lb_m_la=(lngfi-lngi)*Math.PI/180
			cosfia=Math.cos(latirad)
			sinfia=Math.sin(latirad)
			sinfib=Math.sin(latfrad)
			cosfib=Math.cos(latfrad)
			cos_lb_m_la=Math.cos(lb_m_la)
			sin_lb_m_la=Math.sin(lb_m_la)
			capo= Math.atan(cosfib*sin_lb_m_la/(cosfia*sinfib-sinfia*cosfib*cos_lb_m_la))*180/Math.PI
			if( (latfi-lati)<0)
			{capo=180+capo}
			else {capo=(capo+360)%360}
			dist= Math.acos(sinfia*sinfib+cosfia*cosfib*cos_lb_m_la)/Math.PI*180*60
			return [dist,capo]
			}


			function deplacement(latinit,lnginit,dt,vitesse,cap)
			{		
				cap_r=cap*Math.PI/180
				latfdep=latinit+vitesse*dt/3600/60*Math.cos(cap_r)
				lngfdep=lnginit+vitesse*dt/3600/60*Math.sin(cap_r)/Math.cos(latinit*Math.PI/180)
				arrivee=[latfdep,lngfdep]
				return arrivee 

			}

            function polyline_twa(latdep,lngdep,latf,lngf,tsimul)
			{  
				//console.log ('latdep dans polyline twa :' +latdep+ ' lngdep : ' +lngdep +' latf : ' +latf +' lngf : '+lngf +' tsimul : '+tsimul)
				//Cap généré par le curseur recherche du vent et twa en consequence 
				hdg_ini=dist_cap_ortho(latdep,lngdep,latf,lngf,)[1]
                //console.log( 'cap initial :' + hdg_ini)
				vent_ini=vit_angle_vent (latdep,lngdep,tsimul)
				tws_ini=vent_ini[0]
				twd_ini=vent_ini[1]				
				twa_ini=ftwao(hdg_ini,twd_ini)
				polyline= [[latdep,lngdep]]  //initialisation de la polyline
				dt=600   //intervalle entre deux points =10 mn

				lat6 = latdep
				lng6= lngdep
				
                twa=twa_ini    // la twa est celle donnée initialement par le curseur
				capa=hdg_ini
				t=tsimul
				for (var i=0;i<=72;i++)
				{tsimul = t+i*dt
				meteo=vit_angle_vent (lat6,lng6,tsimul)
				vit_polaire=polinterpol2d(polairesjs,twa_ini,meteo[0])	
                capa=twa_ini+meteo[1]
				point=deplacement(lat6,lng6,dt,vit_polaire,capa)     //calcul du nouveau point 
				lat6=point[0];lng6=point[1];
				polyline.push(point)	
				}
				//console.log (' polyline '+polyline)
			return [polyline,twa_ini]  
			}

            function polyline_cap(latdep,lngdep,latf,lngf,tsimul)
			{  
				console.log ('latdep dans polyline cap :' +latdep+ ' lngdep : ' +lngdep +' latf : ' +latf +' lngf : '+lngf +' tsimul : '+tsimul)
				//Cap généré par le curseur recherche du vent et twa en consequence 
				hdg_ini=dist_cap_ortho(latdep,lngdep,latf,lngf,)[1]

                // console.log( 'cap initial :' + hdg_ini)
				vent_ini=vit_angle_vent (latdep,lngdep,tsimul)
				tws_ini=vent_ini[0]
				twd_ini=vent_ini[1]				
				twa_ini=ftwao(hdg_ini,twd_ini)
				polyline2= [[latdep,lngdep]]  //initialisation de la polyline
				dt=600   //intervalle entre deux points =10 mn
				lat7 = latdep
				lng7= lngdep
				twa=twa_ini    // la twa est celle donnée initialement par le curseur
				capi=hdg_ini

				 t=tsimul
				 for (var i=0;i<=72;i++)
                    {tsimul = t+i*dt
                     meteo=vit_angle_vent (lat7,lng7,tsimul)
                     twa=ftwa(hdg_ini,meteo[1])
                    //  console.log ('hdg_ini ' + hdg_ini + ' meteo 1 '+meteo[1] )
                    //  console.log( 'test dans polyline_cap   twa : '+ twa + 'cap : ' +capi+' dirvent :'+meteo[1] + 'vit_vent :' + meteo[0]) 

                     vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])	                
                    // console.log('cap dans polylinecap'+capi )
                    point=deplacement(lat7,lng7,dt,vit_polaire,capi)     //calcul du nouveau point 
                    lat7=point[0];lng7=point[1];
                    polyline2.push(point)	
                    }
			//	console.log (' polyline '+polyline2)
			return [polyline2,capi]  
			}

            function polyline_cap2(latdep,lngdep,cap,tsimul)
			{  
				console.log ('Donnees de  polyline cap  latdep :' +latdep+ ' lngdep : ' +lngdep +' cap: ' +cap +' tsimul : '+tsimul)
				//Cap généré par le curseur recherche du vent et twa en consequence 
				hdg_ini=cap    // console.log( 'cap initial :' + hdg_ini)
                meteo_ini=vit_angle_vent (latdep,lngdep,tsimul)
                console.log(' llllllll 336 meteo_ini '+ meteo_ini)
				tws_ini=meteo_ini[0]
				twd_ini=meteo_ini[1]				
				twa_ini=ftwao(hdg_ini,twd_ini)
				polyline2= [[latdep,lngdep]]  //initialisation de la polyline
				dt=600   //intervalle entre deux points =10 mn
				lat7 = latdep
				lng7= lngdep
				twa=twa_ini    // la twa est celle donnée initialement par le curseur
				capi=hdg_ini

				 t=tsimul
				 for (var i=0;i<=72;i++)
                    {tsimul = t+i*dt
                     meteo=vit_angle_vent (lat7,lng7,tsimul)
                     twa=ftwa(hdg_ini,meteo[1])
                    //  console.log ('hdg_ini ' + hdg_ini + ' meteo 1 '+meteo[1] )
                    //  console.log( 'test dans polyline_cap   twa : '+ twa + 'cap : ' +capi+' dirvent :'+meteo[1] + 'vit_vent :' + meteo[0]) 

                     vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])	                
                    // console.log('cap dans polylinecap'+capi )
                    point=deplacement(lat7,lng7,dt,vit_polaire,capi)     //calcul du nouveau point 
                    lat7=point[0];lng7=point[1];
                    polyline2.push(point)	
                    }
			//	console.log (' polyline '+polyline2)
			return [polyline2,capi]  
			}




    // Fonction zezo                
        function crsdist(lat1, lon1, lat2, lon2)
         {
            var a = crsdist_num(lat1, lon1, lat2, lon2);
            var dist = Math.round(a[1] * 34377.4)/10;
            if (dist.toString().indexOf('.') < 0)
             {
                    dist += '.0';
             }
            var dir = Math.round(a[0] * (180/Math.PI) * 10)/10;
            if (dir.toString().indexOf('.') < 0) 
            {
                dir += '.0';
            }
            dir = dir.toString();
            dist = dist.toString();
                while (dir.length < 5) 
            {
                dir = " " + dir;
            }
            while (dist.length < 6) {
                dist = " " + dist;
            }
            //var res = dist + 'nm ' + dir + '°';
            var res = 'Cap :'+dir +'° Distance :'+dist+'M';
        return res;
        }
        


            function crsdist_num(lat1, lon1, lat2, lon2)
        {
            lat1 = lat1 * Math.PI/180;
            lon1 = lon1 * Math.PI/180;
            lat2 = lat2 * Math.PI/180;
            lon2 = lon2 * Math.PI/180;
            var crs;        
            var d=Math.acos(Math.sin(lat1)*Math.sin(lat2)+Math.cos(lat1)*Math.cos(lat2)*Math.cos(lon1-lon2));
            var argacos=(Math.sin(lat2)-Math.sin(lat1)*Math.cos(d))/(Math.sin(d)*Math.cos(lat1));
            if (Math.sin(lon2-lon1) > 0){   
                    crs=Math.acos(argacos); 
            } else {
                    crs=2*Math.PI-Math.acos(argacos); 
            }
            return [crs,d];
        }

        



        // pour formater les dates
            var intl=new Intl.DateTimeFormat("en-US",{month:"2-digit",day:"2-digit", hour12: false,hour:"2-digit", minute:"2-digit" });
         // on recupere les donnees postées
            latdep        = - {{ latdep }}
            lngdep        =   {{ lngdep }}
            latar         = - {{  latar }}
            lngar         =   {{  lngar }}
            
            polylinered   =   {{  multipolyred }}
            polylineblack =   {{  multipolyblack }}
            polylineblue  =   {{  route }}
            comment       =   {{  comment }}
            l1            =   {{ l1 }}           // cles pour lire les tableaux de polaire
            l2            =   {{ l2 }}
            polairesjs    =   {{ polairesjs }}; 
            
            U10 = {{ U10 }};
			V10 = {{ V10 }};
			tig = {{ tig   }};
            tsimul  = {{ t0    }};

			latini= {{ latini }};
			latfin= {{ latfin }};
			lngini= {{ lngini }};
			lngfin= {{ lngfin }}; 
            

			console.log('tig : ' + tig )
			console.log('latini : '+ latini)
			console.log('latfin : '+ latfin)
			console.log( 'lngini : '+ lngini)
			console.log('lngfin : '+ lngfin)
         
            var tooltip = new Array();
            
            for ( var i=0 ; i<comment.length ; i++ )
            {
             // secondes depuis le depart    
             sec= comment[i][2]-tsimul
             sec=sec-(sec%60)
            tooltip[i]='<b>'+intl.format(1000*comment[i][2])+' soit +  '+ h_mn(sec)+  '<br> Lat : '+comment[i][0].toFixed(4) +'° ('+pos_dec_mn(comment[i][0])+')<br>Lng : ' +comment[i][1].toFixed(4) +'° (' +pos_dec_mn(comment[i][1])+')<br> TWS : ' +comment[i][3].toFixed(2)
                +' Noeuds  -  TWD : ' +comment[i][4].toFixed(0)+'° <br>  Cap ' +comment[i][5].toFixed(1) +'°     -  TWA ' +comment[i][6].toFixed(1) +'° <br> Vitesse :  ' +comment[i][7].toFixed(2) +' Noeuds'}    
            
             // centrage de la carte 
             var latmap=(latdep+latar)/2;           
            var lngmap=(lngdep+lngar)/2;

            dist=((latdep-latar)**2+(lngdep-lngar)**2)**.5;
            //console.log('***************dist : '+dist);
            if(dist<5)
                {zoomp=7}
            else if (dist<10)
                {zoomp=6}
            else if (dist<20)
                {zoomp=5}  
            else if (dist<70)
                {zoomp=5}  
            else {zoomp=4}

            console.log('***************zoom : '+zoomp);
            // test polaires    

            twa= 63	
			tws= 7.5
            console.log('-------------',tsimul)

			res=polinterpol2d(polairesjs,twa,tws)
			console.log('*******resultat pour twa par fonction = '+twa+ '  tws  '+ tws +'  resultat  '+res   )

       



        function initialize()
        {            
            document.formu.latdep.value = latdep.toFixed(4)+' ( '+pos_dec_mn(latdep) +' )'
            document.formu.lngdep.value = lngdep.toFixed(4)+' ( '+pos_dec_mn(lngdep) +' )'
            document.formu.latar.value  = latar.toFixed(4)+' ( '+pos_dec_mn(latar) +' )'
            document.formu.lngar.value  = lngar.toFixed(4)+' ( '+pos_dec_mn(lngar) +' )'
            //document.formu.test.value=dist
        }
   

        const options = {
        key: 'ydO74Xuxv2WWOEShDpel1kaiae8zCnLO',
        verbose: true,

        // Optional: Initial state of the map
        lat: (latdep+latar)/2,
        lon: (lngdep+lngar)/2,
        zoom: zoomp,
        };

    // Initialize Windy API
        windyInit(options, windyAPI =>
    {
        // windyAPI is ready, and contain 'map', 'store',
        // 'picker' and other usefull stuff
        // const { map } = windyAPI;
        // const { store } = windyAPI;
        // const { picker } = windyAPI;
       
        const { map,picker, utils, broadcast,store } = windyAPI;
        
       
    // Ajout des isochrones et de la route
            L.polyline(polylineblack).setStyle({
            color: 'black',
            weight:1,
            opacity:0.3,
            }).addTo(map);

            L.polyline(polylinered).setStyle({
            color: 'red',
            weight:1,
            opacity:0.3,

            }).addTo(map);

            L.polyline(polylineblue).setStyle({
            color: 'blue',
            weight:2,
            }).addTo(map);


    // classes pour les icones
            var LeafletIcon=L.Icon.extend({
            options:{
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            shadowSize: [41, 41],
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34] 
                    }
            });

            var greenIcon = new LeafletIcon({ iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png'});
            var blackIcon = new LeafletIcon({ iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-black.png'});    
            var redIcon   = new LeafletIcon({ iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png'});   

    // marqueurs depart et arrivee        
        L.marker([latdep, lngdep],  {icon: blackIcon}).addTo(map);
        L.marker([latar, lngar],    {icon: redIcon}).addTo(map);
            
        /*/ Ajout de Marker
                var depart = L.marker([latdep,lngdep], {
                    icon: blackIcon,
                    title: "Depart"
                }).addTo(map);
        depart.bindPopup("<b>Depart</b><br> Latitude : " + latdep + '<br>Longitude : ' +lngdep).openPopup();
        */

    //marqueur echelle ne fonctionne pas    
        L.marker([45, -0.09], {icon: greenIcon}).addTo(map);
        L.control.scale({
        metric:true,
        imperial:false,
        position:'topleft'
        }).addTo(map) 

         
    // points au differents points de passage
    
    for ( var i=0 ; i<polylineblue.length ; i++ )
       { var circle = L.circle(polylineblue[i], {
                color: 'black',
                fillColor: '#f03',
                opacity:0.9,
                fillOpacity: 0.3,
                radius: 200,
            }).bindTooltip(tooltip[i]).addTo(map);
       }    
 



     
    //L.marker([49.16, -4.54], {icon: redIcon}).addTo(map);
    //L.marker([latdep,lngdep]).addTo(map)

    

    // function onMapClick(e){
    //     popup
    //     .setLatLng(e.latlng)
    //     .setContent("Les coordonnées du point sont :<br> " +e.latlng.toString())
    //     .openOn(map);
    
    // //alert("You clicked the map at " + e.latlng);
    //     }

    //     map.on('click',onMapClick)

    
    map.on('mousemove', function(e)
    
    {
        meteo=vit_angle_vent (e.latlng.lat,e.latlng.lng ,tsimul)
        direction=dist_cap_ortho(latdep,lngdep,e.latlng.lat,e.latlng.lng)
        twac=ftwao(direction[0],meteo[1])
       // console.log('Test direction ' + direction[1]) 
//console.log(e.latlng);
// document.getElementById('latlngid').style.color='blue'
// document.getElementById('latlngid').value=e.latlng.lat
document.formu.latm.value=e.latlng.lat.toFixed(4)+' soit  '+pos_dec_mn(e.latlng.lat)
document.formu.lngm.value=e.latlng.lng.toFixed(4)+' soit  '+pos_dec_mn(e.latlng.lng)
document.formu.twsm.value=meteo[0].toFixed(2)
document.formu.twdm.value=meteo[1].toFixed(2)
document.formu.capm.value=direction[1].toFixed(1)
document.formu.twam.value=twac.toFixed(1)
document.formu.dism.value=direction[0].toFixed(1)

// document.getElementById("latlng'").innerhtml="<h2>Toto</h2>"
    });


   




//initialisation des figures


    var popup = L.popup({ offset: L.point(0, 0) });
    var poly
    var circle=new Array();
    var circle1=new Array();
    poly= new L.Polyline ([[0,0],[1,1]]).setStyle({color:'red',weight:1,});
    poly2= new L.Polyline ([[0,0],[1,1]]).setStyle({color:'red',weight:1,});
    for ( var i=0 ; i<74 ; i++ )
       {      circle[i] = new L.circle([1][1], {
                color: 'yellow',
                fillColor: '#f03',
                opacity:0.9,
                fillOpacity: 0.3,
                radius: 200,
            });
       }

       for ( var i=0 ; i<74 ; i++ )
       {      circle1[i] = new L.circle([1][1], {
                color: 'yellow',
                fillColor: '#f03',
                opacity:0.9,
                fillOpacity: 0.3,
                radius: 200,
            });
       }


    map.on('click', function(e)
    {
        latclick=e.latlng.lat
        lngclick=e.latlng.lng
        cap_dist  =crsdist( latdep ,lngdep,latclick, lngclick);
        cap_dist2=dist_cap_ortho( latdep ,lngdep,latclick, lngclick)
        latf= latclick
        lngf=lngclick   

        polytwa=polyline_twa(latdep,lngdep,latf,lngf,tsimul)
        polycap=polyline_cap(latdep,lngdep,latf,lngf,tsimul)
        
        popup
        .setLatLng(e.latlng)
        //.setContent("Latitude  &nbsp; &nbsp;   : " +e.latlng.lat.toFixed(4) +" ("+ pos_dec_mn(e.latlng.lat) + ") <br> Longitude : " +arrondi(e.latlng.lng,4) +" ("+ pos_dec_mn(e.latlng.lng) + ")<br> " +cap_dist +'<br> TWA :'+(polytwa[1]).toFixed(1))
        .setContent("<b><font color='red'> Cap : " +cap_dist2[1].toFixed(1) +"</font><br><font color='green' > TWA : "+(polytwa[1]).toFixed(1))
        .openOn(map);
        
        document.formu.latc.value=latclick.toFixed(4) + ' soit '+  pos_dec_mn(e.latlng.lat);
        document.formu.lngc.value =lngclick.toFixed(4)+ ' soit '+  pos_dec_mn(e.latlng.lng);
        document.formu.capc.value =cap_dist2[1].toFixed(2)
        document.formu.twac.value =polytwa[1].toFixed(1)
        document.formu.disc.value =cap_dist2[0].toFixed(2)
       


        console.log(dist_cap_ortho( latdep ,lngdep,latclick, lngclick))
      //  document.formu.cap.value =cap(lngclick,latclick,lngdep,latdep);
       // document.formu.test3.value =crsdist( latdep ,lngdep,latclick, lngclick);
     
        map.removeLayer(poly);
        map.removeLayer(poly2);
        for ( var j=0 ; j<74 ; j++ )
       {map.removeLayer(circle[j]);
        map.removeLayer(circle1[j]);
       }
       
       //ligne droite
        // ligne=[[latdep,lngdep],[latclick,lngclick]]
        // poly=new L.polyline(ligne).setStyle({
        //     color: 'red',
        //     weight:2,
        //     opacity:0.5,
        //     }).addTo(map);



        // Nouvelle fonction     
       
            
        for ( var i=0 ; i<polytwa[0].length ; i++ )
       {      circle[i] = L.circle(polytwa[0][i], {
                color: 'lime',
                fillColor: '#f03',
                opacity:0.9,
                fillOpacity: 0.3,
                radius: 200,
            }).addTo(map);
       }   

       poly3= new L.polyline(polycap[0])



       for ( var i=0 ; i<polycap[0].length ; i++ )
       {      circle1[i] = L.circle(polycap[0][i], {
                color: 'red',
                fillColor: '#f03',
                opacity:0.9,
                fillOpacity: 0.3,
                radius: 200,
            }).addTo(map);
       }   




       // var ligne2= trace_polyline(latdep,lngdep,latclick,lngclick,tsimul) 

       // console.log('xxxxxxxxxxxxxxxxxxxxxxxxx  Ligne2 :   '+ ligne2)  
        poly2= new L.polyline(polytwa[0])
        .setStyle
            ({
            color: 'lime',
            weight:2,
            opacity:0.5,
            }).addTo(map);







   
    });

    // broadcast.once('redrawFinished', () => {
    //         //picker.open({ lat: 48.4, lon: 14.3 });
    //         // Opening of a picker (async)
    //         console.log('XXXXXXXXXXXXXXXXXXXXXXAAAAAAAAAA    '+store.get('timestamp'))  
    //     });

    // broadcast.on('redrawFinished', params => {
    // // Wow Windy has finished rendering.

    //         console.log ("Test ecart en h")
    //         console.log (' Ecart en h ' +(store.get('timestamp')-Date.now())/3600/1000)
    //         console.log (' Ecart en mn ' +(store.get('timestamp')-Date.now())/60/1000)
    //         console.log (' Ecart en s ' +(store.get('timestamp')-Date.now())/1000)
    //         var sec=((store.get('timestamp')-Date.now())/1000);
    //         console.log(' ecart en secondes '+sec+' numero point'+ numero_point(sec))

    //         var circle = L.circle(polylineblue[ numero_point(sec)  ], {
    //             color: 'white',
    //             fillColor: '#f03',
    //             opacity:0.9,
    //             fillOpacity: 0.3,
    //             radius: 200,
    //         }).addTo(map);

    //      })


}); //fin de windyinit


    // function onMapClick(e){
    //         popup
    //         .setLatLng(e.latlng)
    //         .setContent("Les coordonnées du point sont :<br> " +e.latlng.toString())
    //         .openOn(map);
        
    //     //alert("You clicked the map at " + e.latlng);
    //         }

    //     map.on('click',onMapClick)
        </script>

<script>
	$( function() {
	  var spinner = $( "#twaspin" ).spinner();
	  spinner.spinner( "value", 45 );
    } );
</script>      






       
        <style>
            #windy {  width: 100%; height: 90%;            }
            #sur { z-index: 1;  margin: 0px;   background: white;  opacity=0.1;}
            #main {
                    margin-top: 25px;
                    text-align: center;
                    font-size: 10px;
                }

        </style>
    </head>
  
    

 
    <body onload="initialize()">
        <div text-align='right' id='sur' >
            <!-- <div id= "latlngid" > Latlng </div> -->
             
            <form action="http://localhost:8080/windleaf" method="get" name='formu'>

               <label><b>Depart</b></label> Latitude :</label>
                            <input type="text" name="latdep"  value = "" />
                <label>Longitude :</label>
                            <input type="text" name="lngdep"  value="" />
                          
                <label><b>Arrivee</b></label> Latitude</label> : 
                            <input type="text" name="latar" />
                <label>Longitude</label> : 
                            <input type="text" name="lngar" />             
                            <input type="submit" value="Ok" /><br>

                   Curseur      Latitude  : <input type="text" name="latm" />
                                Longitude : <input type="text" name="lngm" />
                                HDG : <input type="text" name="capm" size="8"/>
                                TWA : <input type="text" name="twam" size="8"/>
                                TWS : <input type="text" name="twsm" size='8'/>
                                TWD : <input type="text" name="twdm" size='8'/>                                
                                Dist: <input type="text" name="dism" size="8"/><br>         

                    Click       Latitude            : <input type="text" name="latc" /> 
                                Longitude   : <input type="text" name="lngc" />
                            <b><span style ="color:red" > HDG     </span>    : <input type="text" name="capc" size="8"/>
                                <span style ="color:green" > TWA         : <input type="text" name="twac" size='8'/>                                
                                Dist        : <input type="text" name="disc" size="8"/>
                                <p>
						<label for="spinner">TWA:</label>
						<input id="twaspin" name="value">
					  </p>

                                
                  <!-- Test :<input type="text" name="test3" /> -->
                  <!-- GFS :<input type="text" name="gfs" /> -->
                </form>
                  
            
        </div>

        <div id="windy">
        </div>


        
    </body>
</html>