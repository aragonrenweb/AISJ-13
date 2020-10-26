function sendFormSignature(){
    var canvas = document.getElementById('signature-pad');
    var dataURL = canvas.toDataURL();
    dataURL = dataURL.replace('data:image/png;base64,','');
    $("#inputSignature").val(dataURL);
    $("#btnForm").click();
}

$( document ).ready(function() {
  var signaturePad = new SignaturePad(document.getElementById('signature-pad'), {
      backgroundColor: 'rgba(255, 255, 255, 0)',
      penColor: 'rgb(0, 0, 0)'
  });
  /*
      var saveButton = document.getElementById('save');
      var cancelButton = document.getElementById('clear');

      saveButton.addEventListener('click', function (event) {
        var data = signaturePad.toDataURL('image/png');

      // Send data to server instead...
        window.open(data);
      });

      cancelButton.addEventListener('click', function (event) {
        event.preventDefault();
        signaturePad.clear();
      });
  */
  $("#clear").click(function() {
      var signaturePad = new SignaturePad(document.getElementById('signature-pad'), {
        backgroundColor: 'rgba(255, 255, 255, 0)',
        penColor: 'rgb(0, 0, 0)'
      });
      $("#imgDefault").hide();
  });
});

