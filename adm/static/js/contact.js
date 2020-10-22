(function(){
	"use strict";
	var contador = -1;
	
	function toggleContactType(){
		var contact_id_select = this.parentNode.parentNode.parentNode.querySelector("select[name='contact_existing_id']");
		var new_contact_form = this.parentNode.parentNode.parentNode.parentNode.querySelector("div.new-contact-form");

		if(this.value == "new"){
			contact_id_select.disabled=true;
			new_contact_form.style.display = "flex";

			//controla que se seleccione nuevamente new contact luego de seleccionar en tipo usuario existente
            $(contact_id_select).val("");
            $(this).parent().parent().parent().find("input").addClass("newRequired");
            $(this).parent().parent().parent().find("img").remove();

			$(new_contact_form).find("select, input").prop("disabled", false);
			
		}else if(this.value == "existing"){
			contact_id_select.disabled=false;
			new_contact_form.style.display = "none";
			$(new_contact_form).find("select, input").prop("disabled", true);
		}
	}

	function getPhotoContactExisted(){
	        var elem = $(this);
            $.ajax({
                url:"/admission/"+$("#application_id").attr("value")+"/getPhotoContact",
                type:"POST",
                data:{"partner_id": $(this).val()},
                success:function(data){
                    if(data != ''){
                        var test = elem;
                        test.parent().parent().parent().find(".inputFile").prepend("<img src='"+data+"' width='175'>")
                        test.parent().parent().parent().find("input").removeClass("newRequired");
                    }
                }
            })
	}

	function submitToController(){
        //submitButton

﻿        //var photoFiles = document.querySelectorAll("input[type=file]");
        var photoFiles = $("input[type=file]:not('.newRequired')");
        for (var idx = 0; idx < photoFiles.length; idx++) {
            if(photoFiles[idx].value == ''){
                var fakeFile = document.createElement("input");
                fakeFile.setAttribute('value', '-1');
                fakeFile.setAttribute('name',photoFiles[idx].name);

//                OCULTAMOS TANTO EL ARCHIVO A SUBIR OCMO EL TEXTO QUE INDICA LA SUBIDA DE LA FOTO,
//                PARA EVITAR QUE DE PROBLEMAS EN LA CANTIDAD DE FOTOS QUE LLEGAN AL SERVIDOR
                fakeFile.style.display = "none";
                $(".textUpload").hide()
//                fakeFile.setAttribute('disabled','disabled');
                var div = photoFiles[idx]

                div.parentNode.insertBefore(fakeFile, div.nextSibling);
                div.remove();
            }
        }



        document.getElementById("submitButton").click();
	}

	function addContact() {
		var contactClonnable = document.getElementById("form-template").cloneNode(true);
		var contactForms = document.getElementById("contact_forms");
	    $(".add-contact").remove()
		var existingValues = [];

	    $(contactForms).find("select[name='contact_existing_id']").each(function(index, data){
		//document.querySelectorAll("select[name='contact_existing_id']").forEach(function(data,index){
			if (!$(this).prop("disabled")) {
				$(contactClonnable).find("select[name='contact_existing_id']")
								   .find("option[value='"+$(this).val()+"']").remove();
			} 
		})
		
		contactForms.appendChild(contactClonnable)
		var contact_type_select = contactClonnable.querySelector("select[name='contact_type_select']");
		contact_type_select.addEventListener("change",toggleContactType);

		var contact_type_select = contactClonnable.querySelector("select[name='contact_existing_id']");
		contact_type_select.addEventListener("change",getPhotoContactExisted);
//		$(toggleContactType).trigger("change");
		
	// $(contactClonnable).find("").on("disabled", true);
	// $(contactClonnable).find("select[name='contact_id']").prop("disabled",
	// true);
		
		contador--;
		$(contactClonnable).attr("id", "relationship_" + contador)
		$(contactClonnable).removeClass("d-none");
		var removeButton = $(contactClonnable).find("button")
		//$(removeButton).data("id", contador).on("click", removeContact);
        $(removeButton).attr("data-id", contador).on("click", removeContact);

//		$(this).remove();
	
		$("#contact_forms").append("<button type='button' class='add-contact btn btn-secondary d-block ml-auto mt-2'>&#10010; Add family member</button>");
		$(contactClonnable).find(".inputFile").append("<input class='newRequired' required='required' id='new_file_upload"+contador+"' type='file' name='new_file_upload"+contador+"'/><div class='alert alert-info pt-0 pb-0 mt-1' style='width: fit-content;' role='alert'>Subir la foto del familiar.</div>");

		$(".add-contact").on("click", addContact);
		$(".checkEmailExisted").on("change", checkEmailExisted);

		var section_radio_count = document.getElementsByClassName("sectionRadioSaved").length;

        for (var idx = 0; idx<section_radio_count; idx++)
           $(document.getElementsByClassName("sectionRadioSaved")[idx]).find(".newRadio").attr("name","title_new_radio_"+idx)


         document.querySelectorAll(".checkDuplicated").forEach(
                                                                function(element){
                                                                    element.addEventListener("change", checkDuplicateContact)
                                                                }
                                                            );
	}
	
	function changeState() {
		var select_state = $(this).parents("div.row").find("select.state")
		select_state.children("option:gt(0)").hide();
		select_state.children("option[data-country='" + $(this).val() + "']").show();
	
		if (select_state.children("option:selected").is(":hidden")){
			select_state.children("option:nth(0)").prop("selected", true);
		}
	}
	
	function removeContact() {
		var id = $(this).data("id");
		$("#relationship_" + id).remove();
		$(this).remove();

		var section_radio_count = document.getElementsByClassName("sectionRadioSaved").length;
        for (var idx = 0; idx<section_radio_count; idx++)
           $(document.getElementsByClassName("sectionRadioSaved")[idx]).find(".radio").attr("name","title_radio_"+idx)

        var section_new_radio_count = document.getElementsByClassName("sectionNewRadioSaved").length;
        for (var idx = 0; idx<section_new_radio_count; idx++)
           $(document.getElementsByClassName("sectionNewRadioSaved")[idx]).find(".newRadio").attr("name","title_new_radio_"+idx)

	}
	

	function disableCheckboxes(){
//		event.preventDefault();
		
		$(this).find(".true-emergency-contact").each(function(){
			if(this.checked){
				$(this).next(".false-emergency-contact")[0].disabled = true
			}
		})
		
	}
	
	function ready(fn) {
		if (document.readyState != 'loading'){
			fn();
		} else {
			document.addEventListener('DOMContentLoaded', fn);
		}
	}

	function nodeIterate(nodeList, functionCallback) {
		var i = nodeList.length;
		while (i){
			functionCallback(nodeList[--i]);
		}
	}

	function addEvent(nodeList, event, fn){
		nodeIterate(nodeList, function(element){
			element.addEventListener(event, fn);
		});
	}

	function triggerEvent(nodeList, eventName){
		var event = document.createEvent('HTMLEvents');
		event.initEvent(eventName, true, false);
		nodeIterate(nodeList, function(element){
			element.dispatchEvent(event);
		})
	}

	function checkEmailExisted(){
	        var elem = $(this);
            $.ajax({
                url:"/admission/"+$("#application_id").attr("value")+"/check_email",
                type:"POST",
                data:{"email": $(this).val()},
                success:function(data){
                    var jsonData = JSON.parse(data);
                    var element_event = elem;
                    if(jsonData.exists){
                        $("#emailChecked").text(jsonData.email);
                        $("#modalError").modal('show')
                        element_event.val('');
                    }

                }
            })
	}


    function checkDuplicateContact(){
            var first_name = $(this).parent().parent().parent().find(".firstname");
            var last_name = $(this).parent().parent().parent().find(".lastname");
            var email = $(this).parent().parent().parent().find(".email");
            var cellphone = $(this).parent().parent().parent().find(".phone");

            if( first_name.val() != undefined && first_name.val() != '' &&
                last_name.val() != undefined && last_name.val() != '' &&
                email.val() != undefined && email.val() != '' &&
                cellphone.val() != undefined && cellphone.val() != '' ){

                $.ajax({
                    url:"/admission/checkDuplicateContact",
                    type:"POST",
                    data:{
                        "firstname": first_name.val(),
                        "lastname": last_name.val(),
                        "email": email.val(),
                        "cellphone": cellphone.val()
                    },
                    success:function(data){
                        var jsonData = JSON.parse(data);
                        //var element_event = elem;
                        if(jsonData.parent_name || jsonData.email || jsonData.cellphone){
                            $("#emailChecked").text(jsonData.email);
                            $("#modalError").modal('show');
                            var messageResponse= '';
                            //element_event.val('');

                            messageResponse = 'Hi, ' + first_name.val() +' '+ last_name.val() +'<br>'

                            if(jsonData.parent_name)
                               messageResponse += 'In the system exists a contact with same name.<br>'

                            if(jsonData.email)
                               messageResponse += 'The email <b>' + email.val() + '</b> exists in the system.<br>'

                            if(jsonData.cellphone)
                                messageResponse += 'The mobile <b>' + cellphone.val() + '</b> exists in the system.<br>'

                            messageResponse += "If you want to add this person to the family. Please contact with the admission support to <b>support@iae.edu</b>."

                            $("#bodyMessageIssue").html(messageResponse);
                        }

                    }
                })
            }
    }

	ready(function() {

		addEvent(document.querySelectorAll(".add-contact"), "click", addContact);
		addEvent(document.querySelectorAll(".remove-contact"), "click", removeContact);
		addEvent(document.querySelectorAll("select.country"), "change", changeState);
        addEvent(document.querySelectorAll("#submitButtonFake"), "click", submitToController);


		// triggerEvent(document.querySelectorAll("select.country"), "change");

        var section_radio_count = document.getElementsByClassName("sectionRadioSaved").length;

        for (var idx = 0; idx<section_radio_count; idx++)
           $(document.getElementsByClassName("sectionRadioSaved")[idx]).find(".radio").attr("name","title_radio_"+idx)


        var current_photos_total = document.getElementsByName("file_upload").length;
        for (var idx = 0; idx<current_photos_total; idx++) {
           var lbl_name="file_upload_"+idx;
           (document.getElementsByName("file_upload")[0]).setAttribute("name",lbl_name);
        }
//        var contact_types = document.querySelectorAll("select[name='relationship_type'] option[selected=true]");

        if($("#requestSent").length <= 0){
        //      COMPROBAMOS DE QUE LA MADRE ESTE AÑADIDA DE LO CONTRARIO AÑADIMOS UN CONTACTO Y LE MODIFICAMOS EL TYPE
                if(document.querySelectorAll("select[name='relationship_type'] option[selected=true][value='mother']").length == 0){
                    addContact();
                    $("select[name='new_relationship_type']").last().val('mother');
                }
        //      COMPROBAMOS DE QUE LA PADRE ESTE AÑADIDA DE LO CONTRARIO AÑADIMOS UN CONTACTO Y LE MODIFICAMOS EL TYPE
                if(document.querySelectorAll("select[name='relationship_type'] option[selected=true][value='father']").length == 0){
                    addContact();
                    $("select[name='new_relationship_type']").last().val('father');
                }
        }

		document.getElementById("family_form").addEventListener("submit", disableCheckboxes);
		addEvent(document.querySelectorAll(".checkEmailExisted"), "change", checkEmailExisted);
	});

})()

