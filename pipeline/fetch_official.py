"""Arkansas's official records -> data/raw/official/ (git-ignored, never public). Nick approved both sources on 2026-11-06 ("Yes, all
four", through the parent session).

1. ADH inspections: the Arkansas Department of Health's Food Establishment Inspection search
   (foodserviceprod.adh.arkansas.gov/Web/inspection/publicinspectionsearch.aspx), an ASP.NET postback form. For each county, one
   search over the last 12 months, then its result pages (15 establishments each): name, address, phone, the most recent
   inspection's date and type and ADH's own count of observations ("Observation(s) 6", or none), and the past inspections listed
   with it. ADH gives no score or grade; nothing here makes one. No robots.txt (404), no CAPTCHA.
2. DFA ABC permits: the monthly full permit spreadsheet from dfa.arkansas.gov's "Permit Changes" page (robots.txt allows it).

One request at a time, PAUSE seconds apart, a generic client name and no email in the User-Agent; GETs and the search form's own
postbacks only. Each county is saved as it finishes (data/raw/official/adh/county-<id>.json), so a stopped run resumes.
Usage: ../.venv/bin/python fetch_official.py --go [--abc-only | --adh-only]   (without --go it only prints the plan)
"""
import datetime, html, json, os, re, sys, time
import requests

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "official")
ADH = os.path.join(OUT, "adh")
ABC = os.path.join(OUT, "abc")
URL = "https://foodserviceprod.adh.arkansas.gov/Web/inspection/publicinspectionsearch.aspx"
ABC_FILE = "FullPermit202609.xlsx"   # posted 2026-10-12 (the September 2026 list)
ABC_URL = "https://www.dfa.arkansas.gov/wp-content/uploads/" + ABC_FILE
UA = "Mozilla/5.0 (compatible; EatsRankedDataCheck/1.0)"
PAUSE = 3.0
TODAY = datetime.date.today()
END = TODAY - datetime.timedelta(days=1)
START = END - datetime.timedelta(days=365)

S = requests.Session()
S.headers["User-Agent"] = UA


def hidden(s):
    return {m.group(1): html.unescape(m.group(2)) for m in re.finditer(r'<input type="hidden" name="([^"]+)" id="[^"]*" value="([^"]*)"', s)}


def text(s):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or ""))).strip()


def request(method, data=None):
    for attempt in range(4):
        try:
            r = S.get(URL, timeout=120) if method == "GET" else S.post(URL, data=data, timeout=180)
            if r.status_code == 200:
                if re.search(r"(?i)captcha|access denied|unusual traffic", r.text[:5000]):
                    sys.exit("ADH answered with a challenge: stopping (nothing more is requested)")
                return r.text
            print("  http", r.status_code, flush=True)
        except requests.RequestException as e:
            print("  error", e, flush=True)
        time.sleep(15 * (attempt + 1))
    sys.exit("ADH didn't answer after 4 tries: stopping")


def rows(page):
    """The main grid's establishments on one result page."""
    out = []
    for m in re.finditer(r'<tr class="Grid(?:Alt)?Item" NonFormattedNameAddress="[^"]*">\s*<td style="width:20%;">(.*?)</td><td align="center" style="width:10%;">([^<]*)</td>'
                         r'<td align="center" style="width:10%;">([^<]*)</td><td align="center" style="width:10%;">\s*<a [^>]*id="MainContent_gvInspections_lnkViolations_\d+"[^>]*>([^<]*)</a>'
                         r'(.*?)(?=<tr class="Grid(?:Alt)?Item" NonFormattedNameAddress="[^"]*">\s*<td style="width:20%;">|<tr class="GridPager"|\Z)', page, re.S):
        cell, date, typ, obs, rest = m.groups()
        parts = re.split(r"<BR>|<div[^>]*>", cell, flags=re.I)
        name = text(parts[0])
        # the street and the "City, AR zip" are separated by a run of spaces: keep it as " | " so the town can be read back
        divs = [text(re.sub(r"\s{3,}", " | ", x.strip())) for x in re.findall(r"<div[^>]*>(.*?)</div>", cell, re.S)]
        key = re.search(r'lnkPastInspections_\d+" Key="(\d+)"', rest)
        past = []
        for pm in re.finditer(r'<td align="center">(\d\d/\d\d/\d{4})</td><td align="center" style="width:10%;">([^<]*)</td><td align="center">\s*<a [^>]*>([^<]*)</a>', rest):
            past.append([pm.group(1), text(pm.group(2)), text(pm.group(3))])
        out.append({"name": name, "addr": divs[0] if divs else "", "phone": divs[1] if len(divs) > 1 else "", "date": text(date),
                    "type": text(typ), "obs": text(obs), "key": key.group(1) if key else None, "past": past})
    return out


