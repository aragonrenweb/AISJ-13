import json

from odoo import http


# Se añaden campos:
# - Siblings
# - Datos de los hermanos
# - Horario de contacto
# - Comment en res.parthner



#controlador encargado de devolver datos de las admisiones, para insertarlas en FACTS
class admisionController(http.Controller):    
    # Definiendo la url desde donde va ser posible acceder, tipo de metodo, cors para habiltiar accesos a ip externas.
    @http.route("/admission/adm", auth="public", methods=["GET"], cors='*') #csrf: hay que añadir este parametro siu es POST, PUT, etc, para todo menos para GET.
    # define una funcion principal
    def get_adm_uni(self, **params): 
        
        permitidas_url = http.request.env['ir.config_parameter'].sudo().get_param('allow_urls','')
        
        origen_url = '-1'
        
#        if('HTTP_ORIGIN' in http.request.httprequest.headers.environ):
        
#            origen_url = http.request.httprequest.headers.environ['HTTP_ORIGIN']
        
#        if(origen_url is '-1' or origen_url not in permitidas_url):
        
#            return 'Denied access'                
        

        # Array con los campos del alumno y de las familias y los contactos
        campos_contactos = ["company_type","type","first_name","middle_name","last_name","street","street2","city","state_id","zip","country_id",
                            "function","phone","mobile","email","website","title","lang","category_id","vat","company_id","citizenship",
                            "identification","marital_status","parental_responsability",
                            "title","work_address","work_phone","child_ids","user_id","person_type","grade_level_id","homeroom","student_status",
                            "comment_facts","facts_id","facts_id_int","is_in_application","application_id","inquiry_id","gender","relationship_ids","family_ids"]
        
        # DATOS DE LA APPLICATION        
        
        # Crea una variable con el modelo desde donde se va a tomar la información 
        application = http.request.env['adm.application'].sudo()        
        
        # Array donde se buscaran las applications
        busqueda =["done","stage"]
        
        # filtro del modelo: status = done y el checkBox Imported = False
        search_domain = [("status_id.type_id","=",busqueda)]#,("partner_id.x_imported","=",False)] 
        # search_domain = [("status_type","=","fact_integration")] #,("country_id", "=", int(params['country_id']))] if "country_id" in params else []
        # search_domain = [("status_type","=","fact_integration"),("country_id", "=", int(params['country_id']))] 
        
        # Tomar informacion basado en el modelo y en el domain IDS 
        application_record = application.search(search_domain)      
        
        # Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior
        application_values = application_record.read(["id","status_type","first_name","middle_name","last_name","contact_time_id","grade_level","gender","father_name",
                                                "mother_name","task_ids","street","city","state_id","zip","country_id","home_phone","phone","email","date_of_birth","citizenship",
                                                "first_language","first_level_language","second_language","second_level_language","third_language","third_level_language",
                                                "previous_school_ids","doctor_name","doctor_phone","doctor_address","permission_to_treat","blood_type",
                                                      "medical_conditions_ids","medical_allergies_ids","medical_medications_ids",
                                                "relationship_ids","partner_id","name","house_address_ids","siblings",
                                               ])
        
        # recorremos el array y vamos tratando los datos. Se modifica el formato del for: se añade index y enumerate para poder hacer busquedas
        # por el index, esto se usa en las familias.
        for index,record in enumerate(application_values): 
            # Convertir fechas a string
            if record["date_of_birth"]:
                record["date_of_birth"] = record["date_of_birth"].strftime('%m/%d/%Y')
            else:
                record["date_of_birth"] = ''   
                

            # SchooCode
            if record["grade_level"]:
                record["SCName"] = []
                datosSC = http.request.env['school_base.grade_level'].sudo()  
                search_domain_SC = [("id", "=", record["grade_level"][0])]
                datosSC_record = datosSC.search(search_domain_SC)
                #Si existe cogemos el nombre asociado al school_code_id 
                if datosSC_record.school_code_id:
                    datosSC_values = datosSC_record.school_code_id.name 
                record["SCName"] = datosSC_values
            
            
            
            # Sacamos datos de los Horarios de contacto   
            # Array para los Horarios de contacto
            if record["contact_time_id"]:
                record["horarioContactoDatos"] = []

                # crea una variable con el modelo desde donde se va a tomar la información
                datosHor = http.request.env['adm.contact_time'].sudo()  
                # filtro del modelo basados en parametros de la url
                search_domain_Hor = [("id", "=", record["contact_time_id"][0])] # ("res_model", "=", "adm_uni.application"),
                # Tomar informacion basado en el modelo y en el domain IDS
                datosHor_record = datosHor.search(search_domain_Hor)  
                # Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior
                datosHor_values = datosHor_record.read(["name","from_time","to_time"]) 
                record["horarioContactoDatos"] = datosHor_values
            
            
            
            
            
            
            # Sacamos datos de los Hermanos    
            # Array para los Hermanos
            record["hermanosDatos"] = []

            # crea una variable con el modelo desde donde se va a tomar la información
            datosHer = http.request.env['adm.application.sibling'].sudo()
            # filtro del modelo basados en parametros de la url
            search_domain_Her = [("id", "=", record["siblings"])] # ("res_model", "=", "adm_uni.application"),
            # Tomar informacion basado en el modelo y en el domain IDS
            datosHer_record = datosHer.search(search_domain_Her)
            # Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior
            datosHer_values = datosHer_record.read(["name","age","school"]) 
            record["hermanosDatos"] = datosHer_values
            
            # Sacamos datos de las Tasks    
            # Array para las task
            record["task"] = []

            # crea una variable con el modelo desde donde se va a tomar la información
            datosTask = http.request.env['adm.application.task'].sudo()  
            # filtro del modelo basados en parametros de la url
            search_domain_Task = [("id", "=", record["task_ids"])] # ("res_model", "=", "adm_uni.application"),
            # Tomar informacion basado en el modelo y en el domain IDS
            datosTask_record = datosTask.search(search_domain_Task)
            # Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior
            datosTask_values = datosTask_record.read(["name","description","display_name"]) 
            record["task"] = datosTask_values
                
            # Sacamos datos de las relationship    
            # Array para las relationships  
            record["relationship"] = []

            # crea una variable con el modelo desde donde se va a tomar la información
            datosRelationship = http.request.env['adm.relationship'].sudo()  
            # filtro del modelo basados en parametros de la url
            search_domain_Rel = [("id", "=", record["relationship_ids"])]
            # Tomar informacion basado en el modelo y en el domain IDS
            datosRel_record = datosRelationship.search(search_domain_Rel)
            # Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior
            datosRel_values = datosRel_record.read(["partner_2","relationship_type"]) 
            record["relationship"] = datosRel_values
                
            # Sacamos datos del previous school
            #if record["previous_school_ids"]:  
            
            # Array para los datos del colegio previo    
            record["previousSchool"] = []

            # crea una variable con el modelo desde donde se va a tomar la información
            datosSchoolPrev = http.request.env['adm.previous_school_description'].sudo()  
            # filtro del modelo basados en parametros de la url
            search_domain_prev = [("id", "=", record["previous_school_ids"])]
            # Tomar informacion basado en el modelo y en el domain IDS
            datosPrev_record = datosSchoolPrev.search(search_domain_prev)
            # Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior
            datosPrev_values = datosPrev_record.read(["application_id","id","name","street","zip","country_id","from_date","to_date","extracurricular_interests",
                                                        "city","state_id","grade_completed"
                                                        ])    
                
            # Recorremos los datos obtenidos y transformamos las fechas para evitar errores
            for record_school in datosPrev_values: 
                # Convertir fechas a string
                if record_school["from_date"]:
                    record_school["from_date"] = record_school["from_date"].strftime('%m/%d/%Y')
                else:
                    record_school["from_date"] = ''  

                if record_school["to_date"]:
                    record_school["to_date"] = record_school["to_date"].strftime('%m/%d/%Y')
                else:
                    record_school["to_date"] = ''

            record["previousSchool"] = datosPrev_values                            
            
            # Array para los datos de las direcciones    
            record["address"] = []

            # crea una variable con el modelo desde donde se va a tomar la información
            datosAddress = http.request.env['adm.house_address'].sudo()  
            # filtro del modelo basados en parametros de la url
            search_domain_prev = [("id", "=", record["house_address_ids"])]
            # Tomar informacion basado en el modelo y en el domain IDS
            datosAdd_record = datosAddress.search(search_domain_prev)
            # Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior
            datosAdd_values = datosAdd_record.read(["name","country_id","state_id","street","zip"]) 

            record["address"] = datosAdd_values      
                    
            # Sacamos datos de las medicals conditions
            # if record["medical_conditions_ids"]:  
                
            # Array para los datos medicos Conditions  
            record["medicalConditions"] = []

            # crea una variable con el modelo desde donde se va a tomar la información
            datosMedicosCond = http.request.env['adm.medical_condition'].sudo()  
            # filtro del modelo basados en parametros de la url
            search_domain_Cond = [("id", "=", record["medical_conditions_ids"])]
            # Tomar informacion basado en el modelo y en el domain IDS
            datosCond_record = datosMedicosCond.search(search_domain_Cond)
            # Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior
            datosCond_values = datosCond_record.read(["name","comment"]) 
            record["medicalConditions"] = datosCond_values
            
            # Sacamos datos de las medicals allergies
            #if record["medical_allergies_ids"]:  
                
            # Array para los datos medicos Allergies  
            record["medicalAllergies"] = []

            # crea una variable con el modelo desde donde se va a tomar la información
            datosMedicosAller = http.request.env['adm.medical_allergy'].sudo()  
            # filtro del modelo basados en parametros de la url
            search_domain_Aller = [("id", "=", record["medical_allergies_ids"])]
            # Tomar informacion basado en el modelo y en el domain IDS
            datosAller_record = datosMedicosAller.search(search_domain_Aller)
            # Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior
            datosAller_values = datosAller_record.read(["name","comment"])   
            record["medicalAllergies"] = datosAller_values
                
            # Sacamos datos de las medicals medications
            #if record["medical_medications_ids"]:  
            
            # Array para los datos medicos Medications  
            record["medicalMedications"] = []

            # crea una variable con el modelo desde donde se va a tomar la información
            datosMedicosMedic = http.request.env['adm.medical_medication'].sudo()  
            # filtro del modelo basados en parametros de la url
            search_domain_Medic = [("id", "=", record["medical_medications_ids"])]
            # Tomar informacion basado en el modelo y en el domain IDS
            datosMedic_record = datosMedicosMedic.search(search_domain_Medic)
            # Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior
            datosMedic_values = datosMedic_record.read(["name","comment"])  
            record["medicalMedications"] = datosMedic_values
            
            # DATOS DEL ALUMNO        
            
            # Sacamos datos del alumno
            #if record["partner_id"]:                                

            # Array para los datos alumnos  
            record["alumnoDatos"] = []

            # crea una variable con el modelo desde donde se va a tomar la información
            datos_partner = http.request.env['res.partner'].sudo()  
            # filtro del modelo basados en parametros de la url
            search_domain_partner = [("id", "=", record["partner_id"][0])] # Recuperamos una tupla y solo necesitamos el primer valor
                
            # Tomar informacion basado en el modelo y en el domain IDS
            datos_partner_record = datos_partner.search(search_domain_partner)
                
            # Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior
            datos_partner_values = datos_partner_record.read(campos_contactos) 
                    
            record["alumnoDatos"] = datos_partner_values       
                
            # DATOS DE LA FAMILIA              
            # Array para los datos de cada familia  
            record["familiaDatos"] = []               
            
            # 
            familia = application_record[index].partner_id.parent_id
            
            datos_familias_values = familia.read(campos_contactos)

            record["familiaDatos"] = datos_familias_values
            
            
            
            # DATOS IS IN APPLICATION            
            # Array para los datos de is in aplication 
