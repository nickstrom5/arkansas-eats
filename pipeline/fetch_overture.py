"""Download the Overture Maps extracts that arkansas.py reads -> data/ar/

- overture_ar_bbox.parquet     every place in Arkansas's bounding box (name, category, address, point)
- overture_ar_sources.parquet  which datasets each Arkansas eating/drinking listing came from (Meta, Foursquare, ...)
- ar_shapes.json               simplified state and county outlines for the map
- ar_state_detail.geojson      the state outline at full detail, for the in-state test

Reads the public Overture bucket over S3 with DuckDB (no account needed). Ported from ms-eats/pipeline/fetch_overture.py.
Arkansas: land division areas; the "counties" are its 75. The script checks the towns on and near its lines (Texarkana on State Line
Avenue, Fort Smith by Arkoma and Pocola, Siloam Springs, Bella Vista, West Memphis by Memphis, Lake Village and Helena across the river
from Mississippi, El Dorado above Louisiana, Blytheville and Mammoth Spring below Missouri) so a Texas, Oklahoma, Missouri, Tennessee,
Mississippi or Louisiana listing stays out.
"""
import os, json, time
import duckdb
from shapely import wkb
from shapely.geometry import mapping, Polygon

RELEASE = "2026-10-21.0"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "ar")
# Arkansas (33.0°N–36.5°N, 89.64°W–94.62°W) plus a margin for the border towns
BBOX = "bbox.xmin BETWEEN -94.75 AND -89.5 AND bbox.ymin BETWEEN 32.9 AND 36.6"
EAT = "('restaurant','casual_eatery','bar','fast_food_restaurant','coffee_shop','cafe','smoothie_juice_bar','brewery','food_court')"
os.makedirs(OUT, exist_ok=True)

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial; SET s3_region='us-west-2';")
places = f"s3://overturemaps-us-west-2/release/{RELEASE}/theme=places/type=place/*.parquet"

t = time.time()
if not os.path.exists(f"{OUT}/overture_ar_bbox.parquet"):
    con.execute(f"""
COPY (
  SELECT id, names.primary AS name, basic_category AS cat, taxonomy.primary AS tax, taxonomy.hierarchy AS hier, confidence,
         operating_status AS status, brand.names.primary AS brand, addresses[1].freeform AS street, addresses[1].locality AS city,
         addresses[1].postcode AS zip, addresses[1].region AS region, ST_Y(geometry) AS lat, ST_X(geometry) AS lon, websites[1] AS web,
         phones[1] AS phone
  FROM read_parquet('{places}', hive_partitioning=1) WHERE {BBOX}
) TO '{OUT}/overture_ar_bbox.parquet' (FORMAT PARQUET)""")
    print("places in bbox", round(time.time() - t), "s", flush=True)
if not os.path.exists(f"{OUT}/overture_ar_sources.parquet"):
    con.execute(f"""
COPY (
  SELECT id, list_transform(sources, lambda x: x.dataset) AS ds, list_transform(sources, lambda x: x.update_time) AS ut,
         list_transform(sources, lambda x: x.record_id) AS rid,
         len(socials) AS n_soc, len(websites) AS n_web, len(phones) AS n_ph
  FROM read_parquet('{places}', hive_partitioning=1)
  WHERE {BBOX} AND basic_category IN {EAT}
) TO '{OUT}/overture_ar_sources.parquet' (FORMAT PARQUET)""")
    print("sources", round(time.time() - t), "s", flush=True)

areas = f"s3://overturemaps-us-west-2/release/{RELEASE}/theme=divisions/type=division_area/*.parquet"
rows = con.execute(f"""
  SELECT subtype, names.primary AS name, ST_AsWKB(geometry) AS g
  FROM read_parquet('{areas}', hive_partitioning=1)
  WHERE country = 'US' AND region = 'US-AR' AND subtype IN ('region', 'county') AND class = 'land'
    AND bbox.xmin > -94.8 AND bbox.xmax < -89.4 AND bbox.ymin > 32.8 AND bbox.ymax < 36.7""").fetchall()


