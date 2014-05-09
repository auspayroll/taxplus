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



	resultLayer = new OpenLayers.Layer.Vector("Result Layer"); 
	map.addLayer(resultLayer);

    

	function controlFeatureHandler(data)
	{
		getCoordinates();
		polygon.deactivate();			
	}
	
	$("id^=generate").click(function(){
		id = $(this).attr('id');
		id = id.replace("generatetax", "");
		//alert(id);
	});	
}
    

function declare()
{
	plot_id = $("#id_plot_id").val();
	querystring = "plot_id="+plot_id;
	search_property_by_fields(querystring, false);
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
				//alert(request.responseText);
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
	if($("#id_upi").val()!="")
	{
		querystring = "upi="+$("#id_upi").val();
		return querystring;
	}
	condition_count=0;
	if($.trim($("#id_sector").val())!="")
	{
		condition_count++;
		querystring = "sector="+$.trim($("#id_sector").val());
	}
	//if($.trim($("#id_village").val())!="")
	//{
	//	condition_count++;
	//	if(condition_count>1){querystring=querystring+"&"}
	//	querystring = querystring + "village="+$.trim($("#id_village").val());
	//}
	if($.trim($("#id_cell").val())!="")
	{
		condition_count++;
		if(condition_count>1){querystring=querystring+"&"}
		querystring = querystring + "cell="+$.trim($("#id_cell").val());
	}
	if($.trim($("#id_parcel_id").val())!="")
	{
		if(isNaN($.trim($("#id_parcel_id").val())))
		{
			$("#keyword_error").html("Parcel ID is invalid!");
			return "";
		}
		condition_count++;
		if(condition_count>1){querystring=querystring+"&"}
		querystring = querystring + "parcel_id="+$.trim($("#id_parcel_id").val());
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
				//alert(request.responseText);
			}
	});
}