#            record["isInAppDatos"] = []               
            
            # 
#            familia = application_record[index].partner_id.application_id
            
#            datos_appl = familia.read("name")

#            record["isInAppDatos"] = datos_appl            
            
            
            

            
            # DATOS DE LOS CONTACTOS              
            # Array para los datos de cada contacto  
            record["contactoDatos"] = []               
            
            # 
            contacto = application_record[index].partner_id.parent_id.child_ids.filtered(lambda member_id: member_id != application_record[index].partner_id)
            
            datos_contactos_values = contacto.read(campos_contactos)  
            
            record["contactoDatos"] = datos_contactos_values
            
        
            # DATOS DE LOS FICHEROS              
            # Array para los datos de cada fichero de la aplicacion  
            record["datosFicheros"] = []
        
            #crea una variable con el modelo desde donde se va a tomar la información
            attachments = http.request.env['ir.attachment'].sudo()        
        
            #filtro del modelo basados en parametros de la url
            search_domain_attach = [("res_model", "=", "adm.application"),("res_id","=",record["id"])]
        
            #Tomar informacion basado en el modelo y en el domain IDS
            attachments_record = attachments.search(search_domain_attach)      
        
            #Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior
            #mimetype: tpo de archivo, datas: arhivo en binario
            attachments_values = attachments_record.read(["id","name"])  
