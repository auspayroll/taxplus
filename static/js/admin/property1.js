var lon=30.05979;
var lat=-1.94479;
var zoom = 18;
var polygon;
var renderer;
var map;
var polygonLayer;
var newLayer;
var apiKey = "AqTGBsziZHIJYYxgivLBf0hVdrAk9mWO5cQcb8Yux8sW5M8c8opEC2lZqKR1ZZXf";
 	
//Initialise the 'map' object
function init() 
{
    if ($("#map").length > 0) {
        loadMap();

        var points = $.trim($("#points").html());
        if (points == null || points == '' || points == 'undefined' || points == '[]') {
            return;
        }
        points = "(" + points + ")";
        points = eval(points);
        var polygon_points = [];
        //if(polygon_points.length==0)
        //{return;}

        for (j = 0; j < points.length; j++) {
            point = points[j];
            x = point['x'];
            y = point['y'];
            p = new OpenLayers.Geometry.Point(x, y);
            polygon_points.push(p);
        }
        var ring = new OpenLayers.Geometry.LinearRing(polygon_points);
        var polygon_obj = new OpenLayers.Geometry.Polygon([ring]);
        var feature = new OpenLayers.Feature.Vector(polygon_obj, {});
        var label = $("div#displaytext").html();
        feature.style = { label: label, fillColor: color_house, fillOpacity: 0.2, strokeColor: color_house, strokeWidth: 1, fontColor: color_house, };
        polygonLayer.addFeatures([feature]);
        var bounds = polygonLayer.getDataExtent();
        map.zoomToExtent(bounds);
    }
}

$(document).ready(function(){	
	$('li[id^="li_"]').mouseover(function(){
		$(this).css("cursor","pointer");
		$(this).css("background-color","red");
	});
	$('li[id^="li_"]').mouseleave(function(){
		$(this).css("background-color","#cccccc");
	});

	$("#leasing_checkbox").click(function () {
	    var status = 0;
	    if ($("#leasing_checkbox:checked").is(':checked'))
	    {
	        status = 1;
	    }

	    $.get('/admin/property/property/toggle_lease/' + $("#property_id").val() + "/", { "status": status}, function (data) {
	        
	    });
	});

	$("#land_lease_checkbox").click(function () {
	    var status = 0;
	    if ($("#land_lease_checkbox:checked").is(':checked')) {
	        status = 1;
	    }

	    $.get('/admin/property/property/toggle_landlease/' + $("#property_id").val() + "/", { "status": status }, function (data) {

	    });
	});

	$("#land_use_type_select").change(function () {
	    if ($(this).val() != '') {
	        $.get('/admin/property/property/update_landusetype/' + $("#property_id").val() + "/", { "land_use_type": $(this).val() }, function (data) {

	        });
	    }
	});

	$("#land_lease_type_select").change(function () {
	    if ($(this).val() != '') {
	        $.get('/admin/property/property/update_landleasetype/' + $("#property_id").val() + "/", { "land_lease_type": $(this).val() }, function (data) {

	        });

	        //update size type depend on land use type
	        if ($(this).val() != 'Agriculture') {
	            $("#size_type").html("M&sup2;");
	        }
	        else {
	            $("#size_type").html("Hectares");
	        }
	        $('#property_size').val('');
	    }
	});
	

	if ($("#property_size").length > 0) {
	    $("#property_size").keyup($.debounce(1000, function () {
	        if ($(this).val() != '') {
                property_size = $(this).val();
                if(isNaN(property_size))
                {
                    $("#size_error").html('Invalid size.');
                    return;
                }
                else{

                    $("#size_error").html('');
                    $.get('/admin/property/property/update_size/' + $("#property_id").val() + "/", { "size": $(this).val() }, function (data) {
	                });
                }
	        }
	    }));
	}
	
	$("#citizen_label").autocomplete({
		source: "/admin/ajax/search_citizen_clean/",
		minLength: 2,
		select: function (event, ui) {
			$("#citizen_id").val(ui.item['id']);
		}
	});
	

    //append setup payment installments dialog
	$('<div id="dialog"></div>').appendTo('body')
      .html('<div>Please ensure Documents for Approval of Payment in Installments have been provided and validated. Those support documents also need to be uploaded later<br/>Choose "Yes" to set up 4 Installments Payment Plan.</div>')
      .dialog({
          autoOpen: false,
          title: "Set up Payment by Installments",
          modal: true,
          buttons: {
              "Yes": function () {
                  window.location = $("#installment_payment_link").val();
              },
              "No": function () {
                  $(this).dialog("close");
              }
          }
      });

});


function setup_payment_installments()
{
    $("#dialog").dialog("open");
}

// property declaration section (begin)
function declare_value()
{
    amount = $.trim($("#declare_amount").val());
    //strip of any , 
    amount = amount.replace(/,/g, '');
	citizen_id = $.trim($("#citizen_id").val());

	if( amount=="" || isNaN(amount) )
	{
		$("#declare_amount_error").html("Please enter a valid amount!");
		$("#declare_amount_error").show();
		$("#declare_amount").focus();
		return false;
	}
	else if( citizen_id=="")
	{
		$("#declare_amount_error").html("Please enter citizen name or citizen ID!");
		$("#declare_amount_error").show();
		$("#citizen_label").focus();
		return false;
	}
	return true;
}
// property declaration section (end)


