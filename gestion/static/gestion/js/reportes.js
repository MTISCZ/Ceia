/**
 * reportes.js — Módulo de la pestaña "Reportes".
 */
(function (global) {
  "use strict";

  async function cargar() {
    const bars = document.getElementById("bars");
    bars.innerHTML = '<p class="empty">Cargando…</p>';
    try {
      const data = await CeiaAPI.reportePorCurso();

      document.getElementById("stat-cursos").textContent = data.length;
      document.getElementById("stat-estudiantes").textContent = data.reduce((s, d) => s + d.total_estudiantes, 0);
      document.getElementById("stat-atrasos").textContent = data.reduce((s, d) => s + d.total_atrasos, 0);

      const maxAtrasos = Math.max(1, ...data.map((d) => d.total_atrasos));
      bars.innerHTML = "";
      if (data.length === 0) { bars.innerHTML = '<p class="empty">Sin datos para mostrar.</p>'; }
      data.forEach((d) => {
        const row = document.createElement("div");
        row.className = "bar-row";
        const pct = Math.round((d.total_atrasos / maxAtrasos) * 100);
        row.innerHTML =
          '<div class="name">' + d.curso + "</div>" +
          '<div class="bar-track"><div class="bar-fill" style="width:' + pct + '%"></div></div>' +
          '<div class="val">' + d.total_atrasos + "</div>";
        bars.appendChild(row);
      });

      const tbody = document.getElementById("tabla-reportes");
      tbody.innerHTML = "";
      data.forEach((d) => {
        const tr = document.createElement("tr");
        tr.innerHTML =
          '<td data-label="Curso">' + d.curso + "</td>" +
          '<td data-label="Estudiantes">' + d.total_estudiantes + "</td>" +
          '<td data-label="Atrasos (mes)">' + d.total_atrasos + "</td>" +
          '<td data-label="Promedio minutos">' + d.promedio_minutos + "</td>";
        tbody.appendChild(tr);
      });
    } catch (err) {
      bars.innerHTML = '<p class="empty">No se pudo cargar el reporte.</p>';
    }
  }

  global.CeiaReportes = { cargar };
})(window);
