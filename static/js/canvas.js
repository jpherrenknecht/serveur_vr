window.addEventListener('load',function()
{
 

    
   


});
      


function dessinerRectangle()
    {
    ctx1.fillStyle="#cccccc"
    ctx1.fillRect(100,100,300,50)
    }

function line0(ctx,x1,y1,x2,y2,color,thickness)
{ 
    eval(ctx+'.beginPath()');
    eval(ctx+'.strokeStyle=color');
    eval(ctx+'.moveTo(x1,y1)');
    eval(ctx+'.lineTo(x2,y2)');
    eval(ctx+'.lineWidth=thickness');
    eval(ctx+'.stroke()');
}    


function lineP(ctx,x1,y1,x2,y2,color,thickness)
{ 
    eval(ctx+'.beginPath()');
    eval(ctx+'.strokeStyle=color');
    eval(ctx+'.moveTo(x1,y1)');
    eval(ctx+'.lineTo(x2,y2)');
    eval(ctx+'.lineWidth=thickness');
    ctx3.setLineDash([15,3]);
    eval(ctx+'.stroke()');

}    



function cercle0(ctx,x,y,r,a1,a2,color,thickness)
    {
        eval(ctx+'.beginPath()');
        eval(ctx+'.strokeStyle=color');
        eval(ctx+'.lineWidth=thickness');
        eval(ctx+'.arc(x,y,r,a1,a2)')
        eval(ctx+'.stroke()')
    }




