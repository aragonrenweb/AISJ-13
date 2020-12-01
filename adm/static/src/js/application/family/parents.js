odoo.define('adm.family.parents', require => {

    require('web.core');

    function sendRelationshipInfoToServer() {

        const jsonData = {
            relationshipParents: []
        };

        $('[data-adm-model-fields="1"]').each((i, elModel) => {
            const $elModel = $(elModel);

            const modelFieldsValues = {};
            $elModel.find('[data-adm-field]').each((i, elField) => {
                const fieldName = elField.dataset.admField;
                modelFieldsValues[fieldName] = elField.value;
            });
            jsonData.relationshipParents.push(modelFieldsValues)

        });

        console.log('jsonData: ', JSON.stringify(jsonData));
    }

    $(document).ready(() => {
        const $btnFamilyParentsSave = $(document.getElementById('btnFamilyParentsSave'));
        $btnFamilyParentsSave.on('click', sendRelationshipInfoToServer);
    });

});