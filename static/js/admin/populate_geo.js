$(document).ready(function(){

	var init_district_val = $("#search_table #id_district").val();

	var init_sector_val = $("#search_table #id_sector").val();

	var init_cell_val = $("#search_table #id_cell").val();	

	var init_village_val = $("#search_table #id_village").val();


    district_sector_disabled = false;

    if($('#id_district')!=null && $('#id_sector')!=null && $("#id_sector").prop('disabled') && $("#id_district").prop('disabled'))
    {
        district_sector_disabled = true;
    }

    if($('#id_district')!=null && $('#id_sector')!=null)
    {
        $("#id_sector").prop('disabled','disabled');
    }

    if($('#id_sector')!=null && $('#id_cell')!=null)
    {
        $("#id_cell").prop('disabled','disabled');
    }

    if($('#id_cell')!=null && $('#id_village')!=null)
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
		var cell_val = $("#search_table #id_cell").val();
		$.ajax({
			type:"get",
			url: "/admin/ajax/getObjectsByParentId/?object_type=cell&object_id="+cell_val,
			success:function(data)
			{
				villages = data['objects'];
				for(i=0; i<villages.length; i++)
				{
					village = villages[i];
					if(parseInt(init_village_val) == parseInt(village['key'])){
						$("#search_table #id_village").append('<option selected="selected" value="'+ village['key'] +'">'+ village['value'] +'</option>');
					}
					else{
						$("#search_table #id_village").append('<option value="'+ village['key'] +'">'+ village['value'] +'</option>');
					}
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
		var sector_val = $("#search_table #id_sector").val();
		$("#search_table #id_cell").children("option[value!='']").remove();
		$("#search_table #id_cell").siblings("span").html('---------');
		$("#search_table #id_village").children("option[value!='']").remove();
		$("#search_table #id_village").siblings("span").html('---------');
		$.ajax({
			type:"get",
			url: "/admin/ajax/getObjectsByParentId/?object_type=sector&object_id="+sector_val,
			success:function(data)
			{
				cells = data['objects'];
				for(i=0; i<cells.length; i++)
				{
					cell = cells[i];
					if(init_cell_val == cell['key']){
						$("#search_table #id_cell").append('<option selected="selected" value="'+ cell['key'] +'">'+ cell['value'] +'</option>');
					}
					else{
						$("#search_table #id_cell").append('<option value="'+ cell['key'] +'">'+ cell['value'] +'</option>');	
					}
					
				}
				$("#search_table #id_cell").trigger("chosen:updated");
				var cell_val = $("#search_table #id_cell").val();
				if(cell_val != ''){
					$("#search_table #id_cell").change();
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
		var district_val = $("#search_table #id_district").val();
		$("#search_table #id_sector").children("option[value!='']").remove();
		$("#search_table #id_sector").siblings("span").html('---------');
		$("#search_table #id_cell").children("option[value!='']").remove();
		$("#search_table #id_cell").siblings("span").html('---------');
		$("#search_table #id_village").children("option[value!='']").remove();
		$("#search_table #id_village").siblings("span").html('---------');

		$.ajax({
			type:"get",
			url: "/admin/ajax/getObjectsByParentId/?object_type=district&object_id="+district_val,
			success:function(data)
			{
				sectors = data['objects'];
				for(i=0; i<sectors.length; i++)
				{
					sector = sectors[i];
					if(init_sector_val == sector['key']){
						$("#search_table #id_sector").append('<option selected="selected" value="'+ sector['key'] +'">'+ sector['value'] +'</option>');
					}
					else{
						$("#search_table #id_sector").append('<option value="'+ sector['key'] +'">'+ sector['value'] +'</option>');
					}
				}
				$("#search_table #id_sector").trigger("chosen:updated");
				var sector_val = $("#search_table #id_sector").val();
				if(sector_val != ''){
					$("#search_table #id_sector").change();
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


	if(init_district_val != ''){

		/*
		$("#search_table #id_sector").change(function(){
			$("#search_table #id_cell").change();
		});

		$("#search_table #id_district").change(function(){
			$("#search_table #id_sector").change();
		});
		*/
		$("#search_table #id_district").change();
	}	

	/*
	if(sector_val != ''){
		$("#search_table #id_sector").change();
	}	

	if(cell_val != ''){
		$("#search_table #id_cell").change();
	}	
	*/
	
	

	
	
	
	
	
	
	
	// the following source code are used in user and group pages
	
});