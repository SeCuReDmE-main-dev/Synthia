(function () {
  const root = document.documentElement;
  const key = "synthia.locale.v1";
  const aliases = { fr: "fr-CA", "fr-ca": "fr-CA", en: "en-CA", "en-ca": "en-CA", es: "es" };
  const cache = new Map();
  const attributes = ["aria-label", "alt", "placeholder", "title"];

  function normalize(value) {
    if (!value) return null;
    const lowered = String(value).toLowerCase();
    return aliases[lowered] || aliases[lowered.split("-")[0]] || null;
  }

  function resolve() {
    const query = normalize(new URLSearchParams(location.search).get("lang"));
    if (query) return query;
    const stored = normalize(localStorage.getItem(key));
    if (stored) return stored;
    for (const candidate of navigator.languages || [navigator.language]) {
      const locale = normalize(candidate);
      if (locale) return locale;
    }
    return "en-CA";
  }

  async function catalog(locale) {
    if (cache.has(locale)) return cache.get(locale);
    const response = await fetch(`i18n/${locale}.json`, { cache: "no-cache" });
    if (!response.ok) throw new Error(`Missing Synthia locale ${locale}`);
    const value = await response.json();
    cache.set(locale, value);
    return value;
  }

  function clean(value) { return String(value || "").replace(/\s+/g, " ").trim(); }

  function applyStrings(selected, canonical) {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        if (!node.parentElement || node.parentElement.closest("script,style,code,pre")) return NodeFilter.FILTER_REJECT;
        return clean(node.nodeValue) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      }
    });
    let node = walker.nextNode();
    while (node) {
      const source = node.__synthiaCanonical || clean(node.nodeValue);
      node.__synthiaCanonical = source;
      const value = selected.strings[source] ?? canonical.strings[source] ?? source;
      const leading = node.nodeValue.match(/^\s*/)?.[0] || "";
      const trailing = node.nodeValue.match(/\s*$/)?.[0] || "";
      node.nodeValue = `${leading}${value}${trailing}`;
      node = walker.nextNode();
    }
    document.querySelectorAll("*").forEach((element) => attributes.forEach((attribute) => {
      if (!element.hasAttribute(attribute)) return;
      const storage = `synthiaCanonical${attribute.replace(/(^|-)([a-z])/g, (_, __, letter) => letter.toUpperCase())}`;
      const source = element.dataset[storage] || clean(element.getAttribute(attribute));
      if (!source) return;
      element.dataset[storage] = source;
      element.setAttribute(attribute, selected.strings[source] ?? canonical.strings[source] ?? source);
    }));
    const sourceTitle = root.dataset.canonicalTitle || document.title;
    root.dataset.canonicalTitle = sourceTitle;
    document.title = selected.strings[sourceTitle] ?? canonical.strings[sourceTitle] ?? sourceTitle;
  }

  async function setLocale(value) {
    const locale = normalize(value) || "en-CA";
    const [selected, canonical] = await Promise.all([catalog(locale), catalog("en-CA")]);
    root.lang = locale;
    root.dir = "ltr";
    root.dataset.locale = locale;
    localStorage.setItem(key, locale);
    applyStrings(selected, canonical);
    document.querySelectorAll("[data-language-select]").forEach((select) => { select.value = locale; });
    document.dispatchEvent(new CustomEvent("synthia:locale-changed", { detail: { locale } }));
  }

  window.SynthiaI18n = { setLocale };
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-language-select]").forEach((select) => select.addEventListener("change", () => setLocale(select.value)));
    setLocale(resolve()).catch(() => { root.lang = "en-CA"; });
  }, { once: true });
})();
