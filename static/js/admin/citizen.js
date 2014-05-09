
function check_citizen_registration_form(form)
{
	citizen_id = $.trim(form.citizen_id.value);
	first_name = $.trim(form.first_name.value);
	last_name = $.trim(form.last_name.value);
	
	if(citizen_id==''){
		reset_citizen_registration_form_error_fields();
		$("#citizen_id_error").html('Please enter citizen ID.');
		return false;
	}
	if(first_name==''){
		reset_citizen_registration_form_error_fields();
		$("#first_name_error").html('Please enter name.');
		//$("#first_name_error").html('Please enter first name.');
		return false;		  
	}
	if(last_name==''){
		reset_citizen_registration_form_error_fields();
		$("#last_name_error").html('Please enter last name.');
		return false;		  
	}

	if($("#id_status")&&($("#id_status").val()==''))
	{
		$("#status_error").html("Please select status.");
		return false;
	}
	return true;
}

function reset_citizen_registration_form_error_fields()
{
	$("#first_name_error").html('');
	$("#last_name_error").html('');
	$("#citizen_id_error").html('');
}


function check_citizen_select_or_not(form)
{
	if($.trim(form.keyword.value)=="")
	{
		$("#name_error").html("Please enter citizen's name or ID to search!");
		return false;
	}
	else if($.trim(form.citizen_id.value) == '')
	{
		$("#name_error").html("Please select a citizen from the suggestion list, and then add the citizen if not found!");
		$("#add_citizen_link").show();
		return false;	
	}
	return true;
}

$(function () {
    $("#id_keyword").autocomplete({
        source: "/admin/ajax/search_citizen_clean/",
        minLength: 2,
        select: function (event, ui) {
            $("#id_citizen_id").val(ui.item['id']);
            if ($("#citizen_form").length > 0)
            {
				var action = $("#citizen_form").attr("action");
				$("#citizen_form").attr("action", action + ui.item['id'] + "/");
            }
        }
    });
});