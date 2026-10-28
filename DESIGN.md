---
name: SolutionSync
description: A local harbor-chart dashboard that reads each Manila day as one rising tide of verified uploads.
colors:
  ground: "#e6eeeb"
  panel: "#ffffff"
  panel-2: "#f2f7f5"
  ink: "#0f2a33"
  ink-2: "#3a5761"
  ink-3: "#536f79"
  line: "#cddbd6"
  line-2: "#e0e9e5"
  rail: "#0e3442"
  rail-2: "#164a5b"
  rail-ink: "#e2efea"
  rail-ink-2: "#a9cbc1"
  rail-line: "#22596a"
  foam: "#3f9b88"
  foam-ink: "#1b6a5a"
  foam-bg: "#dcefe8"
  buoy: "#d9581c"
  buoy-ink: "#a3400f"
  buoy-bg: "#fbe6da"
  storm: "#c4372d"
  storm-ink: "#a12a21"
  storm-bg: "#f8e0dc"
  brass: "#b08a1e"
  brass-ink: "#765c10"
  sand: "#dcc790"
  mist: "#a3b6bb"
  btn: "#0e3442"
  btn-ink: "#ffffff"
  btn-hover: "#164a5b"
typography:
  display:
    fontFamily: "Bahnschrift, \"DIN Alternate\", \"DIN 2014\", \"Segoe UI\", sans-serif"
    fontSize: "52px"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "-0.01em"
    fontFeature: "tnum"
  headline:
    fontFamily: "Bahnschrift, \"DIN Alternate\", \"DIN 2014\", \"Segoe UI\", sans-serif"
    fontSize: "26px"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "-0.005em"
  figure:
    fontFamily: "Bahnschrift, \"DIN Alternate\", \"DIN 2014\", \"Segoe UI\", sans-serif"
    fontSize: "30px"
    fontWeight: 600
    lineHeight: 1.1
    fontFeature: "tnum"
  title:
    fontFamily: "Bahnschrift, \"DIN Alternate\", \"DIN 2014\", \"Segoe UI\", sans-serif"
    fontSize: "16px"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "0.01em"
  body:
    fontFamily: "\"Segoe UI Variable Text\", \"Segoe UI\", system-ui, -apple-system, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Bahnschrift, \"DIN Alternate\", \"DIN 2014\", \"Segoe UI\", sans-serif"
    fontSize: "12.5px"
    fontWeight: 600
    letterSpacing: "0.04em"
rounded:
  sm: "4px"
  control: "7px"
  md: "8px"
  lg: "12px"
  pill: "999px"
spacing:
  xs: "6px"
  sm: "8px"
  md: "14px"
  panel: "20px"
  section: "22px"
  page: "34px"
components:
  button-primary:
    backgroundColor: "{colors.btn}"
    textColor: "{colors.btn-ink}"
    rounded: "{rounded.control}"
    padding: "9px 15px"
  button-primary-hover:
    backgroundColor: "{colors.btn-hover}"
  button-secondary:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "9px 15px"
  button-secondary-hover:
    backgroundColor: "{colors.panel-2}"
  chip-published:
    backgroundColor: "{colors.foam-bg}"
    textColor: "{colors.foam-ink}"
    rounded: "{rounded.pill}"
    padding: "3px 10px 3px 8px"
  chip-missing:
    backgroundColor: "{colors.buoy-bg}"
    textColor: "{colors.buoy-ink}"
    rounded: "{rounded.pill}"
    padding: "3px 10px 3px 8px"
  chip-failed:
    backgroundColor: "{colors.storm-bg}"
    textColor: "{colors.storm-ink}"
    rounded: "{rounded.pill}"
    padding: "3px 10px 3px 8px"
  chip-pending:
    backgroundColor: "{colors.panel-2}"
    textColor: "{colors.ink-2}"
    rounded: "{rounded.pill}"
    padding: "3px 10px 3px 8px"
  chip-unverified:
    backgroundColor: "{colors.panel-2}"
    textColor: "{colors.ink-3}"
    rounded: "{rounded.pill}"
    padding: "3px 10px 3px 8px"
  panel:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
  input:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "9px 12px"
    height: "40px"
  nav-item:
    textColor: "{colors.rail-ink-2}"
    rounded: "6px"
    padding: "10px 12px"
  nav-item-active:
    backgroundColor: "{colors.rail-2}"
    textColor: "{colors.rail-ink}"
---

# Design System: SolutionSync

## Overview

**Creative North Star: "Harbor Tide Table"**

