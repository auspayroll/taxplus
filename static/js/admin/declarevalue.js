var lon = 30.05979;
var lat = -1.94479;
var zoom = 18;
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

var style_green = { 
   fillColor: "green",
   fillOpacity: 0.25,
   strokeColor: "green",
   strokeOpacity: 1, 
   strokeWidth:1
};
var style_red = { 
   fillColor: "orange",
   fillOpacity: 0.25,
   strokeColor: "orange",
   strokeOpacity: 1, 
   strokeWidth:1
};
var style_black = { 
   fillColor: "red",
   fillOpacity: 0.25,
   strokeColor: "red",
   strokeOpacity: 1, 
   strokeWidth:1
};
 	
//Initialise the 'map' object
function init() 
{
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
    




function getCoordinates()
{
	str="";
	points = polygonLayer.features[0].geometry.getVertices();
	for(i=0;i<points.length;i++)
	{
		if(i>0){str=str+"#";}
		str=str+points[i].x+","+points[i].y;
	}
	$("#id_boundary").val(str);
	if(points.length>=3)
	{
		$("#boundary_error").html("Drawed!");
	}
	else
	{
		$("#boundary_error").html("Invalid area!");
	}
}

function refreshMap()
{
	polygonLayer.removeFeatures(polygonLayer.features);
	resultLayer.removeFeatures(resultLayer.features);	
	//resultLayer = new OpenLayers.Layer.Vector("Result Layer"); 
	//map.addLayer(resultLayer);
	$("#id_boundary").val("");
	$("#boundary_error").html("");
	table=document.getElementById("search_declared_values");
	for(var i = table.rows.length - 1; i >= 0; i--)
	{
		table.deleteRow(i);
	}
}

    
   	    
function toggle() 
{
	refreshMap();
	polygon.activate();
}

function check_search_conditions()
{	
	// check whether a search option is selected
	$("#search_error").html("");
	//if (!$("input[name='search_option']:checked").val())
	//{
	//	$("#search_error").html("Please select a search option.");
	//	$("#boundary_error").html("");
	//	return false;	
	//}
	
	// check whether an area is drawed
	if($('#id_boundary').val()==''||polygonLayer.features.length==0)
	{
		$("#search_error").html("Please draw an area to search.");
		$("#boundary_error").html("");
		return false;
	}
	// check whether we already have the result.
	if(resultLayer.features.length>0){return;}
	// check if the polygon contains at least 3 vertices	
 	if(polygonLayer.features.length>0)
 	{
		points = polygonLayer.features[0].geometry.getVertices();
		if(points.length<3)
		{ 
			polygonLayer.removeFeatures(polygonLayer.features);
			return;
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
			type:"get",
			url: "/admin/ajax/search_property_in_area/",
			data: {boundary: $("#id_boundary").val(),  purpose:"value declaration"},
			success:function(data)
			{
				if(data==""){return;}
				else
				{
					showResults(data);
				}
			},
			error: function(request)
			{
				alert(request.responseText);
			}
		}
	)
	
	return false;
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
		$("#keyword_"+search_field).val($(this).html());
	});
}


// get the query string out of the entered search conditions
function get_query_string()
{
	var querystring ="";
	if($("#plotid").val()!="")
	{
		if(isNaN($("#plotid").val()))
		{
			$("#keyword_error").html("Plot ID is invalid!");
		}
		else{querystring = "plotid="+$("#plotid").val();}	
		return querystring;
	}
	condition_count=0;
	if($.trim($("#keyword_suburb").val())!="")
	{
		condition_count++;
		querystring = "suburb="+$.trim($("#keyword_suburb").val());
	}
	if($.trim($("#keyword_streetname").val())!="")
	{
		condition_count++;
		if(condition_count>1){querystring=querystring+"&"}
		querystring = querystring + "streetname="+$.trim($("#keyword_streetname").val());
	}
	if($.trim($("#streetno").val())!="")
	{
		if(isNaN($.trim($("#streetno").val())))
		{
			$("#keyword_error").html("Street no is invalid!");
			return "";
		}
		condition_count++;
		if(condition_count>1){querystring=querystring+"&"}
		querystring = querystring + "streetno="+$.trim($("#streetno").val());
	}
	return querystring;
}


