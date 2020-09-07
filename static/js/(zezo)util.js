function gc_destination (lon1, lat1, brng, dist) 
{
	var  lon2, lat2;
	dist /= 3437.74;
		
	lat2 = Math.asin(Math.sin(lat1)*Math.cos(dist) + Math.cos(lat1)*Math.sin(dist)*Math.cos(brng));
	lon2 = lon1 + Math.atan2(Math.sin(brng)*Math.sin(dist)*Math.cos(lat1), Math.cos(dist)-Math.sin(lat1)*Math.sin(lat2));
	lon2 = (lon2+Math.PI)%(2*Math.PI) - Math.PI;
	return [lon2, lat2];
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

function crsdist(lat1, lon1, lat2, lon2) {
		var a = crsdist_num(lat1, lon1, lat2, lon2);
		
        var dist = Math.round(a[1] * 34377.4)/10;
        if (dist.toString().indexOf('.') < 0) {
                dist += '.0';
        }
        var dir = Math.round(a[0] * (180/Math.PI) * 10)/10;
        if (dir.toString().indexOf('.') < 0) {
                dir += '.0';
        }
        dir = dir.toString();
        dist = dist.toString();
        
        while (dir.length < 5) {
                dir = " " + dir;
        }

        while (dist.length < 6) {
                dist = " " + dist;
        }
        var res = dist + 'nm ' + dir + '&deg;';
        return res;
}

function angle_diff (a1, a2) {
	var a = Math.round(360 + a1 - a2) % 360;
	if (a <= 180) 
		return a;
	else 
		return 360 - a;
}

function cancel_mo(e)
{	
	var tag;
	e = e || window.event;
	var next = e.relatedTarget || e.toElement;
	try {	
			tag = next.tagName;
	} catch(err) {
		tag = null;
	}
	if (!next || !tag || tag === "HTML" || tag === "BODY" || tag === "IFRAME" || tag === "DIV" ||
		!e.target || e.target.className === 'menuitem' ) {
		return true;
	}

	if (e.stopPropagation) {
		e.stopPropagation();
	}
	e.cancelBubble = true;
	return false;
}
	
function cancel_event(e)
{
	e = e || window.event;
	if (!e.target) {
		return false; //IE shit
	}
	if (e.target.tagName == "INPUT") {
		return true;
	}
	if (e.preventDefault) {
			e.preventDefault();
	}
	if (e.stopPropagation) {
		e.stopPropagation();
	}
	e.cancelBubble = true;
	return false;
}

function addDocListener(eventName, fn)
{
	if (document.addEventListener) {
		document.addEventListener(eventName, fn, false);
	} else if (document.attachEvent) {
		document.attachEvent("on" + eventName, fn);
	}
}

function removeDocListener(eventName, fn)
{
	if (document.removeEventListener) {
		document.removeEventListener(eventName, fn, false);
	} else if (document.detachEvent) {
		document.detachEvent("on" + eventName, fn);
	}
}

function addListener(obj, eventName, fn)
{
	if (obj.addEventListener) {
		obj.addEventListener(eventName, fn, false);
	} else if (obj.attachEvent) {
		obj.attachEvent("on" + eventName, fn);
	}
}

function removeListener(obj, eventName, fn)
{
	if (obj.removeEventListener) {
		obj.removeEventListener(eventName, fn, false);
	} else if (obj.detachEvent) {
		obj.detachEvent("on" + eventName, fn);
	}
}

