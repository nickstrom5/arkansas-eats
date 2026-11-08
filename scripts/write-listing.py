#!/usr/bin/env python3
"""Writes playbook/app-store/listing.json (the App Store listing, the family's format: wy-eats/playbook/app-store/listing.json) with
every count taken from data/app/places.json, so the copy can't drift from the data. Checks Apple's lengths, that no keyword repeats a
word of the name or subtitle, and that no keyword is "best", "top" or "#1".
Usage (from ar-eats/): .venv/bin/python scripts/write-listing.py   (re-run after every data rebuild)"""
import json, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
d = json.load(open(f"{ROOT}/data/app/places.json"))
P = [p for p in d["places"] if not p.get("v")]
bit = {t: 1 << i for i, t in enumerate(d["tags"])}
n = {t: sum(1 for p in P if p.get("hc") and (p.get("g", 0) & bit[t])) for t in d["tags"]}
n_hc = sum(1 for p in P if p.get("hc") and (p.get("g", 0) & sum(bit.values())))
hon = sum(1 for p in P if p.get("mi") or p.get("jbf"))
bib = sum(1 for p in P if p.get("mi") == 2)
towns = len({p["c"] for p in P if p.get("c") is not None})
R = len(P)
scored = sum(1 for p in P if p.get("in"))
inspected = scored
SITE = "https://nickstrom5.github.io/arkansas-eats/"
name = "Arkansas Eats: Restaurants"
sub = "Cheese Dip, Barbecue & Catfish"
desc = f"""Arkansas's restaurants, from cheese dip in Little Rock to barbecue in the Delta and dairy bars in the Ozarks.

Arkansas Eats is a free guide to eating in Arkansas: {n['cheesedip']} stops on the Cheese Dip Trail, {n['bbq']} barbecue places, {n['catfish']} catfish houses, {n['dairybar']} dairy bars and drive-ins, {n['pies']} places for homemade pie and {n['halloffame']} Arkansas Food Hall of Fame restaurants we checked by hand, plus {R:,} restaurants, cafés, bars and bakeries in {towns} towns, from Little Rock, Fayetteville and Fort Smith to Hot Springs, Jonesboro and the Delta. No account, no ads.

ARKANSAS GUIDES
• Cheese Dip Trail: the dip Arkansas claims, from the Heights in Little Rock to Hot Springs and Fayetteville.
• Barbecue: Jones Bar-B-Q Diner in Marianna to McClard's in Hot Springs.
• Catfish Houses: Des Arc on the White River to El Dorado.
• Dairy Bars & Drive-Ins: burgers and shakes from Siloam Springs to Blytheville.
• Homemade Pie: Keo, the Ozarks and Springdale.
• Food Hall of Fame: the Arkansas Food Hall of Fame's inductees that are still serving.
• James Beard: {hon} honored Arkansas restaurants, from America's Classics to recent finalists.

FIND IT FAST
• Sort by distance, or browse the map by guide.
• Search by name, town, street or dish: "cheese dip", "barbecue hot springs", "dairy bar".
• Filter by town or cuisine, or hide chains.
• Save places, and find hand-checked places from iPhone search (Spotlight).

LIVE DETAILS FROM APPLE MAPS
Tap "Ratings, hours & photos" on any place to open Apple Maps' own place card, with current hours, photos, ratings and directions.

HOW THE LISTS ARE BUILT
Every guide place was checked by hand in fall 2026 against a 2025 or 2026 source: Arkansas Tourism's own pages, the Arkansas Food Hall of Fame or a dated local story. The rest come from Overture Maps open data. For {inspected:,} places, the app shows the Arkansas Department of Health's latest inspection as ADH lists it: the date and the number of observations on its report, with ADH's note that an inspection is a snapshot in time. ADH gives no score or grade; the app computes none and never ranks by inspections. Alcohol permits come from DFA Alcoholic Beverage Control's monthly permit list. Website links are checked too. Newer restaurant data downloads from the Arkansas Eats website when there is some.

PRIVATE BY DESIGN
No account, no tracking, no ads. Your location, if you share it, only sorts lists on your device. Saved places stay on your device.

Places open and close, so check before you go. Spot a mistake? Email nick@eatsranked.com.

An independent app, not affiliated with any restaurant, chain or government agency (including the State of Arkansas, the Arkansas Department of Health, Arkansas Tourism or the Division of Arkansas Heritage), or with the Arkansas Food Hall of Fame or the James Beard Foundation. James Beard Foundation and James Beard Award are trademarks of the James Beard Foundation. Place data from Overture Maps Foundation (CDLA Permissive 2.0) and others; sources and licenses are on the About tab."""
kw = "little rock,fayetteville,hot springs,fort smith,bentonville,ozarks,delta,queso,dairy bar,drive in"
promo = (f"Cheese dip, barbecue, catfish houses and dairy bars: {n_hc} places checked by hand, plus {R:,} Arkansas restaurants, "
         "nearest first.")
