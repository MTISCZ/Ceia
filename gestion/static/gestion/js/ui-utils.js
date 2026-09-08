/**
 * ui-utils.js — Helpers de interfaz compartidos por todos los módulos.
 * Evita repetir la misma lógica de mensajes/formato en cada archivo.
 */
(function (global) {
  "use strict";

  function showMsg(el, text, type) {
    el.textContent = text;
    el.className = "msg show " + type;
  }

  function hideMsg(el) {
    el.className = "msg";
  }

  function fullName(estudiante) {
    return [estudiante.nombre, estudiante.apellido_paterno, estudiante.apellido_materno]
      .filter(Boolean).join(" ");
  }

  function setApiStatus(ok) {
    const el = document.getElementById("api-status");
    if (!el) return;
    el.textContent = ok ? "Conectado a la API" : "Sin conexión a la API";
    el.classList.toggle("live", ok);
  }

  global.CeiaUI = { showMsg, hideMsg, fullName, setApiStatus };
})(window);
