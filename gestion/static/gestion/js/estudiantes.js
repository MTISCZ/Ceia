/**
 * estudiantes.js — Módulo de la pestaña "Estudiantes".
 * Expone CeiaEstudiantes.cargar() para que main.js lo invoque al activar
 * la pestaña, y mantiene su propia caché para no repetir llamadas.
 */
(function (global) {
  "use strict";

  let cache = [];

  function render(lista) {
    const tbody = document.querySelector("#tabla-estudiantes tbody");
    tbody.innerHTML = "";
    if (lista.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="empty">No se encontraron estudiantes.</td></tr>';
      return;
    }
    lista.forEach((e) => {
      const tr = document.createElement("tr");
      tr.innerHTML =
        '<td data-label="Nombre">' + CeiaUI.fullName(e) + "</td>" +
        '<td data-label="RUT">' + e.rut + "</td>" +
        '<td data-label="Curso">' + e.curso + "</td>" +
        '<td data-label="Apoderado">' + (e.email_apoderado || "—") + "</td>" +
        '<td data-label="Acción"><button class="btn sm ghost" data-goto-atraso="' + e.id_estudiante + '">Registrar atraso</button></td>';
      tbody.appendChild(tr);
    });
  }

  function pobladoCursos(lista) {
    const cursos = [...new Set(lista.map((e) => e.curso))].sort();
    const sel = document.getElementById("curso-select");
    sel.innerHTML = '<option value="">Todos los cursos</option>';
    cursos.forEach((c) => {
      const opt = document.createElement("option");
      opt.value = c; opt.textContent = c;
      sel.appendChild(opt);
    });
  }

  async function cargar() {
    try {
      cache = await CeiaAPI.listarEstudiantes();
      CeiaUI.setApiStatus(true);
      render(cache);
      pobladoCursos(cache);
      global.CeiaAtrasos && global.CeiaAtrasos.pobladoSelectEstudiantes(cache);
      return cache;
    } catch (err) {
      CeiaUI.setApiStatus(false);
      CeiaUI.showMsg(document.getElementById("msg-estudiantes"),
        "No se pudo conectar con la API (" + err.message + "). Verifica que el servidor Django esté corriendo.", "warn");
      return [];
    }
  }

  function getCache() { return cache; }

  function initEvents() {
    document.querySelector("#tabla-estudiantes").addEventListener("click", (e) => {
      const id = e.target.getAttribute("data-goto-atraso");
      if (id && global.CeiaTabs) {
        document.getElementById("atraso-estudiante").value = id;
        global.CeiaTabs.activar("tab-atrasos");
      }
    });

    document.getElementById("btn-buscar-est").addEventListener("click", async () => {
      const rut = document.getElementById("rut-input").value.trim();
      const curso = document.getElementById("curso-select").value;
      const msg = document.getElementById("msg-estudiantes");
      CeiaUI.hideMsg(msg);
      try {
        let data;
        if (rut) {
          const est = await CeiaAPI.buscarEstudiantePorRut(rut);
          data = est.error ? [] : [est];
        } else if (curso) {
          data = await CeiaAPI.estudiantesPorCurso(curso);
        } else {
          data = await CeiaAPI.listarEstudiantes();
        }
        render(data);
        CeiaUI.showMsg(msg,
          data.length ? (data.length + " estudiante(s) encontrado(s).") : "No se encontró ningún estudiante con esos criterios.",
          data.length ? "ok" : "warn");
      } catch (err) {
        render([]);
        CeiaUI.showMsg(msg, "No se encontró ningún estudiante con esos criterios.", "warn");
      }
    });

    document.getElementById("btn-limpiar-est").addEventListener("click", () => {
      document.getElementById("rut-input").value = "";
      document.getElementById("curso-select").value = "";
      render(cache);
      CeiaUI.hideMsg(document.getElementById("msg-estudiantes"));
    });
  }

  global.CeiaEstudiantes = { cargar, getCache, initEvents };
})(window);
