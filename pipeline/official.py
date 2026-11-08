"""Official records for Arkansas -> one table (empty for now; playbook/12-sources.md).

The Arkansas Department of Health (ADH) inspects every food establishment in all 75 counties (no city or county runs its own program).
Its Food Establishment Inspection search (foodserviceprod.adh.arkansas.gov/Web/inspection/publicinspectionsearch.aspx) is an ASP.NET
postback form (name, street, city, county, ZIP, date range); it posts observations, never a score, grade or placard. It has no export
or API, and harvesting it waits on Nick's yes (the prompt), so no inspection result is read and every place links to the search.
DFA Alcoholic Beverage Control posts a full permit spreadsheet most months (dfa.arkansas.gov, "Permit Changes"; FullPermit202609.xlsx,
posted 2026-10-12) with no terms of use on the page; Arkansas.gov's acceptable-use page says only not to frame its pages or present
its content as your own. Using it waits on Nick's call (as wv-eats did for West Virginia's CSV), so "Serves alcohol" is unknown.

load() returns an empty table with the columns the pipeline reads (0 official places).
"""
import os, re, json, datetime, glob
import numpy as np, pandas as pd
from common import norm_name, RAW, name_sim, _stems, GENERIC, canon_city, nice

OFF = os.path.join(RAW, "official")
DIRS = {"N": "N", "S": "S", "E": "E", "W": "W", "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W"}
TYPES = set("ST STREET AVE AV AVENUE BLVD BOULEVARD RD ROAD DR DRIVE LN LANE CT COURT PL PLACE PKWY PARKWAY TER TRL TRAIL WAY HWY CIR "
            "CIRCLE PLZ SQ MALL BND PASS XING RUN ROW WALK RDG LOOP FWY FREEWAY EXPY EXPRESSWAY PIKE PK PKE".split())


def road(a):
    """One spelling for numbered roads. Arkansas writes one road as 'Route 100', 'US 7', 'Rt 2', 'AR 100' or 'AR Route 100', so every
    numbered US or state route is 'SH n' (as in ri-eats); 'N INTERSTATE 95' = 'I-95'; 'COUNTY ROAD 5' = 'CR 5'."""
    a = re.sub(r"(\d)\s*&\s*(\d)", r"\1-\2", a.upper())
    a = re.sub(r"\b(US|AR|SR|SH|CR|I|IH|RT|RTE)-(\w)", r"\1 \2", a)
    a = re.sub(r"\b(?:INTERSTATE(?: HIGHWAY| HWY)?|IH|I H)\s*(?=\d)", "I ", a)
    a = re.sub(r"\b(?:US|U S)\s+(?:HIGHWAY|HWY)\b", "US", a)
    a = re.sub(r"\b(?:FARM[- ]TO[- ]MARKET(?: ROAD| RD)?|FARM (?:ROAD|RD)|F M)\b", "FM", a)
    a = re.sub(r"\b(?:RANCH[- ]TO[- ]MARKET(?: ROAD| RD)?|RANCH (?:ROAD|RD)|RR|RM)\b(?=\s*\d)", "RM", a)
    a = re.sub(r"\b(?:STATE (?:HIGHWAY|HWY|ROAD|RD|ROUTE|RTE)|SR|SH|WEST VIRGINIA (?:ROUTE|RTE|HIGHWAY|HWY)|AR (?:ROUTE|RTE|RT|HIGHWAY|HWY)|AR|"
               r"US (?:ROUTE|RTE|RT)|US|ROUTE|RTE|RT|HWY|HIGHWAY)\b\.?(?=\s*\d)", "SH", a)
    a = re.sub(r"\b(?:COUNTY (?:HIGHWAY|HWY|ROAD|RD)|CO RD|CTY (?:HWY|RD)|CR)\b", "CR", a)
    a = re.sub(r"\bHIGHWAY\b", "HWY", a)
    return re.sub(r"\b(US|SH|CR|HWY|FM|RM|I) (\w+)\s*-\s*\w+", r"\1 \2", a)


ORD = {"FIRST": "1ST", "SECOND": "2ND", "THIRD": "3RD", "FOURTH": "4TH", "FIFTH": "5TH", "SIXTH": "6TH", "SEVENTH": "7TH",
       "EIGHTH": "8TH", "NINTH": "9TH", "TENTH": "10TH", "ELEVENTH": "11TH", "TWELFTH": "12TH"}


