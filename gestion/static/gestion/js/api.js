/**
 * api.js — Cliente HTTP centralizado.
 * Único punto de la app que sabe cómo hablar con el backend (/api/...).
 * Todos los demás módulos importan window.CeiaAPI en vez de usar fetch()
 * directamente, para que un cambio en la forma de llamar a la API
 * (headers, manejo de errores, base URL) se haga en un solo lugar.
 */
(function (global) {
  "use strict";

  const BASE = "/api";

  async function request(path, opts) {
    const res = await fetch(BASE + path, Object.assign(
      { headers: { "Content-Type": "application/json" } },
      opts || {}
    ));
    let data = null;
    try { data = await res.json(); } catch (e) { /* respuesta vacía, ok */ }
    if (!res.ok) {
      const err = new Error((data && (data.error || data.detail)) || ("Error " + res.status));
      err.status = res.status;
      err.data = data;
      throw err;
    }
    return data;
  }

  const CeiaAPI = {
    get: (path) => request(path, { method: "GET" }),
    post: (path, body) => request(path, { method: "POST", body: JSON.stringify(body || {}) }),

    // Estudiantes
    listarEstudiantes: () => request("/estudiantes/"),
    buscarEstudiantePorRut: (rut) => request("/estudiantes/buscar_por_rut/?rut=" + encodeURIComponent(rut)),
    estudiantesPorCurso: (curso) => request("/estudiantes/por_curso/?curso=" + encodeURIComponent(curso)),

    // Atrasos
    listarAtrasos: () => request("/atrasos/"),
    registrarAtraso: (id_estudiante, minutos_atraso) =>
      request("/atrasos/registrar/", { method: "POST", body: JSON.stringify({ id_estudiante, minutos_atraso }) }),
    reportePorCurso: () => request("/atrasos/reporte_por_curso/"),

    // Inventario
    listarProductos: () => request("/productos/"),
    subirStock: (id_producto, cantidad, usuario_responsable) =>
      request("/movimientos/subir_stock/", { method: "POST", body: JSON.stringify({ id_producto, cantidad, usuario_responsable }) }),
    bajarStock: (id_producto, cantidad, usuario_responsable) =>
      request("/movimientos/bajar_stock/", { method: "POST", body: JSON.stringify({ id_producto, cantidad, usuario_responsable }) }),

    // Apoderados
    listarApoderados: () => request("/apoderados/"),
    buscarApoderadoPorRut: (rut) => request("/apoderados/buscar_por_rut/?rut=" + encodeURIComponent(rut)),
    apoderadosPorEstudiante: (id_estudiante) => request("/estudiante-apoderado/por_estudiante/?id_estudiante=" + id_estudiante),

    // Autenticación
    login: (email, password) => request("/login/", { method: "POST", body: JSON.stringify({ email, password }) }),
  };

  global.CeiaAPI = CeiaAPI;
})(window);
