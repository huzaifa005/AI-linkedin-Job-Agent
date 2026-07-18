---
name: Ops Console Aesthetic
colors:
  surface: '#1D1C22'
  surface-dim: '#141318'
  surface-bright: '#3a383e'
  surface-container-lowest: '#0e0e12'
  surface-container-low: '#1c1b20'
  surface-container: '#201f24'
  surface-container-high: '#2b292f'
  surface-container-highest: '#353439'
  on-surface: '#e5e1e8'
  on-surface-variant: '#d7c3ae'
  inverse-surface: '#e5e1e8'
  inverse-on-surface: '#313035'
  outline: '#9f8e7a'
  outline-variant: '#524534'
  surface-tint: '#ffb955'
  primary: '#ffc880'
  on-primary: '#452b00'
  primary-container: '#f5a623'
  on-primary-container: '#644000'
  inverse-primary: '#835500'
  secondary: '#5bd5fc'
  on-secondary: '#003543'
  secondary-container: '#00a3c8'
  on-secondary-container: '#003341'
  tertiary: '#9bd9ff'
  on-tertiary: '#00344a'
  tertiary-container: '#3ac2ff'
  on-tertiary-container: '#004d6a'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffddb4'
  primary-fixed-dim: '#ffb955'
  on-primary-fixed: '#291800'
  on-primary-fixed-variant: '#633f00'
  secondary-fixed: '#b7eaff'
  secondary-fixed-dim: '#5bd5fc'
  on-secondary-fixed: '#001f28'
  on-secondary-fixed-variant: '#004e61'
  tertiary-fixed: '#c4e7ff'
  tertiary-fixed-dim: '#7cd0ff'
  on-tertiary-fixed: '#001e2c'
  on-tertiary-fixed-variant: '#004c69'
  background: '#141318'
  on-background: '#e5e1e8'
  surface-variant: '#353439'
  border: '#2A2933'
  text-primary: '#EDEBF2'
  text-muted: '#9A98A6'
  status-error: '#FF4B4B'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  body-base:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.4'
  label-mono:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: '1.2'
  console-log:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: '1.6'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  container-max: 900px
  gutter: 1rem
  margin-mobile: 1.25rem
  stack-gap: 1.5rem
---

## Brand & Style

The design system is built for an autonomous job-hunting agent, emphasizing precision, technical authority, and automation. It moves away from "friendly" consumer SaaS tropes toward a specialized "Ops Console" environment. The interface should feel like a high-performance tool piloted by a human, prioritizing clarity and functional feedback over marketing flourishes.

The visual style is **Corporate / Modern** with a **Technical/Minimalist** edge. It utilizes a deep, focused color palette to reduce cognitive load and high-contrast accents to guide the user's attention to active processes.

**Key Stylistic Principles:**
- **Automation Forward:** Every background task is surfaced via a signature "Live Console" motif.
- **Confident & Quiet:** Copy is written in the active voice using plain verbs. No exclamation marks or celebratory language.
- **Zero Fluff:** Avoid gradients, glassmorphism, and soft drop shadows. Depth is created through 1px borders and tonal layering.

## Colors

The palette is rooted in a "Deep Charcoal" ecosystem to provide a low-glare environment suitable for monitoring background tasks. 

- **Primary (Amber #F5A623):** Reserved for "In-Progress" states and primary calls to action. It signifies energy and active processing.
- **Secondary (Cyan #4CC9F0):** Used for data visualization, links, and "Success/Fit" states. It represents completion and technical accuracy.
- **Neutral:** A tiered system of dark greys. `#16151A` serves as the foundation, while `#1D1C22` is used for cards and panels to create subtle separation.
- **Status Dots:** 
    - Pulsing Amber: Active/Processing.
    - Solid Cyan: Done/Success.
    - Muted Grey: Idle.
    - Rose/Red: Error.

## Typography

Typography is used to distinguish between human-readable interface elements and machine-generated data logs.

- **Inter:** The primary workhorse for the UI. Headlines should use semibold weights with tight tracking to maintain a compact, "engineered" look.
- **JetBrains Mono:** Used for all technical contexts—logs, status lines, counters, and dates. This font reinforces the "Ops Console" feel and ensures data readability.

**Mobile Considerations:**
For mobile viewports, maintain the legibility of `console-log` at a minimum of 13px. Headline sizes should scale down (e.g., `headline-lg` becomes 24px) to avoid excessive wrapping on narrow screens.

## Layout & Spacing

This design system uses a **fixed-width centered grid** for desktop to maintain focus on the agent's pipeline.

- **Content Width:** Desktop content is capped between 720px and 900px to ensure the interface remains scannable and "quiet."
- **Grid:** A standard 12-column system is used within the container, though most layouts will favor simple 1 or 2 column structures for clarity.
- **Responsiveness:**
    - **Desktop:** Generous whitespace, horizontal alignment of filters.
    - **Mobile:** Elements stack vertically. The primary action button (e.g., "Start Fetching") moves to a fixed bottom bar for thumb-accessibility.
- **Vertical Rhythm:** A consistent 8px-based spacing system governs the gap between cards and console elements.

## Elevation & Depth

Depth is achieved through **Tonal Layers** and **Low-Contrast Outlines** rather than shadows.

- **Base Layer (#16151A):** The background of the entire application.
- **Surface Layer (#1D1C22):** Used for cards, panels, and the signature console box.
- **Borders (#2A2933):** 1px solid borders provide the only visual separation between surfaces. 
- **The Signature Console:** This element is slightly darker than the surface layer or features a subtle scanline texture to differentiate it from standard UI cards. It uses no shadows, relying on the contrast between the border and the base background.

## Shapes

The shape language is precise and geometric. A small radius of **6px to 8px** is applied to all cards, buttons, and input fields. Fully rounded/pill-shaped elements are strictly prohibited as they conflict with the technical, "ops" aesthetic. 

The goal is to maintain a professional, slightly sharp appearance that aligns with the monospaced typography and terminal motifs.

## Components

### Signature Element: The Live Console
The core visual identifier of the product. It is a dark terminal-style box:
- **Header:** Includes a status dot (pulsing or solid), a mono label (e.g., `agent · fetching`), and a status summary.
- **Body:** Monospace log lines prefixed with a Cyan `$`.
- **Active State:** Includes a blinking block cursor on the final line.

### Buttons
- **Primary (Amber):** Solid background with dark text. Used for "Open Agent," "Start Fetching," and "Analyze."
- **Secondary/Ghost:** 1px border (#2A2933) with primary text (#EDEBF2).
- **Links:** Cyan for success-path links; Muted Grey for utility links (e.g., "View original posting").

### Job Cards
- **Structure:** 2-column grid on desktop.
- **Content:** Title (Bold), Company/Location (Muted), and action links.
- **States:** "Fit" jobs get a Cyan tag. "Non-match" jobs fade to 40% opacity with a muted label.

### Inputs & Selects
Field backgrounds match the surface color (`#1D1C22`) with a `#2A2933` border. Use JetBrains Mono for numeric inputs and Inter for text-heavy fields.

### Status Indicators
Small 8px circles (dots) are used throughout the UI—within the console, beside LinkedIn connection status, and in the session history list—to provide instant visual feedback on system health.