def street_key(a):
    """'2505 Monroe St' -> ('2505', 'MONROE'); '1000 OSAGE STREET' -> ('1000', 'OSAGE'); 'E Colfax Ave' keeps 'COLFAX'."""
    if not isinstance(a, str):
        return None, None
    # "8901 Jenny Lind #7", "1300 N. Thompson #E": a suite after "#" isn't part of the street (ok-eats' fix: "GORE C" missed "Gore Blvd Ste C")
    a = re.sub(r"(?i)\b(US|HWY|HIGHWAY|ROUTE|RTE|RT|SH|I)\s*#\s*(?=\d)", r"\1 ", a)   # "601 Highway #49" is a route number, not a suite
    a = re.sub(r"(?<=\w)\s*#\s*[A-Za-z0-9-]+\b", " ", road(a))
    a = re.sub(r"[.,#]", " ", a)
    # "20940-A North Frederick Ave": a hyphenated unit letter is part of the number (Maryland's Montgomery County wrote them so)
    m = re.match(r"^\s*(\d+)(?:-?[A-Z])?(?:\s*-\s*\d+[A-Z]?)?\s+(.*)$", a)
    if not m:
        return None, None
    words = [w for w in m.group(2).split() if w]
    if len(words) > 1 and words[0] in DIRS:
        words = words[1:]
    core = []
    for w in words:
        if w in TYPES and core:
            break
        core.append(w)
    # "Hwy 45 North" = "Highway 45 N": a direction word after the street is its letter (Columbus's Mugshots was listed twice)
    core = [ORD.get(w, DIRS.get(w, w)) for w in core]
    return m.group(1), " ".join(core[:3]) or None


def street_compat(a, b):
    """Same street, or one is a whole-word prefix of the other: Boulder's 2025 set sometimes truncates ("1206 CENTAUR" = Centaur Village Dr)."""
    if not isinstance(a, str) or not isinstance(b, str) or not a or not b:
        return False
    return a == b or a.startswith(b + " ") or b.startswith(a + " ")


def street_nums(a):
    """'157-159 W Main St' -> {'157', '159'}; '2505 Monroe St' -> {'2505'}."""
    if not isinstance(a, str):
        return set()
    a = road(a)
    m = re.match(r"^\s*(\d+)[A-Z]?(?:\s*-\s*(\d+)[A-Z]?)?\s", a.upper() + " ")
    if not m:
        return set()
    lo = int(m.group(1)); hi = int(m.group(2)) if m.group(2) else lo
    if hi < lo:   # "1500-02"
        hi = int(str(lo)[: len(str(lo)) - len(m.group(2))] + m.group(2)) if m.group(2) else lo
    return {str(x) for x in range(lo, hi + 1, 2 if (hi - lo) % 2 == 0 else 1)} if 0 <= hi - lo <= 12 else {str(lo)}


def _names(*vals):
    out = []
    for v in vals:
        if not isinstance(v, str):
            continue
        v = re.sub(r"\s*\((?:MOBILE|MOBILE UNIT|COMMISSARY|CATERING|SPECIAL EVENT|SPEC EVENT|TEMP(?:ORARY)? EVENT|CP|INSIDE [^)]*)\)\s*$", "", v, flags=re.I)
        for part in re.split(r"\s*/\s*|\s+\bdba\b\s+|\s+&\s+(?=[A-Z][a-z])", v, flags=re.I):
            k = norm_name(re.sub(r"\b(?:LLC|INC|CORP|CORPORATION|LTD|CO)\b\.?", "", part, flags=re.I))
            if k and k not in out:
                out.append(k)
    return out



ADH_DIR = os.path.join(OFF, "adh")
ABC_DIR = os.path.join(OFF, "abc")
META = json.load(open(os.path.join(ADH_DIR, "meta.json"))) if os.path.exists(os.path.join(ADH_DIR, "meta.json")) else {}
ABC_META = json.load(open(os.path.join(ABC_DIR, "meta.json"))) if os.path.exists(os.path.join(ABC_DIR, "meta.json")) else {}
LIST_DATE = META.get("end")          # the last day of the ADH search window (the day before the pull)
MONT_PAGE = "https://www.dfa.arkansas.gov/office/alcohol-beverage-control/permit-changes/"   # the ABC permit list's page
PERMITS_POSTED = ABC_META.get("posted")   # the permit spreadsheet's posting date
# ADH's Food Establishment Inspection search (checked 2026-11-06: 200, no robots.txt, no CAPTCHA)
INSPECTIONS_URL = "https://foodserviceprod.adh.arkansas.gov/Web/inspection/publicinspectionsearch.aspx"
DISCLAIMER = ("Remember this inspection is only a snapshot in time. It represents only what the inspector saw on the particular date of "
              "inspection.")
