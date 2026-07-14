"use strict";

const TRACE_URL = "./data/aburria-trace.json";
const STORAGE_KEY = "synthia.trace-language";
const FALLBACK_LANGUAGE = "en";
const SUPPORTED_LANGUAGES = new Set(["en", "fr", "es", "it"]);

const byId = (id) => document.getElementById(id);

function safeLanguage(value) {
  return SUPPORTED_LANGUAGES.has(value) ? value : FALLBACK_LANGUAGE;
}

function preferredLanguage() {
  let stored = null;
  try {
    stored = window.localStorage.getItem(STORAGE_KEY);
  } catch (_) {
    // Storage may be disabled; the trace remains fully usable.
  }
  if (SUPPORTED_LANGUAGES.has(stored)) return stored;
  return safeLanguage((navigator.language || FALLBACK_LANGUAGE).slice(0, 2).toLowerCase());
}

function clearNode(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
}

function appendListItems(target, values) {
  clearNode(target);
  values.forEach((value) => {
    const item = document.createElement("li");
    item.textContent = value.replaceAll("_", " ");
    target.appendChild(item);
  });
}

function renderTimeline(trace, copy) {
  const timeline = byId("trace-timeline");
  clearNode(timeline);
  trace.timeline.forEach((event) => {
    const item = document.createElement("li");
    const marker = document.createElement("span");
    const body = document.createElement("div");
    const year = document.createElement("strong");
    const summary = document.createElement("p");
    const citation = document.createElement(event.public_url ? "a" : "span");

    marker.className = "timeline-marker";
    body.className = "timeline-body";
    year.textContent = String(event.year);
    summary.textContent = copy[event.summary_key] || event.citation;
    citation.className = "timeline-citation";
    citation.textContent = event.citation;
    if (event.public_url) {
      citation.href = event.public_url;
      citation.target = "_blank";
      citation.rel = "noopener noreferrer";
    }

    body.append(year, summary, citation);
    item.append(marker, body);
    timeline.appendChild(item);
  });
}

function renderSources(trace) {
  const registry = byId("source-registry");
  clearNode(registry);
  trace.source_registry.forEach((source) => {
    const card = document.createElement("article");
    const label = document.createElement("span");
    const citation = document.createElement("p");
    label.textContent = `${source.year} · ${source.kind.replaceAll("_", " ")}`;
    citation.textContent = source.citation;
    card.append(label, citation);
    if (source.public_url) {
      const link = document.createElement("a");
      link.href = source.public_url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = "Open public source ↗";
      card.appendChild(link);
    }
    registry.appendChild(card);
  });
}

function renderTrace(trace, language) {
  const selected = safeLanguage(language);
  const copy = trace.locales[selected] || trace.locales[FALLBACK_LANGUAGE];
  document.documentElement.lang = selected;
  byId("language-selector").value = selected;
  byId("trace-eyebrow").textContent = copy.eyebrow;
  byId("trace-title").textContent = copy.title;
  byId("trace-subtitle").textContent = copy.subtitle;
  byId("trace-taxon").textContent = trace.canonical_taxon;
  byId("trace-authority").textContent = trace.formal_authority;
  byId("trace-schema").textContent = trace.schema_version;
  byId("repairs-title").textContent = copy.repairs_title;
  byId("unresolved-title").textContent = copy.unresolved_title;
  byId("sources-title").textContent = copy.sources_title;
  byId("authority-boundary-title").textContent = copy.boundary_title;
  byId("authority-boundary").textContent = trace.authority_boundary;
  byId("trace-hierarchy").textContent = trace.hierarchy;
  renderTimeline(trace, copy);
  renderSources(trace);
  appendListItems(byId("repair-list"), trace.memory_repairs);
  appendListItems(byId("unresolved-list"), trace.unresolved_layers);
}

async function loadTrace() {
  const response = await fetch(TRACE_URL, { credentials: "same-origin" });
  if (!response.ok) throw new Error(`trace request failed: ${response.status}`);
  const trace = await response.json();
  if (trace.schema_version !== "synthia.showcase.trace.v1") {
    throw new Error("unsupported trace schema");
  }
  return trace;
}

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const trace = await loadTrace();
    const selector = byId("language-selector");
    renderTrace(trace, preferredLanguage());
    selector.addEventListener("change", () => {
      const language = safeLanguage(selector.value);
      try {
        window.localStorage.setItem(STORAGE_KEY, language);
      } catch (_) {
        // A blocked storage surface does not affect the selected language.
      }
      renderTrace(trace, language);
    });
    byId("trace-loading").hidden = true;
    byId("trace-content").hidden = false;
  } catch (error) {
    byId("trace-loading").hidden = true;
    byId("trace-error").hidden = false;
    console.error("Synthia public trace error", error);
  }

  byId("copy-command").addEventListener("click", async () => {
    const command = byId("showcase-command").textContent;
    try {
      await navigator.clipboard.writeText(command);
      byId("copy-status").textContent = "Command copied.";
    } catch (_) {
      byId("copy-status").textContent = "Select the command above and copy it manually.";
    }
  });
});