def counties(page):
    m = re.search(r'<select[^>]*name="ctl00\$MainContent\$wucStateCountiesFS\$ddlCounty"[^>]*>(.*?)</select>', page, re.S)
    return [(v, n) for v, n in re.findall(r'<option[^>]*value="(\d+)"[^>]*>([^<]*)<', m.group(1)) if n.strip() and n != "UNKNOWN"]


def adh():
    os.makedirs(ADH, exist_ok=True)
    first = request("GET")
    cl = counties(first)
    state = re.search(r'name="ctl00\$MainContent\$wucStateCountiesFS\$ddlState".*?<option selected="selected" value="(\d*)"', first, re.S)
    print(f"ADH: {len(cl)} counties, {START:%m/%d/%Y}..{END:%m/%d/%Y}", flush=True)
    for cid, cname in cl:
        path = os.path.join(ADH, f"county-{cid}.json")
        if os.path.exists(path):
            continue
        time.sleep(PAUSE)
        page = request("GET")
        f = hidden(page)
        f.update({"ctl00$MainContent$wucStateCountiesFS$ddlState": state.group(1) if state else "67",
                  "ctl00$MainContent$wucStateCountiesFS$ddlCounty": cid,
                  "ctl00$MainContent$dteInspectionBeginDate$txtDate": f"{START:%m/%d/%Y}",
                  "ctl00$MainContent$dteInspectionEndDate$txtDate": f"{END:%m/%d/%Y}",
                  "ctl00$MainContent$btnSearch": "Search", "ctl00$MainContent$txtEstablistmentName": "",
                  "ctl00$MainContent$txtStreetAddress": "", "ctl00$MainContent$txtCity": "", "ctl00$MainContent$txtZip": ""})
        time.sleep(PAUSE)
        page = request("POST", f)
        got, n, seen_first = rows(page), 1, None
        while True:
            pages = [int(x) for x in re.findall(r"Page\$(\d+)", page)]
            if n + 1 not in pages and not re.search(r"Page\$Next|Page\$Last", page):
                if n + 1 not in pages:
                    break
            f = hidden(page)
            for k in ("ctl00$MainContent$btnSearch",):
                f.pop(k, None)
            f.update({"__EVENTTARGET": "ctl00$MainContent$gvInspections", "__EVENTARGUMENT": f"Page${n + 1}",
                      "ctl00$MainContent$wucStateCountiesFS$ddlState": state.group(1) if state else "67",
                      "ctl00$MainContent$wucStateCountiesFS$ddlCounty": cid,
                      "ctl00$MainContent$dteInspectionBeginDate$txtDate": f"{START:%m/%d/%Y}",
                      "ctl00$MainContent$dteInspectionEndDate$txtDate": f"{END:%m/%d/%Y}"})
            time.sleep(PAUSE)
            page = request("POST", f)
            batch = rows(page)
            if not batch or (batch and batch[0] == seen_first):
                break
            seen_first = batch[0]
            got += batch
            n += 1
        json.dump({"county": cname, "id": cid, "start": str(START), "end": str(END), "pages": n, "rows": got}, open(path, "w"))
        print(f"  {cname}: {len(got)} establishments, {n} pages", flush=True)
    json.dump({"fetched": str(TODAY), "start": str(START), "end": str(END), "source": URL}, open(os.path.join(ADH, "meta.json"), "w"), indent=1)


