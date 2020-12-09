odoo.define('adm.family.parents', require => {
    "use strict";

    require('web.core');

    $(document).ready(() => {

        $('input.js_existing:checkbox').on('change', (event) => {

            const el = event.currentTarget;
            const isChecked = !!el.checked;
            const $container =  $(el).closest('.container');
            $container.find('.js_existing_selection').toggle(isChecked);
           $container.find('.js_invisible_existing').toggle(!isChecked)
                .find('input, select').prop('disabled', isChecked);

        });

    });
})