review = f"""1. Purpose and audience: Arkansas Eats is a free guide to restaurants in Arkansas (the U.S. state). Its focus is the state's own food: the Cheese Dip Trail, barbecue, catfish houses, dairy bars and drive-ins, homemade pie and the Arkansas Food Hall of Fame, {n_hc} places checked by hand in fall 2026 against a 2025 or 2026 source, plus James Beard honorees. It also lists {R:,} restaurants, cafés and bars in {towns} towns from open map data. It is for residents and visitors deciding where to eat, with no ads, account or tracking.

2. How to use it (no login, no setup, no sample files needed):
- Home → Cheese Dip Trail (or Barbecue, Catfish Houses, Dairy Bars & Drive-Ins, Homemade Pie, Food Hall of Fame, James Beard Honors, Oldest Places, Near Me) → tap any place.
- On a place, tap "Ratings, hours & photos" to open Apple Maps' own place card through MapKit. Directions, Call and Website are below it; further down, the Health inspections section shows the state health department's latest inspection (date and count of observations, as ADH lists it), with a link to its search in Safari.
- Search from the Home search box by name, town, street or dish ("cheese dip", "barbecue hot springs", "dairy bar").
- The Map tab shows each guide as pins. "My location" and the Nearest sort use location only if allowed, on the device.
- The heart saves a place on the device (Saved tab). The About tab lists the sources, licenses and the independence statement.
- On iPad, a sidebar replaces the tabs; a place opens in the right-hand column.
- Location: if you're outside Arkansas (as App Review usually is), the map says so and stays on Arkansas, and distance sorting still works from where you are.

3. External services and data:
- Apple MapKit: maps, local search to find a place's Apple Maps listing, and Apple's place card for live hours, photos and ratings.
- Core Location: optional, on-device only, for distance sorting.
- Data updates: at most once a day, the app checks the Arkansas Eats website (static files on GitHub Pages) for newer restaurant data and downloads it if there is some. The requests carry no identifiers or location.
- No backend, accounts, analytics, advertising, payments or AI services. The restaurant data is bundled in the app.
- Bundled data sources: Overture Maps Foundation open place data (CDLA Permissive 2.0 and others; license texts are in the app); the inspections the Arkansas Department of Health lists in its public search; DFA Alcoholic Beverage Control's public permit list; the Arkansas Food Hall of Fame's inductees and James Beard Foundation honors (facts only); and our own research of public tourism pages and local news.
- The website with the privacy policy and support page is static and hosted on GitHub Pages: {SITE}

4. Regional differences: none. The content covers Arkansas; the app is offered in the United States and works the same everywhere.

5. Regulated or protected material: the app is not in a regulated industry and includes no protected third-party material. The data is open-licensed or public record, with attribution and licenses on the About tab. Inspections are shown only as the state health department lists them, dated and labeled official, with its note; the app computes no grade and never ranks by inspections. No permit holder's personal name is shown. Ratings, hours and photos are shown only inside Apple's own place card through MapKit; the app stores no ratings or reviews. Every website link was checked before release, and adult venues are excluded. The app is independent and not affiliated with any restaurant, agency, the Arkansas Food Hall of Fame or the James Beard Foundation.

Support: nick@eatsranked.com"""
L = {"bundleId": "com.arkansaseats.ios", "name": name, "subtitle": sub, "privacyPolicyUrl": SITE + "privacy.html",
     "primaryCategory": "FOOD_AND_DRINK", "secondaryCategory": "TRAVEL", "description": desc, "keywords": kw, "promotionalText": promo,
     "supportUrl": SITE, "marketingUrl": SITE, "reviewNotes": review}
for k, lim in [("name", 30), ("subtitle", 30), ("keywords", 100), ("promotionalText", 170), ("description", 4000), ("reviewNotes", 4000)]:
    assert len(L[k]) <= lim, (k, len(L[k]), lim)
    print(f"{k}: {len(L[k])}/{lim}")
words = {w.lower().strip(":,&") for w in (name + " " + sub).split()}
assert not ({w for w in kw.replace(",", " ").split()} & words), "a keyword repeats the name or subtitle"
assert not any(b in kw.split(",") for b in ("best", "top", "#1"))
os.makedirs(f"{ROOT}/playbook/app-store", exist_ok=True)
json.dump(L, open(f"{ROOT}/playbook/app-store/listing.json", "w"), indent=1, ensure_ascii=False)
print("wrote playbook/app-store/listing.json")