def rings(geom, tol, min_area):
    geom = geom.simplify(tol, preserve_topology=True)
    polys = [p for p in getattr(geom, "geoms", [geom]) if p.geom_type == "Polygon" and p.area >= min_area]
    return [[[round(x, 3), round(y, 3)] for x, y in p.exterior.coords] for p in polys]


out = {"state": None, "counties": []}
for sub, name, g in rows:
    geom = wkb.loads(bytes(g)).buffer(0)
    if sub == "region":
        json.dump(mapping(geom.simplify(0.0005, preserve_topology=True)), open(f"{OUT}/ar_state_detail.geojson", "w"))
        out["state"] = [[r] for r in rings(geom, 0.002, 0.000005)]
    else:
        out["counties"].append({"name": name, "c": rings(geom, 0.004, 0.00002)})
# full-detail county polygons for assigning each place to a county (not shipped)
json.dump({name: mapping(wkb.loads(bytes(g)).buffer(0).simplify(0.0003, preserve_topology=True))
           for sub, name, g in rows if sub == "county"}, open(f"{OUT}/ar_counties_detail.geojson", "w"))
json.dump(out, open(f"{OUT}/ar_shapes.json", "w"), separators=(",", ":"))
print("outlines: state", len(out["state"] or []), "rings +", len(out["counties"]), "counties;", round(time.time() - t), "s total")
# border towns: each must fall on the right side of the detailed state outline
from shapely.geometry import shape, Point
st = shape(json.load(open(f"{OUT}/ar_state_detail.geojson")))
for nm, lon, lat, want in [("Texarkana", -94.0377, 33.4418, True), ("Fort Smith", -94.3985, 35.3859, True), ("Van Buren", -94.3483, 35.4368, True),
                           ("Siloam Springs", -94.5405, 36.1881, True), ("Bella Vista", -94.2730, 36.4815, True), ("West Memphis", -90.1845, 35.1465, True),
                           ("Lake Village", -91.2818, 33.3290, True), ("Helena", -90.5918, 34.5293, True), ("El Dorado", -92.6663, 33.2076, True),
                           ("Blytheville", -89.9190, 35.9273, True), ("Mammoth Spring", -91.5404, 36.4956, True), ("Little Rock", -92.2896, 34.7465, True),
                           ("Texarkana, TX", -94.0477, 33.4251, False), ("Arkoma, OK", -94.4383, 35.3543, False), ("Pocola, OK", -94.4766, 35.2312, False),
                           ("West Siloam Springs, OK", -94.5677, 36.1859, False), ("Memphis, TN", -90.0490, 35.1495, False), ("Greenville, MS", -91.0618, 33.4101, False),
                           ("Monroe, LA", -92.1193, 32.5093, False), ("Poplar Bluff, MO", -90.3929, 36.7570, False), ("Vicksburg, MS", -90.8779, 32.3526, False)]:
    ok = st.contains(Point(lon, lat))
    print(f"  {nm}: {'inside' if ok else 'outside'}{'' if ok == want else '  <-- WRONG'}")
print("counties:", len(out["counties"]), sorted(c["name"] for c in out["counties"]))

# the neighbours' land (Missouri, Tennessee, Mississippi, Louisiana, Texas, Oklahoma): listings.py widens Arkansas's outline ~300 m, but only where no
# neighbour's land is, so a Memphis, Greenville or Texarkana, TX listing across the line stays out
nb = con.execute(f"""
  SELECT region, ST_AsWKB(geometry) FROM read_parquet('{areas}', hive_partitioning=1)
  WHERE country = 'US' AND region IN ('US-MO', 'US-TN', 'US-MS', 'US-LA', 'US-TX', 'US-OK') AND subtype = 'region' AND class = 'land'""").fetchall()
from shapely.ops import unary_union
from shapely.geometry import box
near = box(-94.8, 32.8, -89.4, 36.7)
nbg = unary_union([wkb.loads(bytes(g)).buffer(0).intersection(near) for _, g in nb])
json.dump(mapping(nbg.simplify(0.0002, preserve_topology=True)), open(f"{OUT}/ar_neighbors.geojson", "w"))
print("neighbours:", sorted(r for r, _ in nb))
