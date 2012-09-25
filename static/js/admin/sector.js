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

function check_sector_registration_form()
{
	name=$.trim($("#id_name").val());
	if(name==''){
		$("#error").html('Please enter sector name.');
		return false;		  
	}
	
	if($("#id_boundary").html()=="")
	{
		$("#error").html("Please add boundary for this sector!");
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
			url: "/admin/ajax/add_sector/",
			data: {name: $("input#id_name").val(), council:$("#id_council").val(), district:$("#id_district").val(), boundary:$("#id_boundary").html()},
			success:function(data)
			{
				$("div#error").html("Sector added successfully!");
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
   
function checkSectorConditions()
{
	name =  $.trim($("#id_name").val());
	if(name!=""){ return true;}
	else
	{
		$("#search_error").html("Please enter sector name.");
		return false;
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








function selectSectorRepeater()
{
	$('li[id^="li_district_"]').mouseover(function(){
		$(this).css("cursor","pointer");
		$(this).css("background-color","red");
	});
	$('li[id^="li_district_"]').mouseleave(function(){
			$(this).css("background-color","#cccccc");
		});
	
	$('li[id^="li_district_"]').click(function(){
		$('#id_name').val($(this).html());
		$('#id_id').val($(this).attr("districtid"));
	});
}

function selectSector()
{
	
	$(document).ready(function(){
		$('#matched_users_list').mouseleave(function(){
			$(this).fadeOut();
		});
		
		
		$('#id_name').click(function(){
			if($.trim($(this).val())=='')
			{
				$('#matched_users_list').html('');
				$('#matched_users_list').hide();
				$('#id_id').val('');
				return;
			}
			else
			{
				kw = $.trim($(this).val());
				querystring = "keyword="+kw + "&object_name=sector";
				$.ajax(
					{
						type:"get",
						url: "/admin/ajax/search_object_names/",
						data: querystring,
						success:function(data)
						{
							if(data=="")
							{
								$('#matched_users_list').html('');
								$('#matched_users_list').hide();
								$('#id_id').val('');
								return;
							}
							else
							{
								str="<ul>";
								districts=data.split('#');
								for(i=0;i<districts.length;i++)
								{
									district=districts[i];
									district_parts=district.split(':')
									districtid=district_parts[0];
									name=district_parts[1];
									str=str+"<li id='li_district_"+i+"' districtid="+ districtid + ">"+ name+"</li>";										
								}
								str=str+"</ul>";
								$('#matched_users_list').html(str);
								$('#matched_users_list').show();
								selectSectorRepeater();
							}
						},
						error: function(request)
						{
							alert(request.responseText);
						}
					}
				)
			}
		});
		
		
		$('#id_name').keyup(function(){
			if($.trim($(this).val())=='')
			{
				$('#matched_users_list').html('');
				$('#matched_users_list').hide();
				$('#id_id').val('');
				return;
			}
			else
			{
				kw = $.trim($(this).val());
				querystring = "keyword="+kw + "&object_name=sector";
				$.ajax(
					{
						type:"get",
						url: "/admin/ajax/search_object_names/",
						data: querystring,
						success:function(data)
						{
							if(data=="")
							{
								$('#matched_users_list').html('');
								$('#matched_users_list').hide();
								$('#id_id').val('');
								return;
							}	
							else
							{
								str="<ul>";
								districts=data.split('#');
								for(i=0;i<districts.length;i++)
								{
									district=districts[i];
									district_parts=district.split(':')
									districtid=district_parts[0];
									name=district_parts[1];
									str=str+"<li id='li_district_"+i+"' districtid="+ districtid + ">"+ name+"</li>";										
								}
								str=str+"</ul>";
								$('#matched_users_list').html(str);
								$('#matched_users_list').show();
								selectSectorRepeater();
							}
						},
						error: function(request)
						{
							alert(request.responseText);
						}
					}
				)
			}
		});
		
	});
}






