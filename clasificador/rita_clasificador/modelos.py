"""Líneas base del clasificador (semanas 5 y 6 del curso).

1. Mayoritaria: siempre la clase más frecuente del entrenamiento. El piso absoluto.
2. Reglas: palabras clave escritas a mano, en el orden de la guía de etiquetado.
   Es lo que haría alguien sin aprendizaje automático.
3. Naïve Bayes multinomial sobre conteos de palabras y pares de palabras.
4. Regresión logística sobre TF-IDF, con C elegido por validación cruzada agrupada por
   guion dentro del entrenamiento. Es la línea base que Kev tiene que superar.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, GroupKFold
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


class Mayoritaria:
    nombre = "mayoritaria"

    def fit(self, x, y, grupos=None):
        self.clase = Counter(y).most_common(1)[0][0]
        self.classes_ = np.array(sorted(set(y)))
        return self

    def predict(self, x):
        return np.array([self.clase] * len(x))

    def predict_proba(self, x):
        p = (self.classes_ == self.clase).astype(float)
        return np.tile(p, (len(x), 1))


REGLAS = [
    ("estafa", r"clave|contrasena|codigo (que|de)|premio|sorteo|se gano|felicitaciones|fiscalia|captura|"
               r"consign|no le diga|numero de (la )?tarjeta|usuario y"),
    ("cobranza", r"deuda|mora\b|cartera|obligacion|acuerdo de pago|centrales de riesgo|cobro|vencid"),
    ("encuesta", r"encuesta|opinion|escala del|satisfech|estudio de"),
    ("comercial", r"\bplan\b|promocion|oferta|seguro|preaprobad|descuento|gigas|megas|gratis|le interesa"),
    ("equivocada", r"equivoq|marque mal|numero equivocado|hablo con|disculpe la molestia"),
    ("legitima", r"cita|pedido|domicili|entrevista|hoja de vida|numero nuevo|cambie de numero|vecin|taller"),
]


class Reglas:
    nombre = "reglas"

    def fit(self, x, y, grupos=None):
        self.respaldo = Counter(y).most_common(1)[0][0]
        self.classes_ = np.array(sorted(set(y)))
        return self

    def _una(self, texto: str) -> str:
        t = normalizar(texto)
        if len(t.split()) < 5:
            return "no_identificable"
        for etiqueta, patron in REGLAS:
            if re.search(patron, t):
                return etiqueta
        return self.respaldo

    def predict(self, x):
        return np.array([self._una(t) for t in x])


def naive_bayes():
    m = make_pipeline(CountVectorizer(ngram_range=(1, 2), strip_accents="unicode", lowercase=True),
                      MultinomialNB(alpha=1.0))
    m.nombre = "naive_bayes"
    return m


class RegresionLogistica:
    nombre = "regresion_logistica"
    REJILLA_C = [0.1, 0.3, 1, 3, 10, 30]

    def fit(self, x, y, grupos):
        tuberia = make_pipeline(
            TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, strip_accents="unicode"),
            LogisticRegression(max_iter=3000, class_weight="balanced"),
        )
        n_grupos = len(set(grupos))
        if n_grupos >= 3:
            busqueda = GridSearchCV(tuberia, {"logisticregression__C": self.REJILLA_C},
                                    cv=GroupKFold(n_splits=min(5, n_grupos)), scoring="f1_macro")
            busqueda.fit(list(x), list(y), groups=list(grupos))
            self.modelo = busqueda.best_estimator_
            self.c_elegido = busqueda.best_params_["logisticregression__C"]
        else:
            self.modelo = tuberia.fit(list(x), list(y))
            self.c_elegido = 1.0
        self.classes_ = self.modelo.classes_
        return self

    def predict(self, x):
        return self.modelo.predict(list(x))

    def predict_proba(self, x):
        return self.modelo.predict_proba(list(x))


def todas():
    return [Mayoritaria(), Reglas(), naive_bayes(), RegresionLogistica()]
