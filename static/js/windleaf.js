
var intl=new Intl.DateTimeFormat("fr-EU",{month:"2-digit",day:"2-digit", year:"2-digit",hour12: false,hour:"2-digit", minute:"2-digit" });
var intlhmn=new Intl.DateTimeFormat("fr-FR",{day:"2-digit",month:"2-digit", hour12: false,hour:"2-digit", minute:"2-digit" });
            function arrondi(a,n)
            {return(Math.round(a*10**n)/10**n);}


            function h_mn(sec)
			{   sec=sec
				h=Math.floor(sec/3600)	
				mn=Math.ceil((sec-3600*h)/60)
				s=sec-3600*h-60*mn 
				res=h+'h '+mn+'mn'
				return res
			}

			function h_mn2(sec)
			{   sec=sec
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
                return npt+1;
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

            function polinterpol2d(bateau,twa,tws)
			{	// parametres : polaires du bateau twa et tws
			    var i_sup=l2.findIndex(element => element > twa);
				var j_sup=l1.findIndex(element => element > tws);				
				var twa_inf=l2[i_sup-1]
				var twa_sup=l2[i_sup]
				var tws_inf=l1[j_sup-1]
				var tws_sup=l1[j_sup]
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
                //console.log( 'lat0 '+ lat0 +' Lng0 '+lng0 +' t0 ' + t0)  
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
				console.log ('Valeurs dans interpolation 3d lat0 '+lat0+' lng0 '+lng0+' dec_t '+dec_t+' dec_lat '+dec_lat+' dec_lng '+dec_lng)
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
				//console.log('isup : '+ i_sup)
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


			function vit_angle_vent (lat,lng ,t1000)
			{
			itemp=(t1000-tig)/3600/3     // Ecart en heures avec le tig  modulo 3h
		    ilati=-(lat-latini)       // ecart avec la latitude du grib chargé
			ilong=(360+lng-lngini)%360
			// console.log(' ')
			// console.log ('Indices : '+itemp+' '+ilati+' '+ilong)		
			
			iitemp    = Math.floor(itemp)       // partie entiere
			iilati    = Math.floor(ilati)
			iilong    = Math.floor(ilong)
			ditemp    = itemp%1						// partie decimale				
			dilati    = ilati%1
			dilong    = ilong%1
			
			u000=U10[iitemp][iilati][iilong]
    		u010=U10[iitemp][iilati+1][iilong]
    		u001=U10[iitemp][iilati][iilong+1]
			u011=U10[iitemp][iilati+1][iilong+1]
			
			v000=V10[iitemp][iilati][iilong]
    		v010=V10[iitemp][iilati+1][iilong]
    		v001=V10[iitemp][iilati][iilong+1]
    		v011=V10[iitemp][iilati+1][iilong+1]
			// console.log ( 'valeurs u000 ... '+u000+' '+u010+ ' '+u001+ ' '+u011)
			// console.log ( 'valeurs v000 ... '+v000+' '+v010+ ' '+v001+ ' '+v011)
			
			u0x0=u000+dilati*(u010-u000)
    		u0x1=u001+dilati*(u011-u001)
			u0xx=u0x0+dilong*(u0x1-u0x0)

			v0x0=v000+dilati*(v010-v000)
    		v0x1=v001+dilati*(v011-v001)
			v0xx=v0x0+dilong*(v0x1-v0x0)

			// console.log ( 'valeurs u0x0 ... '+u0x0+' '+u0x1+ ' '+u0xx)
			// console.log ( 'valeurs v0x0 ... '+v0x0+' '+v0x1+ ' '+v0xx)

			u100=U10[iitemp+1][iilati][iilong]
    		u110=U10[iitemp+1][iilati+1][iilong]
    		u101=U10[iitemp+1][iilati][iilong+1]
    		u111=U10[iitemp+1][iilati+1][iilong+1]

			v100=V10[iitemp+1][iilati][iilong]
    		v110=V10[iitemp+1][iilati+1][iilong]
    		v101=V10[iitemp+1][iilati][iilong+1]
    		v111=V10[iitemp+1][iilati+1][iilong+1]

			u1x0=u100+dilati*(u110-u100)
    		u1x1=u101+dilati*(u111-u101)
    		u1xx=u1x0+dilong*(u1x1-u1x0)
			uxxx=u0xx+ditemp*(u1xx-u0xx) 
			  
			v1x0=v100+dilati*(v110-v100)
    		v1x1=v101+dilati*(v111-v101)
    		v1xx=v1x0+dilong*(v1x1-v1x0)
    		vxxx=v0xx+ditemp*(v1xx-v0xx)  
		
			vit = Math.sqrt(uxxx*uxxx + vxxx*vxxx)
			angle= Math.acos(vxxx/vit)*180/Math.PI+180;
			if (uxxx<0)
			{angle=360-angle}
			vit*= 1.94384     // Vitesse en noeuds
			//console.log('vitesse : '+vit+' angle : '+angle)	

			res=[vit,angle]
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

            // function polyline_twa(latdep,lngdep,latf,lngf,tsimul)
			// {  
			// 	//console.log ('latdep dans polyline twa :' +latdep+ ' lngdep : ' +lngdep +' latf : ' +latf +' lngf : '+lngf +' tsimul : '+tsimul)
			// 	//Cap généré par le curseur recherche du vent et twa en consequence 
			// 	hdg_ini=dist_cap_ortho(latdep,lngdep,latf,lngf,)[1]
            //     //console.log( 'cap initial :' + hdg_ini)
			// 	vent_ini=vit_angle_vent (latdep,lngdep,tsimul)
			// 	tws_ini=vent_ini[0]
			// 	twd_ini=vent_ini[1]				
			// 	twa_ini=ftwao(hdg_ini,twd_ini)
			// 	polyline= [[latdep,lngdep]]  //initialisation de la polyline
			// 	dt=600   //intervalle entre deux points =10 mn

			// 	lat6 = latdep
			// 	lng6= lngdep
				
            //     twa=twa_ini    // la twa est celle donnée initialement par le curseur
			// 	capa=hdg_ini
			// 	t=tsimul
			// 	for (var i=0;i<=72;i++)
			// 	{tsimul = t+i*dt
			// 	meteo=vit_angle_vent (lat6,lng6,tsimul)
			// 	vit_polaire=polinterpol2d(polairesjs,twa_ini,meteo[0])	
            //     capa=twa_ini+meteo[1]
			// 	point=deplacement(lat6,lng6,dt,vit_polaire,capa)     //calcul du nouveau point 
			// 	lat6=point[0];lng6=point[1];
			// 	polyline.push(point)	
			// 	}
			// 	//console.log (' polyline '+polyline)
			// return [polyline,twa_ini]  
			// }


			// function polyline_twa2(latdep,lngdep,latf,lngf,tsimul,twaini)
			// {  
			// 	//console.log ('latdep dans polyline twa :' +latdep+ ' lngdep : ' +lngdep +' latf : ' +latf +' lngf : '+lngf +' tsimul : '+tsimul)
			// 	//Cap généré par le curseur recherche du vent et twa en consequence 
			// 	hdg_ini=dist_cap_ortho(latdep,lngdep,latf,lngf,)[1]
            //     //console.log( 'cap initial :' + hdg_ini)
			// 	meteo=vit_angle_vent (latdep,lngdep,tsimul)
			// 	tws_ini=meteo[0]
			// 	console.log ('meteo : vitesse et direction '+meteo)
			// 	twd_ini=meteo[1]				
			// 	//twa_ini=ftwao(hdg_ini,twd_ini)
			// 	polyline= [[latdep,lngdep]]  //initialisation de la polyline
			// 	dt=600   //intervalle entre deux points =10 mn

			// 	lat6 = latdep
			// 	lng6= lngdep
				
			// 	twa=+twaini    // la twa initiale est celle donnée initialement par le curseur
			// 	capa=(twaini+meteo[1])%360	//le cap initial est deduit de la twa par la twaini et la direction du vent 

			// 	console.log ('CAP a '+capa)
			// 	t=tsimul
			// 	for (var i=0;i<=72;i++)
			// 	{tsimul2 = t+i*dt
			// 	meteo=vit_angle_vent (lat6,lng6,tsimul2)
			// 	vit_polaire=polinterpol2d(polairesjs,twaini,meteo[0])	
            //     capa=twaini+meteo[1]
			// 	point=deplacement(lat6,lng6,dt,vit_polaire,capa)     //calcul du nouveau point 
			// 	lat6=point[0];lng6=point[1];
			// 	polyline.push(point)	
			// 	}
			// 	//console.log (' polyline '+polyline)
			// return [polyline,twaini]  
			// }



            // function polyline_cap(latdep,lngdep,latf,lngf,tsimul)
			// {  
			// 	console.log (' polyline latdep  :' +latdep+ ' lngdep : ' +lngdep +' latf : ' +latf +' lngf : '+lngf +' tsimul : '+tsimul)
			// 	//Cap généré par le curseur recherche du vent et twa en consequence 
			// 	hdg_ini=dist_cap_ortho(latdep,lngdep,latf,lngf,)[1]

            //     // console.log( 'cap initial :' + hdg_ini)
			// 	vent_ini=vit_angle_vent (latdep,lngdep,tsimul)
			// 	tws_ini=vent_ini[0]
			// 	twd_ini=vent_ini[1]				
			// 	twa_ini=ftwao(hdg_ini,twd_ini)
			// 	polyline2= [[latdep,lngdep]]  //initialisation de la polyline
			// 	dt=600   //intervalle entre deux points =10 mn
			// 	lat7 = latdep
			// 	lng7= lngdep
			// 	twa=twa_ini    // la twa est celle donnée initialement par le curseur
			// 	capi=hdg_ini

			// 	 t=tsimul
			// 	 for (var i=0;i<=72;i++)
            //         {tsimul = t+i*dt
            //          meteo=vit_angle_vent (lat7,lng7,tsimul)
            //          twa=ftwa(hdg_ini,meteo[1])
            //         //  console.log ('hdg_ini ' + hdg_ini + ' meteo 1 '+meteo[1] )
            //         //  console.log( 'test dans polyline_cap   twa : '+ twa + 'cap : ' +capi+' dirvent :'+meteo[1] + 'vit_vent :' + meteo[0]) 

            //          vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])	                
            //         // console.log('cap dans polylinecap'+capi )
            //         point=deplacement(lat7,lng7,dt,vit_polaire,capi)     //calcul du nouveau point 
            //         lat7=point[0];lng7=point[1];
            //         polyline2.push(point)	
            //         }
			// //	console.log (' polyline '+polyline2)
			// return [polyline2,capi]  
			// }


			function polyline_cap2(latdep,lngdep,cap,tsimul)
			{  
				//console.log ('Donnees de  polyline cap  latdep :' +latdep+ ' lngdep : ' +lngdep +' cap: ' +cap +' tsimul : '+tsimul)
				//Cap généré par le curseur recherche du vent et twa en consequence 
				hdg_ini=cap    // console.log( 'cap initial :' + hdg_ini)
				meteo_ini=vit_angle_vent (latdep,lngdep,tsimul)
	//			console.log ('394 meteo_ini'+ meteo_ini)
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
                    {tsimul2 = t+i*dt
					 meteo=vit_angle_vent (lat7,lng7,tsimul2)
					//console.log( 'hdg_ini'+ hdg_ini+' angle vent'+meteo[1]) 
                     twa=ftwa(hdg_ini,meteo[1])
                    //  console.log ('hdg_ini ' + hdg_ini + ' meteo 1 '+meteo[1] )
                    //  console.log( 'test dans polyline_cap   twa : '+ twa + 'cap : ' +capi+' dirvent :'+meteo[1] + 'vit_vent :' + meteo[0]) 
					//console.log('twa : '+twa+' vit vent '+meteo[0])	
                    vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])	                
                    // console.log('cap dans polylinecap'+capi )
                    point=deplacement(lat7,lng7,dt,vit_polaire,capi)     //calcul du nouveau point 
                    lat7=point[0];lng7=point[1];
                    polyline2.push(point)	
                    }
			//	console.log (' polyline '+polyline2)
			return [polyline2,capi]  
			}


			function polyline_twa3(latdep,lngdep,twa_ini,tsimul)
			{   // ici la twa est une twa orientée

				//console.log ('latdep dans polyline twa :' +latdep+ ' lngdep : ' +lngdep +' latf : ' +latf +' lngf : '+lngf +' tsimul : '+tsimul)
				//Cap généré par le curseur recherche du vent et twa en consequence 
				//hdg_ini=dist_cap_ortho(latdep,lngdep,latf,lngf,)[1]
                //console.log( 'cap initial :' + hdg_ini)
				meteo=vit_angle_vent (latdep,lngdep,tsimul)

				//console.log (' (js l 432 )meteo '+meteo)
				//console.log('polaires pour test dans polylinetwa3'+polairesjs) 
				tws_ini=meteo[0]
				twd_ini=meteo[1]
				polyline= [[latdep,lngdep]]  //initialisation de la polyline
				dt=600   //intervalle entre deux points =10 mn
				lat6 = latdep
				lng6= lngdep
   				twa=+twa_ini    // la twa est celle donnée initialement 
				capa=(twd_ini+twa_ini)%360
				t=tsimul
				for (var i=0;i<=72;i++)
				{tsimul3 = t+i*dt
				meteo=vit_angle_vent (lat6,lng6,tsimul3)				
				vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])	
				//console.log('test de polaires twa'+twa+'Vitesse vent'+ meteo[0] +'vitesse polaire'+vit_polaire)	
				capa=(+360+twa+meteo[1])%360
				//console.log ('twa, twd,capa'+twa+' '+ meteo[0]+' '+capa)
				point=deplacement(lat6,lng6,dt,vit_polaire,capa)     //calcul du nouveau point 
				//console.log('lat6,lng6,dt,twa,tws,vit_polaire,capa, point : '+lat6+' '+lng6+' '+dt+' '+twa+' '+meteo[0]+' '+vit_polaire+' '+capa+' '+ point) 
				lat6=point[0];lng6=point[1];
				polyline.push(point)	
				}
				//console.log (' polyline dans wondleaf js '+polyline)
			return [polyline,twa_ini]  
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

		function testPolyline(tsimul)
		{   console.log ('(js ligne 526)'+tsimul )
			twasimul1=+document.getElementById('twasimul1').value
			twasimul2=+document.getElementById('twasimul2').value
			twasimul3=+document.getElementById('twasimul3').value
			twasimul4=+document.getElementById('twasimul4').value
			
			capsimul1=+document.getElementById('capsimul1').value
			capsimul2=+document.getElementById('capsimul2').value
			capsimul3=+document.getElementById('capsimul3').value
			capsimul4=+document.getElementById('capsimul4').value
			
			tsimulation1=+document.getElementById('tsimul1').value
			tsimulation2=+document.getElementById('tsimul2').value
			tsimulation3=+document.getElementById('tsimul3').value
			tsimulation4=+document.getElementById('tsimul4').value

			console.log ('*************************************************************')
			console.log ('********************* SIMULATION ****************************')
			console.log ('*************************************************************')



			
			if(	document.getElementById('twa1').checked)
			{choix1='twa';valeur1= twasimul1}
			else if(	document.getElementById('cap1').checked)
			{choix1='cap';valeur1= capsimul1}
			else {choix1='rien';valeur1=0}

			if(	document.getElementById('twa2').checked)
			{choix2='twa';valeur2= twasimul2}
			else if(	document.getElementById('cap2').checked)
			{choix2='cap';valeur2= capsimul2}
			else {choix2='rien';valeur2=0}

			if(	document.getElementById('twa3').checked)
			{choix3='twa';valeur3= twasimul3}
			else if(	document.getElementById('cap3').checked)
			{choix3='cap';valeur3= capsimul3}
			else {choix3='rien';valeur3=0}

			if(	document.getElementById('twa4').checked)
			{choix4='twa';valeur4= twasimul4}
			else if(	document.getElementById('cap4').checked)
			{choix4='cap';valeur4= capsimul4}
			else {choix4='rien';valeur4=0}
			

			//calcul des points 
			polyline= [[latdep,lngdep]]  //initialisation de la polyline
			
			t100 =tsimul

			

			// conditions au depart
			meteo=vit_angle_vent (latdep,lngdep,tsimul)
			tws_ini=meteo[0]
			twd_ini=meteo[1]
			lat8=+latdep
			lng8=+lngdep
			dt=600   //intervalle entre deux points 10mn
			
			t1=tsimulation1/10 // recalcul toutes les 10mn 
			t2=tsimulation2/10 
			t3=tsimulation3/10 
			t4=tsimulation4/10 
			
			
			// 1er tronçon
			console.log('choix1 '+choix1+' : '+valeur1 )
			for (var i=0;i<(tsimulation1/10);i++)
			{tsimul1 = t100+(i*600)         // intervalles de 600s soit 10mn
				console.log ('tsimul1  '+tsimul1)
				
				if (choix1=='twa')
				{	meteo=vit_angle_vent (lat8,lng8,tsimul1)
					twa =twasimul1
					console.log('twasimul1 : '+twasimul1)
					vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])
					console.log('vit_polaire : '+vit_polaire)
					capa=+twa+meteo[1]
					console.log('capa : '+capa)
					point=deplacement(lat8,lng8,dt,vit_polaire,capa) 
					console.log('nouveau point : '+point) 
					lat8=point[0];lng8=point[1];
					polyline.push(point)	
					}
				if (choix1=='cap')
				{	meteo=vit_angle_vent (lat8,lng8,tsimul1)
					cap1 =capsimul1
					console.log('twasimul1 : '+twasimul1)
					twa=ftwa(cap1,meteo[1])
					vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])
					console.log('vit_polaire : '+vit_polaire)
					console.log('capa : '+capa)
					point=deplacement(lat8,lng8,dt,vit_polaire,cap1) 
					console.log('nouveau point : '+point) 
					lat8=point[0];lng8=point[1];
					polyline.push(point)	
					}
			}

				// 2eme troncon
			console.log('choix2 '+choix2+' : '+valeur2 )
			for (var i=0;i<(tsimulation2/10);i++)
			{tsimul2 = t100+(tsimulation1*60)+i*600
				console.log ('****************************************tsimul2  '+tsimul2)
				console.log ( 'pour test'+lat8 +' '+ lng8+' '+tsimul2)
				if (choix2=='twa')
				{	meteo=vit_angle_vent (lat8,lng8,tsimul2) //lat8 lng8 sont les latitudes issues de la sequence precedente
					twa =twasimul2
					console.log('twasimul2 : '+twasimul2)
					vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])
					console.log('vit_polaire : '+vit_polaire)
					capa=+twa+meteo[1]
					console.log('capa : '+capa)
					point=deplacement(lat8,lng8,dt,vit_polaire,capa) 
					console.log('nouveau point : '+point) 
					lat8=point[0];lng8=point[1];
					polyline.push(point)	
					}
				if (choix2=='cap')
				{	meteo=vit_angle_vent (lat8,lng8,tsimul2)
					cap2 =capsimul2
					console.log('capsimul2 : '+capsimul2)
					twa=ftwa(cap2,meteo[1])
					vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])
					console.log('vit_polaire : '+vit_polaire)
					console.log('capa : '+capa)
					point=deplacement(lat8,lng8,dt,vit_polaire,cap2) 
					console.log('nouveau point : '+point) 
					lat8=point[0];lng8=point[1];
					polyline.push(point)	
					}
			}


			// 3eme troncon
			console.log('ZZZZZZZZZZZZZZZZZZ choix3 '+choix3+' : '+valeur3 )
			for (var i=0;i<(tsimulation3/10);i++)
		

			{tsimul3 = t100+(+tsimulation1+tsimulation2)*60+i*600
				// console.log ('XXXXXXXXXXXXXXXXXtsimul3  '+tsimul3)
				// console.log ( 'pour test'+lat8 +' '+ lng8+' '+tsimul3)
				if (choix3=='twa')
				{	meteo=vit_angle_vent (lat8,lng8,tsimul3) //lat8 lng8 sont les latitudes issues de la sequence precedente
					twa =twasimul3
					console.log('twasimul3 : '+twasimul3)
					vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])
					console.log('vit_polaire : '+vit_polaire)
					capa=+twa+meteo[1]
					console.log('capa : '+capa)
					point=deplacement(lat8,lng8,dt,vit_polaire,capa) 
					console.log('nouveau point : '+point) 
					lat8=point[0];lng8=point[1];
					polyline.push(point)	
					}
				if (choix3=='cap')
				{	meteo=vit_angle_vent (lat8,lng8,tsimul3)
					cap3 =capsimul3
					console.log('capsimul3 : '+capsimul3)
					twa=ftwa(cap3,meteo[1])
					vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])
					console.log('vit_polaire : '+vit_polaire)
					console.log('capa : '+capa)
					point=deplacement(lat8,lng8,dt,vit_polaire,cap3) 
					console.log('nouveau point : '+point) 
					lat8=point[0];lng8=point[1];
					polyline.push(point)	
					}
			}


			// 4eme troncon
			console.log('choix3 '+choix4+' : '+valeur4 )

			console.log('tsimulation 1 +2 + 3  : '+(tsimulation1+tsimulation2 +tsimulation3))
			for (var i=0;i<tsimulation4/10;i++)
			{tsimul4 = t100+(+tsimulation1+tsimulation2 +tsimulation3)*60+i*600
				console.log ('********************************tsimul4  '+tsimul4)
				console.log ( 'pour test'+lat8 +' '+ lng8+' '+tsimul4)
				if (choix4=='twa')
				{	meteo=vit_angle_vent (lat8,lng8,tsimul3) //lat8 lng8 sont les latitudes issues de la sequence precedente
					twa =twasimul4
					console.log('twasimul4 : '+twasimul4)
					vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])
					console.log('vit_polaire : '+vit_polaire)
					capa=+twa+meteo[1]
					console.log('capa : '+capa)
					point=deplacement(lat8,lng8,dt,vit_polaire,capa) 
					console.log('nouveau point : '+point) 
					lat8=point[0];lng8=point[1];
					polyline.push(point)	
					}
				if (choix4=='cap')
				{	meteo=vit_angle_vent (lat8,lng8,tsimul4)
					cap4 =capsimul4
					console.log('capsimul4 : '+capsimul4)
					twa=ftwa(cap4,meteo[1])
					vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])
					console.log('vit_polaire : '+vit_polaire)
					console.log('capa : '+capa)
					point=deplacement(lat8,lng8,dt,vit_polaire,cap4) 
					console.log('nouveau point : '+point) 
					lat8=point[0];lng8=point[1];
					polyline.push(point)	
					}
			}










			//var polylinesimul=[[latdep,lngdep],[latdep,lngdep+2],[latdep+1,lngdep+3],[latdep+2,lngdep+4]]
		
			//document.formu.stocksimul.value=polylinesimul
			

			//alert('latdep : '+ latdep + ' choix1 : '+choix1+ ' valeur '+ valeur1+ ' choix2 : '+choix2+ ' valeur '+ valeur2+'  choix3 : '+choix3+ ' valeur '+ valeur3 )
			return polyline
		
		}

		// function testPolyline(){
		// polyline=	[[latdep,lngdep],[latdep,lngdep+2],[latdep+1,lngdep+3],[latdep+2,lngdep+4]]
		// return polyline

		// }
			

		