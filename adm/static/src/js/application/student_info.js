odoo.define('adm.application.student_info', require => {
    "use strict";

    require('web.core');
    const utils = require('web.utils');
    let partnerAvatarFile;
    let partnerPassportFile;
    let partnerResidencyPermit;

    function toggleStudentNameEdit(event) {
        $(document.getElementById('change_name_div')).toggle();
    }

    $(document).ready(function () {
        const elAvagarPhoto = document.getElementById('avatar_photo');
        const $elAvagarPhotoFile = $(document.getElementById('avatar_photo_file'));
        $elAvagarPhotoFile.on('input', event => {
            $(document.getElementById('student_avatar_loading')).show();
            const avatarFile = event.currentTarget.files[0];
            utils.getDataURLFromFile(avatarFile).then((base64Buffer) => {
                elAvagarPhoto.src = base64Buffer;
                partnerAvatarFile = {
                    "name": avatarFile.name,
                    "file": base64Buffer,
                    "content_type": avatarFile.type,
                }
                // Animation
                $(document.getElementById('student_avatar_loading')).hide();
                const $uploadImageSuccess = $(document.getElementById('upload_image_success'));
                $uploadImageSuccess.show();
                $uploadImageSuccess.addClass('checkmark');
                $uploadImageSuccess.delay(1500).fadeOut(1000);
                setTimeout(() => {
                    $uploadImageSuccess.removeClass('checkmark');
                }, 8000);
            });
        });

        $(document.getElementById('passport_file')).on('input', event => {
            const elFile = event.currentTarget;
            const file = elFile.files[0];
            utils.getDataURLFromFile(file).then(buffer => {
                partnerPassportFile = {
                    "name": file.name,
                    "file": buffer,
                    "content_type": file.type,
                }
            })
        });

        $(document.getElementById('passport_residency_permit')).on('input', event => {
            const elFile = event.currentTarget;
            const file = elFile.files[0];
            utils.getDataURLFromFile(file).then(buffer => {
                partnerResidencyPermit = {
                    "name": file.name,
                    "file": buffer,
                    "content_type": file.type,
                }
            })
        });

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

        function convertToFieldType(el, val) {

            switch ((el.dataset.admFieldType || '').toUpperCase()) {
                case 'MANY2ONE':
                    val = {id: parseInt(val)};
                    break;
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
                const fieldName = elField.dataset.admField;
                switch (elField.tagName) {
                    case 'SELECT':
                        // jsonToBuild[fieldName] = convertToFieldType(elField, $(elField).find('option').filter(':selected').val());
                        jsonToBuild[fieldName] = convertToFieldType(elField, $(elField).val());
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

        const applicationId = $('meta[name="_application_id"]').attr("value");//$('meta[name="_application_id"]').val();
        $.ajax({
            url: '/admission/applications/' + applicationId + '/',
            method: 'PUT',
            contentType: 'application/json',
            data: jsonToSend,
            csrf_token: odoo.csrf_token,
        })

        if (partnerAvatarFile) {
            $.ajax({
                url: '/admission/applications/' + applicationId + '/avatar',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(partnerAvatarFile),
                csrf_token: odoo.csrf_token,
            });
        }

        if (partnerPassportFile || partnerResidencyPermit) {

            const dataFiles = {
                passportFile: partnerPassportFile,
                residencyFile: partnerResidencyPermit,
            }

            $.ajax({
                url: '/admission/applications/' + applicationId + '/student-files',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(dataFiles),
                csrf_token: odoo.csrf_token,
            })
        }
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