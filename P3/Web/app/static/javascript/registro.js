$(document).ready(function() {
  $('#regform #campocontrasena').keyup(function() {
    var valor = $('#regform #campocontrasena').val();
    var seguridad = 0;
    if(valor.length >= 8){ //La contraseña consta de 8 o más caracteres
      seguridad += 1;
    }
    if(valor.match(/[0-9]/)){ //Tiene al menos un dígito
      seguridad += 1;
    }
    if(valor.match(/[.!@#$%^&*_]/)){ //Tiene al menos un caracter especial
      seguridad += 1;
    }
    switch(seguridad){
      case 1:
        $('#regform #seguridad').text('Bajo');
        $('#regform #seguridad').css('color', 'orange');
        break;
      case 2:
        $('#regform #seguridad').text('Medio');
        $('#regform #seguridad').css('color', 'yellowgreen');
        break;
      case 3:
        $('#regform #seguridad').text('Alto');
        $('#regform #seguridad').css('color', 'green');
        break;
      default:
        $('#regform #seguridad').text('Muy bajo');
        $('#regform #seguridad').css('color', 'red');
    }
    return;
  })
  return;
})

function check(){
  var auxform = document.getElementById('regform');
  var valid = true;
  document.getElementById('notreqerr').innerText = '';
  if(auxform['nombre'].value == ''){
    document.getElementById('notreqerr').innerText = 'Todos los campos son obligatorios.';
    valid = false;
  }
  else if(auxform['apellido'].value == ''){
    document.getElementById('notreqerr').innerText = 'Todos los campos son obligatorios.';
    valid = false;
  }
  else if(auxform['fechanacimiento'].value == ''){
    document.getElementById('notreqerr').innerText = 'Todos los campos son obligatorios.';
    valid = false;
  }
  else if(auxform['email'].value == ''){
    document.getElementById('notreqerr').innerText = 'Todos los campos son obligatorios.';
    valid = false;
  }
  else if(auxform['tarjeta'].value == ''){
    document.getElementById('notreqerr').innerText = 'Todos los campos son obligatorios.';
    valid = false;
  }
  else if(auxform['contrasena'].value == ''){
    document.getElementById('notreqerr').innerText = 'Todos los campos son obligatorios.';
    valid = false;
  }
  else if(auxform['contrasena'].value != auxform['contrasenaconf'].value){
    document.getElementById('notreqerr').innerText = 'Las contraseñas no coinciden';
    valid = false;
  }
  return valid;
}
