# App Review: Guideline 2.1 "Information Needed" (prepared before submitting)

Expect a 2.1 request for a physical-device screen recording plus six answers (Wisconsin's first submission drew one). Record the
screen recording **before** submitting and upload it in **App Review Information → Attachment**; the listing's review notes
(playbook/app-store/listing.json) already answer the questions. If Apple asks anyway, paste the reply below into **Reply to App
Review** with the recording. Keep it under 4,000 characters (now 3,991); recount after the final data build.

## Screen recording (Nick, on his iPhone, latest iOS)
Install through TestFlight first (internal group; the tester email must be the Apple ID under Settings › your name › Media &
Purchases). Record with Control Center → Screen Recording, 60–120 s, no sound:
1. Start on the Home Screen and tap **Arkansas Eats**. The recording must begin with the launch.
2. Home: scroll the guide cards a little.
3. Tap **Barbecue**, then **McClard's Bar-B-Q** (Hot Springs, founded 1928, a Food Hall of Fame inductee).
4. Tap **Ratings, hours & photos**. Apple's place card opens. Close it.
5. Tap the **heart** (Save), then go back twice.
6. Tap the Home search box and type `dairy bar`. Open **Salem Dairy Bar**.
7. Tap the **Map** tab, then **Arkansas picks**. Tap a numbered circle to zoom in, then a pin, then the ⓘ in its bubble.
8. Tap **Saved**, where the saved place shows. Then **About**, and scroll to the sources.

## Reply text
```
Thank you. Here is the information requested. A screen recording from an iPhone running the latest iOS is attached. It starts at launch and shows the full flow.

1. Screen recording: attached. There is no account, login, user-generated content or paid content.

2. Purpose and audience: Arkansas Eats is a free guide to restaurants in Arkansas (the U.S. state). Its focus is the state's own food: the Cheese Dip Trail, barbecue, catfish houses, dairy bars and drive-ins, homemade pie and the Arkansas Food Hall of Fame, 68 places checked by hand in fall 2026 against a 2025 or 2026 source, plus James Beard honorees. It also lists 7,279 restaurants, cafés and bars in 336 towns from open map data. It is for residents and visitors deciding where to eat, with no ads, account or tracking.

3. How to use it (no login, no setup, no sample files needed):
- Home → Cheese Dip Trail (or Barbecue, Catfish Houses, Dairy Bars & Drive-Ins, Homemade Pie, Food Hall of Fame, James Beard Honors, Oldest Places, Near Me) → tap any place.
- On a place, tap "Ratings, hours & photos" to open Apple Maps' own place card through MapKit. Directions, Call and Website are below it; further down, the Health inspections section shows the state health department's latest inspection (date and count of observations, as ADH lists it), with a link to its search in Safari.
- Search from the Home search box by name, town, street or dish ("cheese dip", "barbecue hot springs", "dairy bar").
- The Map tab shows each guide as pins. "My location" and the Nearest sort use location only if allowed, on the device.
- The heart saves a place on the device (Saved tab). The About tab lists the sources, licenses and the independence statement.
- On iPad, a sidebar replaces the tabs; a place opens in the right-hand column.
- Location: if you're outside Arkansas (as App Review usually is), the map says so and stays on Arkansas, and distance sorting still works from where you are.

4. External services and data:
- Apple MapKit: maps, local search to find a place's Apple Maps listing, and Apple's place card for live hours, photos and ratings.
- Core Location: optional, on-device only, for distance sorting.
- Data updates: at most once a day, the app checks the Arkansas Eats website (static files on GitHub Pages) for newer restaurant data and downloads it if there is some. The requests carry no identifiers or location.
- No backend, accounts, analytics, advertising, payments or AI services. The restaurant data is bundled in the app.
- Bundled data sources: Overture Maps Foundation open place data (CDLA Permissive 2.0 and others; license texts are in the app); the inspections the Arkansas Department of Health lists in its public search; DFA Alcoholic Beverage Control's public permit list; the Arkansas Food Hall of Fame's inductees and James Beard Foundation honors (facts only); and our own research of public tourism pages and local news.
- The website with the privacy policy and support page is static and hosted on GitHub Pages: https://nickstrom5.github.io/arkansas-eats/

5. Regional differences: none. The content covers Arkansas; the app is offered in the United States and works the same everywhere.

6. Regulated or protected material: the app is not in a regulated industry and includes no protected third-party material. The data is open-licensed or public record, with attribution and licenses on the About tab. Inspections are shown only as the state health department lists them, dated and labeled official, with its note; the app computes no grade and never ranks by inspections. No permit holder's personal name is shown. Ratings, hours and photos are shown only inside Apple's own place card through MapKit; the app stores no ratings or reviews. Every website link was checked before release, and adult venues are excluded. The app is independent and not affiliated with any restaurant, agency, the Arkansas Food Hall of Fame or the James Beard Foundation.

Support: nick@eatsranked.com
```

## If Apple cites 4.3(a) (one app per state)
Arkansas Eats is built around Arkansas's own food and sources: Arkansas Tourism's Cheese Dip Trail, Delta and Hot Springs barbecue,
catfish houses on the White River, the state's dairy bars and drive-ins, homemade pie, and the Arkansas Food Hall of Fame's inductees.
No place, guide or text is shared with another app. (Never compare it with other state apps in the Notes.)
