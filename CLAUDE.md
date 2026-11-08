# Arkansas Eats (ar-eats) — notes for Claude Code sessions

Built 2026-11-06 by a side session for Nick's "build the 17 states left" (group: Alabama, Mississippi, Arkansas, Oklahoma), ported from
`../ms-eats/` (itself from `../al-eats/` and `../wy-eats/`, the newest finished state of 2026-11-05: delivery-only brands hidden, the
website blocklist and `link_blocklist.py`, the Share link `Links.site + explore/#p=<id>`, over-the-air data, adult-venue filtering, the
Denny's delivery-brand rule, the `playbook/app-store/listing.json` format). Local only: git-ignored data, no repo, no remote, nothing
published, nothing in App Store Connect. Sources: `playbook/12-sources.md`. Brand: `playbook/05-naming.md` — **final** (Nick's decisions, 2026-11-07: "Arkansas Eats: Restaurants", Home Screen "Arkansas Eats"; a cheese dip bowl and chip icon, concept A, on
cardinal; Ozark forest #2E5E3E, cardinal #9D2235, charcoal #2B2B2B, diamond gold #E9C46A as a fill only, limestone #F3EEE3; a
diamond header band).

## Status (2026-11-07)
- See the end of this file (updated last).

## Arkansas is different
- **Two official lists (Nick's yes, 2026-11-06).** ADH's inspection search (`fetch_official.py --go`; 12 months, every county; the
  search stops at 500 results, so `--months <county ids>` reads the big counties month by month) and DFA ABC's monthly permit
  spreadsheet. Both only attach to places they match; `official._group_biz` groups one business's records (its inspection and its
  permit) at the same number and street in the same zip or town (the lists disagree on zips). A place shows its latest ADH inspection as ADH lists it ("Latest inspection (ADH) · date · 6 observations", ADH's note
  word for word), never a grade; "ADH Inspections" is one list among the guides, sorted by date, distance or name. "Serves alcohol"
  comes only from a matched on-premises permit (unknown, never "no", otherwise).
- **No Google data anywhere**, not even the private web build (`listings.py` makes an empty Google 2021 table). With no official
  list, `calibrate.py` measures nothing; the keep rule is the family's (Meta 0.95, or 0.90 with a website).
- **No MICHELIN Guide covers Arkansas**: the honors guide is "James Beard Honors"; the Bib Gourmand filter hides itself.
- **Hand-checked matching is strict** (from ms-eats): a statewide name match must be within 30 km of the checked town's centre, and
  the checked town overrides a listing's town only when the source's address matched. Every research file's spellings count
  (`load_research` merges `match_names` across files). Keep short aliases out of `match_names`: "DIZZYS" also matched Izzy's.
- **Guides** (tags in `arkansas.py` TAGS; bits 1..64): cheesedip (Arkansas Tourism's Cheese Dip Trail), bbq, catfish, pies (homemade
  pie), dairybar (dairy bars and drive-ins), halloffame (Arkansas Food Hall of Fame inductees with a 2025-26 source showing them
  open), oldest (founded 1960 or earlier, by the 2026 source's year; some have moved since). Research is hand-written in
  `data/research/app/*.json`; `build_research.py` only checks it and writes `LEADS.md`.
- **Honors**: James Beard: Jones Bar-B-Q Diner (America's Classics 2012) and Lassis Inn (2020); Conifer (Matthew Cooper) and Yeyo's
  (Rafael Rios), Best Chef: South finalists 2025; Heirloom (Jason Paul) and Onyx Coffee Lab, finalists 2026; Wright's Barbecue
  (Jordan Wright), semifinalist 2025.
- **Venues**: the Razorback and Arkansas State stadiums and arenas, Simmons Bank Arena, the prisons (Cummins, Varner, Tucker,
  Wrightsville units) and bases (Little Rock AFB, Fort Chaffee, Camp Robinson, Pine Bluff Arsenal); airports by address (Clinton
  National and XNA at 1 Airport, Fort Smith at 6700 McKennon, Texarkana at 201 Airport). CASINO is no venue word (Oaklawn, Southland,
  Saracen).

## Rebuild
```bash
cd pipeline
../.venv/bin/python check_sources.py URL...   # a new host first
../.venv/bin/python fetch_overture.py && ../.venv/bin/python fetch_extras.py && ../.venv/bin/python fetch_official.py --go   # ~2 h; then --months 198,210,217,220,254,260,266
../.venv/bin/python geocode_official.py && ../.venv/bin/python geocode_census.py && ../.venv/bin/python listings.py
../.venv/bin/python calibrate.py && ../.venv/bin/python arkansas.py && ../.venv/bin/python build_research.py
AR_APP=1 ../.venv/bin/python arkansas.py && cd .. && cp data/app/places.json data/app/detail-*.json ArkansasEats/Resources/
.venv/bin/python pipeline/check_websites.py && .venv/bin/python pipeline/check_websites.py --retry-transient   # then re-export
.venv/bin/python scripts/make-site.py && .venv/bin/python scripts/publish_app_data.py && .venv/bin/python scripts/publish_app_data.py --check
.venv/bin/python scripts/qa-site.py && .venv/bin/python scripts/write-listing.py
```
The `.venv` is on the python.org framework Python 3.12 with md-eats' versions. `data/chain_auv.json` is a copy of wy-eats'.

## App, site, screenshots
- App: `ArkansasEats/` (XcodeGen `project.yml`, bundle `com.arkansaseats.ios`, display "Arkansas Eats"), tests in
  `ArkansasEatsTests/` (fixture, guides, inspections as ADH lists them, never a grade, outline towns: Texarkana, Fort Smith, West Memphis in; Texarkana TX,
  Arkoma OK, Memphis, Greenville MS out; data guards) and `ArkansasEatsUITests/`. Tests: `xcodebuild test -scheme ArkansasEats
  -destination id=<sim> -parallel-testing-enabled NO` with `DEVELOPER_DIR="/Applications/Xcode 1.app/Contents/Developer"` (no
  CODE_SIGNING_ALLOWED=NO: UI tests need a signed runner). Archive only with Xcode 1.app (27.2, 27B52). Run `xcodegen generate`
  whenever `Resources/*.json` changes.
- Site: `scripts/make-site.py` → `docs/` (no static inspections page: ADH's inspections are one list in the web app, "ADH inspections"); `scripts/explore.js` the web app;
  `scripts/qa-site.py`. URL for now: nickstrom5.github.io/arkansas-eats (no CNAME). City pages from CITY_WANTED where a town has at
  least 4 listed places (Little Rock, Fayetteville).
- Screenshots: `scripts/capture-screenshots.sh <sim> home cheesedip bbq catfish dairybar pies halloffame detail map honors oldest
  inspections saved about` (ScreenshotMode pins Little Rock's Riverdale; downtown Little Rock for the map, a 5 km span so Doe's and Dizzy's are single pins; Benton for the dairy bars; Hot Springs for the detail, McClard's), then
  `scripts/site-images.sh`, make-site, qa-site; App Store frames `scripts/appstore-screenshots.py` (iPhone: home cheesedip detail
  bbq dairybar map catfish saved; iPad: home cheesedip bbq map dairybar halloffame).

## Rules
No commits, pushes, public repos, App Store Connect or DNS changes without Nick's yes each time; never submit for review or accept
agreements; never publish Google-derived data. Support email nick@eatsranked.com. Commit author "Nick Soderstrom"
<329204362+nickstrom5@users.noreply.github.com> via `-c user.name -c user.email`.

## Status (2026-11-07, final)
- DONE: pipeline (Overture 2026-10-21.0, 75 counties, border towns checked), ADH's inspection search and DFA ABC's permit list
  (Nick's yes, 2026-11-06), research (75 entries, 73 matched; Taco Mama in Hot Springs and Bruce Terri Drive-In in Barling are
  leads), app export **7,602 places / 7,279 restaurants** (5,645 places show ADH's latest inspection as ADH lists it, 5,430 of them
  restaurants; 1,441 an ABC on-premises permit), website link check (3,200 OK), Swift app, icon concepts (all pass check.swift) +
  make-brand, site (15 pages incl. Little Rock and Fayetteville) + web app, OTA local copy `--check` OK, `listing.json` (lengths
  checked), 12-sources and 13-app-review-reply (3,991 characters) at the final counts.
- Records group by zip or town (DFA lists Doe's in Little Rock at 72207, ADH at 72201): 41 more places got an inspection and
  36 a permit. The street key drops "# suite" (ok-eats' fix, 2026-11-07:
  "8901 Jenny Lind #7" is Jenny Lind), so 8 more places got an inspection and 3 a permit.
- Tests (iOS 27.0 simulators, Xcode 1.app 27.2): iPhone 17 Pro Max: 49 unit + 6 UI tests pass (the launch-time test skipped on a
  busy Mac). iPad 13": all pass but testLaunchIsQuick, which measured 6.35 s at load 16.5 (limit 6 s) and, rerun alone, was skipped
  at load 26 (5.4 s) and again from a quiet start (7.0 s at load 53). On a quiet Mac (the parent session's run, 2026-11-07) it
  passed on iPhone at 4.56 s and on iPad at 4.85 s. After the last data change (the grouping) the unit tests, data guards included, passed again on both.
- Screenshots: 13 iPhone + 6 iPad captures (the map recaptured on downtown Little Rock, single pins; the place, inspections and
  every iPad frame recaptured on the final data), App Store frames in `playbook/app-store/{iphone,ipad}/`, site images; full
  `qa-site.py` (static + browser) passes.
- **Ready to publish**; nothing is public. Nick's decisions (2026-11-07): the name "Arkansas Eats: Restaurants", the subtitle
  "Cheese Dip, Barbecue & Catfish", icon A (the cheese dip bowl and chip, on cardinal) and the palette are final. The launch-time
  test passed on a quiet Mac (iPhone 4.56 s, iPad 4.85 s, the parent session's run of 2026-11-07). The "# suite" street-key fix is rebuilt (data, site, listing),
  its unit tests pass on iPhone and iPad (2026-11-08), and the screens that show its counts are recaptured (iPhone home,
  inspections and About; the iPad home frame); full `qa-site.py` passes. Arkansas is final.
