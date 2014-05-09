$(document).ready(function(){
    district_sector_disabled = false;
    if($('#id_district')!=null&&$('#id_sector')!=null&&$("#id_sector").prop('disabled')&&$("#id_district").prop('disabled'))
    {

        district_sector_disabled = true;
    }
    if($('#id_district')!=null&&$('#id_sector')!=null)
    {
        $("#id_sector").prop('disabled','disabled');
    }
    if($('#id_sector')!=null&&$('#id_cell')!=null)
    {
        $("#id_cell").prop('disabled','disabled');
    }
    if($('#id_cell')!=null&&$('#id_village')!=null)
    {
         $("#id_village").prop('disabled','disabled');
    }

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
                if(district_sector_disabled)
                {
                    $("#search_table #id_sector").prop('disabled','disabled');
                }
                else
                {
                    $("#search_table #id_sector").prop('disabled',false);
                }
                $("#search_table #id_cell").prop('disabled','disabled');
                $("#search_table #id_village").prop('disabled','disabled');
                $('#district_refresh').hide();
                $('#sector_refresh').hide();
                $('#cell_refresh').hide();
			},
			error: function(request)
			{
                $("#search_table #id_sector").prop('disabled','disabled');
                $("#search_table #id_cell").prop('disabled','disabled');
                $("#search_table #id_village").prop('disabled','disabled');
                $('#district_refresh').show();
                $('#sector_refresh').hide();
                $('#cell_refresh').hide();
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
                if(district_sector_disabled)
                {
                    $("#search_table #id_sector").prop('disabled','disabled');
                }
                else
                {
                    $("#search_table #id_sector").prop('disabled',false);
                }
                $("#search_table #id_cell").prop('disabled',false);
                $("#search_table #id_village").prop('disabled','disabled');
                $('#district_refresh').hide();
                $('#sector_refresh').hide();
                $('#cell_refresh').hide();
			},
			error: function(request)
			{
                if(district_sector_disabled)
                {
                    $("#search_table #id_sector").prop('disabled','disabled');
                }
                else
                {
                    $("#search_table #id_sector").prop('disabled',false);
                }
                $("#search_table #id_cell").prop('disabled','disabled');
                $("#search_table #id_village").prop('disabled','disabled');
                $('#district_refresh').hide();
                $('#sector_refresh').show();
                $('#cell_refresh').hide();
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

                if(district_sector_disabled)
                {
                    $("#search_table #id_sector").prop('disabled','disabled');
                }
                else
                {
                    $("#search_table #id_sector").prop('disabled',false);
                }
                $("#search_table #id_cell").prop('disabled',false);
                $("#search_table #id_village").prop('disabled',false);
                $('#district_refresh').hide();
                $('#sector_refresh').hide();
                $('#cell_refresh').hide();
			},
			error: function(request)
			{
                if(district_sector_disabled)
                {
                    $("#search_table #id_sector").prop('disabled','disabled');
                }
                else
                {
                    $("#search_table #id_sector").prop('disabled',false);
                }
                $("#search_table #id_cell").prop('disabled',false);
                $("#search_table #id_village").prop('disabled','disabled');
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
                if(district_sector_disabled)
                {
                    $("#search_table #id_sector").prop('disabled','disabled');
                }
                else
                {
                    $("#search_table #id_sector").prop('disabled',false);
                }
                $("#search_table #id_cell").prop('disabled',false);
                $("#search_table #id_village").prop('disabled','disabled');
                $('#district_refresh').hide();
                $('#sector_refresh').hide();
                $('#cell_refresh').hide();
			},
			error: function(request)
			{
                if(district_sector_disabled)
                {
                    $("#search_table #id_sector").prop('disabled','disabled');
                }
                else
                {
                    $("#search_table #id_sector").prop('disabled',false);
                }
                $("#search_table #id_cell").prop('disabled','disabled');
                $("#search_table #id_village").prop('disabled','disabled');
                $('#district_refresh').hide();
                $('#sector_refresh').show();
                $('#cell_refresh').hide();
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
                if(district_sector_disabled)
                {
                    $("#search_table #id_sector").prop('disabled','disabled');
                }
                else
                {
                    $("#search_table #id_sector").prop('disabled',false);
                }
                $("#search_table #id_cell").prop('disabled','disabled');
                $("#search_table #id_village").prop('disabled','disabled');
                $('#district_refresh').hide();
                $('#sector_refresh').hide();
                $('#cell_refresh').hide();
			},
			error: function(request)
			{
                $("#search_table #id_sector").prop('disabled','disabled');
                $("#search_table #id_cell").prop('disabled','disabled');
                $("#search_table #id_village").prop('disabled','disabled');
                $('#district_refresh').show();
                $('#sector_refresh').hide();
                $('#cell_refresh').hide();
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
                $("#search_table #id_pay_sector").prop('disabled',false);
                $("#search_table #id_pay_cell").prop('disabled','disabled');
                $('#district_refresh').hide();
                $('#sector_refresh').hide();
			},
			error: function(request)
			{
                $("#search_table #id_pay_sector").prop('disabled','disabled');
                $("#search_table #id_pay_cell").prop('disabled','disabled');
                $('#district_refresh').show();
                $('#sector_refresh').hide();
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
                $("#search_table #id_pay_sector").prop('disabled',false);
                $("#search_table #id_pay_cell").prop('disabled',false);
                $('#district_refresh').hide();
                $('#sector_refresh').hide();
			},
			error: function(request)
			{
                $("#search_table #id_pay_sector").prop('disabled',false);
                $("#search_table #id_pay_cell").prop('disabled','disabled');
                $('#district_refresh').hide();
                $('#sector_refresh').show();
			}
		});	
	});
	
	

	
	
	
	
	
	
	
	// the following source code are used in user and group pages
	
});