#            attachments_values = attachments_record.read(["id","name","mimetype","datas"])  
                
            #Recorremos los datas y las pasamos a str. Los [] son para quitar dos caracteres, el primero y el ultimo
#            for item in attachments_values:
#                item['datas'] = str(item['datas'])[2:-1]
                
            record["datosFicheros"] = json.dumps(attachments_values)
            #for item in attachments_values:
               # for data_item in attachments_datas:
                    #if item.id == data_item.id:
                     #   item.update( {"file_data":str("item.datas")})
                #item.update( {"file_data":str(attachments_record.read(["datas"]))})

            #attachments_values["datas"] = "hola"#str(attachments_record.read(["datas"]))    
        
        #pintar la información obtenida, esto lo utilizamos para parsearlo en el ajax.         
        return json.dumps(application_values)
   
    
    #Metodo para hacer comprobaciones, no sirve para la aplicacion.
#    @http.route("/admission/check", auth="public", methods=["GET"], cors='*', csrf=False)
    # define una funcion principal 
#    def insertId(self, **kw):   
        
#        permitidas = http.request.env['ir.config_parameter'].get_param('allow_urls','')
        
#        variable = http.request.httprequest.headers.environ['HTTP_ORIGIN']
        
        #return json.dumps(request.httprequest.url +' | '+ request.httprequest.base_url  +' | '+ request.httprequest.host_url)
