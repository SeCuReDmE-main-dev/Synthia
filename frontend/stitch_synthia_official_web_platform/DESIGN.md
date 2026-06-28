---
name: Technical Precision
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#3a3939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#c0caae'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#8a947b'
  outline-variant: '#404a35'
  surface-tint: '#85dd00'
  primary: '#ffffff'
  on-primary: '#1d3700'
  primary-container: '#9bfb22'
  on-primary-container: '#417000'
  inverse-primary: '#3d6a00'
  secondary: '#c8c6c5'
  on-secondary: '#313030'
  secondary-container: '#474746'
  on-secondary-container: '#b7b5b4'
  tertiary: '#ffffff'
  on-tertiary: '#332d45'
  tertiary-container: '#e8ddfd'
  on-tertiary-container: '#68607b'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#9bfb22'
  primary-fixed-dim: '#85dd00'
  on-primary-fixed: '#0f2000'
  on-primary-fixed-variant: '#2d5000'
  secondary-fixed: '#e5e2e1'
  secondary-fixed-dim: '#c8c6c5'
  on-secondary-fixed: '#1b1b1b'
  on-secondary-fixed-variant: '#474746'
  tertiary-fixed: '#e8ddfd'
  tertiary-fixed-dim: '#ccc2e1'
  on-tertiary-fixed: '#1e182f'
  on-tertiary-fixed-variant: '#4a435c'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
  data-white: '#FFFFFF'
  grid-line: '#262626'
  system-alert: '#FF4B4B'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  body-base:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: '0'
  label-mono:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1.0'
    letterSpacing: 0.1em
  data-display:
    fontFamily: JetBrains Mono
    fontSize: 24px
    fontWeight: '700'
    lineHeight: '1.0'
    letterSpacing: '0'
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
spacing:
  grid-unit: 8px
  gutter: 16px
  margin-desktop: 64px
  margin-mobile: 24px
  max-width: 1440px
---

## Brand & Style

This design system is built on the **I_system^S** aesthetic—a visual language that treats the user interface as a high-precision research instrument rather than a consumer application. The brand persona is clinical, transparent, and authoritative, designed for environments where data integrity and technical clarity are paramount.

The visual style is a fusion of **Technical Minimalism** and **High-Contrast Cybernetics**. It rejects decorative flourishes in favor of structural transparency. Every element serves a functional purpose, utilizing heavy whitespace, sharp geometric intersections, and a strict adherence to a technical grid. The emotional response is one of serious intellectual engagement, providing the user with a sense of "system-level" control.

## Colors

The palette is anchored in a high-contrast dark environment to reduce eye strain during deep focus and to maximize the luminance of data-critical elements.

- **Primary (Neon Green):** Reserved exclusively for high-priority data points, active states, and successful system confirmations. It should be used sparingly to maintain its "signal" value against the "noise."
- **Neutral (The Void):** The `#0A0A0A` background provides the foundational canvas, ensuring zero-bleed contrast.
- **Secondary (Surface):** `#1B1B1B` is used for containers and structural demarcations, creating a subtle hierarchy of depth without the use of shadows.
- **Named Colors:** White is used for primary text to ensure maximum legibility, while "Grid-Line" handles the technical structural overlays.

## Typography

Typography is used as a data-mapping tool. The pairing of **Inter** and **JetBrains Mono** creates a clear distinction between narrative content and technical data.

- **Inter:** Used for all prose, headings, and instructional text. It provides a modern, neutral clarity that keeps the interface feeling sophisticated.
- **JetBrains Mono:** Used for labels, timestamps, coordinates, and any "instrument output." All-caps mono labels with high letter-spacing should be used for section headers to evoke a blueprint or terminal aesthetic.
- **Weights:** Use bold weights for primary data headers and light/regular weights for descriptive text to maintain a hierarchy of "fact vs. explanation."

## Layout & Spacing

The layout is governed by a **strict 12-column fixed grid** that emphasizes mathematical precision. 

- **The Grid:** A visible 1px grid pattern (using the `grid-line` color) may be used in the background of headers or specific data modules to reinforce the "instrument" aesthetic.
- **Rhythm:** All margins and paddings must be multiples of the **8px grid unit**. 
- **Adaptation:** On desktop, the layout utilizes wide margins to center focus. On mobile, the system collapses to a single column, but maintains the 1px border separations to preserve the structured feel.
- **Gutters:** 16px gutters are mandatory between all data-carrying modules to ensure no "information bleed" occurs.

## Elevation & Depth

This design system avoids all organic or ambient shadows. Depth is communicated through **Tonal Layering** and **Technical Outlines**.

- **Level 0 (Background):** `#0A0A0A` – The base system layer.
- **Level 1 (Surfaces):** `#1B1B1B` – Used for cards, sidebars, and input fields.
- **Level 2 (Active/Focus):** Defined by a 1px solid border of the primary color (`#9DFD24`) or the `data-white`.

To create a sense of sophisticated depth, use **Backdrop Blurs** (Glassmorphism) on overlaying panels (like modals or tooltips), but keep the blur saturation low and the border sharp. This mimics a lens or glass display on a physical instrument.

## Shapes

The shape language is strictly **Sharp (0px)**. 

Curves are perceived as "soft" or "consumer-friendly," which contradicts the serious research intent of this system. Every button, card, input, and modal must utilize 90-degree angles. This reinforces the grid-based construction and the uncompromising nature of the software. 

The only exception to the "no curves" rule is for data visualization (e.g., circular nodes in a network graph), where the shape carries specific semantic meaning.

## Components

- **Buttons:** Rectangular with a 1px border. Primary buttons use a solid `#9DFD24` fill with black text. Secondary buttons use a transparent fill with a white 1px border.
- **Input Fields:** Underlined or fully boxed with a 1px border using `#262626`. Upon focus, the border transitions to the primary neon green.
- **Data Cards:** No shadows. Separation is achieved via the `#1B1B1B` surface color and a top-aligned "status bar" (a 2px thick line) that indicates the module's state.
- **Chips/Status Tags:** Use JetBrains Mono in all caps. Status is indicated by a small 4px square icon next to the text (e.g., a green square for "LIVE").
- **Scrollbars:** Custom-styled to be extremely thin (4px) using the `grid-line` color, becoming primary neon green on hover.
- **Technical Readouts:** Use "Data-Display" typography for large metrics, often accompanied by a small label-mono descriptor positioned above or below the value.