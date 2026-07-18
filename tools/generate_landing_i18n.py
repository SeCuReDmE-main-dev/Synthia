from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

import argostranslate.translate


ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "web" / "landing"
OUTPUT = LANDING / "i18n"
FILES = ("index.html", "trace-lab.html")
ATTRIBUTES = {"aria-label", "alt", "placeholder", "title"}
PROTECTED = (
    "SecuredMe", "Synthia", "Trace Lab", "T-I-F", "JSON", "GitHub", "CLI", "API",
    "Aburria aburri", "Lesson, 1828", "Aguilar H. F. & R. F. Aguilar, 2012",
    "Plithogenic Engine", "Neutrosophic", "Autism Calm", "ADHD Sprint", "Deep Work",
)

OVERRIDES = {
    "fr-CA": {
        "Language": "Langue", "Theme": "Thème", "Access": "Accès", "Theme: Night": "Thème : nuit",
        "Theme: Light": "Thème : jour", "Presentation": "Présentation", "Functionality": "Fonctionnalités",
        "Dashboard": "Tableau de bord", "Governance": "Gouvernance", "Source": "Source",
        "Open Trace Lab": "Ouvrir Trace Lab", "Explore source": "Explorer le code source",
        "Primary navigation": "Navigation principale", "Footer navigation": "Navigation de pied de page",
        "Close": "Fermer", "Profile": "Profil", "Contrast": "Contraste", "Large text": "Texte agrandi",
        "Reduced motion": "Mouvement réduit", "Overview": "Présentation", "Public JSON": "JSON public",
        "Code": "Code", "Back to Synthia": "Retour à Synthia", "Public trace": "Trace publique",
        "Open JSON contract": "Ouvrir le contrat JSON", "CLI source": "Source CLI",
        "Landing": "Accueil", "Human review required": "Révision humaine requise",
        "Synthia Engine: lexical intelligence and uncertainty management.": "Synthia Engine : intelligence lexicale et gestion de l’incertitude.",
        "Engine: lexical intelligence and uncertainty management.": "Engine : intelligence lexicale et gestion de l’incertitude.",
        "This static proof surface shows how Synthia exposes source lineage, unresolved layers, and the human-review boundary for a scientific-memory candidate.": "Cette surface de preuve statique montre comment Synthia expose la filiation des sources, les couches non résolues et la frontière de relecture humaine d’une mémoire scientifique candidate.",
    },
    "es": {
        "Language": "Idioma", "Theme": "Tema", "Access": "Acceso", "Theme: Night": "Tema: noche",
        "Theme: Light": "Tema: día", "Presentation": "Presentación", "Functionality": "Funcionalidades",
        "Dashboard": "Panel", "Governance": "Gobernanza", "Source": "Código fuente",
        "Open Trace Lab": "Abrir Trace Lab", "Explore source": "Explorar el código fuente",
        "Primary navigation": "Navegación principal", "Footer navigation": "Navegación del pie de página",
        "Close": "Cerrar", "Profile": "Perfil", "Contrast": "Contraste", "Large text": "Texto grande",
        "Reduced motion": "Movimiento reducido", "Overview": "Presentación", "Public JSON": "JSON público",
        "Code": "Código", "Back to Synthia": "Volver a Synthia", "Public trace": "Traza pública",
        "Open JSON contract": "Abrir el contrato JSON", "CLI source": "Fuente CLI",
        "Landing": "Inicio", "Human review required": "Revisión humana requerida",
        "Synthia Engine: lexical intelligence and uncertainty management.": "Synthia Engine: inteligencia léxica y gestión de la incertidumbre.",
        "Engine: lexical intelligence and uncertainty management.": "Engine: inteligencia léxica y gestión de la incertidumbre.",
        "This static proof surface shows how Synthia exposes source lineage, unresolved layers, and the human-review boundary for a scientific-memory candidate.": "Esta superficie de prueba estática muestra cómo Synthia expone la procedencia de las fuentes, las capas no resueltas y el límite de revisión humana de una memoria científica candidata.",
    },
}


def normalize(value: str) -> str:
    return " ".join(value.split())


class Extractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.values: set[str] = set()
        self.skip = 0

    def add(self, value: str | None) -> None:
        canonical = normalize(value or "")
        if canonical and any(character.isalpha() for character in canonical):
            self.values.add(canonical)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "code", "pre"}:
            self.skip += 1
        mapping = dict(attrs)
        if tag == "meta" and (mapping.get("name") == "description" or mapping.get("property", "").startswith("og:")):
            self.add(mapping.get("content"))
        for name, value in attrs:
            if name in ATTRIBUTES:
                self.add(value)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "code", "pre"} and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.add(data)


def protect(value: str) -> tuple[str, dict[str, str]]:
    result = value
    mapping: dict[str, str] = {}
    for index, term in enumerate(sorted(PROTECTED, key=len, reverse=True)):
        if term in result:
            token = f"ZXQ{index}QXZ"
            result = result.replace(term, token)
            mapping[token] = term
    return result, mapping


def restore(value: str, mapping: dict[str, str]) -> str:
    result = value
    for token, term in mapping.items():
        result = re.sub(re.escape(token), term, result, flags=re.IGNORECASE)
    return result


def main() -> int:
    extractor = Extractor()
    for name in FILES:
        extractor.feed((LANDING / name).read_text(encoding="utf-8"))
    canonical = sorted(extractor.values)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "en-CA.json").write_text(json.dumps({"locale": "en-CA", "strings": {v: v for v in canonical}}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for locale, target in (("fr-CA", "fr"), ("es", "es")):
        translator = argostranslate.translate.get_translation_from_codes("en", target)
        if translator is None:
            raise SystemExit(f"Missing Argos model en->{target}")
        strings: dict[str, str] = {}
        for value in canonical:
            if value in OVERRIDES[locale]:
                strings[value] = OVERRIDES[locale][value]
                continue
            protected, mapping = protect(value)
            strings[value] = restore(translator.translate(protected), mapping).strip()
        payload = {"locale": locale, "status": "machine-draft-with-reviewed-core-glossary", "strings": strings}
        (OUTPUT / f"{locale}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated Synthia landing catalogs with {len(canonical)} strings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
