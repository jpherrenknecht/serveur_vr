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

function cercle0(ctx,x,y,r,a1,a2,color,thickness)
    {
        eval(ctx+'.beginPath()');
        eval(ctx+'.strokeStyle=color');
        eval(ctx+'.lineWidth=thickness');
        eval(ctx+'.arc(x,y,r,a1,a2)')
        eval(ctx+'.stroke()')
    }




function trace()    // trace le canevas sur ctx1
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


    myCanvas2.addEventListener("mousemove", function depl(evt)
    {        
    if ( isdrawing==true)
        {
            angleini=0
            x=(evt.offsetX)-10
            y =(evt.offsetY)-200
            angle=Math.round(Math.atan(y/x)*180/Math.PI +90) ;
            longueur=185/Math.sqrt(x*x+y*y)
            if (angleini != angle) 
                {ctx2.clearRect(-10,-200, 400, 400); // vider le canevas
                line0('ctx2',0,0,x*longueur,y*longueur,'blue',1);
                cercle2(x*longueur,y*longueur,4,-3.14,3.14,'blue',1)   // petite boule
                write2(angle+'°','red','12px Calibri','start',x*longueur+15,y*longueur)
                angleini=angle;
               // ecrire2 ('TWA : '+angle)
                document.getElementById('twa1').innerHTML=angle
                tws=document.getElementById('tws').value
                res=polinterpol2d(polaires,angle,tws)
                document.getElementById('speed1').innerHTML=res.toFixed(2)
                //console.log('resultat'+res)
               // ecrire3 ('Vitesse : '+res.toFixed(2)    )
                }   
        }
    });


function dessiner()
{
    trace()

}