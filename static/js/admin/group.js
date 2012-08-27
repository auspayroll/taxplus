function check_group_registration_form()
{
	name=$.trim($("#id_name").val());
	if(name == '')
	{
		$('#name_error').html('Please enter group name');
		return false;
	}
	if($("#id_permissions_selected option")!=null)
	{
		$("#id_permissions_selected option").each(function(){
			$(this).attr("selected","selected");
		})
	}
	return true;
}


function check_group_select_or_not()
{
	if (!$("input[name='group_id']:checked").val()) {
	   $("#name_error").html('No group is selected.');
	   return false;
	}
	else {
	  return true;
	}
}


function addGroup()
{
	if($("#id_permissions_selected option")!=null)
	{
		$("#id_permissions_selected option").each(function(){
			$(this).remove();
		})
	}
}


function changeGroup()
{
	if($("#id_permissions_all option")!=null&&$("#id_permissions option")!=null)
	{
		addGroup();
		original_options = $("#id_permissions option:selected");
		for(i=0;i<original_options.length;i++)
		{
			value = original_options[i].value;
			if($("#id_permissions_all option[value="+value+"]")!=null)
			{
				$("#id_permissions_all option[value="+value+"]").remove(); 
			}			
		}
		$('#id_permissions_selected').append($(original_options).clone());
		
		if($('#id_permissions_selected option').length>0)
		{
			$('#id_permissions_selected option').each(function(){
				$(this).attr("selected",false);
			});
		}
	}
}


function check_group_change_form()
{
	name=$.trim($("#id_name").val());
	if(name == '')
	{
		$('#name_error').html('Please enter group name');
		return false;
	}
	if($("#id_permissions_selected option")!=null)
	{
		$("#id_permissions_selected option").each(function(){
			$(this).attr("selected","selected");
		})
	}
	return true;
}






