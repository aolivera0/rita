"""Clasificador del prototipo: TF-IDF + regresión logística, más pistas por reglas.

Es la línea base de la propuesta. Kev necesita GPU y se prueba aparte (Colab o Kaggle);
cuando esté listo, basta con otra función que devuelva el mismo formato de Clasificación.
"""

from __future__ import annotations

import re
import unicodedata

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline

from .datos_sinteticos import CATEGORIAS, generar

# Cada pista es una pregunta de sí o no. Aquí se responde con reglas (0 o 1);
# con Kev serían probabilidades.
PISTAS = {
    "pide_datos_bancarios": r"clave|contrasena|numero de (la )?tarjeta|codigo de|codigo que|usuario y|datos bancarios|cvv|pin\b",
    "pide_pago_o_transferencia": r"consign|transferencia|transfier|pagar|pague|pago|multa|abono|mande .*(plata|pesos)|deposit|numero de cuenta",
    "presiona_con_urgencia": r"urgente|ya mismo|hoy mismo|ahora mismo|inmediat|en \w+ minutos|antes de (que|las)|solo por hoy|no le diga|pierde",
    "dice_ser_autoridad": r"fiscal|policia|juzgado|dian\b|captura|proceso penal|embargo",
    "ofrece_premio_o_regalo": r"gano|ganaste|premio|sorteo|felicitaciones|gratis|reembolso|le vamos a devolver",
    "intenta_manipular_al_asistente": r"clasifica|ignora (tus|las|todas)|olvida (tus|las)|eres un|marca (esta|la) llamada|legitima|instrucciones",
}

NOMBRES_PISTA = {
    "pide_datos_bancarios": "¿Pide datos bancarios, claves o códigos?",
    "pide_pago_o_transferencia": "¿Pide un pago o una transferencia?",
    "presiona_con_urgencia": "¿Presiona con urgencia?",
    "dice_ser_autoridad": "¿Dice ser una autoridad?",
    "ofrece_premio_o_regalo": "¿Ofrece un premio, regalo o devolución?",
    "intenta_manipular_al_asistente": "¿Intenta darle instrucciones al asistente?",
}


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def pistas(texto: str) -> dict[str, float]:
    t = normalizar(texto)
    return {k: 1.0 if re.search(p, t) else 0.0 for k, p in PISTAS.items()}


def _texto(turnos: list[str]) -> str:
    return " ".join(turnos)


def _nuevo_modelo():
    return make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, strip_accents="unicode",
                        min_df=1),
        LogisticRegression(max_iter=2000, C=4.0, class_weight="balanced"),
    )


class Clasificador:
    nombre_modelo = "tfidf-regresion-logistica"

    def __init__(self) -> None:
        ejemplos = generar()
        self.x = [_texto(e["turnos"]) for e in ejemplos]
        self.y = [e["categoria"] for e in ejemplos]
        self.grupos = [e["guion_id"] for e in ejemplos]
        self.metricas = self._validacion_cruzada()
        self.modelo = _nuevo_modelo().fit(self.x, self.y)

    def _validacion_cruzada(self) -> dict:
        """Validación cruzada agrupada por guion: ningún guion queda a los dos lados."""
        y = np.array(self.y)
        pred = np.empty_like(y)
        x = np.array(self.x, dtype=object)
        for tr, te in GroupKFold(n_splits=5).split(x, y, self.grupos):
            m = _nuevo_modelo().fit(list(x[tr]), list(y[tr]))
            pred[te] = m.predict(list(x[te]))
        legit = y == "legitima"
        fp_legit = float(np.mean(pred[legit] != "legitima")) if legit.any() else 0.0
        return {
            "ejemplos": len(y),
            "guiones": len(set(self.grupos)),
            "f1_macro": round(float(f1_score(y, pred, average="macro")), 3),
            "exactitud": round(float(np.mean(pred == y)), 3),
            "legitimas_mal_marcadas": round(fp_legit, 3),
            "categorias": CATEGORIAS,
            "matriz_confusion": confusion_matrix(y, pred, labels=CATEGORIAS).tolist(),
        }

    def clasificar(self, texto_llamante: str, llamada_id: str | None = None) -> dict:
        """Devuelve el formato *Clasificación* acordado entre frentes."""
        if not texto_llamante.strip():
            probs = {c: 0.0 for c in CATEGORIAS}
            probs["no_identificable"] = 1.0
        else:
            p = self.modelo.predict_proba([texto_llamante])[0]
            probs = {c: round(float(v), 4) for c, v in zip(self.modelo.classes_, p)}
        etiqueta = max(probs, key=probs.get)
        return {
            "llamada_id": llamada_id,
            "modelo": self.nombre_modelo,
            "etiqueta": etiqueta,
            "confianza": probs[etiqueta],
            "probabilidades": dict(sorted(probs.items(), key=lambda kv: -kv[1])),
            "pistas": pistas(texto_llamante),
        }
