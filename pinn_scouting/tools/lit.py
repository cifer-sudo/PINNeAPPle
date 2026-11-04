"""Literature saturation probe on OpenAlex (title+abstract search).

python lit.py <tag> "<search expression>" [n]
Writes lit/<tag>.json with the total count, counts per year and the top-n works by relevance
(DOI, year, venue, citations, abstract reconstructed from OpenAlex's inverted index).
"""
import json
import os
import sys
import urllib.parse
import urllib.error
import urllib.request

BASE = "https://api.openalex.org/works"


def get(params, tries=4):
    import time
    url = BASE + "?" + urllib.parse.urlencode(params)
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "pinn-scouting/0.1"}),
                                        timeout=60) as r:
                return json.load(r), url
        except urllib.error.HTTPError as e:
            if e.code != 429 or k == tries - 1:
                raise
            time.sleep(30 * (k + 1))


def abstract(inv):
    if not inv:
        return ""
    pos = {}
    for w, idx in inv.items():
        for i in idx:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))


def main():
    tag, expr = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    flt = f"title_and_abstract.search:{expr}"
    d, url = get({"filter": flt, "per-page": n, "sort": "relevance_score:desc"})
    g, _ = get({"filter": flt, "group_by": "publication_year"})
    out = {"tag": tag, "expr": expr, "url": url, "count": d["meta"]["count"],
           "by_year": {x["key"]: x["count"] for x in g["group_by"]}, "works": []}
    for w in d["results"]:
        src = ((w.get("primary_location") or {}).get("source") or {})
        out["works"].append({"title": w.get("title"), "year": w.get("publication_year"), "doi": w.get("doi"),
                             "venue": src.get("display_name"), "cited_by": w.get("cited_by_count"),
                             "abstract": abstract(w.get("abstract_inverted_index"))[:1500]})
    os.makedirs("lit", exist_ok=True)
    json.dump(out, open(f"lit/{tag}.json", "w"), indent=1)
    yrs = {k: v for k, v in sorted(out["by_year"].items()) if int(k) >= 2019}
    print(f"[{tag}] count={out['count']} by_year={yrs}")
    for w in out["works"]:
        print(f"  {w['year']} | {w['cited_by']:>4} | {(w['venue'] or '')[:38]:38} | {w['doi']} | {w['title'][:110]}")


if __name__ == "__main__":
    main()
