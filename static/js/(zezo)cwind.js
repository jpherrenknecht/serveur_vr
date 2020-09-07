"use strict";

var polar_data = null;

var w_canvas_c = null;
var wind_style = 2;
var wind_array = [];
	
function lin(x) {
	return Math.round(Math.sqrt(x) * 13);
}

function speed_color(speed) {
	if (speed > 20) {
		speed = 20 + (speed-20)/4;
	} 
	if (speed > 37) {
		speed = 37;
	}
	speed = Math.floor(speed * 7);
	var r,g,b;
	if (speed < 128 ) {
		g = 208;
		if (speed < 64 ) {
			r = 0; b = lin(255 - 4 * speed);
		} else { // > 64
			b = 0; r = lin(4 * (speed - 64));
		} 
	} else { // > 128 
		r = 208;
		if (speed < 192) {
			b = 0; g = lin(255 - 4 * (speed - 128));
		} else {
			g = 0; b = lin(4 * (speed-192));
		}
	}
	return 'rgb(' + r + ',' + g + ',' + b + ')'; 
}

function barb(c,x,y,speed,dir,sign) {
	var s = 5 * Math.round(speed / 5);
	var cy = (s > 20)?24:20;
	var color = (wind_style == 1)?'#000': speed_color(speed);
	c.strokeStyle = color;
	c.save();
	c.translate(x-0.5, y-0.5);
	c.beginPath();
	if (s > 0) {
		c.rotate(dir * Math.PI/180);
		c.moveTo(0,0);
		c.lineTo(0,-cy -2 * (s >= 50));
		if (s === 5) {
			cy -= 4;
		} else if (s >= 50) {
			c.stroke();
			c.beginPath();
			c.moveTo(0,-cy -2);
			c.lineTo(10 * sign,-cy -2);
			c.lineTo(0,-cy + 4);
			c.fillStyle=color;
			c.closePath();
			c.fill();
			cy -= 8;
			s -= 50;
		}
		while (s > 0) {
			c.moveTo(0, -cy);
			if (s > 5) {
				c.lineTo(10 * sign, -(cy + 6));
			} else {
				c.lineTo(7 * sign, -(cy + 4.2));
			}
			s-= 10;
			cy-= 4;
		}
	} else {
		c.arc(0,0,3,0,2*Math.PI,0);
		c.rect(-0.5,-0.5,1,1);
	}
	c.stroke();
	c.restore();
}

function arrow(c,x,y,speed,dir,sign) {
	c.save();
	c.translate(x, y);
	c.rotate(dir * Math.PI/180);
	var scale = Math.sqrt(speed) / 6 + 0.15;
	c.scale(scale,scale);

	c.beginPath();
	c.moveTo(0,-7);
	c.lineTo(5,-9);
	c.lineTo(0,9);
	c.lineTo(-5,-9);
	c.closePath();
	c.fillStyle=speed_color(speed);
	c.fill();
	c.restore();
}

function extract_winds_a(img, wind) {
	var p_canvas = document.createElement('CANVAS');
	p_canvas.width=360;
	p_canvas.height = 180;
	var c = p_canvas.getContext("2d");
	c.drawImage(img,0,0,360,180);
	wind_array[wind/3] = c.getImageData(0,0,360,180).data;
}

function extract_winds(img) {
	w_canvas_c.drawImage(img,0,0,360,180);
	wind_array["current_wind"] = w_canvas_c.getImageData(0, 0, 360, 180).data;
	if (wind_style > 0 ) {
		show_canvas_wind();
	}
}

function load_wind(wind, in_ar) {
	var wind_img = new Image();
	if (in_ar) {
		wind_img.onload=function() {extract_winds_a(this, wind);};
	} else {
		if (wind_array[wind/3]) { // we happen to have it loaded
			wind_array["current_wind"] = wind_array[wind/3];
			if (wind_style > 0 ) {
				show_canvas_wind();
			}
			return;
		}	
		wind_img.onload=function() {extract_winds(this);};
	}
	var d = new Date((windbase+3600*wind)*1000);
	wind_img.src="/windp/" + 
		d.getUTCFullYear()  + 
		("0" + (d.getUTCMonth() + 1)).slice(-2) +  
		("0" + d.getUTCDate()).slice(-2) + "_" + 
		("00" + d.getUTCHours()).slice(-3) + "_uv.png?" + datastamp;
}

function load_array_winds() {
	for (var i = 0; i <= 8 + grib_steps/18; i++) {
		if (! wind_array[i]) {
			load_wind(i * 3,1);
		}
	}
}

function extract_polars(img) {
	var p_canvas = document.createElement('CANVAS');
	p_canvas.width = 130;
	p_canvas.height = 181;
	var c = p_canvas.getContext("2d");
	c.drawImage(img,0,0,130,181);
	polar_data = c.getImageData(0,0,130,181).data;
}

function load_polars(pro) {
	var polar_img = new Image();
	polar_img.onload = function() {extract_polars(this);};
	polar_img.src="ideal_" + pro + ".png?1";
}

function plot_winds(canvas, clear) {
	var fun = barb;
	var x,y,a,hemi,sc;
	var c = canvas.getContext("2d");
	if (clear) {
		canvas.width = canvas.width;
	}

	if (wind_style == 3) { // arrow	
		sc = (scale<32)?18:36;
		fun = arrow;
	} else {
		sc = (scale<32)?24:36;
		if (wind_style == 1) {
			c.lineWidth = 0.5;
		} else {
			c.lineWidth = 1.5;	
		}
	}
	for (x = canvas.xpos % sc; x <= canvas.width; x+=sc) {
		for (y = canvas.ypos % sc; y <= canvas.height; y+=sc) {
			a = get_interp_wind((x+canvas.xpos)/scale, hemi=(y+ canvas.ypos)/scale, "current_wind");
			fun(c,x,y,a[0]/1.852,a[1],(hemi>90)?-1:1);
		}
	}
}

function init_wind() {
	var w_canvas = document.createElement('CANVAS');
	if (w_canvas.getContext) {	//IE8?
		w_canvas.width=360;
		w_canvas.height=180;
		w_canvas_c = w_canvas.getContext("2d");
		wind_tile_size = 360;
	} else {
		return 0;
	}
	if (wind_time > 0) {
		load_wind(wind_time); 
	} else {
		load_wind(0, 0);
		load_wind(0, 1);
		load_wind(3, 1);
	}
	return 1;
}

