
function check_permissions()
{
	valid = true;	
	$("div[id^='error_message']").html("");
	
	// 
	group_name = $.trim($("#id_group_name").val());
	if(group_name=="")
	{
		$("#error_message").html("Please enter the group name");
		$("#id_group_name").focus();
		return false;	
	}
	else
	{
		if(document.URL.indexOf('change_')==-1)
		{
			$.ajax({
					type:"GET",
					url: "/admin/auth/ajax/check_group_exist/?name="+group_name,
					success:function(data)
					{
						if(data=='YES')
						{
							$("#error_message").html("This group already exists!");
							$("#id_group_name").focus();
							valid = false;
							return false;
						}
					},
					error: function(request)
					{
						//document.write(request.responseText);
						//alert(request.responseText);
					}
				})
		}
	}
	
	$("select[id^=id_province_]").each(function(){
		id = $(this).prop("id");
		id = id.replace("id_province_","");
		
		// check whether an area is selected for this permission
		province = $('#id_province_'+id).val();
		if(province=='')
		{
			$("#error_message_"+id).html("Please select the area where this permission is restricted in.");
			$("#error_message_"+id).parent().siblings("div.box_title").children('span.minimizebox').show();
			$("#error_message_"+id).parent().siblings("div.box_title").children('span.maximizebox').hide();
			$("#error_message_"+id).parent().show();
			$("#error_message_"+id).focus();
			valid=false;
			return false;
		}
		
		/*
		if($("input[name='tax_types_"+id+"[]']:checked").length==0)
		{
			$("#error_message_"+id).html("Please select the tax types allowed by this permission.");
			$("#error_message_"+id).focus();
			valid  = false;
			return false;
		}
		*/
		
		
		// check whether actions are selected for this permission
		if(!$("#id_selected_actions_"+id+" option").length)
		{
			$("#error_message_"+id).html("Please select the actions allowed by this permission.");
			$("#error_message_"+id).parent().siblings("div.box_title").children('span.minimizebox').show();
			$("#error_message_"+id).parent().siblings("div.box_title").children('span.maximizebox').hide();
			$("#error_message_"+id).parent().show();
			$("#error_message_"+id).focus();
			valid = false;
			return false;
		}
	});
	
	if(valid)
	{
		$("select[id^='id_selected_actions_'] option").attr("selected",true);
	}
	
	return valid;
}


