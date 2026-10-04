"""s4_symmetrie_auswertung.py - Auswertung der Laeufe aus s2_symmetrie_laeufe.py (Teil A, Aufg. 2-3).

Je Basispunkt und Fenster: groesste Abweichung der sechs S3-Bilder vom Basispunkt (id) in
F_mean (Linksrechteck), Schiefe, lambda, F_min, F_max, |N_k| (k=1..6) und im Residuum der
Phasenregel arg N_k(gA) - arg N_k(A) - k*phi_ref (k=1..6).
Fenster W1 = 5-15 s (Zyklen 50-149, wie Engine), W2 = 50-60 s (Zyklen 500-599).
Modus shift = aequivalent gestartet (t0 = -tau_ref), std = alle mit Standardstart t0 = 0.
Ausserdem (nur std, W2): Spiegelbild (-phi2,-phi3) und 120-Grad-Bild gegen id."""
import os
import numpy as np
import sr_engine as se

WIN = {'W1 5-15 s': (50, 150), 'W2 50-60 s': (500, 600)}
KS = 6


def load(mode):
    d = dict(np.load(f's2_laeufe_{mode}.npz', allow_pickle=False))
    d['L'] = int(d['L']); d['dt'] = float(d['dt'])
    return d


def obs(d, ca, cb):
    w = se.window(d, ca, cb)
    return w


def dev_table(d, names, elems, pref, sel_base, ca, cb):
    w = obs(d, ca, cb)
    rows = {}
    for base in sel_base:
        idx = [i for i in range(len(names)) if names[i] == base and elems[i] in
               ('id', '(23)', '(12)', '(123)', '(13)', '(132)')]
        i0 = [i for i in idx if elems[i] == 'id'][0]
        r = dict(dmean=0.0, dmrk=0.0, dskew=0.0, dlam=0.0, dfmin=0.0, dfmax=0.0, dNk=0.0, dph=0.0, dv=0.0,
                 lam=w['liftoff'][i0], skew=w['skew'][i0], fmin=w['F_min'][i0], fmax=w['F_max'][i0],
                 mean=w['mean_N1'][i0])
        for i in idx:
            r['dmean'] = max(r['dmean'], abs(w['mean_N1'][i] - w['mean_N1'][i0]))
            r['dmrk'] = max(r['dmrk'], abs(w['mean_RK4'][i] - w['mean_RK4'][i0]))
            r['dskew'] = max(r['dskew'], abs(w['skew'][i] - w['skew'][i0]))
            r['dlam'] = max(r['dlam'], abs(w['liftoff'][i] - w['liftoff'][i0]))
            r['dfmin'] = max(r['dfmin'], abs(w['F_min'][i] - w['F_min'][i0]))
            r['dfmax'] = max(r['dfmax'], abs(w['F_max'][i] - w['F_max'][i0]))
            r['dNk'] = max(r['dNk'], np.max(np.abs(np.abs(w['Nk'][i, :KS]) - np.abs(w['Nk'][i0, :KS]))))
            k = np.arange(1, KS + 1)
            ratio = w['Nk'][i, :KS] / w['Nk'][i0, :KS] * np.exp(-1j * k * np.radians(pref[i]))
            big = np.abs(w['Nk'][i0, :KS]) > 1e-3        # nur Harmonische mit |N_k| > 1 mN
            if big.any():
                r['dph'] = max(r['dph'], np.degrees(np.max(np.abs(np.angle(ratio[big])))))
            r['dv'] = max(r['dv'], abs(w['dv'][i]))
        rows[base] = r
    return rows


