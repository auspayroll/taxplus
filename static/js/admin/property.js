var lon=30.05979;
var lat=-1.94479;
var zoom = 18;
var polygon;
var renderer; //= OpenLayers.Util.getParameters(window.location.href).renderer;
//renderer = (renderer) ? [renderer] : OpenLayers.Layer.Vector.prototype.renderers;
var map; //complex object of type OpenLayers.Map
var polygonLayer;
var newLayer;
var apiKey = "AqTGBsziZHIJYYxgivLBf0hVdrAk9mWO5cQcb8Yux8sW5M8c8opEC2lZqKR1ZZXf";
 	
//Initialise the 'map' object
function init() 
{
	map_div = document.getElementById("map");
 	if(map_div==null)
 	{
 		return;
 	}
 	renderer = OpenLayers.Util.getParameters(window.location.href).renderer;
 	renderer = (renderer) ? [renderer] : OpenLayers.Layer.Vector.prototype.renderers;
 	
 	
   	map = new OpenLayers.Map 
   	("map", {controls:
    	[
            new OpenLayers.Control.Navigation(),
            new OpenLayers.Control.PanZoomBar(),
            new OpenLayers.Control.Permalink(),
            new OpenLayers.Control.ScaleLine({geodesic: true}),
            new OpenLayers.Control.Permalink('permalink'),
            new OpenLayers.Control.MousePosition(),                    
            new OpenLayers.Control.Attribution()
        ],
        maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
        maxResolution: 156543.0339,
        numZoomLevels: 19,
        units: 'm',
        projection: new OpenLayers.Projection("EPSG:900913"),
        displayProjection: new OpenLayers.Projection("EPSG:4326")
        });
	
	
		
	
        // This is the layer that uses the locally stored tiles
        //newLayer = new OpenLayers.Layer.OSM("Local Tiles");
        
	    var gsat = new OpenLayers.Layer.Google("Google Satellite",{type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 19});
    	map.addLayer(gsat);
	    
	    newLayer = new OpenLayers.Layer.OSM("Local Tiles", map_url+"/osm/${z}/${x}/${y}.png", {numZoomLevels: 19});
	    newLayer.tileOptions={crossOriginKeyword: null};
	    map.addLayer(newLayer);
	    
    	 var aerial = new OpenLayers.Layer.Bing({
            name: "Aerial",
            key: apiKey,
            type: "Aerial",
            numZoomLevels: 19
        });	    
	    map.addLayer(aerial);
	    
	    
		polygonLayer = new OpenLayers.Layer.Vector("Polygon Layer", { renderers: renderer });
		map.addLayer(polygonLayer);
	
		
		map.addControl(new OpenLayers.Control.LayerSwitcher());
	
	
	    if( ! map.getCenter() ){
	        var lonLat = new OpenLayers.LonLat(lon, lat).transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject());
	    	map.setCenter (lonLat, zoom);
	    }
	    
	    polygon = new OpenLayers.Control.DrawFeature(
			polygonLayer,
			OpenLayers.Handler.Polygon,
			{
				handlerOptions: {holeModifier: "altKey"},
			}
		);
		
		polygon.events.register("featureadded", '', controlFeatureHandler);
		
		function controlFeatureHandler(data)
		{
			// deal with some data storing
			//candraw = false;
			getCoordinates();
			polygon.deactivate();
		}
		map.addControl(polygon);	
}
   
function getCoordinates()
{
	str="";
	points = polygonLayer.features[0].geometry.getVertices();
	for(i=0;i<points.length;i++)
	{
		if(i>0){str=str+"#";}
		str=str+points[i].x+","+points[i].y;
	}
	$("#id_boundary").html(str);
	if(points.length>=3)
	{
		$("#boundary_error").html("Boundary added!");
	}
	else
	{
		$("#boundary_error").html("Invalid boundary!");
	}
}

function refreshMap()
{
	map.removeControl(polygon);
	map.removeLayer(polygonLayer);
	polygon.destroy();
	polygonLayer.destroy();
	$("#id_boundary").html("");
	$("#boundary_error").html("");
	polygonLayer = new OpenLayers.Layer.Vector("Vector Layer", { renderers: renderer });
	map.addLayer(polygonLayer);
	polygon = new OpenLayers.Control.DrawFeature(
		polygonLayer,
		OpenLayers.Handler.Polygon,
		{
			handlerOptions: {holeModifier: "altKey"},
		}
	);
	
	polygon.events.register("featureadded", '', controlFeatureHandler);
	
	function controlFeatureHandler(data)
	{
		//deal with some data storing
		//candraw = false;
		getCoordinates();
		polygon.deactivate();
	}
	map.addControl(polygon);
}
	    
