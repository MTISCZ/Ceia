/**
 * inventario.js — Módulo de la pestaña "Inventario".
 */
(function (global) {
  "use strict";

  function render(productos) {
    const tbody = document.getElementById("tabla-inventario");
    tbody.innerHTML = "";
    if (productos.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="empty">No hay productos cargados.</td></tr>';
      return;
    }
    productos.forEach((p) => {
      const critico = p.stock_actual <= p.stock_minimo;
      const tr = document.createElement("tr");
      tr.innerHTML =
        '<td data-label="Producto">' + p.nombre + "</td>" +
        '<td data-label="Ubicación">' + (p.ubicacion || "—") + "</td>" +
        '<td data-label="Stock">' + p.stock_actual + "</td>" +
        '<td data-label="Mínimo">' + p.stock_minimo + "</td>" +
        '<td data-label="Estado"><span class="pill ' + (critico ? "warn" : "ok") + '">' + (critico ? "Stock crítico" : "OK") + "</span></td>" +
        '<td data-label="Movimiento">' +
        '<button class="btn sm ghost" data-in="' + p.id_producto + '">+10 ingreso</button> ' +
        '<button class="btn sm ghost" data-out="' + p.id_producto + '">-10 despacho</button>' +
        "</td>";
      tbody.appendChild(tr);
    });
  }

  async function cargar() {
    const tbody = document.getElementById("tabla-inventario");
    tbody.innerHTML = '<tr><td colspan="6" class="empty">Cargando…</td></tr>';
    try {
      render(await CeiaAPI.listarProductos());
    } catch (err) {
      tbody.innerHTML = '<tr><td colspan="6" class="empty">No se pudo cargar el inventario.</td></tr>';
    }
  }

  function initEvents() {
    document.getElementById("tabla-inventario").addEventListener("click", async (e) => {
      const msg = document.getElementById("msg-inventario");
      const inId = e.target.getAttribute("data-in");
      const outId = e.target.getAttribute("data-out");
      if (!inId && !outId) return;
      const usuario = (global.CeiaAuth && global.CeiaAuth.usuarioActual())
        ? global.CeiaAuth.usuarioActual().email : "panel-web";
      try {
        const data = inId
          ? await CeiaAPI.subirStock(inId, 10, usuario)
          : await CeiaAPI.bajarStock(outId, 10, usuario);
        CeiaUI.showMsg(msg, (inId ? "Ingreso" : "Despacho") + " registrado: " + data.producto + " → nuevo stock " + data.stock_actual + ".", "ok");
        cargar();
      } catch (err) {
        CeiaUI.showMsg(msg, err.message || "No se pudo registrar el movimiento.", "warn");
      }
    });
  }

  global.CeiaInventario = { cargar, initEvents };
})(window);
