odoo.define('adm.kanban_view_button', function (require){
    "use strict";
    var core = require('web.core');
    var KanbanController = require('web.KanbanController');
    var KanbanView = require('web.KanbanView');

    var includeDict = {
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (this.modelName == 'adm.reenrollment') {
                var your_btn = this.$buttons.find('button.o_kanban_button_import_students');
                your_btn.on('click', this.proxy('o_kanban_button_import_students'));
            }
        },
        o_kanban_button_import_students: function(){
                $.ajax({
                    url: '/admission/reenrollment/import_students',
                    type: 'POST',
                    success: function(data){
                        $.each(JSON.parse(data), function(i, state){
                            $('#selState').append(`<option value='${state.id}'>${state.name}</option>`)
                        })
                    },
                    error: function(){
                        console.error("Un error ha ocurrido al cargar los states");
                    }
                });
//        console.log("hola");
//            this.do_action({
//                name: "Open a wizard",
//                type: 'ir.actions.act_window',
//                res_model: 'locations.quants.report',
//                view_mode: 'form',
//                view_type: 'form',
//                views: [[false, 'form']],
//                target: 'new',
//            });
        }
    };

    KanbanController.include(includeDict);

    includeDict = {
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (this.modelName == 'adm.reenrollment') {
                var your_btn = this.$buttons.find('button.o_kanban_button_import_students2');
                your_btn.on('click', this.proxy('o_kanban_button_import_students2'));
            }
        },
        o_kanban_button_import_students2: function(event) {
            event.preventDefault();
            var self = this;
            self.do_action({
                'type': 'ir.actions.act_window',
                'name': 'Warning : Customer is about or exceeded their credit limit',
                'res_model': 'sale.control.limit.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': 9,
                'views': [[false, 'form']],
                'target': 'new'
            });
        }
    };

    KanbanController.include(includeDict);
});