function toggle() {
	if(polygon!=null)
	{
		if(!polygon.active)
		{
			if($("#id_boundary").html()=='')
			{polygon.activate();}
			else
			{
				refreshMap();
				polygon.activate();	
			}
		}
		else 
		{
			refreshMap();
			polygon.activate();
		}				
	}
}

function check_property_registration_form()
{
	plotid=$.trim($("#id_plotid").val());
	suburb = $.trim($("#id_suburb").val());

	if(plotid==''){
		$("#error").html('Please enter plot id.');
		return false;		  
	}
	else if(isNaN(plotid))
	{
		$("#error").html('Plot id is invalid.');
		return false;
	} 
	
	
	if(suburb==''){
		$("#error").html('Please enter suburb name.');
		return false;		  
	}
	
	if($("#id_boundary").html()=="")
	{
		$("#error").html("Please add boundary for this property!");
		return false;
	}
	else
	{
		string=$("#id_boundary").html();
		points=string.split('#');
		if(points.length<2)
		{	
			$("#error").html("Please add a valid boundary!");
			return false;
		}
	}
	
	$('html').ajaxSend(function(event, xhr, settings) {
	    function getCookie(name) {
	        var cookieValue = null;
	        if (document.cookie && document.cookie != '') {
	            var cookies = document.cookie.split(';');
	            for (var i = 0; i < cookies.length; i++) {
	                var cookie = jQuery.trim(cookies[i]);
	                // Does this cookie string begin with the name we want?
	                if (cookie.substring(0, name.length + 1) == (name + '=')) {
	                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
	                    break;
	                }
	            }
	        }
	        return cookieValue;
	    }
	    if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
	        // Only send the token to relative URLs i.e. locally.
	        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
	    }
	});
	
	
	$.ajax({
			type:"post",
			url: "/admin/ajax/add_property/",
			data: {plotid: $("input#id_plotid").val(), streetno: $("input#id_streetno").val(), streetname: $("input#id_streetname").val(), suburb: $("input#id_suburb").val(), boundary:$("#id_boundary").html()},
			success:function(data)
			{
				$("div#error").html("Property added successfully!");
				toggle();
				return;
			},
			error: function(request)
			{
				alert(request.responseText);
			}
		}
	)
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	return true;
}
   
function checkPropertyConditions()
{
	plotid =  $.trim($("#id_plotid").val());
	streetno =  $.trim($("#id_streetno").val());
	streetname =  $.trim($("#id_streetname").val());
	suburb =  $.trim($("#id_suburb").val());
	if(plotid!="")
	{
		if(isNaN(plotid))
		{
			$("#search_error").html("Plot id is not a valid number.");
			return false;
		}
		return true;
	}
	else
	{
		if((streetno=="")&(streetname=="")&(suburb==""))
		{
			$("#search_error").html("No property details entered!");
			return false;
		}
		if(isNaN(streetno))
		{
			$("#search_error").html("Street number is not a valid number.");
			return false;
		}
		if((streetno!="")&(streetname!="")&(suburb!=""))
		{
			return true;
		}
		else
		{
			$("#search_error").html("Please enter street number, street name and suburb. Alternatively, you can enter plot ID only.");
			return false;
		}
	}
}

function showPropertyOnMap()
{
	var points=$("#points").html();
	points=eval("("+points+')');
		
	popup_message ="Hello";
	popup_message = "<div>"+popup_message+"</div>";
	var polygon_points = [];
	for( j=0;j<points.length;j++)
	{
		point=points[j];
		x = point['x'];
		y = point['y'];
		p = new OpenLayers.Geometry.Point(x,y);
  		polygon_points.push(p);
	}
	var ring = new OpenLayers.Geometry.LinearRing(polygon_points);
	var polygon_obj= new OpenLayers.Geometry.Polygon([ring]);
	var feature = new OpenLayers.Feature.Vector(polygon_obj,{});
	var anchor = {'size': new OpenLayers.Size(0,0), 'offset': new OpenLayers.Pixel(0, 0)};
    popup = new OpenLayers.Popup.FramedCloud(
      	"",
      	feature.geometry.getBounds().getCenterLonLat(),
      	new OpenLayers.Size(100,100),
      	popup_message,
      	anchor,
      	false
      	);
    feature.popup = popup;
	polygonLayer.addFeatures([feature]);
    map.addPopup(popup);
}