function add_permission()
{
	if(!check_permissions())
	{
		return false;
	}
	max_id = 0;
	$("select[id^='id_province_']").each(function(){
		id = $(this).prop('id').replace('id_province_','');
		id = parseInt(id);
		if(id>max_id){max_id=id;}
	});
	max_id = max_id + 1;
	
	str = '<div class="box" style="width:900px;">';
	str+= '    <div class="box_title">';
	str+= '			Permission'; 
	str+= '			<span class="deletebox"></span>';
	str+= '			<span class="minimizebox"></span>';
	str+= '			<span style="display:none;" class="maximizebox"></span>';
	str+= '		</div>';
	str+= '		<div class="content">';
	str+= '			<div>';
	str+= '				<table id="search_table">';
	str+= '					<tr>';
	str+= '						<td width="50">Province: </td>';
	str+= '						<td width="200">';
	str+= '							<div class="selector" id="uniform-id_province_' + max_id + '">';
	str+= '								<span>-----------</span>';
	str+= '								<select style="opacity:0;" name="province_' + max_id + '" id="id_province_' + max_id + '">';
	str+= '									<option value="">----------</option>';
	
	$("#all_provinces option").each(function(){
		str+='<option value="'+ $(this).val() +'">'+ $(this).html() +'</option>';	
	});
	
	str+= '								</select>';
	str+= '							</div>';
	str+= '						</td>';
	str+= '						<td style="padding-left:20px;" width="50">District: </td>';
	str+= '						<td width="200">';
	str+= '							<div class="selector" id="uniform-id_district_' + max_id + '">';
	str+= '								<span>-----------</span>';
	str+= '								<select style="opacity:0" name="district_' + max_id + '" id="id_district_' + max_id + '">';
	str+= '									<option value="">----------</option>';
	str+= '								</select>';
	str+= '							</div>';
	str+= '						</td>';
	str+= '						<td style="padding-left:20px;" width="50">Sector: </td>';
	str+= '						<td width="200">';
	str+= '							<div class="selector" id="uniform-id_sector_' + max_id + '">';
	str+= '								<span>-----------</span>';
	str+= '								<select style="opacity:0" name="sector_' + max_id + '" id="id_sector_' + max_id + '">';
	str+= '									<option value="">----------</option>';
	str+= '								</select>';
	str+= '							</div>';
	str+= '						</td>';
	str+= '					</tr>';
	str+= '				</table>';
	str+= '			</div>';
	
	str+= '			<div style="margin-top:30px; color:#888; font-size:15px; font-style:italic;">Please select tax types allowed by this permission.</div>';
	str+='			<div style="margin-top:10px;">';
	str+='				<ul class="tax_type_list">';
	
	$("#all_taxtypes option").each(function(index){
		str += '			<li style="display:inline-block; float:left;">';
		str += '				<label for="id_tax_types_'+max_id+'_'+index+'" >';
		str += '					<div class="checker" id="uniform-id_tax_types_'+max_id+'_'+index+'" >';
		str += '						<span>';
		str += '							<input type="checkbox" name="tax_types_'+ max_id + '[]" value="'+ $(this).val() +'" id="id_tax_types_'+max_id+'_'+index+'" style="opacity:0;" >';
		str += '						</span>';
		str += '					</div>';
		str += 						$(this).html();
		str += '				</label>';
		str += '			</li>';					
	});
	str+='				<ul>';
	str+='				<div style="clear:both;"></div>';
	str+='			</div>';
	
	
	str+= '			<div style="margin-top:30px; color:#888; font-size:15px; font-style:italic;">Please add the actions allowed by this permission to the right box.</div>';
	str+= '				<div style="margin-top:10px;">';
	str+= '					<table cellpadding="0" cellspacing="0">';
	str+= '						<tr>';
	str+= '							<td>';
	str+= '								<select multiple="multiple" name="actions_' + max_id + '" id="id_actions_' + max_id + '" style="width:250px;" size="10">';
	$("#all_actions option").each(function(){
		str+='<option value="'+ $(this).val() +'">'+ $(this).html() +'</option>';	
	});
	str+= '								</select>';
	str+= '							</td>';		
	str+= '							<td width="80" valign="middle" align="center">';
	str+= '								<div>';
	str+= '									<button id="add_' + max_id + '" type="button" class="btn">&gt;&gt;</button>';
	str+= '								</div>';
	str+= '								<div style="margin-top:30px;">';
	str+= '									<button id="remove_' + max_id + '" type="button" class="btn">&lt;&lt;</button>';
	str+= '								</div>';
	str+= '							</td>';
	str+= '							<td>';
	str+= '								<select multiple="multiple" name="selected_actions_' + max_id + '" id="id_selected_actions_' + max_id + '" style="width:250px;" size="10">';
	str+= '								</select>';
	str+= '							</td>';
	str+= '						</tr>';
	str+= '					</table>';
				
	str+= '				</div>';
	str+= '				<div class="error_message" id="error_message_' + max_id + '"></div>';
	str+= '			</div>';
	str+= '		</div>';
	
	$("#permissions").append(str);
	initialize_events();
}