SolutionSync looks like a printed harbor tide table that has been made interactive. A deep-sea teal rail holds the chart's title and the automation pennant. The working area is sea-glass ground with white panels, all drawn from one tide-water tonal ramp. Each Manila day is a single tide that rises with verified uploads. Before any figure, the visitor reads a harbor-conditions bulletin (fair, caution or storm) that answers "is everything OK".

The density is that of a calm operations sheet. There is one hairline weight, one 8px corner and one tonal ramp. Figures and labels are set in Bahnschrift with tabular numerals, the way a tide table sets its readings. Prose is set in Segoe UI Variable. Every number is printed next to its proof: a figure gets a one-line sentence underneath saying where it came from. The system has light and dark tides that follow `prefers-color-scheme`. The rail stays deep teal in both, and in dark mode it remains a distinct band against the near-black sea.

The world rejects the category default of a row of identical stat tiles above a generic chart. Figures sit in one band divided by hairlines, and the chart is the day's tide drawn against the limit.

**Key Characteristics:**
- Deep-teal rail with a triangular pennant flag. The flag marks automation state at the rail's foot and the current nav item.
- Sea-foam means published and healthy, buoy orange means attention, signal red means failure, and chart brass means limits and schedule.
- Bahnschrift with tabular numerals for every figure, heading and label. Segoe UI Variable for sentences.
- Single 1px hairlines, an 8px panel corner, and a soft ambient shadow only.
- One authored motion: the tide line draws in once.

## Colors

The palette is a harbor chart: teal water neutrals with four signal hues, and each signal hue carries a fixed meaning.

### Primary
- **Deep-Sea Teal** (rail): the navigation rail, the mobile tab bar and the selected segmented control. In light mode the primary button uses the same value (btn). The darker step **Rail Swell** (rail-2) marks the current nav item and the brand tile.
- **Sea Foam** (foam): published and healthy. Used for the tide fill, history bars, used limit slots, the active pennant, focus rings, the selection color and `accent-color`. **Foam Ink** (foam-ink) is the readable foam used for the tide line, upload markers, links and success text. **Foam Wash** (foam-bg) is the published chip ground.

### Secondary
- **Buoy Orange** (buoy, buoy-ink, buoy-bg): attention. Used for the caution bulletin, warning chips and figures, the "off" pennant, and the warn border on the run strip.
- **Signal Red** (storm, storm-ink, storm-bg): failure only. Used for the storm bulletin, failed chips and figures, load errors, and the progress segment for failed items.

### Tertiary
- **Chart Brass** (brass, brass-ink): limits and schedule. Used for the dashed daily-limit line, schedule ticks, the paused pennant and over-limit slot borders. **Sand** (sand) fills the missing segment of the station progress bar and over-limit slots.

### Neutral
- **Sea-Glass Ground** (ground): page background.
- **Chart Paper** (panel) / **Shallows** (panel-2): panel surface, plus the recessed surface used for table heads, chips, steppers and hover.
- **Deep Ink / Channel Ink / Sounding Ink** (ink, ink-2, ink-3): text in three steps: primary, secondary/context, and meta/timestamps.
- **Hairline / Faint Hairline** (line, line-2): panel borders and control strokes / row separators inside panels.
- **Mist** (mist): hover border on controls, pending segments, the idle pennant and the scrollbar thumb.
- **Rail Ink / Rail Ink Dim / Rail Line** (rail-ink, rail-ink-2, rail-line): text and dividers on the rail.

