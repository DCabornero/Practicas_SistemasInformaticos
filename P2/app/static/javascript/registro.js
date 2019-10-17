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
