/**
 * auth.js — Login y control de acceso por rol.
 * La sesión se guarda solo en memoria (variable JS): al recargar la
 * página se pide iniciar sesión de nuevo. Es intencional para esta
 * etapa: evita depender de cookies/localStorage mientras no exista
 * un mecanismo de sesión de servidor (token/JWT), que queda para
 * una etapa posterior.
 */
(function (global) {
  "use strict";

  const TABS_POR_ROL = {
    director: ["tab-estudiantes", "tab-atrasos", "tab-inventario", "tab-apoderados", "tab-reportes"],
    administrativo: ["tab-estudiantes", "tab-atrasos", "tab-inventario", "tab-reportes"],
    consulta: ["tab-estudiantes", "tab-reportes"],
  };

  let sesion = null;

  function usuarioActual() { return sesion; }

  function aplicarVisibilidadPorRol() {
    const permitidas = sesion ? (TABS_POR_ROL[sesion.rol] || []) : [];
    document.querySelectorAll("nav.tabs button").forEach((btn) => {
      btn.hidden = !permitidas.includes(btn.id);
    });
  }

  function mostrarApp() {
    document.getElementById("login-screen").hidden = true;
    document.getElementById("app-shell").hidden = false;
    document.getElementById("user-chip").textContent =
      sesion.nombre_completo + " · " + sesion.rol;
    aplicarVisibilidadPorRol();
    // Activa la primera pestaña visible para este rol
    const primera = document.querySelector("nav.tabs button:not([hidden])");
    if (primera && global.CeiaTabs) global.CeiaTabs.activar(primera.id);
  }

  function mostrarLogin() {
    sesion = null;
    document.getElementById("login-screen").hidden = false;
    document.getElementById("app-shell").hidden = true;
  }

  function initAuth() {
    const form = document.getElementById("login-form");
    const msg = document.getElementById("msg-login");
    const btn = document.getElementById("btn-login");

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = document.getElementById("login-email").value.trim();
      const password = document.getElementById("login-password").value;
      CeiaUI.hideMsg(msg);
      btn.disabled = true;
      try {
        const data = await CeiaAPI.login(email, password);
        sesion = data.usuario;
        mostrarApp();
      } catch (err) {
        CeiaUI.showMsg(msg, err.message || "No se pudo iniciar sesión.", "warn");
      } finally {
        btn.disabled = false;
      }
    });

    document.getElementById("btn-logout").addEventListener("click", mostrarLogin);
  }

  global.CeiaAuth = { initAuth, usuarioActual, mostrarLogin, mostrarApp };
})(window);
