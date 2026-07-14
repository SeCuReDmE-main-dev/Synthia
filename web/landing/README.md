# Synthia Public Site

Static public site package for `synthia.securedme.ca`.

The landing page uses a resilient visual system:

- The visible identity is CSS-rendered so the page stays polished even if image uploads fail.
- `synthia-logo.png` and `synthia-hero.png` can still be uploaded as optional future assets, but the current public page does not depend on them to render.
- The Trace Lab uses a small browser script to render a versioned JSON file from
  the same public origin. It makes no AI/API call, stores no key, has no
  server-side dependency, and contains no private evidence.

Deploy the generated `dist/synthia-public/` package to the cPanel document root:

```text
/home/xacm7978/synthia.securedme.ca/
  index.html
  neutrosophic-lexicon.html
  trace-lab.html
  trace-lab.js
  synthia-landing.css
  data/
    aburria-trace.json
  assets/
    synthia-hero.png
    synthia-logo.png
```

Upload checklist:

1. Upload `index.html`.
2. Upload `neutrosophic-lexicon.html`.
3. Upload `trace-lab.html`, `trace-lab.js`, and `data/aburria-trace.json`.
4. Upload `synthia-landing.css`.
5. Upload the complete `assets/` folder.
6. Verify the asset and Trace Lab URLs return `200`.

cPanel Git workflow:

```text
Repository clone:
/home/xacm7978/synthia.secureme.ca/Synthia/codebase

Public document root:
/home/xacm7978/synthia.securedme.ca
```

After pulling the latest `main` in the cPanel Git clone, copy the contents of
`dist/synthia-public/` into the public document root. Verify the exact document
root before copying because the Git clone path and public domain path differ by
one directory name.

The site presents Synthia as an educational research project for context-preserving lexicon intelligence, biology classification, source traceability, taxonomy memory, and uncertainty-aware classification. It does not present Synthia as a production scientific authority, medical tool, environmental deployment system, drone-control platform, or formal nomenclatural authority.