function tracefond()    // trace le canevas sur ctx1
    {
        var x=10,y=200,r=30,a1=-Math.PI/2 ,a2=Math.PI/2 ,color='green'
        r=[60,90,120,150,180]
        for (var i=0;i<r.length;i++)        // trace des cercles
        cercle0('ctx1',x,y,r[i],a1,a2,'black',1)
        angles=[0,20,40,60,80,100,120,140,160,180]
        longueur=190
        for (var i=0;i<angles.length;i++)   //trace des rayons avec les valeurs
            {    
                x1=10+longueur*Math.sin(angles[i]*Math.PI/180)
                y1=200-longueur*Math.cos(angles[i]*Math.PI/180)
                line0 ('ctx1',10,200,x1,y1,'grey',1)
                write (angles[i]+'°','red','12px Calibri','start',x1,y1)
            }
    }

    function write (texte,style,police,align,x,y)
    {
    //ctx1.save()
    ctx1.fillStyle=style;
    ctx1.font=police;
    ctx1.textAlign=align     // start,end,right,center
    ctx1.fillText(texte,x,y,200)
    ctx1.stroke()
    //ctx1.restore()
    }

    function cercle(x,y,r,a1,a2,color,thickness)
    {
    ctx1.beginPath();
    ctx1.strokeStyle=color;
    ctx1.lineWidth=thickness;
    //ctx1.moveTo(x,y)
    ctx1.arc(x,y,r,a1,a2)
    ctx1.stroke()
    }

    function cercle2(x,y,r,a1,a2,color,thickness)
    {
    ctx2.beginPath();
    ctx2.lineWidth=thickness;
    ctx2.fillStyle=color;
    ctx2.arc(x,y,r,a1,a2)
    ctx2.fill();
    }

    function cercle3(x,y,r,a1,a2,color,thickness)
    {
    ctx3.beginPath();
    ctx3.lineWidth=0;
    ctx3.fillStyle=color;
    ctx3.arc(x,y,r,a1,a2)
    ctx3.fill();
    }

    function triangle(x,y,r,a1,a2,color,thickness)
    {
    x1=x+r*Math.cos(a1)
    y1=y+r*Math.sin(a1)
    x2=x+r*Math.cos(a2)
    y2=y+r*Math.sin(a2)
    ctx3.beginPath();
    ctx3.moveTo(x,y);
    ctx3.lineTo(x1,y1);
    ctx3.lineTo(x2,y2);
    ctx3.lineTo(x,y);
    ctx3.lineWidth=0;
    ctx3.fillStyle=color;
    ctx3.strokeStyle=color
    ctx3.fill();
    ctx3.stroke()
    }





    function write2 (texte,style,police,align,x,y)
    {
    //ctx1.save()
    ctx2.fillStyle=style;
    ctx2.font=police;
    ctx2.textAlign=align     // start,end,right,center
    ctx2.fillText(texte,x,y,200)
    ctx2.stroke()
    //ctx1.restore()
    }

    function write3 (texte,style,police,align,x,y)
    {
    //ctx1.save()
    ctx3.fillStyle=style;
    ctx3.font=police;
    ctx3.textAlign=align     // start,end,right,center
    ctx3.fillText(texte,x,y,200)
    ctx3.stroke()
    //ctx1.restore()
    }

    function tracepol(polaires,tws)  //trace de la courbe
    {
        // On commence par reinitialiser le canvas
        ctx3.clearRect(0,0, 400, 400); // vider le canevas
        xtwai=10
        ytwai=200
                for (var twa=0; twa<=180;twa++)  // trace de la courbe
                 { 
                valeur2= 8*polinterpol2d(polaires,twa,tws)  
                twa2=twa*Math.PI/180    
                xtwa=10+Math.sin(twa2)*valeur2 
                ytwa=200-Math.cos(twa2)*valeur2
                line0('ctx3',xtwai,ytwai,xtwa,ytwa,'red',2)
                xtwai=xtwa;
                ytwai=ytwa
                 }

    }

    function cherchevmg(polaires,tws)
    {
        // On commence par reinitialiser le canvas
                vmgmax=0;vmvamax=0 ;speedmax=0;twamax=45;twamax2=145;twaopti=0;
                // on cherche la twa au pres entre 30 et 60 
                for (var twa=300; twa<=600;twa++)  
                 { 
                vmg=polinterpol2d(polaires,twa/10,tws)*Math.cos(twa/10*Math.PI/180)
                if (vmg>vmgmax){vmgmax=vmg;twamax=twa/10}
                //if (-vmg>vmvamax){vmvamax=vmg;twaarmax=twa/10}
                 }
                 for (var twa=80; twa<=140;twa++)  // recherche vitesse max 
                 { 
                speed=polinterpol2d(polaires,twa,tws)
                if (speed>speedmax){speedmax=speed;twaopti=twa}
                 }
                 for (var twa=1400; twa<=1700;twa++)  // recherche sur vent arriere 
                 { 
                vmg=polinterpol2d(polaires,twa/10,tws)*Math.cos(twa/10*Math.PI/180)
                if (vmg<vmvamax){vmvamax=vmg;twamax2=twa/10}
                 }

                 document.getElementById('twamax').innerHTML=twamax.toFixed(1)+'°  '
                 document.getElementById('vmgmax').innerHTML=vmgmax.toFixed(2)+'knts'
                 document.getElementById('vmvamax').innerHTML=vmvamax.toFixed(2)+'knts'
                 document.getElementById('twamax2').innerHTML=twamax2.toFixed(1)+'°  '
                 document.getElementById('speedmax').innerHTML=speedmax.toFixed(2)+'knts'
                 document.getElementById('twaopti').innerHTML=twaopti.toFixed(1)+'°  '

               var a1=twamax*Math.PI/180-Math.PI/2
               var a2=0-Math.PI/2
               thickness=0
               color='rgba(200, 200, 255, 0.5)'
               cercle3(10,200,180,a2,a1,color,thickness)
               triangle(10,200,180,a1,a2,color,thickness)               
               x5=10+190*Math.cos(a1)
               y5=200+190*Math.sin(a1) 
               line0 ('ctx3',10,200,x5,y5,'black',1)
               write3 (twamax+'°','black','12px Calibri','start',x5,y5)
               a3=(twamax2-90)*Math.PI/180
               a4=Math.PI/2
               x6=10+190*Math.cos(a3)
               y6=200+190*Math.sin(a3) 
               cercle3(10,200,180,a3,a4,color,thickness)
               triangle(10,200,180,a3,a4,color,thickness)
               line0 ('ctx3',10,200,x6,y6,'black',1)
               //line3 (10,200,x6,y6,'black')
               write3 (twamax2+'°','black','12px Calibri','start',x6,y6)
                // trace de speedmax avec speedmax et twaopti
               aopti= twaopti*Math.PI/180-Math.PI/2
               x7=10+190*Math.cos(aopti)
               y7=200+190*Math.sin(aopti) 
               lineP ('ctx3',10,200,x7,y7,'green',1)
               write3 (twaopti.toFixed(0)+'°','green','12px Calibri','start',x7,y7)

    }

