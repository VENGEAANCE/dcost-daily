# Motion rehearsal

Intent: a real input produces one readable response, then the page rests. Location: the existing battery progress, savings comparison, calculator savings, mobile menu and action buttons. Focal object: the cell just read or the value just changed. Payoff: a filled cell or current comparison, left visible. No artificial cursor, sample data, autoplay demo or decorative loop.

Applied skill: [benjitaylor/skills stageshow](https://github.com/benjitaylor/skills/tree/main/stageshow), particularly motion.md and craft.md. Studied the choreography example's retained tracks and overlapping dependent responses. This is an adaptation to the existing live HTML/CSS/JS product, not a faux-product Stage: no gold component or React kit was copied. Stage-specific film/gate tools were not used or claimed to pass.

Motion specification:
- New reading completion: the existing button retains its identity and focus; its fill travels left to right for 450ms. Previously read cells stay filled without replay on refresh.
- Updated savings/progress text: a 220ms opacity response on the actual value; no interpolated or invented numbers.
- Current EIA comparison: two bars settle over 650ms, staggered by 70ms, once at 30% visibility after data arrives. The savings value overlaps the bar response. The dashed gap keeps its final geometry.
- Menu: 160ms opacity and 200ms, 6px travel; closing disables interaction immediately using inert. Escape and rapid toggles preserve the real control state.
- Buttons: 1px press/hover feedback; charger filtering uses a 200ms opacity transition.
- Reduced motion: CSS transitions and battery animation stop, JS animations cancel on preference change, and the real final values stay visible. No essential content is hidden behind animation.

Rehearsal evidence:
- [1280 progress frames](motion-1280-frames.png), [390 progress frames](motion-390-frames.png): start, travel, landing and rest. Reviewed the phone sheet for label legibility, stable button geometry and final fill.
- Checked both widths: retained cell identity, completed state, no replay of saved cells, animation cleanup and reduced-motion behavior. Phone menu is inert when closed.
- Verified the comparison waits below the fold, animates on entry, cancels immediately when reduced motion is enabled mid-animation, and does not replay when scrolled away and back.
- Re-ran all 194 page/viewport checks and the menu, calculator/state-rate, charger-filter, persistence/focus and fetch-failure checks. All passed. All 6,693 static link/asset targets and sitemap routes resolve.
- Updated the six still screenshots after motion settled. External font, image, newsletter and Worker limitations remain as documented in README.md.

No deployment or merge. Existing data and affiliate configuration are unchanged.
