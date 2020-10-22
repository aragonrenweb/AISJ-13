  $( document ).ready(function() {
      $(".subButton").click(function() {
        var ext = $(this).prev().find('button').prev().val().split('.').pop();
        $(this).prev().find('#origin_filename').val($(this).prev().find('#origin_filename').val()+'.'+ext)
        $(this).prev().find('button').click();
      });

      $(".downloadFile").click(function() {
        var fileUrl =  $(this).attr("value");
        var baseUrl =  window.location.origin;
        window.open(baseUrl+'/web/content/'+fileUrl+'?download=true');
        //window.location.replace('https://sgcalle-hhrr2-developer-1167390.dev.odoo.com/web/content/'+fileUrl+'?download=true');
        //window.location.href = 'https://sgcalle-hhrr2-developer-1167390.dev.odoo.com/web/content/'+fileUrl+'?download=true';
        var gf=2;
      });
  });
