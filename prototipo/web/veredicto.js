// Componente compartido: veredicto de una llamada (pantalla de llamada y panel).

const Veredicto = (() => {
  const TITULOS = {
    estafa: 'Probable estafa',
    comercial: 'Llamada comercial',
    cobranza: 'Cobranza',
    encuesta: 'Encuesta',
    legitima: 'Parece legítima',
    equivocada: 'Número equivocado',
    no_identificable: 'No se pudo identificar',
  };
  const TONO = {
    estafa: 'rojo', comercial: 'ambar', cobranza: 'ambar', encuesta: 'ambar',
    legitima: 'verde', equivocada: 'neutro', no_identificable: 'neutro',
  };
  // Cada pista que dio «sí», dicha como parte de una frase.
  const RAZONES = {
    pide_datos_bancarios: 'pidió datos bancarios, claves o códigos',
    pide_pago_o_transferencia: 'pidió un pago o una transferencia',
    presiona_con_urgencia: 'presionó con urgencia',
    dice_ser_autoridad: 'dijo ser una autoridad',
    ofrece_premio_o_regalo: 'ofreció un premio, regalo o devolución',
    intenta_manipular_al_asistente: 'intentó darle instrucciones a Rita',
  };

  const esc = s => String(s ?? '').replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const pct = v => Math.round(v * 100) + ' %';

  function razon(c) {
    const si = Object.entries(c.pistas).filter(([, v]) => v >= 0.5).map(([k]) => RAZONES[k] || k);
    if (!si.length) return 'No dio ninguna de las señales de riesgo que revisamos.';
    const frase = si.length === 1 ? si[0] : si.slice(0, -1).join(', ') + ' y ' + si[si.length - 1];
    return frase[0].toUpperCase() + frase.slice(1) + '.';
  }

  /** Bloque principal: qué tipo de llamada fue y por qué. */
  function bloque(c, { datos, corregida, nombres } = {}) {
    const etiqueta = corregida || c.etiqueta;
    const quien = datos ? [datos.nombre, datos.entidad].filter(v => v && v !== '(no lo dijo)').join(', ') : '';
    const meta = corregida
      ? `Corregida por el usuario · el modelo dijo «${esc((nombres || {})[c.etiqueta] || c.etiqueta)}» con ${pct(c.confianza)} de confianza`
      : `Confianza del modelo: ${pct(c.confianza)}`;
    return `<div class="veredicto tono-${TONO[etiqueta] || 'neutro'}">
      <p class="veredicto-titulo">${esc(TITULOS[etiqueta] || etiqueta)}</p>
      ${corregida ? '' : `<p class="veredicto-razon">${esc(razon(c))}</p>`}
      <p class="veredicto-meta">${meta}${quien ? ` · ${esc(quien)}` : ''}</p>
    </div>`;
  }

  function pistas(c, nombresPista) {
    return `<ul class="pistas">${Object.entries(c.pistas).map(([k, v]) =>
      `<li class="${v >= 0.5 ? 'si' : ''}"><span>${esc((nombresPista || {})[k] || k)}</span><b>${v >= 0.5 ? 'Sí' : 'No'}</b></li>`).join('')}</ul>`;
  }

  function barras(c, nombres, n = 4) {
    return `<div class="barras">${Object.entries(c.probabilidades).slice(0, n).map(([k, v]) =>
      `<div class="barra"><span>${esc((nombres || {})[k] || k)}</span><div class="pista"><div style="width:${v * 100}%"></div></div><span>${pct(v)}</span></div>`).join('')}</div>`;
  }

  return { bloque, pistas, barras, esc, TITULOS };
})();