# ADH's own wording for each inspection: how many observations its report lists (no score or grade). Index = count, capped at 60.
RESULTS = tuple(["No observations"] + [f"{n} observation" + ("s" if n > 1 else "") for n in range(1, 61)])
ONPREM_T = ("Arkansas ABC on-premises permit",)
RETAIL_T = "Arkansas ABC package permit"
# DFA ABC permit types -> what they let a business serve on the premises (beer, wine, liquor); private clubs serve members, so their
# drinks aren't listed. Package and grocery permits are retail. Suppliers, wholesalers, samplers and the like don't count.
ONPREM_TYPES = {"RESTAURANT MIXED DRINK MAXIMUM": ["liquor"], "RESTAURANT MIXED DRINK MINIMUM": ["liquor"],
                "HOTEL / MOTEL / RESTAURANT MIXED DRINK MAXIMUM": ["liquor"], "HOTEL / MOTEL / RESTAURANT MIXED DRINK MINIMUM": ["liquor"],
                "SMALL RESTAURANT SPIRITUOUS": ["liquor"], "PARIMUTUEL MIXED DRINK": ["liquor"], "RETAIL BEER ON PREMISES": ["beer"],
                "COMBINATION OF RESTAURANT BEER & WINE": ["beer", "wine"], "RESTAURANT WINE": ["wine"], "ON PREMISES WINE": ["wine"],
                "MICROBREWERY RESTAURANT": ["beer"], "PRIVATE CLUB CLASS A - DRY COUNTY": [], "PRIVATE CLUB CLASS A - WET COUNTY": [],
                "PRIVATE CLUB CLASS B - DRY COUNTY": [], "PRIVATE CLUB CLASS B - WET COUNTY": [], "PRIVATE CLUB CLASS A - DRY COUNTY FOR PROFIT": [],
                "PRIVATE CLUB CLASS A - WET COUNTY FOR PROFIT": [], "PRIVATE CLUB - SATELLITE CLASS A": [], "PRIVATE CLUB - SATELLITE CLASS B": [],
                "MICROBREWERY-RESTAURANT PRIVATE CLUB PERMIT-DRY": ["beer"], "BED AND BREAKFAST PRIVATE CLUB": [],
                "HOTEL OR LARGE EVENT FACILITY - PRIVATE CLUB - DRY": []}
RETAIL_TYPES = {"RETAIL LIQUOR", "RETAIL BEER OFF PREMISES", "GROCERY STORE WINE", "CORPORATE RETAIL BEER OFF PREMISES"}


def liq_kind(t):
    """A license type as shown -> on-premises or retail."""
    if not isinstance(t, str):
        return None
    return "onprem" if t in ONPREM_T else "retail" if t == RETAIL_T else None


COLUMNS = ["jur", "lic", "name", "dba", "holder", "keys", "addr", "city", "zip", "num", "street", "lat", "lon", "kind", "active", "ltype",
           "insp", "issued", "biz", "drinks", "county"]


def _zip(z):
    z = re.sub(r"\D", "", str(z or ""))
    return z[:5] if len(z) >= 5 else ""


def _title(a):
    a = re.sub(r"\s+", " ", str(a or "")).strip()
    return re.sub(r"\b([A-Z][A-Z']+)\b", lambda m: m.group(1).capitalize(), a) if a.isupper() else a


def _city(c):
    return canon_city(" ".join(w.capitalize() for w in str(c or "").split())) if isinstance(c, str) and c.strip() else None


def load_abc():
    """One row per DFA ABC permit holder with an on-premises or retail permit (the spreadsheet lists every active permit)."""
    import html as _html
    x = pd.read_excel(os.path.join(ABC_DIR, ABC_META.get("file", "FullPermit202609.xlsx")))
    rows = []
    for _, r in x.iterrows():
        types = {_html.unescape(m.group(1)).strip().replace("\u00e2\u20ac\u201c", "-") for m in
                 re.finditer(r"(.+?)-Active\(\d+-\d+\)", str(r.get("Permit Type") or ""))}
        on = [t for t in types if t in ONPREM_TYPES]
        retail = [t for t in types if t in RETAIL_TYPES]
        if not on and not retail:
            continue
        name = _title(r.get("Alias") if isinstance(r.get("Alias"), str) and r.get("Alias").strip() else r.get("Company"))
        if not name:
            continue
        addr = _title(r.get("Business Physical Address"))
        num, st = street_key(addr)
        drinks = sorted({d for t in on for d in ONPREM_TYPES[t]}) or None
        holder = _title(r.get("Company")) if isinstance(r.get("Company"), str) else None
        rows.append({"jur": "abc", "lic": f"abc-{int(r['Permit Number'])}-{int(r['Permit Suffix'])}", "name": name, "dba": name,
                     "holder": holder, "keys": _names(name, holder), "addr": addr, "city": _city(r.get("City")), "zip": _zip(r.get("Zip")),
                     "num": num, "street": st, "lat": None, "lon": None, "kind": "liquor", "active": True,
                     "ltype": ONPREM_T[0] if on else RETAIL_T, "insp": [], "issued": None, "drinks": drinks,
                     "county": (str(r.get("County")).strip() + " County") if isinstance(r.get("County"), str) else None})
    return rows


