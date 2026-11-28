"""Métricas e intervalos de confianza.

Por qué estas métricas (va en el informe):
- F1 macro: las clases están desbalanceadas y todas importan; la exactitud premiaría
  acertar solo las frecuentes.
- Legítimas mal marcadas: el error más caro. Marcar como estafa o spam la llamada del
  médico o de un familiar hace que el usuario la pierda; dejar pasar un spam solo le
  cuesta revisarlo en el panel. Es la cifra principal.
- Estafas detectadas (recall de estafa): el segundo error más caro.
- ECE (error de calibración esperado): si el modelo dice 90 %, ¿acierta el 90 % de las
  veces? Importa porque mostramos la confianza al usuario y elegimos umbrales con ella.
- Intervalos: Wilson para proporciones (funciona bien con pocos casos) y bootstrap por
  guion para el F1 (se remuestrean guiones enteros, porque sus variaciones no son
  independientes).
"""

from __future__ import annotations

import math

import numpy as np
from sklearn.metrics import f1_score, precision_recall_fscore_support


def wilson(aciertos: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = aciertos / n
    centro = (p + z * z / (2 * n)) / (1 + z * z / n)
    margen = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, centro - margen), min(1.0, centro + margen))


def f1_macro(y, p, etiquetas=None) -> float:
    # Promedio sobre las clases que aparecen (reales o predichas), como hace scikit-learn
    # por defecto. Así el bootstrap no cuenta como cero una clase que no salió en la muestra.
    return float(f1_score(y, p, average="macro", zero_division=0))


def bootstrap_por_grupo(y, p, grupos, etiquetas, repeticiones: int = 1000, semilla: int = 0) -> tuple[float, float]:
    y, p, grupos = np.asarray(y), np.asarray(p), np.asarray(grupos)
    unicos = np.unique(grupos)
    indices = {g: np.flatnonzero(grupos == g) for g in unicos}
    rng = np.random.default_rng(semilla)
    valores = []
    for _ in range(repeticiones):
        muestra = rng.choice(unicos, size=len(unicos), replace=True)
        idx = np.concatenate([indices[g] for g in muestra])
        valores.append(f1_macro(y[idx], p[idx], etiquetas))
    return (float(np.percentile(valores, 2.5)), float(np.percentile(valores, 97.5)))


def ece(y, probabilidades: np.ndarray, clases: list[str], bins: int = 10) -> float:
    """Error de calibración esperado con la confianza de la clase predicha."""
    probabilidades = np.asarray(probabilidades, dtype=float)
    confianza = probabilidades.max(axis=1)
    prediccion = np.asarray(clases)[probabilidades.argmax(axis=1)]
    acierto = prediccion == np.asarray(y)
    total, n = 0.0, len(y)
    bordes = np.linspace(0, 1, bins + 1)
    for lo, hi in zip(bordes[:-1], bordes[1:]):
        en = (confianza > lo) & (confianza <= hi) if lo > 0 else (confianza >= lo) & (confianza <= hi)
        if en.any():
            total += en.sum() / n * abs(acierto[en].mean() - confianza[en].mean())
    return float(total)


def calcular(y, p, grupos, etiquetas: list[str], probabilidades=None, clases=None,
             repeticiones: int = 1000) -> dict:
    y, p = np.asarray(y), np.asarray(p)
    legit = y == "legitima"
    legit_mal = int((p[legit] != "legitima").sum())
    legit_estafa = int((p[legit] == "estafa").sum())
    estafa = y == "estafa"
    estafa_ok = int((p[estafa] == "estafa").sum())
    prec, rec, f1, soporte = precision_recall_fscore_support(y, p, labels=etiquetas, zero_division=0)

    resultado = {
        "n": int(len(y)),
        "exactitud": float((y == p).mean()),
        "f1_macro": f1_macro(y, p, etiquetas),
        "f1_macro_ic95": bootstrap_por_grupo(y, p, grupos, etiquetas, repeticiones),
        "legitimas": int(legit.sum()),
        "legitimas_mal_marcadas": legit_mal / legit.sum() if legit.any() else float("nan"),
        "legitimas_mal_marcadas_ic95": wilson(legit_mal, int(legit.sum())),
        "legitimas_marcadas_estafa": legit_estafa / legit.sum() if legit.any() else float("nan"),
        "estafas": int(estafa.sum()),
        "estafas_detectadas": estafa_ok / estafa.sum() if estafa.any() else float("nan"),
        "estafas_detectadas_ic95": wilson(estafa_ok, int(estafa.sum())),
        "por_clase": {e: {"precision": float(prec[i]), "recall": float(rec[i]), "f1": float(f1[i]),
                          "soporte": int(soporte[i])} for i, e in enumerate(etiquetas)},
        "ece": None,
    }
    if probabilidades is not None:
        resultado["ece"] = ece(y, probabilidades, clases)
    return resultado
