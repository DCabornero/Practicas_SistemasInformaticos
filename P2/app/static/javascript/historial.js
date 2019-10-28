function toggler(id){
  $('.body'+id).toggle(500);
  var original = $("#detalle"+id).text();
  $("#detalle"+id).text(original == "Mostrar detalles" ? "Ocultar detalles" : "Mostrar detalles");
};
