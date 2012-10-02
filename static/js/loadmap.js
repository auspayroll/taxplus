var lon=30.05979;
var lat=-1.94479;
var zoom = 18;
var polygon;
var renderer;
var map;
var googleLayer;
var osmLayer;
var aerialLayer;
var polygonLayer;
var apiKey = "AqTGBsziZHIJYYxgivLBf0hVdrAk9mWO5cQcb8Yux8sW5M8c8opEC2lZqKR1ZZXf";
renderer = OpenLayers.Util.getParameters(window.location.href).renderer;
renderer = (renderer) ? [renderer] : OpenLayers.Layer.Vector.prototype.renderers; 	


// setup map height according the custom screen size

function loadMap()
{
	if($("div#maparea")!=null)
	{
		setupMapHeight();	
	}
	map = new OpenLayers.Map 
	("map", {controls:
		[
	        new OpenLayers.Control.Navigation(),
	        //new OpenLayers.Control.PanZoomBar(),
	        //new OpenLayers.Control.Permalink(),
	        //new OpenLayers.Control.ScaleLine({geodesic: true}),
	        //new OpenLayers.Control.Permalink('permalink'),
	        new OpenLayers.Control.MousePosition(),                    
	        //new OpenLayers.Control.Attribution()
	    ],
	    maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
	    maxResolution: 156543.0339,
	    numZoomLevels: 19,
	    units: 'm',
	    projection: new OpenLayers.Projection("EPSG:900913"),
	    displayProjection: new OpenLayers.Projection("EPSG:4326")
	});
	    
	    
	googleLayer = new OpenLayers.Layer.Google("Google Satellite",{type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 19});
	osmLayer = new OpenLayers.Layer.OSM("Local Tiles", map_url+"/osm/${z}/${x}/${y}.png", {numZoomLevels: 19});
	osmLayer.tileOptions={crossOriginKeyword: null};
	aerialLayer = new OpenLayers.Layer.Bing({name: "Aerial",key: apiKey,type: "Aerial",numZoomLevels: 19});
	polygonLayer = new OpenLayers.Layer.Vector("Polygon Layer", { renderers: renderer });
	map.addLayer(googleLayer);
	map.addLayer(osmLayer);
	map.addLayer(aerialLayer);
	map.addLayer(polygonLayer);
	map.addControl(new OpenLayers.Control.LayerSwitcher());
	if( ! map.getCenter() ){
	    var lonLat = new OpenLayers.LonLat(lon, lat).transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject());
		map.setCenter (lonLat, zoom);
	}
	$("div.hidepanel img").click(function(){
		$(this).parent().hide();
		$(this).parent().parent().find("div.panelcontent").hide();		
		$(this).parent().parent().find("div.showpanel").show();
	});
	$("div.showpanel img").click(function(){
		$(this).parent().hide();
		$(this).parent().parent().find("div.panelcontent").show();
		$(this).parent().parent().find("div.hidepanel").show();
	});
	
	$("div.hidepanel").each(function(index){
		$(this).css('margin-top',15);
	});
	$("div.showpanel").each(function(index){
		$(this).css('margin-top',15);
	});
}





function setupMapHeight()
{
	var myWidth;
	var myHeight;
	if( typeof( window.innerWidth ) == 'number' ) { 
	
	//Non-IE 
	myWidth = window.innerWidth;
	myHeight = window.innerHeight; 
	} else if( document.documentElement && 
	( document.documentElement.clientWidth || document.documentElement.clientHeight ) ) { 
	
	//IE 6+ in 'standards compliant mode' 
	
	myWidth = document.documentElement.clientWidth; 
	myHeight = document.documentElement.clientHeight; 
	
	} else if( document.body && ( document.body.clientWidth || document.body.clientHeight ) ) { 
	
	//IE 4 compatible 
	
	myWidth = document.body.clientWidth; 
	myHeight = document.body.clientHeight; 
	}
	
	$("div#maparea").height(myHeight - 140);
}



var style_green = { 
   fillColor: "#00ff00",
   fillOpacity: 0.25,
   strokeColor: "#00ff00",
   strokeOpacity: 1, 
   strokeWidth:1
};


var style_orange = { 
   fillColor: "#ffa500",
   fillOpacity: 0.25,
   strokeColor: "#ffa500",
   strokeOpacity: 1, 
   strokeWidth:1
};




var style_purple = { 
   fillColor: "#a020f0",
   fillOpacity: 0.25,
   strokeColor: "#a020f0",
   strokeOpacity: 1, 
   strokeWidth:1
};


var style_skyblue = { 
   fillColor: "#87ceeb",
   fillOpacity: 0.25,
   strokeColor: "#87ceeb",
   strokeOpacity: 1, 
   strokeWidth:1
};


var style_pink = { 
   fillColor: "#ffc0cb",
   fillOpacity: 0.25,
   strokeColor: "#ffc0cb",
   strokeOpacity: 1, 
   strokeWidth:1
};


var style_red = { 
   fillColor: "#ff0000",
   fillOpacity: 0.25,
   strokeColor: "#ff0000",
   strokeOpacity: 1, 
   strokeWidth:1
};


var style_black = { 
   fillColor: "black",
   fillOpacity: 0.25,
   strokeColor: "black",
   strokeOpacity: 1, 
   strokeWidth:1
};


