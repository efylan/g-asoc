function str_isblank(str){
	var cad = str.replace(/ /gi, "");

	if (cad.length == 0)
	{
		return true;
	}
	else
	{
		return false;
	}
}

function get_val(input){
    /* devuelve el valor de una caja de texto */
    str = input.val()
    //alert(str)
    if (str_isblank(String(str)) ){
        input.val(0)
    } 
    return parseFloat(str)
}



$.ajaxSetup({ 
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                 if (cookie.substring(0, name.length + 1) == (name + '=')) {
                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                     break;
                 }
             }
         }
         return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     } 
});

function set_date_input(textinput){
   /* recibe una caja de texto
    y le asigna el datepicker */
    textinput.attr("readonly", "true")
    textinput.datepicker($.datepicker.regional['es'])
}


$( document ).ready( function() {

    set_date_input($('#id_fecha'))

    $('#id_subtotal').change(function() {
        calcular_iva();
    });

    $('#id_impuesto').change(function() {
        calcular_iva();
    });

    $('#id_iva_registrado').change(function() {
        calcular_iva();
    });


    $('#id_importe').change(function() {
        calcular_diferencias();
    });

    $('#id_bancos').change(function() {
        calcular_diferencias();
    });


    $('#id_iva').change(function() {
        calcular_retenciones();
    });


    $('#id_ret_iva').change(function() {
        calcular_retenciones();
    });

    $('#id_ret_isr').change(function() {
        calcular_retenciones();
    });


$("#id_RFC_proveedor").change(function (){
    elegido=$(this).val();
    $.post("/diot/proveedores/consultar/", { elegido: elegido}, function(data){
    if (data.length>1)
    {

        $("#id_nombre_proveedor").val(data);
        $("#id_nombre_proveedor").attr("readonly", "true")
        $("#id_beneficiario").val(data);
    }
    else
    {

        $("#id_nombre_proveedor").removeAttr("readonly"); 
        $("#id_nombre_proveedor").val('');
        $("#id_beneficiario").val('');
    }

});			

})



 });




function calcular_iva()
{
    imp_id = $("#id_impuesto option:selected").val()
    txt_id = '#iva_'+imp_id
    porcentaje = get_val($(txt_id))
    if (isNaN(porcentaje)){porcentaje=0}
    subtotal = get_val($("#id_subtotal"))
    iva = (subtotal * (porcentaje/100))
    iva_registrado=get_val($("#id_iva_registrado"))
    if (isNaN(iva_registrado)){iva_registrado=0}
    diferencia_iva = iva_registrado - iva
    if (isNaN(diferencia_iva)){diferencia_iva=0}
    $('#id_diferencia_iva').val(diferencia_iva.toFixed(2))
    ret_iva = get_val($('#id_ret_iva')) 
    ret_isr = get_val($("#id_ret_isr"))

    total = subtotal + iva_registrado - ret_iva - ret_isr

    diferencia = get_val($('#id_bancos')) - total
    if (isNaN(iva)){iva=0}
    if (isNaN(total)){total=0}
    if (isNaN(diferencia)){diferencia=0}
    $('#id_iva').val(iva.toFixed(2))
    $("#id_importe").val(total.toFixed(2))
    $("#id_diferencia").val(diferencia.toFixed(2))
}

function calcular_diferencias()
{
    diferencia = get_val($('#id_bancos')) - get_val($("#id_importe"))
    if (isNaN(diferencia)){diferencia=0}
    $("#id_diferencia").val(diferencia.toFixed(2))
}

function calcular_retenciones()
{
    imp_id = $("#id_impuesto option:selected").val()
    txt_id = '#iva_'+imp_id
    porcentaje = get_val($(txt_id))
    if (isNaN(porcentaje)){porcentaje=0}
    subtotal = get_val($("#id_subtotal"))
    iva = (subtotal * (porcentaje/100))
    iva = get_val($('#id_iva'))
    if (isNaN(iva)){iva=0}
    diferencia_iva = iva_registrado - iva
    if (isNaN(diferencia_iva)){diferencia_iva=0}
    $('#id_diferencia_iva').val(diferencia_iva.toFixed(2))
    iva_registrado=get_val($("#id_iva_registrado"))
    if (isNaN(iva_registrado)){iva_registrado=0}
    ret_iva = get_val($('#id_ret_iva')) 
    ret_isr = get_val($("#id_ret_isr"))
    total = subtotal + iva_registrado - ret_iva - ret_isr
    if (isNaN(total)){total=0}
    diferencia = get_val($('#id_bancos')) - total
    if (isNaN(diferencia)){diferencia=0}
    $('#id_iva').val(iva.toFixed(2))
    $("#id_importe").val(total.toFixed(2))
    $("#id_diferencia").val(diferencia.toFixed(2))
}

/*
Ejemplo de combo dependiente
*/

