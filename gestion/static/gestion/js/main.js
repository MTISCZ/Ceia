/**
 * main.js — Punto de entrada de la aplicación.
 * Orquesta los módulos (auth, tabs, estudiantes, atrasos, inventario,
 * apoderados, reportes) pero no contiene lógica de negocio propia:
 * cada módulo es responsable de su pestaña.
 */
(function () {
  "use strict";

  function onTabActivated(id) {
    if (id === "tab-estudiantes") CeiaEstudiantes.cargar();
    if (id === "tab-atrasos") CeiaAtrasos.cargar();
    if (id === "tab-inventario") CeiaInventario.cargar();
    if (id === "tab-apoderados") CeiaApoderados.cargar();
    if (id === "tab-reportes") CeiaReportes.cargar();
  }

  document.addEventListener("DOMContentLoaded", () => {
    CeiaAuth.initAuth();
    CeiaTabs.initTabs(onTabActivated);
    CeiaEstudiantes.initEvents();
    CeiaAtrasos.initEvents();
    CeiaInventario.initEvents();
    CeiaApoderados.initEvents();
    // La pestaña Estudiantes se carga automáticamente al iniciar sesión,
    // dentro de CeiaAuth.mostrarApp() -> CeiaTabs.activar(primera pestaña visible).
  });
})();
