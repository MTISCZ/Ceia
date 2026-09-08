/**
 * tabs.js — Controlador de navegación por pestañas.
 * No conoce el contenido de cada panel: solo muestra/oculta y avisa
 * a main.js qué pestaña se activó, para que cargue sus datos.
 */
(function (global) {
  "use strict";

  let onActivate = null;

  function activar(id) {
    const tabs = Array.from(document.querySelectorAll("nav.tabs button"));
    tabs.forEach((b) => {
      const selected = b.id === id;
      b.setAttribute("aria-selected", selected);
      const panel = document.getElementById(b.getAttribute("aria-controls"));
      panel.hidden = !selected;
      panel.classList.toggle("active", selected);
    });
    document.getElementById(id).focus();
    if (onActivate) onActivate(id);
  }

  function initTabs(callback) {
    onActivate = callback;
    const tabs = Array.from(document.querySelectorAll("nav.tabs button"));
    tabs.forEach((btn) => {
      btn.addEventListener("click", () => activar(btn.id));
      btn.addEventListener("keydown", (e) => {
        const visibles = tabs.filter((b) => !b.hidden);
        const idx = visibles.indexOf(btn);
        if (idx === -1) return;
        if (e.key === "ArrowRight") visibles[(idx + 1) % visibles.length].focus();
        if (e.key === "ArrowLeft") visibles[(idx - 1 + visibles.length) % visibles.length].focus();
      });
    });
  }

  global.CeiaTabs = { initTabs, activar };
})(window);