def adh_months(cids):
    """The counties whose 12-month search hit ADH's 500-result cap, one calendar month at a time (county-<id>-<yyyymm>.json)."""
    first = request("GET")
    names = dict(counties(first))
    state = re.search(r'name="ctl00\$MainContent\$wucStateCountiesFS\$ddlState".*?<option selected="selected" value="(\d*)"', first, re.S)
    st = state.group(1) if state else "67"
    months = []
    d = START.replace(day=1)
    while d <= END:
        nxt = (d.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
        months.append((max(d, START), min(nxt - datetime.timedelta(days=1), END)))
        d = nxt
    for cid in cids:
        for a, b in months:
            path = os.path.join(ADH, f"county-{cid}-{a:%Y%m}.json")
            if os.path.exists(path):
                continue
            time.sleep(PAUSE)
            page = request("GET")
            f = hidden(page)
            base = {"ctl00$MainContent$wucStateCountiesFS$ddlState": st, "ctl00$MainContent$wucStateCountiesFS$ddlCounty": cid,
                    "ctl00$MainContent$dteInspectionBeginDate$txtDate": f"{a:%m/%d/%Y}", "ctl00$MainContent$dteInspectionEndDate$txtDate": f"{b:%m/%d/%Y}"}
            f.update(base); f.update({"ctl00$MainContent$btnSearch": "Search", "ctl00$MainContent$txtEstablistmentName": "",
                                      "ctl00$MainContent$txtStreetAddress": "", "ctl00$MainContent$txtCity": "", "ctl00$MainContent$txtZip": ""})
            time.sleep(PAUSE)
            page = request("POST", f)
            got, n, seen_first = rows(page), 1, None
            while n + 1 in [int(x) for x in re.findall(r"Page\$(\d+)", page)]:
                f = hidden(page); f.update(base); f.update({"__EVENTTARGET": "ctl00$MainContent$gvInspections", "__EVENTARGUMENT": f"Page${n + 1}"})
                time.sleep(PAUSE)
                page = request("POST", f)
                batch = rows(page)
                if not batch or batch[0] == seen_first:
                    break
                seen_first = batch[0]; got += batch; n += 1
            json.dump({"county": names.get(cid, cid), "id": cid, "start": str(a), "end": str(b), "pages": n, "rows": got}, open(path, "w"))
            print(f"  {names.get(cid, cid)} {a:%Y-%m}: {len(got)} establishments, {n} pages{' (CAP?)' if len(got) >= 500 else ''}", flush=True)


def abc():
    os.makedirs(ABC, exist_ok=True)
    path = os.path.join(ABC, ABC_FILE)
    if not os.path.exists(path):
        r = S.get(ABC_URL, timeout=120)
        r.raise_for_status()
        open(path, "wb").write(r.content)
    json.dump({"file": ABC_FILE, "url": ABC_URL, "posted": "2026-10-12", "fetched": str(TODAY)}, open(os.path.join(ABC, "meta.json"), "w"), indent=1)
    print("ABC:", ABC_FILE)


if __name__ == "__main__":
    print(f"plan: DFA ABC {ABC_FILE} (1 request); ADH, 75 counties x their result pages, {PAUSE:.0f} s apart, {START}..{END}")
    if "--go" not in sys.argv:
        sys.exit(0)
    if "--adh-only" not in sys.argv:
        abc()
    if "--abc-only" not in sys.argv and "--months" not in sys.argv:
        adh()
    if "--months" in sys.argv:
        adh_months(sys.argv[sys.argv.index("--months") + 1].split(","))