// on dessine la barre avec les valeurs initiales    
 
function traceinitial(twaini){
    ctx2.clearRect(0,-200, 400, 400); // vider le canevas
    angle=twaini*Math.PI/180 ;
    longueur=185
    x1=longueur*Math.sin(angle)
    y1=-longueur*Math.cos(angle)
    line0('ctx2',0,0,x1,y1,'blue',1);
    cercle2(x1,y1,4,-3.14,3.14,'blue',1) 
    write2(twaini.toFixed(1)+'°','green','12px Calibri','start',x1+15,y1)
    
    
    //tracepol(polairesjs,twso)
    //cherchevmg(polairesjs,tws)
}


function petitplus(){
    var valeur=document.getElementById('tws').value;
    tws2=+valeur+0.1
    document.getElementById('tws').value=+tws2
    angle=document.getElementById('twapol').innerHTML
    res=polinterpol2d(polairesjs,angle,tws2)
    document.getElementById('speed1').innerHTML=res.toFixed(3)
    vmg=res*Math.cos(angle*Math.PI/180)
    document.getElementById('speedvmg').innerHTML=vmg.toFixed(3)
    tracepol(polairesjs,tws2)
    cherchevmg(polairesjs,tws2)

}

function petitmoins(){
    var valeur=document.getElementById('tws').value;
    tws2=+valeur-0.1
     document.getElementById('tws').value=+tws2
    document.getElementById('tws').value=+tws2
    angle=document.getElementById('twapol').innerHTML
    res=polinterpol2d(polairesjs,angle,tws2)
    document.getElementById('speed1').innerHTML=res.toFixed(3)
    vmg=res*Math.cos(angle*Math.PI/180)
    document.getElementById('speedvmg').innerHTML=vmg.toFixed(3)
    tracepol(polairesjs,tws2)
    cherchevmg(polairesjs,tws2)
}

function plus(){
    var valeur=document.getElementById('tws').value;
    tws2=+valeur+1
    document.getElementById('tws').value=+tws2
    angle=document.getElementById('twapol').innerHTML
    res=polinterpol2d(polairesjs,angle,tws2)
    document.getElementById('speed1').innerHTML=res.toFixed(3)
    vmg=res*Math.cos(angle*Math.PI/180)
    document.getElementById('speedvmg').innerHTML=vmg.toFixed(3)
    tracepol(polairesjs,tws2)
    cherchevmg(polairesjs,tws2)
}

function moins(){
    var valeur=document.getElementById('tws').value;
    tws2=+valeur-1
    document.getElementById('tws').value=+tws2
    angle=document.getElementById('twapol').innerHTML
    res=polinterpol2d(polairesjs,angle,tws2)
    document.getElementById('speed1').innerHTML=res.toFixed(3)
    vmg=res*Math.cos(angle*Math.PI/180)
    document.getElementById('speedvmg').innerHTML=vmg.toFixed(3)
    tracepol(polairesjs,tws2)
    cherchevmg(polairesjs,tws2)
}

function twaplus(){
    var angle=document.getElementById('twapol').innerHTML;   
    var tws2=document.getElementById('tws').value;
    twa2=+angle+1
    cos=Math.cos(twa2*Math.PI/180)
    res=polinterpol2d(polairesjs,twa2,tws2)
    document.getElementById('twapol').innerHTML=twa2
    document.getElementById('speed1').innerHTML=res.toFixed(3)
    document.getElementById('speedvmg').innerHTML=(res*cos).toFixed(3)
    traceinitial(twa2)
}



function twamoins(){
    var angle=document.getElementById('twapol').innerHTML;   
    var tws2=document.getElementById('tws').value;
    twa2=+angle-1
    cos=Math.cos(twa2*Math.PI/180)
    res=polinterpol2d(polairesjs,twa2,tws2)
    document.getElementById('twapol').innerHTML=twa2
    document.getElementById('speed1').innerHTML=res.toFixed(3)
    document.getElementById('speedvmg').innerHTML=(res*cos).toFixed(3)
    traceinitial(twa2)
}





function dessiner()
{
    document.getElementById('bateau').innerHTML=bateau
    tracefond()
    tracepol(polairesjs,twsvr)
    cherchevmg(polairesjs,twsvr)
    traceinitial(twavr)
}

