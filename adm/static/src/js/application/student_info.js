odoo.define('adm.application.student_info', require => {
    "use strict";

    require('web.core');

    function toggleStudentNameEdit(event) {
        $(document.getElementById('change_name_div')).toggle();
    }

    $(function () {
        $(document.getElementById('toggleStudentName')).on('click', toggleStudentNameEdit);
        $('.form-upload').each((i, el) => {
            const $el = $(el);
            const inputFile = $el.find('input[type=file]');
            const inputSpanLabel = $el.find('.js_input_file_label');
            inputFile.on('change', (event) => {
                inputSpanLabel.text(event.currentTarget.files[0].name);
            });
        });
        $('.js_submit_json').on('click', sendJson);
    });

    function buildJson() {
        const jsonToBuild = {};

        $('[data-adm-model-fields="1"]').each((i, elModel) => {
            const $elModel = $(elModel);

            // const modelFieldsValues = {};
            $elModel.find('[data-adm-field]').each((i, elField) => {
                const fieldName = elField.dataset.admField;
                switch (elField.tagName) {
                    case 'SELECT':
                        jsonToBuild[fieldName] = $(elField).find('option').filter(':selected').val();
                        break;
                    default:
                        jsonToBuild[fieldName] = elField.value;
                }
            });
            // jsonToBuild.push(modelFieldsValues)
        });

        return JSON.stringify(jsonToBuild);
    }

    function sendJson() {
        const jsonToSend = buildJson();

        $.ajax({
            url: '/admission/applications/1/',
            method: 'PUT',
            contentType: 'application/json',
            data: jsonToSend,
        })
        console.log('HHH');
    }

    function change_name() {
        if (document.getElementById('change_name_div').style.display === 'none')
            document.getElementById('change_name_div').style.display = 'block';
        else
            document.getElementById('change_name_div').style.display = 'none';
    }


    function addSibling() {
        var itm = document.getElementById("sibling_base_div");

        var cln = itm.cloneNode(true);
        cln.classList.remove("d-none");
        cln.classList.add("d-flex");
        cln.classList.add("flex-wrap");
        cln.classList.add("p-0");
        document.getElementById("sibling_new_div").appendChild(cln);
    }


});