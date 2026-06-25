# Synthia public landing page

Static landing page files for `synthia.securedme.ca`.

## Files

- `index.html` — public landing page and web infographic.
- `synthia-landing.css` — standalone CSS theme.

## cPanel deployment

Upload both files to the document root for `synthia.securedme.ca`.
In the current cPanel setup, that document root is named `synthia.securedme.ca`.

Expected final layout:

```text
synthia.securedme.ca/
  index.html
  synthia-landing.css
```

The page is intentionally static: no build step, no JavaScript, no external assets, and no private source material.