// search property with the provided conditions
function keyword_search()
{
	querystring = get_query_string();
	if(querystring=="")
	{
		$("#keyword_error").html("Please enter keyword to search!");
		return false;
	}
	search_property_by_fields(querystring, false);
}


// search property according to the querystring
function search_property_by_fields(querystring, refresh)
{
	querystring = querystring + "&purpose=value declaration&refresh=";
	if(refresh){
		querystring = querystring + "1";
	}
	else{
		querystring = querystring + "0";
	}
	$.ajax({
			type:"get",
			url: "/admin/ajax/search_property_by_fields/",
			data: querystring,
			success:function(data)
			{
				if(data==""){return;}
				else
				{
					showResults(data);
				}
			},
			error: function(request)
			{
				alert(request.responseText);
			}
	});
}


function viewPropertyDetail(plotid)
{
	querystring = "plotid="+plotid;
	search_property_by_fields(querystring,true);
}


// According to the Json object data, decide how to display the result
function showResults(data)
{
	properties=data["properties"];
	if(properties.length<2)
	{
		showSinglePropertyResult(data);	
	}
	else
	{
		showMultiplePropertyResults(data);
	}
}



// if the json object data has multiple properties, then a list of properties are display in a table only having plotid, amount, date, due information.
function showMultiplePropertyResults(data)
{
	toggle();
	properties=data["properties"];
	if(properties.length>0)
	{
		row=		"<tr>";
		row+= 			"<td>";
		row+=				"<div class='box'>";			
		row+=					"<div class='box_title'>Multiple results:</div>";
		row+=						"<div class='transactionhistory_div'>";					
		row+=							"<table id='transaction_table' cellpadding='0' cellspacing='0'>";
		row+=								"<tr>";
		row+=									"<td class='firstrowfirstcolumn'>Plot#ID</td>";
		row+=									"<td class='firstrow'>Amount</td>";
		row+=									"<td class='firstrow'>Date</td>";
		row+=									"<td class='firstrow'>Due</td>";
		row+=								"</tr>";
		for(i=0;i<properties.length;i++)
		{
			property=properties[i];
			plotid = property['plotid'];
			address = property['streetno']+ " "+property['streetname']+", "+property['suburb'];
			declareValues = property['declarevalues'];
			if(declareValues.length==0)
			{
				row+=							"<tr>";
				row+=								"<td class='firstcolumn'><a href='#' onclick='viewPropertyDetail("+plotid +")'>" + plotid + "</a></td>";
				row+=								"<td class='normal'> N/A</td>";
				row+=								"<td class='normal'> N/A</td>";
				row+=								"<td class='normal'> N/A</td>";									
				row+=							"<tr>";
			}
			else
			{
				declareValue=declareValues[0];
				row+=							"<tr>";
				row+=								"<td class='firstcolumn'><a href='#' onclick='viewPropertyDetail("+plotid +")'>" + plotid + "</a></td>";
				row+=								"<td class='normal'> "+declareValue['amount']+"</td>";
				row+=								"<td class='normal'> "+declareValue['datetime']+"</td>";
				row+=								"<td class='normal'> "+ getDueStatus(declareValue['datetime']) +"</td>";
				row+=							"</tr>";		
				
			}

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
			if(declareValues.length>0)
			{
				declareValue=declareValues[0];
				if(getDeclareValueStatus(declareValue['datetime'])=="lessthan3")
				{
					feature.style=style_green;	
				}
				if(getDeclareValueStatus(declareValue['datetime'])=="between34")
				{
					feature.style=style_red;	
				}
				if(getDeclareValueStatus(declareValue['datetime'])=="greaterthan4")
				{
					feature.style=style_black;	
				}
			}
			else
			{
				feature.style=style_black;
			}
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
		row+=							"</table>";
		row+=						"</div>";
		row+=					"</div>";
		row+=				"</div>";
		row+=			"</td>";
		row+=		"</tr>";
		$('#search_declared_values').append(row);
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
		polygon.deactivate();
	
}




// If the json object data has only one property, show property details inlcuding property info, latest declared value and transaction history
function showSinglePropertyResult(data)
{
	toggle();
	properties=data["properties"];
	if(properties.length>0)
	{
		for(i=0;i<properties.length;i++)
		{
			property=properties[i];
			declareValues = property['declarevalues'];
			property=properties[i];
			plotid = property['plotid'];
			address = property['streetno']+ " "+property['streetname']+", "+property['suburb'];
			row=		"<tr>";
			row+= 			"<td>";
			row+=    			"<table cellpadding='0' cellspacing='0' id='declaree_value'>";
			row+=        			"<tr>";
			row+=          				"<td border='0'>";
			
			// property info box
			
			row+=								"<div class='box'>";
			row+=									"<div class='box_title'>Property info:</div>";
			row+=									"<div class='box_detail'><strong>Plot ID:</strong> "+plotid+"</div>";
			row+=									"<div class='box_detail'><strong>Address:</strong> "+address+"</div>";
			row+=								"</div>";
			
			// official decared value box
			
			row+=								"<div class='box'>";
			row+=									"<div class='box_title'>Official declared value:</div>";
			if(declareValues.length==0)
			{
				row+=								"<div class='box_detail'><strong>Amount:</strong> N/A</div>";
				row+=								"<div class='box_detail'><strong>Date submitted:</strong> N/A</div>";
				row+=								"<div class='box_detail'><strong>Submitted by:</strong> N/A</div>";
				row+=								"<div class='box_detail'><strong>Staff name:</strong> N/A</div>";	
			}
			else
			{
				latest_declared_value = declareValues[0];
				row+=								"<div class='box_detail'><strong>Amount:</strong> "+latest_declared_value['amount']+"</div>";
				row+=								"<div class='box_detail'><strong>Date submitted:</strong> "+latest_declared_value['datetime']+"</div>";
				row+=								"<div class='box_detail'><strong>Submitted by:</strong> "+latest_declared_value['citizen']+"</div>";
				row+=								"<div class='box_detail'><strong>Staff name:</strong> "+latest_declared_value['staff']+"</div>";	
			}
			row+=								"</div>";
			
			
			// Transaction history box
			
			row+=								"<div class='box'>";			
			row+=									"<div class='box_title'>Transaction history:</div>";
			row+=									"<div class='transactionhistory_div'>";					
			row+=										"<table id='transaction_table' cellpadding='0' cellspacing='0'>";
			row+=											"<tr>";
			row+=												"<td class='firstrowfirstcolumn'>Date</td>";
			row+=												"<td class='firstrow'>Amount</td>";
			row+=												"<td class='firstrow'>Accept</td>";
			row+=												"<td class='firstrow'>Official</td>";
			row+=											"</tr>";
			if(declareValues.length==0)
			{
				row+=										"<tr>";
				row+=											"<td colspan='4' class='firstcolumn' align='center'> This property has no declared values.</td>";
				row+=										"<tr>";
			}
			else
			{
				for(s=0;s<declareValues.length;s++)
				{
					declareValue=declareValues[s];
					row+=									"<tr>";
					row+=										"<td class='firstcolumn'>"+declareValue['datetime']+"</td>";
					row+=										"<td class='normal'>"+declareValue['amount']+"</td>";
					row+=										"<td class='normal'>"+declareValue['accepted']+"</td>";
					row+=										"<td class='normal'>"+declareValue['staff']+"</td>";
					row+=									"</tr>";		
				}
			}
			row+=									"</table>";
			row+=								"</div>";
			row+=							"</div>";
			
			// action: declare a value
			
			row+=							"<div>";
			row+=								"<div style='line-height:30px;'><strong>Declare a new value for this propertry:</strong></div>";
			row+=								"<div>";
			row+=									"<table>";
			row+=										"<tr>";
			row+=											"<td>";
			row+=												"<div style='width:100px; float:left;'>Amount:</div>";
			row+=												"<div style='width:250px; float:left;'><input type='text' name='declare_amount' id='declare_amount'/> ($AUD)</div>";
			row+=												"<div style='clear:both'></div>";
			row+=											"</td>";
			row+=										"</tr>";
			row+=										"<tr>";
			row+=											"<td>";
			row+=												"<div style='width:100px; float:left;'>Citizen ID:</div>";
			row+=												"<div style='width:250px; float:left;'><input id='citizenid' type='text' name='citizenid'/></div>";
			row+=												"<div style='clear:both'></div>";
			row+=											"</td>";
			row+=										"</tr>";
			row+=										"<tr>";
			row+=											"<td colspan='2'><button id='button" + plotid + "' type='button'>Declare</button></td>";
			row+=										"</tr>";
			row+=										"</table>";
			row+=									"</div>";									
			row+=								"<div style='line-height:30px;color:red;' id='declare_amount_error'></div>";
			row+=							"</div>";
			
			
			
			
			
			
			row+=						"</td>";
			row+=					"</tr>";
			row+=				"</table>";
			row+=			"</td>";
			row+=		"</tr>";
			
			
			
			
			
			$('#search_declared_values').append(row);
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
			if(declareValues.length>0)
			{
				declareValue=declareValues[0];
				if(getDeclareValueStatus(declareValue['datetime'])=="lessthan3")
				{
					feature.style=style_green;	
				}
				if(getDeclareValueStatus(declareValue['datetime'])=="between34")
				{
					feature.style=style_red;	
				}
				if(getDeclareValueStatus(declareValue['datetime'])=="greaterthan4")
				{
					feature.style=style_black;	
				}
			}
			else
			{
				feature.style=style_black;
			}
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
		    
		    
		   $('button[id^="button"]').click(function(){
				id = $(this).attr('id');
				plotid = id.replace("button","");
				amount = $.trim($("#declare_amount").val());
				citizenid = $.trim($("#citizenid").val());
				if( amount=="" || isNaN(amount) )
				{
					$("#declare_amount_error").html("Please enter a valid amount!");
					return false;
				}
				else if( citizenid=="" || isNaN(citizenid) )
				{
					$("#declare_amount_error").html("Please enter a valid citizenid!");
					return false;
				}
				else
				{
					querystring = "plotid="+plotid+"&amount="+amount+"&citizenid="+citizenid;
					$.ajax({
						type:"get",
						url: "/admin/ajax/declare_value/",
						data: querystring,
						success:function(data)
						{
							if(data==""){return;}
							else
							{
								if(data=="OK")
								{
									querystring = "plotid=" + plotid;
									search_property_by_fields(querystring,true);
									return true;
								}
								else
								{
									$("#declare_amount_error").html(data);
									return false;
								}
							}
						},
						error: function(request)
						{
							alert(request.responseText);
						}
					});
	
					
					return true;	
				}
				
			});
				    
		    
	
		    
		}
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
		polygon.deactivate();
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
	
	$('input[id^="keyword_"]').keyup(function(){
		search_field = $(this).attr("id").replace("keyword_","");
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
	
});


function getDeclareValueStatus(date_var)
{
	date_parts = date_var.split(' ');
	date_parts = date_parts[0];
	date_parts=date_parts.split('-');
	year=parseInt(date_parts[0]);
	month=parseInt(date_parts[1]);
	day=parseInt(date_parts[2]);
	date_created = new Date(year, month-1, day);
	
	
	status = new Array();
	status[0] = "lessthan3";
	status[1] = "between34";
	status[2] = "greaterthan4";
	
	var today = new Date();
	days=(today.getTime()-date_created.getTime())/(1000*60*60*24);
	
	years = 1.0*days/365;
	if(years<=3){result = status[0];}
	if(years>3&&years<=4){result = status[1];}
	if(years>4){result = status[2];}
	return result;	
}

function getDueStatus(date_var)
{
	status=getDeclareValueStatus(date_var);
	if(status=="greaterthan4")
	{
		return "Yes";
	}
	else
	{
		return "No";
	}
}


