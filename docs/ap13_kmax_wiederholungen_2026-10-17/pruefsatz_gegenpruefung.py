"""Gegenprüfung des Ablauf-Prüfsatzes vor dem Neuschreiben seiner Sollwerte (Korrekturrunde vom 18.10.2026).

Rechnet die Prüfkampagnen des Ablauf-Prüfsatzes mit dem aktuellen Code und vergleicht sie mit einer älteren
Prüfsatzdatei: Inhaltsgrößen und Prüfsummen von Daten, Ziehungen und Schwellen unmittelbar; Köpfe und Entscheidungen,
nachdem die mit ablauf-2 neu protokollierten Felder (g1_klammer, spaet_erkannt, s1) entfernt und der geänderte
Halttext von S2 im Kontrolllauf auf den alten zurückgesetzt sind. Gleichheit belegt, dass sich nur Protokollfelder und
Text, nicht Daten, Ziehungen oder Entscheidungen ändern.

Aufruf vom Repository-Stamm (alte Datei aus dem Stand vor der Korrektur):
    git show 9a1cd2f:tests/fixtures/ap13_ablauf_pruefsatz.json > /tmp/ablauf_pruefsatz_9a1cd2f.json
    python3 docs/ap13_kmax_wiederholungen_2026-10-17/pruefsatz_gegenpruefung.py /tmp/ablauf_pruefsatz_9a1cd2f \\
        docs/ap13_kmax_wiederholungen_2026-10-17/pruefsatz_gegenpruefung.json
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'code'))
from pcmms_auswertung import ablauf, formate                                         # noqa: E402
from pcmms_auswertung.harness import ablauf_pruefsatz as aps                         # noqa: E402

NEUE_FELDER = ('g1_klammer', 'spaet_erkannt', 's1')
ALTER_TEXT = {'Einzelzell-Liftoff im Kontrolllauf L2; ŷ¹ ungültig (§8.2)':
              'Einzelzell-Liftoff in L2; die Konfiguration bleibt in den Blöcken und ist von Tests ausgeschlossen'}


def zurueck(x):
    if isinstance(x, str):
        for n, a in ALTER_TEXT.items():
            x = x.replace(n, a)
        return x
    if isinstance(x, list):
        return [zurueck(y) for y in x]
    if isinstance(x, dict):
        return {k: zurueck(v) for k, v in x.items()}
    return x


def gegenpruefung(alt_pfad):
    _, alt = formate.lies_objekt(alt_pfad, 'pruefsatz')
    out = dict(alt=dict(ablauf_version=alt['ablauf_version'], verfahren=alt['verfahren'],
                        sha256_gesamt=alt['sha256_gesamt']),
               neu=dict(ablauf_version=ablauf.VERSION), neue_felder=list(NEUE_FELDER), alter_text=ALTER_TEXT, faelle={})
    for sid, st, sd, art in aps.FAELLE:
        key = f'{sid}/{st}/{sd}/{art}'
        f, r = aps.fall(sid, st, sd, art)
        a = r['ablauf']
        t1 = a.tabelle()
        koepfe, felder = copy.deepcopy(t1.koepfe), {}
        for k in koepfe:
            for x in NEUE_FELDER:
                if x in k['versuch']:
                    felder[x] = felder.get(x, 0) + 1
                    k['versuch'].pop(x)
        h = alt['faelle'][key]['hashes']
        out['faelle'][key] = dict(
            inhalt_gleich=formate.sha256_json(f['inhalt']) == formate.sha256_json(alt['faelle'][key]['inhalt']),
            daten_gleich=f['hashes']['daten'] == h['daten'], ziehungen_gleich=f['hashes']['ziehungen'] == h['ziehungen'],
            schwellen_gleich=f['hashes']['schwellen'] == h['schwellen'],
            entscheidungen_gleich=f['hashes']['entscheidungen'] == h['entscheidungen'],
            entscheidungen_gleich_mit_altem_text=formate.sha256_json(zurueck(a.z['entscheidungen'])) == h['entscheidungen'],
            koepfe_gleich=f['hashes']['koepfe'] == h['koepfe'],
            koepfe_gleich_ohne_neue_felder_mit_altem_text=formate.sha256_json(zurueck(koepfe)) == h['koepfe'],
            neue_felder=felder,
            x_strich=[dict(versuch=k['versuch']['id'], klammer=k['versuch'].get('g1_klammer'),
                           gueltig=k['versuch']['gueltig']) for k in t1.koepfe if k['versuch']['rolle'] == 'X_strich'],
            s2_bilanz=t1.meta['ablauf']['s2_bilanz'], inhaltliche_gegenprobe=aps._gegenprobe(sid, st, sd, art, r))
    out['ergebnis'] = all(e['inhalt_gleich'] and e['daten_gleich'] and e['ziehungen_gleich'] and e['schwellen_gleich']
                          and e['entscheidungen_gleich_mit_altem_text']
                          and e['koepfe_gleich_ohne_neue_felder_mit_altem_text'] and not e['inhaltliche_gegenprobe']
                          for e in out['faelle'].values())
    return out


if __name__ == '__main__':
    erg = gegenpruefung(sys.argv[1])
    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        f.write(formate.json_text(erg))
    print(json.dumps({k: {x: v for x, v in e.items() if x not in ('x_strich', 's2_bilanz')}
                      for k, e in erg['faelle'].items()}, ensure_ascii=False, indent=1))
    print('Gegenprüfung bestanden' if erg['ergebnis'] else 'Gegenprüfung NICHT bestanden')
    sys.exit(0 if erg['ergebnis'] else 1)