def _adh_addr(a):
    """'1510 Rebsamen Park Rd | Little Rock, AR 72202' -> (street, town, zip)."""
    a = re.sub(r"\s+", " ", a or "").strip()
    street, _, rest = a.partition(" | ")
    m = re.match(r"^(.*?),\s*AR\s*(\d{5})?", rest.strip())
    return _title(street), (_city(m.group(1)) if m else None), (m.group(2) if m and m.group(2) else "")


def _md(d):
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", d or "")
    return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}" if m else None


def _obs(s):
    m = re.search(r"(\d+)", s or "")
    return min(int(m.group(1)), 60) if m else 0


def load_adh():
    """One row per ADH establishment inspected in the window: its inspections newest first, as [date, ADH's observation count as
    words, inspection type, our key]. The counties whose search hit ADH's 500-result cap were read again month by month
    (county-<id>-<yyyymm>.json); one establishment's rows from several files merge. ADH's results never add a place; they only
    attach to the place they match."""
    best = {}
    for f in sorted(glob.glob(os.path.join(ADH_DIR, "county-*.json"))):
        c = json.load(open(f))
        for r in c["rows"]:
            street, town, zp = _adh_addr(r.get("addr"))
            ident = r.get("key") or f"{r['name']}|{street}|{town}"
            visits = {_md(r["date"]): (RESULTS[_obs(r.get("obs"))], r.get("type") or None)}
            for d, typ, obs in r.get("past") or []:
                visits.setdefault(_md(d), (RESULTS[_obs(obs)], typ or None))
            if ident in best:
                for d, v in visits.items():
                    best[ident]["visits"].setdefault(d, v)
            else:
                best[ident] = {"r": r, "street": street, "town": town, "zip": zp, "county": c["county"], "visits": visits}
    rows = []
    for ident, b_ in best.items():
        insp = sorted([[d, res, typ, f"{ident}-{d}"] for d, (res, typ) in b_["visits"].items() if d], key=lambda i: i[0], reverse=True)
        name = _title(b_["r"]["name"])
        num, st = street_key(b_["street"])
        rows.append({"jur": "adh", "lic": f"adh-{ident}", "name": name, "dba": name, "holder": None, "keys": _names(name),
                     "addr": b_["street"], "city": b_["town"], "zip": b_["zip"], "num": num, "street": st, "lat": None, "lon": None,
                     "kind": "inspection", "active": True, "ltype": "ADH food establishment", "insp": insp, "issued": None,
                     "drinks": None, "county": b_["county"] + " County"})
    return rows


def load():
    """DFA ABC's on-premises and retail permits and ADH's inspected establishments (see the docstring)."""
    rows = []
    if os.path.exists(os.path.join(ABC_DIR, "meta.json")):
        rows += load_abc()
    if glob.glob(os.path.join(ADH_DIR, "county-*.json")):
        rows += load_adh()
    df = pd.DataFrame(rows) if rows else pd.DataFrame({c: pd.Series(dtype=object) for c in COLUMNS})
    for c_ in COLUMNS:
        if c_ not in df.columns:
            df[c_] = None
    df["lat"] = df["lat"].astype(float); df["lon"] = df["lon"].astype(float); df["active"] = df["active"].astype(bool)
    df["biz"] = _group_biz(df)
    return df


def _group_biz(df):
    """One business, several records (an inspected establishment and its alcohol license): records at the same street number
    and street, in the same zip or the same town, whose names agree share a business number, so a place shows all of them. Zip or
    town, not zip first: the lists disagree on zips (Doe's in Little Rock is 72207 on DFA's permit list and 72201 at ADH)."""
    parent = list(range(len(df)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    groups = {}
    for i, (n, s_, z, c) in enumerate(zip(df.num, df.street, df.zip, df.city)):
        if isinstance(n, str) and n and isinstance(s_, str) and s_:
            if isinstance(z, str) and z:
                groups.setdefault((n, s_, "zip", z), []).append(i)
            if c:
                groups.setdefault((n, s_, "town", str(c).lower()), []).append(i)
    keys = list(df["keys"])
    for idx in groups.values():
        if len(idx) < 2 or len(idx) > 40:
            continue
        for x in range(len(idx)):
            for y in range(x + 1, len(idx)):
                a, b = idx[x], idx[y]
                if any(name_sim(ka, kb) >= 80 or bool((_stems(ka) - GENERIC) & (_stems(kb) - GENERIC))
                       for ka in (keys[a] or []) for kb in (keys[b] or [])):
                    parent[find(a)] = find(b)
    return [find(i) for i in range(len(df))]