function viewPropertyDetail(plot_id)
{
	querystring = "plot_id="+plot_id;
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



// if the json object data has multiple properties, then a list of properties are display in a table only having plot_id, amount, date, due information.
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
			plot_id = property['plot_id'];
			address = property['parcel_id']+ " "+property['village']+", " + property['cell'] + ", " +property['sector'];
			declareValues = property['declarevalues'];
			propertytaxitems = property['propertytaxitems'];
			if(declareValues.length==0)
			{
				row+=							"<tr>";
				row+=								"<td class='firstcolumn'><a href='/admin/tax/tax/manage_tax/?plot_id="+ plot_id +"'>" + property['upi'] + "</a></td>";
				row+=								"<td class='normal'> N/A</td>";
				row+=								"<td class='normal'> N/A</td>";
				row+=								"<td class='normal'> N/A</td>";									
				row+=							"<tr>";
			}
			else
			{
				declareValue=declareValues[0];
				row+=							"<tr>";
				row+=								"<td class='firstcolumn'><a href='/admin/tax/tax/manage_tax/?plot_id="+ plot_id +"'>" + property['upi'] + "</a></td>";
				row+=								"<td class='normal'> "+declareValue['amount']+"</td>";
				row+=								"<td class='normal'> "+declareValue['datetime']+"</td>";
				row+=								"<td class='normal'> "+ getDueStatus(declareValue['datetime']) +"</td>";
				row+=							"</tr>";		
				
			}

			property_popup_message = "<div>UPI: "+property['upi']+"<br>Address: "+address+"</div>";
			points=property['points'];
			var polygon_points = [];
			
			if(points=='undefined'||points==null)
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
			var feature = new OpenLayers.Feature.Vector(polygon_obj,{});
			if(declareValues.length>0)
			{
				declareValue=declareValues[0];
				status = getDeclareValueStatus(declareValue['datetime']);  
				if(status =="lessthan3")
				{
					feature.style=style_green;	
				}
				if(status == "between34")
				{
					feature.style=style_orange;	
				}
				if(status == "greaterthan4")
				{
					feature.style=style_red;	
				}
				if(status != "greaterthan4"&& status !="between34")
				{
					if(propertytaxitems!=null&&propertytaxitems.length>0)
					{
						propertytaxitem = propertytaxitems[0];
						status = getDeclareValueStatus(propertytaxitem['period_from']);
						if(status =="lessthan1")
						{
							feature.style=style_pink;	
						}
						if(status == "between13")
						{
							feature.style=style_skyblue;	
						}
						if(status == "between34")
						{
							feature.style=style_purple;	
						}
						if(status == "greaterthan4")
						{
							feature.style=style_purple;	
						}
						
					}
					else
					{
						feature.style=style_purple;
					}
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
			propertytaxitems = property['propertytaxitems'];
			property=properties[i];
			plot_id = property['plot_id'];
			address = property['parcel_id']+ " "+property['village']+", " + property['cell'] + ", " +property['sector'];
			row=		"<tr>";
			row+= 			"<td>";
			row+=    			"<table cellpadding='0' cellspacing='0' id='declaree_value'>";
			row+=        			"<tr>";
			row+=          				"<td border='0'>";
			
			// property info box
			
			row+=								"<div class='box'>";
			row+=									"<div class='box_title'>Property info:</div>";
			row+=									"<div class='box_detail'><strong>UPI:</strong> "+property['upi']+"</div>";
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
			
			
			
			
			
			
			
			
			// propertytax history box
			
			row+=								"<div class='box'>";			
			row+=									"<div class='box_title'>Property tax items:</div>";
			row+=									"<div class='transactionhistory_div'>";					
			row+=										"<table id='propertytax_table' cellpadding='0' cellspacing='0'>";
			row+=											"<tr>";
			row+=												"<td class='firstrowfirstcolumn'>Amount</td>";
			row+=												"<td class='firstrow'>Start from</td>";
			row+=												"<td class='firstrow'>End to</td>";
			row+=												"<td class='firstrow'>Is paid</td>";
			row+=											"</tr>";
			if(propertytaxitems==null||propertytaxitems.length==0)
			{
				row+=										"<tr>";
				row+=											"<td colspan='4' class='firstcolumn' align='center'> This property has not paid any propety tax.</td>";
				row+=										"<tr>";
			}
			else
			{
				for(s=0;s<propertytaxitems.length;s++)
				{
					propertytaxitem=propertytaxitems[s];
					row+=									"<tr>";
					row+=										"<td class='firstcolumn'>"+propertytaxitem['currency']+" "+propertytaxitem['amount']+"</td>";
					row+=										"<td class='normal'>"+propertytaxitem['period_from']+"</td>";
					row+=										"<td class='normal'>"+propertytaxitem['period_to']+"</td>";
					row+=										"<td class='normal'>"+propertytaxitem['is_paid']+"</td>";
					row+=									"</tr>";		
				}
			}
			row+=									"</table>";
			row+=								"</div>";
			row+=							"</div>";
			
			
			
			
			// action to generate property tax items
			row+=							"<div>"
			row+=								"<button type='button' id='generatetax" + plot_id + "'>Generate property tax! </button>"
			row+=							"</div>"
			
			
			
			
					
			
			
			row+=						"</td>";
			row+=					"</tr>";
			row+=				"</table>";
			row+=			"</td>";
			row+=		"</tr>";
			
			
			
			
			
			$('#search_declared_values').append(row);
			property_popup_message = "<div>UPI: "+property['upi']+"<br>Address: "+address+"</div>";
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
				status = getDeclareValueStatus(declareValue['datetime']);  
				if(status =="lessthan3")
				{
					feature.style=style_green;	
				}
				if(status == "between34")
				{
					feature.style=style_orange;	
				}
				if(status == "greaterthan4")
				{
					feature.style=style_red;	
				}
				if(status != "greaterthan4"&& status !="between34")
				{
					if(propertytaxitems!=null&&propertytaxitems.length>0)
					{
						propertytaxitem = propertytaxitems[0];
						status = getDeclareValueStatus(propertytaxitem['period_from']);
						if(status =="lessthan1")
						{
							feature.style=style_pink;	
						}
						if(status == "between13")
						{
							feature.style=style_skyblue;	
						}
						if(status == "between34")
						{
							feature.style=style_purple;	
						}
						if(status == "greaterthan4")
						{
							feature.style=style_purple;	
						}
						
					}
					else
					{
						feature.style=style_purple;
					}
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
		    
		    
		   $('button[id^="generatetax"]').click(function(){
				id = $(this).attr('id');
				plot_id = id.replace("generatetax","");
				querystring = "plot_id="+plot_id;
				$.ajax({
					type:"get",
					url: "/admin/ajax/generate_property_tax/",
					data: querystring,
					success:function(data)
					{
						if(data==""){return;}
						else
						{
							var numCols = $('#propertytax_table tr:last td').length;
							if(numCols<=1)
							{
								$("#propertytax_table").find("tr:gt(0)").remove();
							}
							var propertytaxitems = data['propertytaxitems'];
							if(propertytaxitems!=null)
							{
								for(i = 0;i<propertytaxitems.length;i++)
								{
									propertytaxitem = propertytaxitems[i];
									var str="<tr>";
									str+="<td class='firstcolumn'>"+propertytaxitem['currency']+" "+propertytaxitem['amount']+"</td>";
									str+="<td class='normal'>"+propertytaxitem['period_from']+"</td>";
									str+="<td class='normal'>"+propertytaxitem['period_to']+"</td>";
									str+="<td class='normal'>"+propertytaxitem['is_paid']+"</td>";
									str+="</tr>";			
									$('#propertytax_table tr:last').after(str);
								}
							}
						}
					},
					error: function(request)
					{
						//alert(request.responseText);
					}
				});

				return;
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
					//alert(request.responseText);
				}
			});
		}
	});	
	
});


function getDeclareValueStatus(date_var)
{

	// break date_var down to year, month and day
	date_parts=date_var.split('-');
	year = date_parts[0];
	year=parseInt(date_parts[0]);
	
	
	// Stupic javascript parseInt function. Given '09', the function will return 0 instead of 9.
	month = date_parts[1];
	if(month.length>1 && month.charAt(0)=='0')
	{
		month = parseInt(month.charAt(1));
	}
	else
	{			
		month = parseInt(month);
	}
	
	// Stupic javascript parseInt function. Given '09', the function will return 0 instead of 9.
	day = date_parts[2];
	if(day.length>1 && day.charAt(0)=='0')
	{
		day = parseInt(day.charAt(1));
	}
	else
	{			
		day = parseInt(day);
	}
	
	// construct date based on the derived year, month, day
	var date_created = new Date(year, month-1, day);
	var today = new Date();
	days=parseInt((today.getTime()-date_created.getTime())/(1000*60*60*24));
	years = 1.0*days/365;
	if(years<=1){result = "lessthan1"}
	if(years>1&&years<=3){result ="between13";}
	if(years>3&&years<=4){result = "between34";}
	if(years>4){result = "greaterthan4";}
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