function initialize_events()
{
	//initialize checkbox
	
	$("input[name^='tax_types_']").change(function(){
		if(this.checked)
		{
			$(this).parent().removeClass('checked');
			$(this).parent().addClass('checked');
		}
		else
		{
			$(this).parent().removeClass('checked');
		}
	});
	
	// collapse permission box
	$("span.minimizebox").click(function(){
		$(this).parent().siblings('div.content').hide();
		$(this).hide();
		$(this).siblings('span.maximizebox').show();
	});
	
	
	// expand permission box
	$("span.maximizebox").click(function(){
		$(this).parent().siblings('div.content').show();
		$(this).hide();
		$(this).siblings('span.minimizebox').show();
	});
	
	// delete permission
	$("span.deletebox").click(function(){
		$(this).parent().parent().remove();
	});
	
	$("button[id^='add_']").click(function(){
		id = $(this).prop('id');
		id = id.replace('add_','');
		
		original_options = $("#id_actions_"+id+" option:selected");
		if(original_options.length > 0)
		{
			for(i=0;i<original_options.length;i++)
			{
				value = original_options[i].value;
				$("#id_actions_"+id+" option[value="+value+"]").remove();
			}
			$("#id_selected_actions_"+id).append($(original_options).clone());
			
			if($('#id_selected_actions_"+id+" option').length>0)
			{
				$('#id_selected_actions_"+id+" option').each(function(){
					$(this).attr("selected",false);
				});
			}
		}
	});
	
	$("button[id^='remove_']").click(function(){
		id = $(this).prop('id');
		id = id.replace('remove_','');
		
		original_options = $("#id_selected_actions_"+id+" option:selected");
		if(original_options.length > 0)
		{
			for(i=0;i<original_options.length;i++)
			{
				value = original_options[i].value;
				$("#id_selected_actions_"+id+" option[value="+value+"]").remove();
			}
			$("#id_actions_"+id).append($(original_options).clone());
			
			if($('#id_actions_"+id+" option').length>0)
			{
				$('#id_actions_"+id+" option').each(function(){
					$(this).attr("selected",false);
				});
			}
		}
	});
	
		
	$("#add_permission").click(function(){
		if(check_permissions())
		{
			add_permission();
		}
	});
	
	$("select[id^='id_province_']").change(function(){
		$(this).siblings('span').html($(this).children('option:selected').html());
	});
	$("select[id^='id_district_']").change(function(){
		$(this).siblings('span').html($(this).children('option:selected').html());
	});
	$("select[id^='id_sector_']").change(function(){
		$(this).siblings('span').html($(this).children('option:selected').html());
	});
	
	
	
	$("select[id^='id_province_']").change(function(){
		id = $(this).prop('id');
		id = id.replace('id_province_','');
		
		$("#id_district_"+id).children("option[value!='']").remove();
		$("#id_district_"+id).siblings("span").html('---------');
		
		$("#id_sector_"+id).children("option[value!='']").remove();
		$("#id_sector_"+id).siblings("span").html('---------');
		
		province_id = $(this).val();
		
		
		$.ajax({
			type:"get",
			url: "/admin/ajax/getObjectsByParentId/?object_type=province&object_id="+province_id,
			success:function(data)
			{
				districts = data['objects'];
				for(i=0; i<districts.length; i++)
				{
					distirct = districts[i];
					$("#id_district_"+id).append('<option value="'+ distirct['key'] +'">'+ distirct['value'] +'</option>');
				}
			},
			error: function(request)
			{
				alert(request.responseText);
			}
		});	
	});
	
	
	
	$("select[id^='id_district_']").change(function(){
		id = $(this).prop('id');
		id = id.replace('id_district_','');
	
		$("#id_sector_"+id).children("option[value!='']").remove();
		$("#id_sector_"+id).siblings("span").html('---------');
		
		district_id = $(this).val();
		
		
		$.ajax({
			type:"get",
			url: "/admin/ajax/getObjectsByParentId/?object_type=district&object_id="+district_id,
			success:function(data)
			{
				sectors = data['objects'];
				for(i=0; i<sectors.length; i++)
				{
					sector = sectors[i];
					$("#id_sector_"+id).append('<option value="'+ sector['key'] +'">'+ sector['value'] +'</option>');
				}
			},
			error: function(request)
			{
				alert(request.responseText);
			}
		});	
	});
}


$(document).ready(function(){
	initialize_events();
});










