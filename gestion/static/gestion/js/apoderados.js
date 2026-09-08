/**
 * apoderados.js — Módulo de la pestaña "Apoderados" (nuevo en EPE 2).
 * Resuelve el pendiente identificado en el informe de EPE 1.
 */
(function (global) {
  "use strict";

  function render(lista) {
    const tbody = document.getElementById("tabla-apoderados");
    tbody.innerHTML = "";
    if (lista.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" class="empty">No se encontraron apoderados.</td></tr>';
      return;
    }
    lista.forEach((a) => {
      const tr = document.createElement("tr");
      tr.innerHTML =
        '<td data-label="Nombre">' + a.nombre_completo + "</td>" +
        '<td data-label="RUT">' + a.rut + "</td>" +
        '<td data-label="Teléfono">' + (a.telefono || "—") + "</td>" +
        '<td data-label="Email">' + (a.email || "—") + "</td>";
      tbody.appendChild(tr);
    });
  }

  async function cargar() {
    const tbody = document.getElementById("tabla-apoderados");
    tbody.innerHTML = '<tr><td colspan="4" class="empty">Cargando…</td></tr>';
    try {
      render(await CeiaAPI.listarApoderados());
    } catch (err) {
      tbody.innerHTML = '<tr><td colspan="4" class="empty">No se pudo cargar el listado de apoderados.</td></tr>';
    }
  }

  function initEvents() {
    document.getElementById("btn-buscar-apoderado").addEventListener("click", async () => {
      const rut = document.getElementById("apoderado-rut-input").value.trim();
      const msg = document.getElementById("msg-apoderados");
      CeiaUI.hideMsg(msg);
      if (!rut) { cargar(); return; }
      try {
        const data = await CeiaAPI.buscarApoderadoPorRut(rut);
        render(data.error ? [] : [data]);
        CeiaUI.showMsg(msg, data.error ? "No se encontró ningún apoderado con ese RUT." : "Apoderado encontrado.", data.error ? "warn" : "ok");
      } catch (err) {
        render([]);
        CeiaUI.showMsg(msg, "No se encontró ningún apoderado con ese RUT.", "warn");
      }
    });
  }

  global.CeiaApoderados = { cargar, initEvents };
})(window);
