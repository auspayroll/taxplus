var lon=30.05979;
var lat=-1.94479;
var zoom = 17;
var polygon;
var renderer = OpenLayers.Util.getParameters(window.location.href).renderer;
renderer = (renderer) ? [renderer] : OpenLayers.Layer.Vector.prototype.renderers;
var map; //complex object of type OpenLayers.Map
var polygonLayer;
var resultLayer;
var newLayer;
var property_str;
var apiKey = "AqTGBsziZHIJYYxgivLBf0hVdrAk9mWO5cQcb8Yux8sW5M8c8opEC2lZqKR1ZZXf";
var style = { 
  strokeColor: '#0000ff', 
  strokeOpacity: 0.5,
  strokeWidth: 5
};
 	
//Initialise the 'map' object
function initMap() 
{
 
   	map = new OpenLayers.Map 
   	("map", {controls:
    	[
            new OpenLayers.Control.Navigation(),                   
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
		polygon = new OpenLayers.Control.DrawFeature(
			polygonLayer,
			OpenLayers.Handler.Polygon,
			{
				handlerOptions: {holeModifier: "altKey"},
			}
		);
		map.addControl(polygon);     
		polygon.events.register("featureadded", '', controlFeatureHandler); 



		resultLayer = new OpenLayers.Layer.Vector("Result Layer"); 
		map.addLayer(resultLayer);


                                                
		map.addControl(new OpenLayers.Control.LayerSwitcher());
		
					
	    if( ! map.getCenter() ){
	        var lonLat = new OpenLayers.LonLat(lon, lat).transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject());
	    	map.setCenter (lonLat, zoom);
	    }
	    
	
		function controlFeatureHandler(data)
		{
			// deal with some data storing
			//candraw = false;
			getCoordinates();
			polygon.deactivate();			
		}	
}





















function keyword_search()
{
	var condition_count = 0;
	var querystring ="";
	var ids = Array("id_citizenid","id_plotid","id_suburb","id_streetname","id_streetno");
	var descs = Array("Citizen ID", "Plot ID", "", "", "Street no");
	
	// Check number value valid or not, and whether value is entered
	for(var i=0;i<ids.length;i++)
	{
		var id = ids[i];
		var desc = descs[i];
		var value = $("#"+id).val();
		if(value!="")
		{
			if(desc!=""&&isNaN(value))
			{
				$("#keyword_error").html(desc+" is invalid!");
				return false;
			}
			else
			{
				condition_count++;
			}
		}
	}
	if(condition_count==0)
	{
		$("#keyword_error").html("Please enter search conditions!");
		return false;
	}
	return true;
}











function initilizeListEvents()
{
	$('li[id^="li_"]').mouseover(function(){
		$(this).css("cursor","pointer");
		$(this).css("background-color","red");
	});
	$('li[id^="li_"]').mouseleave(function(){
		$(this).css("background-color","#cccccc");
	});
	$('li[id^="li_"]').click(function(){
		id = $(this).attr("id");
		parts = id.split("_");
		search_field = parts[1];
		$("#id_"+search_field).val($(this).html());
	});
}


$(document).ready(function(){	
	$("#tabs").tabs();
	$('.dropdown_list').mouseleave(function(){
		$(this).fadeOut();
	});
	$('li[id^="li_"]').mouseover(function(){
		$(this).css("cursor","pointer");
		$(this).css("background-color","red");
	});
	$('li[id^="li_"]').mouseleave(function(){
		$(this).css("background-color","#cccccc");
	});
	
	$('input[id^="id_"]').keyup(function(){
		search_field = $(this).attr("id").replace("id_","");
		if(search_field!="suburb"&&search_field!="streetname"){return;}
		if($.trim($(this).val())=="")
		{
			$('#'+search_field+"_dropdown_list").html('');
			$('#'+search_field+"_dropdown_list").fadeOut();
			return;
		}
		else
		{
			value = $.trim($(this).val());
			querystring = search_field+"="+value;
			$.ajax({
				type:"get",
				url: "/admin/ajax/search_property_field/",
				data: querystring,
				success:function(data)
				{
					if(data==""){return;}
					else
					{
						str="<ul>";
						for(i=0;i<data.length;i++)
						{
							str=str+"<li id='li_"+search_field+"_"+i+"'>"+ data[i] + "</li>";										
						}
						str=str+"</ul>";
						$('#'+search_field+'_dropdown_list').html(str);
						$('#'+search_field+'_dropdown_list').show();
						initilizeListEvents();
					}
				},
				error: function(request)
				{
					alert(request.responseText);
				}
			});
		}
	});
	
	
	
	
	// draw properties on the map
	if($("#geodata").html()!="")
	{
		var geodata = $.trim($("#geodata").html());
		if(geodata != "")
		{
			geodata = $.parseJSON(geodata);	
		}
		else
		{
			return;
		}
		initMap();
		var properties = geodata['properties'];
		for(i=0;i<properties.length;i++)
		{
			property=properties[i];
			plotid = property['plotid'];
			address = property['streetno']+ " "+property['streetname']+", "+property['suburb'];
			property_popup_message = "<div>Plot ID: "+plotid+"<br>Address: "+address+"</div>";
			points=property['points'];
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
	          	property_popup_message,
	          	anchor,
	          	false
	          	);
		    feature.popup = popup;
			resultLayer.addFeatures([feature]);
		    map.addPopup(popup);
		}
		polygonLayer.removeFeatures(polygonLayer.features);
		
		
		
		// popup effects
		for(s=0;s<resultLayer.features.length;s++)
		{
			resultLayer.features[s].popup.hide();
		}
		
		var selectControl = new OpenLayers.Control.SelectFeature(
			resultLayer, {
				hover: true,
				onBeforeSelect: function(feature) {
					feature.popup.show();   
				        return true;
				},
		    	onUnselect: function(feature) {
			       feature.popup.hide();
			       return true;
		    	}
			}
		);
			
		map.addControl(selectControl);
		selectControl.activate();
						

		
		
		 	
	}
	
	
	
		
});
