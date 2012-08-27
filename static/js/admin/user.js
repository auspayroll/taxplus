function check_user_change_form()
{
	firstname=$.trim($("#id_firstname").val());
	lastname=$.trim($("#id_lastname").val());
	email=$.trim($("#id_email").val());
	password=$.trim($("#id_password").val());
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
	if(password==''){
		reset_user_registration_form_error_fields();
		$("#password_error").html('Please enter password');
		return false;		  
	}
}


function check_user_registration_form()
{
	//username=$.trim($("#id_username").val());
	firstname=$.trim($("#id_firstname").val());
	lastname=$.trim($("#id_lastname").val());
	email=$.trim($("#id_email").val());
	//password1=$.trim($("#id_password1").val());
	//password2=$.trim($("#id_password2").val());
	
	//if(username==''){
	//	reset_user_registration_form_error_fields();
	//	$("#username_error").html('Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.');
	//	return false;		  
	//}
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
	
	//if(password1==''){
	///	reset_user_registration_form_error_fields();
	//	$("#password1_error").html('Please enter password');
	//	return false;		  
	//}
	//if(password2==''){
	//	reset_user_registration_form_error_fields();
	//	$("#password2_error").html('Please confirm password');
	//	return false;		  
	//}
	//if(password2!=password1){
	//	reset_user_registration_form_error_fields();
	//	$("#password2_error").html("The two password fields didn't match.");
	//	return false;		  
	//}
	
	
	return true;
}

function reset_user_registration_form_error_fields()
{
	//$("#username_error").html('');
	$("#firstname_error").html('');
	$("#lastname_error").html('');
	$("#email_error").html('');
	$("#contactnumber_error").html('');
	if($("#password_error")!=null)
	{
		$("#password_error").html('');
	}
	//$("#password1_error").html('');
	//$("#password2_error").html('');
}

function check_user_select_or_not()
{
	if ($.trim($("input[name='user_id']").val())=="") {
	   $("#name_error").html('No user is selected.');
	   return false;
	}
	else {
	  return true;
	}
}



function changeUser()
{
	if($("#id_permissions_selected option")!=null)
	{
		$("#id_permissions_selected option").each(function(){
			$(this).remove();
		})
	}
	if($('#id_permissions option').length>0)
	{
		options = $('#id_permissions option');
		$("#id_permissions_selected").append($(options).clone());
	}
	if($("#id_groups_selected option")!=null)
	{
		$("#id_groups_selected option").each(function(){
			$(this).remove();
		})
	}
	if($('#id_groups option').length>0)
	{
		options = $('#id_groups option');
		$("#id_groups_selected").append($(options).clone());
	}
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
							alert(request.responseText);
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
							alert(request.responseText);
						}
					}
				)
			}
		});
		
	});
}








