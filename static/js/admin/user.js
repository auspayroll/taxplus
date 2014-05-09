function is_email_exist(url)
{
	var exist = false;
	try{
		$.ajax({
			type:"GET",
			url: url,
			async: false,
			success:function(data)
			{
				if(data=='YES')
				{
					$("#email_error").html("This email already exists!");
					$("#id_email").focus();
					exist = true;
				}
			},
			error: function(request)
			{
				//document.write(request.responseText);
				//alert(request.responseText);
			}
		})
	}catch(e){}
	finally{
		return exist;
	}
}



function validate_user_info()
{
	valid = true;

	// reset error fields
	$("#username_error").html('');
	$("#firstname_error").html('');
	$("#lastname_error").html('');
	$("#email_error").html('');
	$("#contactnumber_error").html('');
	$("#password_error").html('');
	$("#confirm_password_error").html('');
					
	// validate form fields
	
	firstname=$.trim($("#id_firstname").val());
	if(firstname==''){
		$("#firstname_error").html('Please enter first name.');
		$("#id_firstname").focus();
		return false;		  
	}
	lastname=$.trim($("#id_lastname").val());
	if(lastname==''){
		$("#lastname_error").html('Please enter last name.');
		$("#id_lastname").focus();user_id
		return false;
	}
	email=$.trim($("#id_email").val());
	if(email==''){
		$("#email_error").html('Please enter email.');none
		$("#id_email").focus();
		return false;	  
	}
	password=$.trim($("#id_password").val());
	if(password==''){
		$("#password_error").html('Please enter password.');
		$("#id_password").focus();
		return false;  
	}
	
	if($("input#id_confirm_password").length > 0)
	{
		confirm_password=$.trim($("#id_confirm_password").val());
		if(confirm_password==''){
			$("#confirm_password_error").html('Please confirm password.');
			$("#id_confirm_password").focus();
			return false;	  
		}
		else
		{
			if(confirm_password!=password)
			{
				$("#confirm_password_error").html('Password is not consistent.');
				$("#id_confirm_password").focus();
				return false;	
			}
		}		
	}
	url = "/admin/auth/ajax/check_user_email_exist/?email="+email;
	if($("input#id_user_id").length>0)
	{
		user_id = $("#id_user_id").val();
		url = url + "&user_id=" +user_id; 
	}
	if(is_email_exist(url))
	{
		return false;
	}
	else
	{
		return true;
	}
}







function check_permissions()
{
	valid = true;
	if(validate_user_info())
	{
		// Validate permissions ...
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
				valid = false;
				return false;
			}
			
			/*
			if($("input[name='tax_types_"+id+"[]']:checked").length==0)
			{
				$("#error_message_"+id).html("Please select the tax types allowed by this permission.");
				$("#error_message_"+id).focus();
				valid = false;
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
	else
	{
		return false;
	}
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









































function check_user_change_form(form)
{

	firstname=$.trim(form.firstname.value);
	lastname=$.trim(form.lastname.value);
	email=$.trim(form.email.value);
	//password=$.trim(form.password.value);

	if(firstname==''){
		reset_user_registration_form_error_fields();
		$("#firstname_error").html('Please enter first name');
		return false;		  
	}
	if(lastname==''){
		reset_user_registration_form_error_fields();
		$("#lastname_error").html('Please enter last name');
		return false;		  
	}
	if(email==''){
		reset_user_registration_form_error_fields();
		$("#email_error").html('Please enter email');
		return false;		  
	}
	//if(password==''){
	//	reset_user_registration_form_error_fields();
	//	$("#password_error").html('Please enter password');
	//	return false;		  
	//}
}






function selectUserRepeater()
{
	$('li[id^="li_user_"]').mouseover(function(){
		$(this).css("cursor","pointer");
		$(this).css("background-color","red");
	});
	$('li[id^="li_user_"]').mouseleave(function(){
			$(this).css("background-color","#cccccc");
		});
	
	$('li[id^="li_user_"]').click(function(){
		$('#id_keyword').val($(this).html());
		$('#id_user_id').val($(this).attr("userid"));
	});
}

function selectUser()
{
	
	$(document).ready(function(){
		$('#matched_users_list').mouseleave(function(){
			$(this).fadeOut();
		});
		
		
		$('#id_keyword').click(function(){
			if($.trim($(this).val())=='')
			{
				$('#matched_users_list').html('');
				$('#matched_users_list').hide();
				return;
			}
			else
			{
				kw = $.trim($(this).val());
				querystring = "keyword="+kw;
				$.ajax(
					{
						type:"get",
						url: "/admin/ajax/search_user/",
						data: querystring,
						success:function(data)
						{
							if(data==""){return;}
							else
							{
								str="<ul>";
								users=data.split('#');
								for(i=0;i<users.length;i++)
								{
									user=users[i];
									user_parts=user.split(':')
									userid=user_parts[0];
									username=user_parts[1];
									str=str+"<li id='li_user_"+i+"' userid="+ userid + ">"+ username+"</li>";										
								}
								str=str+"</ul>";
								$('#matched_users_list').html(str);
								$('#matched_users_list').show();
								selectUserRepeater();
							}
						},
						error: function(request)
						{
							//alert(request.responseText);
						}
					}
				)
			}
		});
		
		
		$('#id_keyword').keyup(function(){
			if($.trim($(this).val())=='')
			{
				$('#matched_users_list').html('');
				$('#matched_users_list').hide();
				return;
			}
			else
			{
				kw = $.trim($(this).val());
				querystring = "keyword="+kw;
				$.ajax(
					{
						type:"get",
						url: "/admin/ajax/search_user/",
						data: querystring,
						success:function(data)
						{
							if(data==""){return;}
							else
							{
								str="<ul>";
								users=data.split('#');
								for(i=0;i<users.length;i++)
								{
									user=users[i];
									user_parts=user.split(':')
									userid=user_parts[0];
									username=user_parts[1];
									str=str+"<li id='li_user_"+i+"' userid="+ userid + ">"+ username+"</li>";										
								}
								str=str+"</ul>";
								$('#matched_users_list').html(str);
								$('#matched_users_list').show();
								selectUserRepeater();
							}
						},
						error: function(request)
						{
							//alert(request.responseText);
						}
					}
				)
			}
		});
		
	});
}

