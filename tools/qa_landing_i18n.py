from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "qa" / "i18n"
BASE_URL = "http://127.0.0.1:8796/"
PAGES = {
    "landing": {"path": "index.html", "selector": "main h1", "expected": {"fr-CA": "intelligence lexicale", "en-CA": "lexical intelligence", "es": "inteligencia léxica"}},
    "trace": {"path": "trace-lab.html", "selector": ".lead", "expected": {"fr-CA": "relecture humaine", "en-CA": "human-review", "es": "revisión humana"}},
}
VIEWPORTS = {"desktop": {"width": 1440, "height": 1000}, "mobile": {"width": 390, "height": 844}}


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    checks: list[dict[str, object]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        for viewport_name, viewport in VIEWPORTS.items():
            context = browser.new_context(viewport=viewport)
            page = context.new_page()
            for page_name, page_contract in PAGES.items():
                for locale, expected in page_contract["expected"].items():
                    page.goto(f"{BASE_URL}{page_contract['path']}?lang={locale}", wait_until="networkidle")
                    page.wait_for_function("locale => document.documentElement.lang === locale", arg=locale)
                    observed = page.evaluate(
                        """({selector}) => ({
                          locale: document.documentElement.lang,
                          text: document.querySelector(selector)?.textContent || '',
                          overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
                          language: document.querySelector('[data-language-select]')?.value || '',
                          theme: Boolean(document.querySelector('[data-theme-toggle]')),
                          access: Boolean(document.querySelector('[data-access-open]'))
                        })""",
                        {"selector": page_contract["selector"]},
                    )
                    passed = (
                        observed["locale"] == locale
                        and expected.lower() in observed["text"].lower()
                        and observed["language"] == locale
                        and observed["theme"]
                        and observed["access"]
                        and not observed["overflow"]
                    )
                    checks.append({"viewport": viewport_name, "page": page_name, "locale": locale, "passed": passed, "observed": observed})
                    page.screenshot(path=OUTPUT / f"{page_name}-{viewport_name}-{locale}.png", full_page=False)
            context.close()
        browser.close()
    report = {"schema": "synthia.landing-i18n-qa.v1", "checks": checks, "passed": all(item["passed"] for item in checks)}
    (OUTPUT / "qa.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    passed_count = sum(bool(item["passed"]) for item in checks)
    print(f"Synthia i18n QA: {passed_count}/{len(checks)} checks passed.")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
