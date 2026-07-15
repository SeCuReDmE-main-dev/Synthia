(function () {
  const root = document.documentElement;
  const consoleNode = document.querySelector("[data-access-console]");
  const saved = JSON.parse(localStorage.getItem("synthia.access") || "{}");

  function apply(state) {
    root.dataset.theme = state.theme || root.dataset.theme || "dark";
    root.dataset.access = state.access || "base";
    root.toggleAttribute("data-contrast", Boolean(state.contrast));
    root.toggleAttribute("data-text", Boolean(state.largeText));
    root.toggleAttribute("data-motion", Boolean(state.reducedMotion));
    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      button.textContent = root.dataset.theme === "dark" ? "Theme: Night" : "Theme: Light";
    });
    document.querySelectorAll("[data-theme-src-dark]").forEach((image) => {
      image.src = root.dataset.theme === "dark" ? image.dataset.themeSrcDark : image.dataset.themeSrcLight;
    });
    localStorage.setItem("synthia.access", JSON.stringify(state));
  }

  const state = {
    theme: saved.theme || "dark",
    access: saved.access || "base",
    contrast: saved.contrast || false,
    largeText: saved.largeText || false,
    reducedMotion: saved.reducedMotion || false
  };
  apply(state);

  document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      state.theme = root.dataset.theme === "dark" ? "light" : "dark";
      apply(state);
    });
  });

  document.querySelectorAll("[data-access-open]").forEach((button) => {
    button.addEventListener("click", () => {
      consoleNode.classList.add("is-open");
      consoleNode.setAttribute("aria-hidden", "false");
    });
  });

  document.querySelectorAll("[data-access-close]").forEach((button) => {
    button.addEventListener("click", () => {
      consoleNode.classList.remove("is-open");
      consoleNode.setAttribute("aria-hidden", "true");
    });
  });

  document.querySelectorAll("[data-access-profile]").forEach((button) => {
    button.addEventListener("click", () => {
      state.access = button.dataset.accessProfile;
      if (state.access === "autism") state.reducedMotion = true;
      if (state.access === "adhd") state.contrast = true;
      if (state.access === "deep") state.contrast = true;
      apply(state);
    });
  });

  const contrast = document.querySelector("[data-contrast-toggle]");
  const text = document.querySelector("[data-text-toggle]");
  const motion = document.querySelector("[data-motion-toggle]");
  if (contrast) contrast.addEventListener("change", () => { state.contrast = contrast.checked; apply(state); });
  if (text) text.addEventListener("change", () => { state.largeText = text.checked; apply(state); });
  if (motion) motion.addEventListener("change", () => { state.reducedMotion = motion.checked; apply(state); });
})();