Dark mode swaps every token in place (see `.impeccable/design.json` colorMeta). The primary button becomes sea foam with dark ink (btn #4fc1a8, btn-ink #062019), so the action stays visible against the dark rail.

### Named Rules
**The Signal Meaning Rule.** Foam means healthy, buoy means look, storm means failed, and brass means limit or schedule. A signal hue never decorates. If nothing is wrong, no orange or red appears on the screen.

**The One Tide-Water Ramp Rule.** Ground, panels, recessed surfaces and hairlines all come from the same teal-grey ramp. Do not introduce a neutral from outside it.

**The Two Tides Rule.** Every surface must work in both the light and dark tide. Colors come only from the custom properties, which swap under `prefers-color-scheme: dark`.

## Typography

**Display / Figure / Label Font:** Bahnschrift (with DIN Alternate, DIN 2014, Segoe UI)
**Body Font:** Segoe UI Variable Text (with Segoe UI, system-ui)
**Mono:** Consolas / Cascadia Mono, only for file paths and run output.

**Character:** The pairing works like a tide table set beside harbor notices. Bahnschrift's condensed engineering forms with tabular numerals carry every reading. Segoe UI Variable carries the sentences. Both are Windows system faces, chosen because of the constraint: no external fonts load.

### Hierarchy
- **Display** (600, 52px, 1; 42px under 760px): only today's tide figure ("4 / 4").
- **Headline** (600, 26px, 1.15; 22px on mobile): the page title in the header.
- **Figure** (600, 30px, 1.1): values in the figures band. The calm "Nothing" state drops to 22px in foam ink.
- **Title** (600, 16–20px, 1.3): panel heads (16px), the bulletin verdict and dialog titles (18px), and the drawer title (20px).
- **Body** (400, 15px, 1.5): prose. Context lines and help text are 14px in ink-2, with help capped at 60ch.
- **Label** (600, 12.5–13px, 0.04em, uppercase): table column heads and timeline day dividers only. Chart ticks and timestamps use Bahnschrift 500 at 11.5–13px without caps.

### Named Rules
**The Tide-Table Numerals Rule.** Every count, time and quantity is set in Bahnschrift with `font-variant-numeric: tabular-nums`, so columns of readings line up.

**The Proof Line Rule.** A figure is never printed alone. It always comes with a 12.5px ink-3 sentence saying what it counts or where it was checked.

## Layout

The shell has a fixed 236px rail and a fluid main column (`grid-template-columns: 236px minmax(0,1fr)`). The rail is sticky and full height, with the brand at the top, four views below, and the pennant pinned to the foot. The main column is padded 26px 34px 48px and stacks sections with a 22px gap. In that column the order is: page header (title and context line at left, actions at right), then the bulletin strip, then a 1.5fr / 1fr row for the tide chart and stations, then the figures band, then a 1fr / 1.25fr row for the 14-day strip and the recent feed.

Panels use 20px horizontal padding (16px top on the head, 14px / 18px in the body). Rows inside panels use 9–14px vertical padding separated by faint hairlines.

- **≤980px:** the two-column rows and the Settings grid collapse to one column.
- **≤760px:** the rail becomes a sticky top bar with the brand and pennant. Navigation moves to a fixed bottom tab bar in rail teal that respects `safe-area-inset-bottom`. The header actions become one compact row: secondary actions turn into icon-only buttons and the primary keeps its label and fills the row. The figures band becomes two columns. Tables become stacked rows, and the detail drawer becomes a bottom sheet with 14px top corners.

## Elevation & Depth

The system is flat with a single soft ambient lift. Panels, the bulletin, the figures band, tables and toasts share one shadow. Dialogs float on a deeper one above a teal-black scrim. Depth comes mostly from the tonal ramp: ground sits beneath panel, and panel-2 is used for recessed areas.

### Shadow Vocabulary
- **Ambient panel** (`box-shadow: 0 1px 2px rgba(14,52,66,.06), 0 6px 18px -8px rgba(14,52,66,.18)`; dark: `0 1px 2px rgba(0,0,0,.4), 0 8px 22px -10px rgba(0,0,0,.6)`): every resting container.
- **Dialog** (`box-shadow: 0 24px 60px -20px rgba(0,0,0,.45)`, backdrop `rgba(6,18,23,.45)`): confirm dialogs and the detail drawer.
- **Button rest** (`box-shadow: 0 1px 1px rgba(14,52,66,.05)`): secondary buttons only.

### Named Rules
**The Single Hairline Rule.** Borders are always 1px, using `line` for container edges and `line-2` for internal separators. In the figures band, separators are drawn with inset 1px shadows so they survive any column wrap.

## Shapes

Shapes are softly squared. Panels, the bulletin, toasts and the run strip use 8px corners. Buttons and inputs use 7px, nav items 6px, and tags and limit slots 4px. Chips are full pills. Dialogs use 12px. The one recurring silhouette is the **pennant**: a right-pointing triangle made with `clip-path: polygon(0 0, 100% 50%, 0 100%)`. It is the automation flag (10×18px), the bulletin flag (14×26px) and the current-nav marker (7×12px).

## Components

### Buttons
Buttons are tactile but quiet.
- **Shape:** gently squared (7px), 9px 15px padding, 600 weight, 14px, with an 18px or 16px icon and an 8px gap.
- **Primary:** the btn token: deep teal in light mode, sea foam with dark ink in dark mode. Hover moves to btn-hover. Use one primary per action group (Run Sync, Save settings, Continue).
- **Secondary:** panel ground with a 1px line border. Hover darkens the border to mist and the ground to panel-2.
- **Quiet:** transparent with no border, for "View all" and close.
- **States:** pressing nudges the button down by 1px. Disabled is 50% opacity with a not-allowed cursor. Settings Save and Cancel stay disabled until a value changes.

### Chips
- **Style:** a pill with a 7px leading dot in currentColor, 12.5px 600 text, no border.
- **Status vocabulary:** Published uses foam wash; Missing uses buoy wash; Failed uses storm wash; Pending uses panel-2 with ink-2; Unable to Verify uses panel-2 with ink-3 and a hollow ring dot instead of a filled one. Unable to Verify is never rendered as Missing.
- **Tag:** a 4px-corner panel-2 label for platform and operation metadata.

### Cards / Containers
- **Corner Style:** 8px.
- **Background:** panel on ground.
- **Shadow Strategy:** ambient panel (see Elevation).
- **Border:** 1px line.
- **Internal Padding:** a 16px 20px head with a Bahnschrift title and right-aligned ink-3 meta, and a body padded 14px 20px 18px.

### Inputs / Fields
- **Style:** panel ground, 1px line, 7px corners, 9px 12px padding, 40px minimum height, 14px text. Search has a 16px inset icon.
- **Focus:** the global 2px foam outline with a 2px offset. Hover sets the border to mist.
- **Stepper:** minus and plus buttons on panel-2 around a 22px Bahnschrift number.
- **Error / OK:** a message line below in storm-ink or foam-ink.
- **Segmented control:** a bordered 7px track. The pressed segment fills with rail teal.

### Navigation
- **Rail items:** rail-ink-2 text at weight 500 with an 18px stroke icon. Hover adds a 6% light wash. The current item sits on rail-2 with a foam pennant at its right edge, and its count badge shifts left to make room.
- **Mobile:** a four-column bottom tab bar with stacked icon and 11.5px label. The current tab uses rail-2.

### Icons
An inline SVG symbol sprite on a 24px grid, drawn with `stroke: currentColor; stroke-width: 1.75`, round caps and joins, and no fill. Icons size at 18px, or 16px inside buttons, feed rows and the timeline.

### Harbor Bulletin (signature)
A full-width strip that opens the Overview: a pennant flag, then the verdict title in 18px Bahnschrift, then a one-line detail. It has three states. **Fair** keeps the panel ground with a foam flag and uses `role="status"`. **Caution** fills with buoy-bg, a buoy border and a buoy flag. **Storm** fills with storm-bg, a storm border and a storm flag. Caution and Storm use `role="alert"` and switch the detail text to full ink.

### Today's Tide (signature)
An SVG chart on a Manila midnight-to-midnight hour axis. A foam-ink line (2.25px) rises with a 16% foam fill under it. Hollow markers (r 4.5, panel fill, foam-ink stroke) sit at each real upload time. A brass dashed limit line (5 5) carries its label, and brass schedule ticks mark the runs. A dashed "now" rule is drawn in ink-2. No marker or rise is ever drawn after "now". The large display figure reads "count / limit". **Motion:** the one authored animation. Web Animations draws the line in over 1100ms, fades the fill in over 900ms after a 250ms delay, and staggers the markers by 80ms, all on `cubic-bezier(.16,1,.3,1)`. It plays once and only when the page is visible. It is skipped under `prefers-reduced-motion`, and the chart is complete without it.

### Stations, Figures band, 14-day strip
- **Station:** a repository row with a Bahnschrift title, a status chip, and a 10px segmented progress bar (foam published, mist pending, sand missing, storm failed, faded ink-3 unverified), followed by facts in 13.5px.
- **Figures band:** a single bordered `<dl>` with auto-fit 170px columns and hairline separators. Each cell is a 13px label, a 30px figure and a proof line. Failed figures use storm-ink and unverified ones use buoy-ink. The Missing figure stays neutral. When nothing is pending, failed or unverified, the band shows a single "Needs attention: Nothing" cell in calm foam.
- **14-day strip:** foam bars at 85% opacity with 3px top corners. Today is solid foam-ink with a bold label. Zero days use a line-colored stub.

## Do's and Don'ts

### Do:
- **Do** read state from the bulletin first. Fair, caution or storm decides whether any buoy or storm color appears below it.
- **Do** set every number in Bahnschrift with tabular numerals and give it a proof line.
- **Do** take colors only from the custom properties so both tides work. Check every new surface in light and dark.
- **Do** use the pennant triangle for state and current-location marks.
- **Do** keep motion state-driven and gated by `prefers-reduced-motion`. The tide draw-in is the only authored entrance, and every view is complete without motion.
- **Do** draw icons from the inline sprite at a 1.75 stroke in currentColor.

### Don't:
- **Don't** build rows of identical stat tiles over a generic chart. Figures share one hairline-divided band.
- **Don't** load external fonts or assets. Only Windows system faces and inline SVG are allowed.
- **Don't** use buoy or storm hues for decoration, and don't show Unable to Verify as Missing.
- **Don't** add a second border weight or new corner radii beyond 4 / 6 / 7 / 8 / 12px and the pill.
- **Don't** use hard offset or colored shadows. Depth is the ambient shadow plus the tonal ramp.
