odoo.define('adm.application.common', require => {

    require('web.core');

    function buildJson() {
        const jsonToBuild = {};

        function convertToFieldType(el, val) {

            switch ((el.dataset.admFieldType || '').toUpperCase()) {
                case 'MANY2ONE':
                case 'INTEGER':
                    val = parseInt(val);
                    break;
                case 'FLOAT':
                    val = parseFloat(val);
            }

            return val;

        }

        $('[data-adm-model-fields="1"]').each((i, elModel) => {
            const $elModel = $(elModel);

            // const modelFieldsValues = {};
            $elModel.find('[data-adm-field]').each((i, elField) => {
                if ($(elField).is(':radio') && !$(elField).is(':checked')) {
                    console.log('checked removed!');
                    return;
                }
                const fieldName = elField.dataset.admField;

                const fieldNameSplitHierarchical = fieldName.split('.');
                let fieldNameToModify = fieldNameSplitHierarchical[0];
                let auxDict = jsonToBuild;

                if (fieldNameSplitHierarchical.length > 1){
                    for (let i = 0; i < fieldNameSplitHierarchical.length; i++) {

                        const auxFieldName = fieldNameSplitHierarchical[i];

                        if (fieldNameSplitHierarchical[i + 1] !== undefined) {
                            if (!Object.hasOwnProperty.call(auxDict, auxFieldName)) {
                                auxDict[auxFieldName] = {};
                            }
                            auxDict = auxDict[auxFieldName]
                        }
                        fieldNameToModify = auxFieldName;
                    }
                }



                auxDict[fieldNameToModify] = convertToFieldType(elField, $(elField).val());
            });
        });

        return JSON.stringify(jsonToBuild);
    }

    function sendJson() {
        const jsonToSend = buildJson();
        console.log(jsonToSend);
        const applicationId = $('meta[name="_application_id"]').attr("value");//$('meta[name="_application_id"]').val();
        $.ajax({
            url: '/admission/applications/' + applicationId + '/',
            method: 'PUT',
            contentType: 'application/json',
            data: jsonToSend,
            csrf_token: odoo.csrf_token,
        })
    }

    $(document).ready(() => {
        $('.js_submit_json').on('click', sendJson);
    });

});