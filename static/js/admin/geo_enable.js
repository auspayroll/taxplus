$(document).ready(function(){
    district_sector_disabled = false;
    $("#district_refresh").click(function(){
        district_id = $("#search_table #id_district").val();
		$.ajax({
			type:"get",
			url: "/admin/ajax/getObjectsByParentId/?object_type=district&object_id="+district_id,
			success:function(data)
			{
				sectors = data['objects'];
				for(i=0; i<sectors.length; i++)
				{
					sector = sectors[i];
					$("#search_table #id_sector").append('<option value="'+ sector['key'] +'">'+ sector['value'] +'</option>');
				}
			},
			error: function(request)
			{

				//alert(request.responseText);
			}
		});
    });


    $("#district_refresh").click(function(){
        sector_id = $("#search_table #id_sector").val();
		$.ajax({
			type:"get",
			url: "/admin/ajax/getObjectsByParentId/?object_type=sector&object_id="+sector_id,
			success:function(data)
			{
				cells = data['objects'];
				for(i=0; i<cells.length; i++)
				{
					cell = cells[i];
					$("#search_table #id_cell").append('<option value="'+ cell['key'] +'">'+ cell['value'] +'</option>');
				}

			},
			error: function(request)
			{
				//alert(request.responseText);
			}
		});
    });




	$("#search_table #id_cell").change(function(){
		$("#search_table #id_village").children("option[value!='']").remove();
		$("#search_table #id_village").siblings("span").html('---------');
		
		cell_id = $("#search_table #id_cell").val();
		
		$.ajax({
			type:"get",
			url: "/admin/ajax/getObjectsByParentId/?object_type=cell&object_id="+cell_id,
			success:function(data)
			{
				villages = data['objects'];
				for(i=0; i<villages.length; i++)
				{
					village = villages[i];
					$("#search_table #id_village").append('<option value="'+ village['key'] +'">'+ village['value'] +'</option>');
				}


                $('#district_refresh').hide();
                $('#sector_refresh').hide();
                $('#cell_refresh').hide();
			},
			error: function(request)
			{

                $('#district_refresh').hide();
                $('#sector_refresh').hide();
                $('#cell_refresh').show();
				//alert(request.responseText);
			}
		});	
	});



	$("#search_table #id_sector").change(function(){
		$("#search_table #id_cell").children("option[value!='']").remove();
		$("#search_table #id_cell").siblings("span").html('---------');
		$("#search_table #id_village").children("option[value!='']").remove();
		$("#search_table #id_village").siblings("span").html('---------');
		sector_id = $("#search_table #id_sector").val();

		$.ajax({
			type:"get",
			url: "/admin/ajax/getObjectsByParentId/?object_type=sector&object_id="+sector_id,
			success:function(data)
			{
				cells = data['objects'];
				for(i=0; i<cells.length; i++)
				{
					cell = cells[i];
					$("#search_table #id_cell").append('<option value="'+ cell['key'] +'">'+ cell['value'] +'</option>');
				}

			},
			error: function(request)
			{

				//alert(request.responseText);
			}
		});	
	});
	
	
	$("#search_table #id_district").change(function(){
		$("#search_table #id_sector").children("option[value!='']").remove();
		$("#search_table #id_sector").siblings("span").html('---------');
		$("#search_table #id_cell").children("option[value!='']").remove();
		$("#search_table #id_cell").siblings("span").html('---------');
		$("#search_table #id_village").children("option[value!='']").remove();
		$("#search_table #id_village").siblings("span").html('---------');
		
		district_id = $("#search_table #id_district").val();
		
		$.ajax({
			type:"get",
			url: "/admin/ajax/getObjectsByParentId/?object_type=district&object_id="+district_id,
			success:function(data)
			{
				sectors = data['objects'];
				for(i=0; i<sectors.length; i++)
				{
					sector = sectors[i];
					$("#search_table #id_sector").append('<option value="'+ sector['key'] +'">'+ sector['value'] +'</option>');
				}

                $('#district_refresh').hide();
                $('#sector_refresh').hide();
                $('#cell_refresh').hide();
			},
			error: function(request)
			{
				//alert(request.responseText);
			}
		});	
	});




    $("#search_table #id_pay_district").change(function(){
		$("#search_table #id_pay_sector").children("option[value!='']").remove();
		$("#search_table #id_pay_sector").siblings("span").html('---------');
		$("#search_table #id_pay_cell").children("option[value!='']").remove();
		$("#search_table #id_pay_cell").siblings("span").html('---------');

		district_id = $("#search_table #id_pay_district").val();

		$.ajax({
			type:"get",
			url: "/admin/ajax/getObjectsByParentId/?object_type=district&object_id="+district_id,
			success:function(data)
			{
				sectors = data['objects'];
				for(i=0; i<sectors.length; i++)
				{
					sector = sectors[i];
					$("#search_table #id_pay_sector").append('<option value="'+ sector['key'] +'">'+ sector['value'] +'</option>');
				}

			},
			error: function(request)
			{
			}
		});
	});

	//// The following code is for verify target page
	$("#search_table #id_pay_sector").change(function(){
		$("#search_table #id_pay_cell").children("option[value!='']").remove();
		$("#search_table #id_pay_cell").siblings("span").html('---------');
	
		sector_id = $("#search_table #id_pay_sector").val();
		
		$.ajax({
			type:"get",
			url: "/admin/ajax/getObjectsByParentId/?object_type=sector&object_id="+sector_id,
			success:function(data)
			{
				cells = data['objects'];
				for(i=0; i<cells.length; i++)
				{
					cell = cells[i];
					$("#search_table #id_pay_cell").append('<option value="'+ cell['key'] +'">'+ cell['value'] +'</option>');
				}

			},
			error: function(request)
			{

			}
		});	
	});
	
	

	
	
	
	
	
	
	
	// the following source code are used in user and group pages
	
});