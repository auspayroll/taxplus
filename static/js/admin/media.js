function add_tag(index) {
    var default_tag = $("#media_row_" + index + " #default_tag");
    var tags = $("#media_row_" + index + " .tags").val();
    var tag = "";

    if (default_tag.css('display') != 'none') {
        tag = default_tag.val().replace("|", "") + "|";
        if (tags.indexOf(tag) === -1) {
            tags += tag;
        }
    }
    else {
        if ($("#media_row_" + index + " #custom_tag").val() != "") {
            tag = $("#media_row_" + index + " #custom_tag").val().replace("|", "") + "|";
            if (tags.indexOf(tag) === -1) {
                tags += tag;
            }
        }
    }

    $("#media_row_" + index + " .tags").val(tags);
    tags = tags.replace(/\|/g, " | ");
    $("#media_row_" + index + " #tags_label").html(tags);
}

function toggle_tag(index) {
    $("#media_row_" + index + " #default_tag").toggle();
    $("#media_row_" + index + " #custom_tag").toggle();
    var label = "add custom tag";
    if ($("#media_row_" + index + " default_tag").css("display") == "none") {
        label = "add default tag";
    }
    $("#media_row_" + index + " toggle_tag_type_link").html(label);
    return false;
}

function clear_ass() {
    $("#citizen").html('N/A');
    $("#id_citizen_id").val('');
    $("#business").html('N/A');
    $("#id_business_id").val('');
    $("#property").html('N/A');
    $("#id_property_id").val('');
    $("#citizen_search").val('');
    $("#business_search").val('');
    $("#property_search").val('');
}

$(function () {
    $("#citizen_search").autocomplete({
        source: "/admin/ajax/search_citizen_clean/",
        minLength: 2,
        select: function (event, ui) {
            $("#citizen").html(ui.item['value']);
            $("#id_citizen_id").val(ui.item['id']);
        }
    });

    $("#business_search").autocomplete({
        source: "/admin/ajax/search_business/",
        minLength: 2,
        select: function (event, ui) {
            $("#business").html(ui.item['value']);
            $("#id_business_id").val(ui.item['id']);
        }
    });

    $("#property_search").autocomplete({
        source: "/admin/ajax/search_property_by_upi/",
        minLength: 2,
        select: function (event, ui) {
            $("#property").html(ui.item['value']);
            $("#id_property_id").val(ui.item['id']);
        }
    });

    $("#media_upload_form").submit(function () {
        if ($("#media_url").val() == "") {
            $("#error").html("Please select a file to upload");
            $("#error").show();
            return false;
        }
    });


});