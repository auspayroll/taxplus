var resultLayer;
var property_str; 	
function init() 
{
 	loadMap();
	
	polygon = new OpenLayers.Control.DrawFeature(
		polygonLayer,
		OpenLayers.Handler.Polygon,
		{
			handlerOptions: {holeModifier: "altKey"},
		}
	);
	map.addControl(polygon);     
	polygon.events.register("featureadded", '', controlFeatureHandler); 
	resultLayer = new OpenLayers.Layer.Vector("Result Layer",{
		styleMap: new OpenLayers.StyleMap({'default':{
				strokeColor: "#00FF00",
				strokeOpacity: 1,
				strokeWidth: 2,
				fillColor: "#FF5500",
				fillOpacity: 0.5,
				pointRadius: 0,
				//pointerEvents: "visiblePainted",
				// label with \n linebreaks
				label : " ${parcel_id} ",
                    
				fontColor: "white",
				fontSize: "13",
				fontFamily: "Courier New, monospace",
				fontWeight: "normal",
				labelAlign: "cm",
				labelXOffset: "0",
				labelYOffset: "0",
				labelOutlineColor: "#fff",
				labelOutlineWidth: 0
			}}),
	
	}); 
	map.addLayer(resultLayer);

	
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
		var properties = geodata['properties'];
		for(i=0;i<properties.length;i++)
		{
			property=properties[i];
			upi = property['upi'];
			if(upi==undefined)
			{
				continue;
			}
			//plot_id = property['plot_id'];
			address = '';

			if(property['village']==undefined)
			{
				address = property['parcel_id']+ ", " + property['cell'] + ", " +property['sector'];
			}
			else
			{
				address = property['parcel_id']+ " "+property['village']+", " + property['cell'] + ", " +property['sector'];
			}

			
			property_popup_message = "<div>UPI: "+upi+"<br>Address: "+address+"</div>";
			points=property['points'];
			var polygon_points = [];

			if(points==undefined||points.length==0)
			{
				continue;
			}
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
			var feature = new OpenLayers.Feature.Vector(polygon_obj,{parcel_id:property['parcel_id']});
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

	map.addControl(new OpenLayers.Control.LayerSwitcher());			
	function controlFeatureHandler(data)
	{
		getCoordinates();
		polygon.deactivate();			
	}
	// This is very important
	var bounds = resultLayer.getDataExtent();
    map.zoomToExtent(bounds);
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
	
	
	//table=document.getElementById("search_declared_values");
	//for(var i = table.rows.length - 1; i >= 0; i--)
	//{
	//	table.deleteRow(i);
	//}
}

    
   	    
function toggle() 
{
	refreshMap();
	polygon.activate();
}


function check_search_conditions()
{	

	$("#search_error").html("");
	if($('#id_boundary').val()==''||polygonLayer.features.length==0)
	{
		$("#search_error").html("Please draw an area to search.");
		$("#boundary_error").html("");
		return false;
	}
	// check whether we already have the result.
	if(resultLayer.features.length>0){return false;}
	// check if the polygon contains at least 3 vertices	
 	if(polygonLayer.features.length>0)
 	{
		points = polygonLayer.features[0].geometry.getVertices();
		if(points.length<3)
		{ 
			polygonLayer.removeFeatures(polygonLayer.features);
			return false;
		}
	}
	return true;
}




function keyword_search()
{
	var condition_count = 0;
	var querystring ="";
	var ids = Array("id_citizen_id","id_upi","id_parcel_id","id_cell","id_sector");
	var descs = Array("", "", "Parcel ID", "", "");
	
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
	
	$("#printall").click(function(){
		query_string = $("#id_query_string").val().replace(/#/g,',');
		
		if(query_string==''){return false;}
		$.ajax({
				type:"get",
				url: "/admin/ajax/search_properties_for_printing/",
				data: query_string,
				success:function(data)
				{

					properties = data['properties'];
					str = "";
					str += "<table border='1' cellpadding='2' cellspacing ='0' style='margin-left:auto; text-align:left;margin-right:auto;'>";
					str +=	"	<tr>";
					str +=	"		<th>Parcel ID</th>";
					str +=	"		<th>Village</th>";
					str +=	"		<th>Cell</th>";
					str +=	"		<th>Sector</th>";
					str +=	"		<th>Owners</th>";
					str +=	"		<th>Phone</th>";
					str +=	"		<th>Email</th>";
					str +=	"		<th>Tax applicable</th>";
					str +=	"	</tr>";
					
					for(i=0; i<properties.length; i++)
					{
						print_id = i+1;
						property = properties[i];
						str+= "<tr class='";
						if(i%2==0){str+="single'";}
						else{str+="double'";}
						str+="><td>"+property['parcel_id']+"</td>";
						str+="><td>"+property["village"]+"</td>";
						str+="><td>"+property["cell"]+"</td>";
						str+="><td>"+property["sector"]+"</td>";
						str+="<td>"+property["all_owners"]+"</td>";
						str+="<td>"+property["phone"]+"</td>";
						str+="<td>"+property["email"]+"</td>";
						str+="<td>"+property["taxes"]+"</td>";
						str+="</tr>";
					}
					str += "</table>";
					$("#properties_in_all_pages").html(str);
					$("#properties_in_all_pages").printElement();
				},
				error: function(request)
				{
					//document.write(request.responseText);
					//alert(request.responseText);
				}
			});
	});
	
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
		if(search_field!="sector"&&search_field!="cell"&&search_field!="village"){return;}
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
					//alert(request.responseText);
				}
			});
		}
	});
});

