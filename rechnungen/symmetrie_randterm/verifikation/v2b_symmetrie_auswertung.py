"""
v2b_symmetrie_auswertung.py - Auswertung der eigenen Engine-Laeufe aus v2_symmetrie_laeufe.py.
Fenster W40 = 40-50 s, W50 = 50-60 s.  Vergleich S3-Bilder gegen Basis, Spiegel- und 120-Grad-Bilder.
"""
import numpy as np
import v_engine as ve

MG = ve.MG


def lade(fn):
    r = np.load(fn)
    o = {k: r[k] for k in ('S1', 'SW', 'S2', 'S3', 'Fmin', 'Fmax', 'LO', 'vS', 'DFT')}
    o['L'] = int(r['L']); o['vSend'] = r['vSend']
    return list(r['names']), r['P2'], r['P3'], r['T0'], o


def tab(fn, titel):
    try:
        names, P2, P3, T0, o = lade(fn)
    except FileNotFoundError:
        print(f'\n### {titel}: Datei {fn} fehlt'); return None
    print(f'\n### {titel} ({fn})')
    W = {'W40': ve.window(o, 400, 500), 'W50': ve.window(o, 500, 600)}
    res = {}
    for i, nm in enumerate(names):
        res[nm] = {wk: {k: (w[k][i] if np.ndim(w[k]) else w[k]) for k in ('N1', 'NW', 'gam', 'lam', 'Fmin', 'Fmax', 'Nk', 'Q', 'R')}
                   for wk, w in W.items()}
        res[nm]['phi'] = (P2[i], P3[i], T0[i])
    for nm in names:
        a = res[nm]['W50']; b = res[nm]['W40']
        p2, p3, t0 = res[nm]['phi']
        print(f'{nm:10s} ({p2:7.2f},{p3:7.2f}) t0={t0:+.5f}  W50: lam {a["lam"]:7.3f} %  gam {a["gam"]:+.5f}  '
              f'Fmin {a["Fmin"]:.5f}  Fmax {a["Fmax"]:8.4f}  N1 {a["N1"]:.7f}  NW {a["NW"]:.7f}  |N1..3| '
              f'{np.round(np.abs(a["Nk"][:3]), 4)} | W40: lam {b["lam"]:7.3f} gam {b["gam"]:+.5f}')
    return res


def s3_vergleich(res, basen, shift):
    print('\nS3-Vergleich (max. Abweichung der 5 Bilder vom Basispunkt g0, Fenster W50):')
    for bn in basen:
        g0 = res[f'{bn}:g0']['W50']
        dd = {k: 0.0 for k in ('N1', 'NW', 'gam', 'lam', 'Fmin', 'Fmax', 'absNk', 'phase')}
        for i in range(1, 6):
            gi = res[f'{bn}:g{i}']['W50']
            for k in ('N1', 'NW', 'gam', 'lam', 'Fmin', 'Fmax'):
                dd[k] = max(dd[k], abs(gi[k] - g0[k]))
            dd['absNk'] = max(dd['absNk'], np.max(np.abs(np.abs(gi['Nk']) - np.abs(g0['Nk']))))
            if shift:
                # Phasenregel: arg N_k(B) = arg N_k(A) + k phi_ref  (B mit t0 = -tau_ref, gleiches Fenster in t')
                t0 = res[f'{bn}:g{i}']['phi'][2]
                phiref = -t0 / ve.T * 360.0
                kk = np.arange(1, ve.KMAX + 1)
                dph = np.degrees(np.angle(gi['Nk'] * np.exp(-1j * np.radians(kk * phiref)) / g0['Nk']))
                dd['phase'] = max(dd['phase'], np.max(np.abs(dph[:3])))
        print(f'  {bn}: |dN1| {dd["N1"]:.2e} N  |dN_RK4| {dd["NW"]:.2e} N  |dgam| {dd["gam"]:.2e}  |dlam| {dd["lam"]:.3f} %-Pkt  '
              f'|dFmin| {dd["Fmin"]:.2e}  |dFmax| {dd["Fmax"]:.2e} N  |d|N_k|| {dd["absNk"]:.2e} N'
              + (f'  Phasenregel k=1..3 {dd["phase"]:.2e} Grad' if shift else ''))


for form in ('frame', 'com'):
    res = tab(f'v2_laeufe_std_{form}.npz', f'Standardstart, {form}')
    if res is None:
        continue
    s3_vergleich(res, ['K1', 'L1', 'L4', 'L5', 'L6'], False)
    print('\nMehrstabilitaet bei Standardstart (lam je Bild, W40 / W50):')
    for bn in ('L4', 'L5', 'L6'):
        s = ', '.join(f'{res[f"{bn}:g{i}"]["W40"]["lam"]:.2f}/{res[f"{bn}:g{i}"]["W50"]["lam"]:.2f}' for i in range(6))
        print(f'  {bn}: {s}')
    print('\nSpiegel- und 120-Grad-Bilder (W50):')
    for bn, kind in [('K1', 'mirror'), ('L1', 'mirror'), ('K1', '+120'), ('L1', '+120'), ('L5', '+120')]:
        a = res[f'{bn}:g0']['W50']; b = res[f'{bn}:{kind}']['W50']
        print(f'  {bn} -> {kind:6s}: lam {a["lam"]:.3f} -> {b["lam"]:.3f} %;  gam {a["gam"]:+.4f} -> {b["gam"]:+.4f};  '
              f'Fmin {a["Fmin"]:.4f} -> {b["Fmin"]:.4f} N;  |N_1| {abs(a["Nk"][0]):.4f} -> {abs(b["Nk"][0]):.4f} N;  '
              f'|N_2| {abs(a["Nk"][1]):.4f} -> {abs(b["Nk"][1]):.4f} N')

res = tab('v2_laeufe_shift_frame.npz', 'aequivalenter Start t0 = -tau_ref, frame')
if res is not None:
    s3_vergleich(res, ['K1', 'L1', 'L4'], True)
