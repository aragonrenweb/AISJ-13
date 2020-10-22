(function(){
	"use strict";
	var contador = -1;

	function addSchool() {
		var schoolClonnable = document.getElementById("form-template").cloneNode(
				true);
		var schoolForms = document.getElementById("school_forms");

		schoolForms.appendChild(schoolClonnable);

		contador--;

		schoolClonnable.id = "previous_school_" + contador;
		$(schoolClonnable).removeClass("d-none");
		var removeButton = $(schoolClonnable).find("button")
		$(removeButton).data("id", contador).on("click", removeSchool);

		$(this).remove();


		$("#school_forms").append("<button type='button' class='add-school btn btn-secondary d-block ml-auto mt-2'>&#10010;Add School</button>");
		$(".add-school").on("click", addSchool);
		var countryElement = document.querySelectorAll("select.country");
		addEvent(countryElement, "change", changeState);
		triggerEvent(countryElement, "change");
	}

	function changeState() {
		var select_state = this.closest("div.row").querySelector("select.state");
		var select_country_selected = this.value;

        for(var i=1; i < select_state.length; i++){
             if(select_state[i].dataset.country != select_country_selected)
                select_state[i].classList.add("d-none");
             else{
                select_state[i].classList.remove("d-none");
                if(select_state[i].getAttribute('selected'))
                   select_state.value = select_state[i].value;
             }
        }

//        select_state.value=-1
//
//        select_country.value
//		var set_options = function(element){
//			if (element.dataset.country === element.value){
//				console.log("QUESO");
//			}
//		};
//
//		select_state.querySelectorAll("option").forEach(set_options);
		// nodeIterate(select_state.querySelectorAll("option"), set_options);

		/* select_state.children("option:gt(0)").hide();
		select_state.children("option[data-country='" + $(this).val() + "']").show();

		if (select_state.ch:ildren("option:selected").is(":hidden")){
			select_state.children("option:nth(0)").prop("selected", true);
		} */
	}

	function removeSchool() {
		var id = $(this).data('id');
		$("#previous_school_" + id).remove();
		$(this).remove();
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
//			functionCallback(nodeList[--i]);
		}
	}

	function addEvent(nodeList, event, fn){
		nodeIterate(nodeList, function(element){
			element.addEventListener(event, fn);
		});

	}

	function triggerEvent(nodeList, eventName){
		var event = new Event(eventName, {"bubbles": true, "cancelable": false})
		nodeIterate(nodeList, function(element){
			element.dispatchEvent(event);
		})
	}

	ready(function() {
	    console.log("rest");
		addEvent(document.querySelectorAll(".add-school"), "click", addSchool);
		addEvent(document.querySelectorAll(".remove-school"), "click", removeSchool);
		addEvent(document.querySelectorAll("select.country"), "change", changeState);

		document.querySelector
		triggerEvent(document.querySelectorAll("select.country"), "change");
	});
})();