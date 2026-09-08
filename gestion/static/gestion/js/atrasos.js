/**
 * atrasos.js — Módulo de la pestaña "Atrasos".
 */
(function (global) {
  "use strict";

  function pobladoSelectEstudiantes(lista) {
    const sel = document.getElementById("atraso-estudiante");
    sel.innerHTML = "";
    lista.forEach((e) => {
      const opt = document.createElement("option");
      opt.value = e.id_estudiante;
      opt.textContent = CeiaUI.fullName(e) + " — " + e.rut + " (" + e.curso + ")";
      sel.appendChild(opt);
    });
  }

  async function cargar() {
    const tbody = document.getElementById("tabla-atrasos");
    tbody.innerHTML = '<tr><td colspan="4" class="empty">Cargando…</td></tr>';
    try {
      const data = await CeiaAPI.listarAtrasos();
      const estudiantes = global.CeiaEstudiantes ? global.CeiaEstudiantes.getCache() : [];
      const hoy = new Date();
      const delMes = data.filter((a) => new Date(a.fecha + "T00:00:00").getMonth() === hoy.getMonth());
      tbody.innerHTML = "";
      if (delMes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty">No hay atrasos registrados este mes.</td></tr>';
        return;
      }
      delMes.slice().reverse().forEach((a) => {
        const est = estudiantes.find((e) => e.id_estudiante === a.id_estudiante);
        const tr = document.createElement("tr");
        tr.innerHTML =
          '<td data-label="Estudiante">' + (est ? CeiaUI.fullName(est) : ("ID " + a.id_estudiante)) + "</td>" +
          '<td data-label="Curso">' + (est ? est.curso : "—") + "</td>" +
          '<td data-label="Fecha">' + a.fecha + "</td>" +
          '<td data-label="Minutos">' + a.minutos_atraso + "</td>";
        tbody.appendChild(tr);
      });
    } catch (err) {
      tbody.innerHTML = '<tr><td colspan="4" class="empty">No se pudo cargar el listado de atrasos.</td></tr>';
    }
  }

  function initEvents() {
    document.getElementById("btn-registrar-atraso").addEventListener("click", async () => {
      const id_estudiante = document.getElementById("atraso-estudiante").value;
      const minutos_atraso = parseInt(document.getElementById("atraso-minutos").value, 10) || 15;
      const msg = document.getElementById("msg-atrasos");
      const btn = document.getElementById("btn-registrar-atraso");
      if (!id_estudiante) {
        CeiaUI.showMsg(msg, "No hay estudiantes cargados todavía.", "warn");
        return;
      }
      btn.disabled = true;
      try {
        const data = await CeiaAPI.registrarAtraso(id_estudiante, minutos_atraso);
        if (data.notificar_apoderado) {
          CeiaUI.showMsg(msg, "Atraso registrado. Acumula " + data.atrasos_mes + " atrasos este mes: se notificará a " + data.email_apoderado + ".", "warn");
        } else {
          CeiaUI.showMsg(msg, "Atraso registrado correctamente. Atrasos del mes: " + data.atrasos_mes + ".", "ok");
        }
        cargar();
      } catch (err) {
        CeiaUI.showMsg(msg, err.message || "No se pudo registrar el atraso.", "warn");
      } finally {
        btn.disabled = false;
      }
    });
  }

  global.CeiaAtrasos = { cargar, initEvents, pobladoSelectEstudiantes };
})(window);
