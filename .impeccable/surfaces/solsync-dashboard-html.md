---
version: 1
slug: "solsync-dashboard-html"
primary_target: "solsync/dashboard.html"
related_targets: []
---

# Dashboard surface brief

Scope: the local SolutionSync dashboard (solsync/dashboard.html), all four views: Overview,
Solutions, Activity, Settings. Visitor mode: Operate.

Audience and job: one student developer, any time of day, light or dark room, opening it
mostly to confirm the automation is healthy and nothing failed; occasionally to find a
solution, run a sync, pause automation, or change the daily limit.

Constraints: real data only from the local API; every control performs a real engine
action; standard web controls; works on desktop and phone; no external assets or fonts
(Windows system faces only); no build step; the UI never counts or bypasses the quota.

Memorable moment: today's tide, the day's uploads drawn as a rising line on a Manila
midnight-to-midnight axis, beside a harbor-conditions verdict.

## Direction contract

THESIS: Each Manila day is one tide that rises with verified uploads, read beside a harbor-conditions bulletin that answers "is everything OK" before anything else. Refuses the category default of a row of identical stat tiles over a generic chart.

OWN-WORLD: Harbor chart palette: deep-sea teal rail (#0e3442), sea-glass ground and panels on one tide-water tonal ramp, sea-foam fills for published/healthy, buoy orange for attention, signal red for failure, chart-brass for limits. Bahnschrift for figures and labels (tide-table tabular numerals, tracked caps), Segoe UI Variable for prose. Single-weight hairlines, 8px corner radius, light and dark tides.

STORY: The visitor sees the bulletin verdict first, then today's tide against the limit, then each platform station's progress, then the evidence: the last runs and commits. They act from the header (Scan, Refresh, Run Sync) or go to the queue.

FIRST VIEWPORT: Left teal rail with brand, four views and the live automation pennant at its foot. Page header with title, context line and actions at right. Bulletin strip full width. Below, two columns: today's tide chart (large figure 4/4, curve with upload markers, hour axis, limit line) and the two stations with progress. Then a figures band and recent log with a 14-day tide strip.

FORM: Harbor Tide Table, position 7 of 7 on the grounded list, seed:b69570e0316c7ad2. Raises: star atlas (one size ramp for importance), centre rail (one hairline weight), zone sheets (one tonal ramp), monochrome (every number paired with its proof).

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