if __name__ == '__main__':
    import s2_symmetrie_laeufe as s2
    bases = [b[0] for b in s2.BASIS]
    coords = {b[0]: (b[1], b[2]) for b in s2.BASIS}
    for mode in ('shift', 'std'):
        d = load(mode)
        names = [str(x) for x in d['names']]; elems = [str(x) for x in d['elems']]; pref = d['pref']
        for wname, (ca, cb) in WIN.items():
            print(f'\n=== Modus {mode}, Fenster {wname}: max. Abweichung der 6 S3-Bilder vom Basispunkt ===')
            print('Basis  (phi2,  phi3)    lambda/%  Schiefe   |dF_mean|/N  |dF_RK4|/N  |dSchiefe|  |dlambda|/%-Pkt  |dF_min|/N  '
                  '|dF_max|/N  max d|N_k|/N  Phasenregel/Grad  max|dv_S|/(m/s)')
            rows = dev_table(d, names, elems, pref, bases, ca, cb)
            for b in bases:
                r = rows[b]; c = coords[b]
                print(f'{b:4s} ({c[0]:5.1f},{c[1]:5.1f})  {r["lam"]:8.3f}  {r["skew"]:+.4f}  {r["dmean"]:.2e}    '
                      f'{r["dmrk"]:.2e}   {r["dskew"]:.2e}   {r["dlam"]:.2e}        {r["dfmin"]:.2e}   {r["dfmax"]:.2e}   {r["dNk"]:.2e}     '
                      f'{r["dph"]:.2e}         {r["dv"]:.2e}')
    # Spiegelung und 120-Grad-Bild (std, W2) sowie Kontrolle W2 gegen W1-Konvergenz
    d = load('std')
    names = [str(x) for x in d['names']]; elems = [str(x) for x in d['elems']]
    w = se.window(d, 500, 600)
    w1 = se.window(d, 400, 500)
    print('\n=== Spiegelung (-phi2,-phi3) und 120-Grad-Bild (phi2+120, phi3+120) gegen Basis, std, Fenster 50-60 s ===')
    print('Basis  Bild      (phi2,  phi3)    lambda/%   Schiefe   F_min/N   F_max/N   |N_1|/N  |N_2|/N  |N_3|/N  '
          '|N_6|/N   dv_S(50-60s)  |Schiefe(40-50)-Schiefe(50-60)|')
    for b in bases:
        for el in ('id', 'mirror', 'plus120'):
            i = [j for j in range(len(names)) if names[j] == b and elems[j] == el][0]
            nk = np.abs(w['Nk'][i])
            print(f'{b:4s}  {el:8s} ({d["phi2_deg"][i]:5.1f},{d["phi3_deg"][i]:5.1f})  {w["liftoff"][i]:8.3f}  '
                  f'{w["skew"][i]:+.5f}  {w["F_min"][i]:7.4f}  {w["F_max"][i]:7.3f}  {nk[0]:7.4f}  {nk[1]:7.4f}  '
                  f'{nk[2]:7.4f}  {nk[5]:7.4f}   {w["dv"][i]:+.1e}     {abs(w["skew"][i] - w1["skew"][i]):.1e}')

    print('\n=== Einzelbilder der multistabilen Basispunkte (std, 50-60 s): lambda/% und Schiefe je S3-Bild ===')
    for b in ('L4', 'L5', 'L6'):
        idx = [j for j in range(len(names)) if names[j] == b and elems[j] not in ('mirror', 'plus120')]
        print(f'{b}: ' + '; '.join(f'{elems[j]} ({d["phi2_deg"][j]:.1f},{d["phi3_deg"][j]:.1f}) '
                                  f'lam {w["liftoff"][j]:.2f} skew {w["skew"][j]:+.3f} dv {w["dv"][j]:+.1e}' for j in idx))
    ds = load('shift')
    ws = se.window(ds, 500, 600)
    ns = [str(x) for x in ds['names']]
    for b in ('L4', 'L5', 'L6'):
        j = [i for i in range(len(ns)) if ns[i] == b][0]
        print(f'{b} aequivalent gestartet (alle Bilder): lam {ws["liftoff"][j]:.2f}, skew {ws["skew"][j]:+.3f}')
    # Saettigung im Huepfbereich: warum die 120-Grad-Verschiebung in Heatmaps scheinbar gilt
    import pandas as pd
    m = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data/sweep_19x19.csv'))
    band = (m.liftoff >= 74) & (m.liftoff <= 77)
    print(f'\n19x19-Karte: {band.sum()} von 361 Punkten ({band.mean() * 100:.1f} %) im gesaettigten Huepfband '
          f'lambda 74-77 %, Schiefe dort {m.F_skew[band].min():.3f} bis {m.F_skew[band].max():.3f}; lambda > 50 %: {(m.liftoff > 50).sum()}')
