#!/usr/bin/env python3
"""P3/neuheit – formale Literaturprüfung (nur lesend, nur Bestand).

Prüft:
  1. \\cite-Schlüssel in AP v2.4 und Dissertation v2.1 gegen references.bib
  2. Vollständigkeit der bib-Einträge (doi/isbn/pages/volume)
  3. Verifikationstabelle AP Anhang C (Spalte DOI/ISBN) gegen bib
  4. BibTeX-Block des Literaturabgleichs 12.09. gegen references.bib (Übernahme?)
  5. FV v2.7 thebibliography gegen bib (Konsistenz Jahr/Seiten/DOI)
Ausgabe: Text auf stdout.
"""
import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AP = REPO / "docs/arbeitspapier/PCMMS_Arbeitspapier_v2_4.tex"
BIB = REPO / "docs/arbeitspapier/references.bib"
FV = REPO / "docs/formelverzeichnis/PCMMS_Formelverzeichnis_v2_7.tex"
LA = REPO / "docs/literaturabgleich_2026-09-12.md"
# Dissertation v2.1: Quelle außerhalb des Repositorys; Pfad zur .tex-Datei bei Bedarf über PCMMS_DISS_TEX angeben
DISS = Path(os.environ["PCMMS_DISS_TEX"]) if os.environ.get("PCMMS_DISS_TEX") else None


def parse_bib(text):
    entries = {}
    for m in re.finditer(r"@(\w+)\{([^,]+),(.*?)\n\}", text, re.S):
        typ, key, body = m.group(1), m.group(2).strip(), m.group(3)
        fields = {}
        for fm in re.finditer(r"(\w+)\s*=\s*\{(.*?)\}\s*,?\s*\n", body + "\n", re.S):
            fields[fm.group(1).lower()] = " ".join(fm.group(2).split())
        entries[key] = (typ, fields)
    return entries


def cites(text):
    keys = set()
    for m in re.finditer(r"\\cite[a-z]*(?:\[[^\]]*\])?\{([^}]*)\}", text):
        keys.update(k.strip() for k in m.group(1).split(","))
    return keys


def main():
    bib = parse_bib(BIB.read_text(encoding="utf-8"))
    ap = AP.read_text(encoding="utf-8")
    print("== 1. Zitierschlüssel ==")
    print(f"references.bib: {len(bib)} Einträge")
    for name, path in [("AP v2.4", AP), ("Diss v2.1", DISS)]:
        if path is None or not path.exists():
            print(f"{name}: Quelle außerhalb des Repositorys, übersprungen")
            continue
        c = cites(path.read_text(encoding="utf-8"))
        print(f"{name}: {len(c)} Schlüssel; nicht im bib: {sorted(c - set(bib))}; "
              f"im bib, nicht zitiert: {sorted(set(bib) - c)}")

    print("\n== 2. Vollständigkeit je Eintrag ==")
    for key, (typ, f) in bib.items():
        miss = []
        if typ == "article":
            for fld in ("journal", "volume", "pages", "year"):
                if fld not in f:
                    miss.append(fld)
            if "doi" not in f:
                miss.append("doi")
        elif typ == "book":
            if "doi" not in f and "isbn" not in f:
                miss.append("doi/isbn")
        print(f"{key:24s} {typ:10s} fehlt: {', '.join(miss) if miss else '-'}"
              + (f"  [note: {f['note']}]" if "note" in f else ""))

    print("\n== 3. AP Anhang C, Tabelle tab:verifikation (Spalte DOI/ISBN) ==")
    m = re.search(r"\\section\{Verifikation je Eintrag\}(.*?)\\end\{tabular\}", ap, re.S)
    rows = [r.strip() for r in m.group(1).split("\\\\") if "&" in r]
    for r in rows:
        cols = [c.strip() for c in r.split("&")]
        if len(cols) >= 4 and not cols[0].startswith("Eintrag"):
            print(" | ".join(cols[:4]))
    print("Hinweis: shabana2010 im bib:", bib.get("shabana2010"))

    print("\n== 4. BibTeX-Block Literaturabgleich 12.09. ==")
    la = LA.read_text(encoding="utf-8")
    block = "\n".join(re.findall(r"```bibtex\n(.*?)```", la, re.S))
    lab = parse_bib(block)
    for key, (typ, f) in lab.items():
        flags = []
        if "doi" not in f:
            flags.append("ohne DOI")
        if typ == "article" and "journal" not in f:
            flags.append("ohne Journal (Preprint)")
        if typ == "article" and "journal" in f and "pages" not in f:
            flags.append("ohne Seiten/Artikelnr.")
        in_ap = key in ap or key.lower() in ap.lower()
        print(f"{key:28s} in references.bib: {key in bib}; im AP zitiert/erwähnt: {in_ap}; {', '.join(flags) or 'vollständig'}")
    surnames = ["Popov", "Madatov", "Flach", "Denisov", "Feng", "Zigelman", "Mao", "Teidelt", "Papangelo", "Wang"]
    print("Nachnamen im AP v2.4:", {s: len(re.findall(s, ap)) for s in surnames})

    print("\n== 5. FV v2.7 thebibliography ==")
    fv = FV.read_text(encoding="utf-8")
    for bm in re.finditer(r"\\bibitem\{(\w+)\}(.*)", fv):
        print(f"FV {bm.group(1)}: {bm.group(2)[:220]}")
    print("AP-bib perretliaudet2003:", bib["perretliaudet2003"])
    print("AP-bib wakou2008:", bib["wakou2008"])


if __name__ == "__main__":
    main()
