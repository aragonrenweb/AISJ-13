odoo.define('adm.application.student_info', require => {
    "use strict";

    require('web.core');

    function toggleStudentNameEdit(event) {
        $(document.getElementById('change_name_div')).toggle();
    }

    $(function () {
       $(document.getElementById('toggleStudentName')).on('click', toggleStudentNameEdit);
       $('.form-upload').each( (i, el) => {
           const $el = $(el);
           const inputFile = $el.find('input[type=file]');
           const inputSpanLabel = $el.find('.js_input_file_label');
           inputFile.on('change', (event) => {
               inputSpanLabel.text(event.currentTarget.files[0].name);
           });
        })
    });

    function change_name() {
        if (document.getElementById('change_name_div').style.display === 'none')
            document.getElementById('change_name_div').style.display = 'block';
        else
            document.getElementById('change_name_div').style.display = 'none';
    }


    function addBrother() {
        var itm = document.getElementById("brother_base_div");

        var cln = itm.cloneNode(true);
        cln.classList.remove("d-none");
        cln.classList.add("d-flex");
        cln.classList.add("flex-wrap");
        cln.classList.add("p-0");
        document.getElementById("brother_new_div").appendChild(cln);
    }


});