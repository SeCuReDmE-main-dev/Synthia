(() => {
  "use strict";

  const root = document.documentElement;
  const storageKey = "synthia.access";
  const mobileNavigation = window.matchMedia("(max-width: 60rem)");
  const accessConsole = document.querySelector("[data-access-console]");
  const navMenu = document.querySelector("[data-nav-menu]");
  const navToggle = document.querySelector("[data-nav-toggle]");
  let lastAccessTrigger = null;

  root.classList.add("js");

  function readStoredState() {
    try {
      const stored = window.localStorage.getItem(storageKey);
      return stored ? JSON.parse(stored) : {};
    } catch {
      return {};
    }
  }

  const saved = readStoredState();
  const state = {
    theme: saved.theme === "light" ? "light" : "dark",
    access: ["base", "autism", "adhd", "deep"].includes(saved.access) ? saved.access : "base",
    contrast: Boolean(saved.contrast),
    largeText: Boolean(saved.largeText),
    reducedMotion: Boolean(saved.reducedMotion)
  };

  function persistState() {
    try {
      window.localStorage.setItem(storageKey, JSON.stringify(state));
    } catch {
      // The public shell remains functional when private browsing blocks storage.
    }
  }

  function applyState() {
    root.dataset.theme = state.theme;
    root.dataset.access = state.access;
    root.toggleAttribute("data-contrast", state.contrast);
    root.toggleAttribute("data-text", state.largeText);
    root.toggleAttribute("data-motion", state.reducedMotion);

    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      const currentTheme = state.theme === "dark" ? "Night" : "Light";
      button.textContent = `Theme: ${currentTheme}`;
      button.setAttribute("aria-label", `Change color theme; current theme is ${currentTheme}`);
    });

    document.querySelectorAll("[data-theme-src-dark]").forEach((image) => {
      const source = state.theme === "dark" ? image.dataset.themeSrcDark : image.dataset.themeSrcLight;
      if (source) image.src = source;
    });

    document.querySelectorAll("[data-access-profile]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.accessProfile === state.access));
    });

    const contrastToggle = document.querySelector("[data-contrast-toggle]");
    const textToggle = document.querySelector("[data-text-toggle]");
    const motionToggle = document.querySelector("[data-motion-toggle]");
    if (contrastToggle) contrastToggle.checked = state.contrast;
    if (textToggle) textToggle.checked = state.largeText;
    if (motionToggle) motionToggle.checked = state.reducedMotion;

    persistState();
  }

  function setNavigationOpen(open) {
    if (!navMenu || !navToggle) return;
    const canOpen = mobileNavigation.matches && open;
    navMenu.classList.toggle("is-open", canOpen);
    navToggle.setAttribute("aria-expanded", String(canOpen));
    root.dataset.navOpen = String(canOpen);
  }

  function setAccessOpen(open) {
    if (!accessConsole) return;
    accessConsole.setAttribute("aria-hidden", String(!open));

    if (open) {
      window.requestAnimationFrame(() => {
        const closeButton = accessConsole.querySelector("[data-access-close]");
        if (closeButton) closeButton.focus();
      });
    } else if (lastAccessTrigger) {
      lastAccessTrigger.focus();
    }
  }

  function trapAccessFocus(event) {
    if (!accessConsole || accessConsole.getAttribute("aria-hidden") === "true" || event.key !== "Tab") return;
    const focusable = [...accessConsole.querySelectorAll("a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex='-1'])")];
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  applyState();
  setNavigationOpen(false);

  document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      state.theme = state.theme === "dark" ? "light" : "dark";
      applyState();
    });
  });

  document.querySelectorAll("[data-access-open]").forEach((button) => {
    button.addEventListener("click", (event) => {
      lastAccessTrigger = event.currentTarget;
      setAccessOpen(true);
    });
  });

  document.querySelectorAll("[data-access-close]").forEach((button) => {
    button.addEventListener("click", () => setAccessOpen(false));
  });

  document.querySelectorAll("[data-access-profile]").forEach((button) => {
    button.addEventListener("click", () => {
      state.access = button.dataset.accessProfile || "base";
      if (state.access === "autism") state.reducedMotion = true;
      if (["adhd", "deep"].includes(state.access)) state.contrast = true;
      applyState();
    });
  });

  const contrastToggle = document.querySelector("[data-contrast-toggle]");
  const textToggle = document.querySelector("[data-text-toggle]");
  const motionToggle = document.querySelector("[data-motion-toggle]");
  if (contrastToggle) contrastToggle.addEventListener("change", () => { state.contrast = contrastToggle.checked; applyState(); });
  if (textToggle) textToggle.addEventListener("change", () => { state.largeText = textToggle.checked; applyState(); });
  if (motionToggle) motionToggle.addEventListener("change", () => { state.reducedMotion = motionToggle.checked; applyState(); });

  if (navToggle) {
    navToggle.addEventListener("click", () => {
      const isOpen = navToggle.getAttribute("aria-expanded") === "true";
      setNavigationOpen(!isOpen);
    });
  }

  if (navMenu) {
    navMenu.addEventListener("click", (event) => {
      if (event.target.closest("a")) setNavigationOpen(false);
    });
  }

  if (accessConsole) {
    accessConsole.addEventListener("click", (event) => {
      if (event.target === accessConsole) setAccessOpen(false);
    });
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      if (accessConsole && accessConsole.getAttribute("aria-hidden") === "false") {
        setAccessOpen(false);
      } else {
        setNavigationOpen(false);
      }
    }
    trapAccessFocus(event);
  });

  const updateForViewport = () => setNavigationOpen(false);
  if (mobileNavigation.addEventListener) {
    mobileNavigation.addEventListener("change", updateForViewport);
  } else {
    mobileNavigation.addListener(updateForViewport);
  }
})();
// Asset fingerprint is verified by scripts/publish_public_shell_assets.py.