#        return json.dumps(variable)
    
    
    #definiendo la url desde donde va ser posible acceder, tipo de metodo, cors para habiltiar accesos a ip externas.
    @http.route("/admission/adm_insertId", auth="public", methods=["POST"], cors='*', csrf=False)
    # define una funcion principal 
    def insertId(self, **kw):  
        data = json.loads(kw["data"])
        for itemData in data: 
            #itemData["odooId"]
            #itemData["factsId"]
            application = http.request.env['res.partner'].sudo()
          
            #search_domain = [("id","=",itemData["odooId"])]
            
            # Con browse podemos buscar todo un array un array y juntamos las lineas de arriba y lade abajo que estan comentadas
            application_record = application.browse([itemData["odooId"]])      
        
            #Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior
            #application_values = application_record.partner_id
        
            #Cambiamos application_values por application_record debido al cambio de la linea 294
            application_record.write({'facts_id': itemData["factsId"]})
            #tomamos el modelo de application
            #application = http.request.env['adm_uni.application']        
            #obtenemos el contacto de odoo
            #contact = http.request.env['res.partner'] 
            #obj = contact.sudo().browse(application_values[0]["id"])
            #actualizamos campo
            #obj.sudo().write({'x_facts_id': itemData["factsId"]}) 
        
        return json.dumps(data)


    
    