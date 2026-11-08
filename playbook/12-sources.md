# Arkansas sources and calibration (checked 2026-11-06)

## Official sources (Nick approved the ADH pull and the ABC list on 2026-11-06: "Yes, all four", through the parent session)
| Source | What it has | Can a script read it? | Used |
|---|---|---|---|
| Arkansas Department of Health, Food Establishment Inspection search (foodserviceprod.adh.arkansas.gov/Web/inspection/publicinspectionsearch.aspx) | every food establishment's inspections (ADH inspects all 75 counties): date, type and the number of observations on the report ("Observation(s) 6", or none); **no score, grade or placard**; the page says each inspection "is only a snapshot in time" | an ASP.NET postback form; no export, API, CAPTCHA or robots.txt | yes: every county, 2025-11-05 to 2026-11-05, 15 establishments a page, one request every 3 s with a generic client name. The search stops at 500 results, so the seven largest counties (Benton, Craighead, Faulkner, Garland, Pulaski, Sebastian, Washington) were read month by month: **24,954 establishments** |
| DFA Alcoholic Beverage Control, full permit list (dfa.arkansas.gov "Permit Changes"; FullPermit202609.xlsx, posted 2026-10-12) | every active permit: company, alias, permit types, owner, address, county | yes: one .xlsx (robots.txt allows it) | yes: 4,709 holders with an on-premises (restaurant mixed drink, beer or wine on premises, private club) or package permit; owner names are never shown |
| ADH records request | an extract | only Arkansas citizens may request | no |
| ABC/GIS "Alcoholic Beverage Wet Dry Areas" layer | dry counties and townships | yes (ArcGIS) | no (dry never means "No": private club permits) |
| GIS Office statewide parcels | land and building values, owner names | yes | no (terms unconfirmed; owner names never ship) |

ADH's rows and ABC's permits never add a place; they attach to the places they match (an address-and-name match), and one
business's records (its inspection and its permit) are grouped. A place shows its latest inspection as ADH lists it: the date and
the number of observations, labeled ADH's, with ADH's note ("Remember this inspection is only a snapshot in time. It represents only
what the inspector saw on the particular date of inspection."); never a grade, and no list is ranked by it. The app's "ADH
Inspections" list sorts by date, distance or name. "Serves alcohol" is yes only for a matched on-premises permit; otherwise unknown.

## Calibration
- The keep rule is the family's (Meta 0.95, or 0.90 with a website); a listing matched to an official record (an ADH inspection or an
  ABC permit) is kept as confirmed. `calibrate.py` gives every listing its county.
- No Google data anywhere (not even the private web build): listings.py's Google 2021 table is empty.
- Overture 2026-10-21.0: 13,185 eating and drinking listings in the Arkansas box (486 marked closed by Overture). Matched to an
  official record: 6,393 listings. The App Store build ships **7,602 places, 7,279 restaurants** (Census CBP 2023: 5,665 NAICS 722
  establishments): 5,645 places (5,430 restaurants) show an ADH inspection and 1,441 an ABC on-premises permit. Records
  of one business group at the same number and street in the same zip or town (DFA lists Doe's in Little Rock at 72207, ADH at 72201).
- Website links: 5,426 checked, 3,200 OK after the checks and the transient retries; gambling, adult and hacked pages dropped.
  One adult club removed (Silver Dollar Cabaret, near an Overture adult venue).
- Border towns checked against the outline: Texarkana, Fort Smith, Van Buren, Siloam Springs, Bella Vista, West Memphis, Lake Village,
  Helena, El Dorado, Blytheville and Mammoth Spring are inside; Texarkana (Texas), Arkoma and Pocola (Oklahoma), West Siloam
  Springs, Memphis, Greenville and Vicksburg (Mississippi), Monroe (Louisiana) and Poplar Bluff (Missouri) are out.

## Research sources (each place cites its own; every host passed check_sources.py)
- Arkansas Tourism: "Arkansas Cheese Dip Trail" and "Follow the Arkansas Cheese Dip Trail" (arkansas.com, current pages, read
  2026-11-06): 15 places (16 entries: Stoby's has two), 15 matched. Its per-restaurant listing pages now redirect to a general page, so none is cited.
- Only in Arkansas, "Arkansas drive-ins and dairy bars" (2025-07-11): 27 places, 28 entries (Tacker's has three), 27 matched.
- Somewhere in Arkansas, "34 Famous Restaurants in Arkansas You Should Visit" (2026-10-04): addresses, founding years and current
  status for the barbecue, catfish, pie, Food Hall of Fame and oldest entries.
- Division of Arkansas Heritage, Arkansas Food Hall of Fame past winners (2017-2025) and 2026 finalists (arkansasheritage.com);
  KKYR, 2025 Food Hall of Fame finalists (2025-07-11) and Arkansas's best barbecue (2025-03-12).
- Tasting Table, the best pie in Arkansas (2026-03-01): Charlotte's Eats & Sweets, Keo.
- jamesbeard.org: Jones Bar-B-Q Diner (America's Classics 2012), Lassis Inn (2020), the 2025 and 2026 semifinalists and nominees
  (Conifer, Yeyo's, Wright's Barbecue, Heirloom, Onyx Coffee Lab). No MICHELIN Guide covers Arkansas.
- Blocked (robots or a bot check): arktimes.com, arkansasonline.com, nwaonline.com, hotsr.com, texarkanagazette.com, kark.com,
  katv.com, kait8.com, ozarksfirst.com, myarklamiss.com, the nwahomepage digital-release pages, talkbusiness.net,
  arkansasbusiness.com, ardot.gov, southernliving.com, eatthis.com; onlyinyourstate.com answers 403. Only in Arkansas's pie,
  catfish and barbecue roundups are dated 2020-2024, too old for the rule.
- Leads (data/research/app/LEADS.md): Taco Mama (two Hot Springs branches; the trail gives no address), Bruce Terri Drive-In
  (Barling; no listing). Food Hall of Fame inductees left out for want of a 2025-26 source: Lassis Inn (on the James Beard list),
  Franke's Cafeteria, Cattleman's Steak-House, Star of India, Bulldog Restaurant, Colonial Steak House, Keeny's Food Market and
  Burge's; K Hall & Sons (2025) is a produce market, not a restaurant.
