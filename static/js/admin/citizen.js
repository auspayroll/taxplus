
function check_citizen_registration_form()
{
	firstname=$.trim($("#id_firstname").val());
	lastname=$.trim($("#id_lastname").val());
	citizenid=$.trim($("#id_citizenid").val());

	if(firstname==''){
		reset_citizen_registration_form_error_fields();
		$("#firstname_error").html('Please enter first name.');
		return false;		  
	}
	if(lastname==''){
		reset_citizen_registration_form_error_fields();
		$("#lastname_error").html('Please enter last name.');
		return false;		  
	}
	if(citizenid==''){
		reset_citizen_registration_form_error_fields();
		$("#email_error").html('Please enter citizen ID.');
		return false;		  
	}
	return true;
}

function reset_citizen_registration_form_error_fields()
{
	$("#firstname_error").html('');
	$("#lastname_error").html('');
	$("#citizen_error").html('');
}


function check_citizen_select_or_not()
{
	if($.trim($('#id_keyword').val())=="")
	{ 
		$("#name_error").html("Citizen's name is not entered!");
		return false;
	}
	else
	{
		len=$("li[id^='li_citizen_']").length;
		if(len==0)
		{
			$("#name_error").html("No citizen found!");
			return false;
		}
		else
		{
			var not_selected = false;
			if($("#id_citizen_id").val()=="")
			{
				not_selected = true;
			}
			if(($("#id_citizen_id").val()!="")&&($("#fullname").html()!=$.trim($("#id_keyword").val())))
			{
				not_selected = true;
			}
			if(not_selected)
			{
				$("#name_error").html("No citizen selected!");
				return false;	
			}
			return true;
		}
	}
}





function selectCitizen()
{
	
	$(document).ready(function(){
		$('#matched_citizens_list').mouseleave(function(){
			$(this).fadeOut();
		});
		
		
		$('#id_keyword').click(function(){
			if($.trim($(this).val())=='')
			{
				$('#matched_citizens_list').html('');
				$('#matched_citizens_list').hide();
				return;
			}
			else
			{
				kw = $.trim($(this).val());
				querystring = "keyword="+kw;
				$.ajax(
					{
						type:"get",
						url: "/admin/ajax/search_citizen/",
						data: querystring,
						success:function(data)
						{
							if(data==""){return;}
							else
							{
								str="<ul>";
								citizens=data.split('#');
								for(i=0;i<citizens.length;i++)
								{
									citizen=citizens[i];
									citizen_parts=citizen.split(':')
									citizenid=citizen_parts[0];
									citizenname=citizen_parts[1];
									str=str+"<li id='li_citizen_"+i+"' citizenid="+ citizenid + ">"+ citizenname+"</li>";										
								}
								str=str+"</ul>";
								$('#matched_citizens_list').html(str);
								$('#matched_citizens_list').show();
								selectCitizenRepeater();
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
				$('#matched_citizens_list').html('');
				$('#matched_citizens_list').hide();
				return;
			}
			else
			{
				kw = $.trim($(this).val());
				querystring = "keyword="+kw;
				$.ajax(
					{
						type:"get",
						url: "/admin/ajax/search_citizen/",
						data: querystring,
						success:function(data)
						{
							if(data==""){return;}
							else
							{
								str="<ul>";
								citizens=data.split('#');
								for(i=0;i<citizens.length;i++)
								{
									citizen=citizens[i];
									citizen_parts=citizen.split(':')
									citizenid=citizen_parts[0];
									citizenname=citizen_parts[1];
									str=str+"<li id='li_citizen_"+i+"' citizenid="+ citizenid + ">"+ citizenname+"</li>";										
								}
								str=str+"</ul>";
								$('#matched_citizens_list').html(str);
								$('#matched_citizens_list').show();
								selectCitizenRepeater();
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



function selectCitizenRepeater()
{
	$('li[id^="li_citizen_"]').mouseover(function(){
		$(this).css("cursor","pointer");
		$(this).css("background-color","red");
	});
	$('li[id^="li_citizen_"]').mouseleave(function(){
			$(this).css("background-color","#cccccc");
		});
	
	$('li[id^="li_citizen_"]').click(function(){
		$('#fullname').html($(this).html());
		$('#id_keyword').val($(this).html());
		$('#id_citizen_id').val($(this).attr("citizenid"));
	});
}


