"""P2/engine – Start auf dem periodischen Orbit: Newton-Iteration auf die diskrete Periodenabbildung
(RK4-Engine, p Zyklen, Zyklusbeginn t0) mit Differenzen-Jacobi-Matrix. Liefert Fixpunkt (z*, ż*),
Floquet-Multiplikatoren (Eigenwerte der Jacobi-Matrix) und Residuen.

Für Dauerkontakt ist die Abbildung affin (lineares System ohne Schalten) -> Newton konvergiert in einem
Schritt; Vergleich mit linear_solver.orbit_state (kontinuierliche, exakte lineare Lösung).
"""
import numpy as np
import eng


def pmap(phi2, phi3, X, t0=0.0, dt=eng.DT, p=1, i0=0):
    """Periodenabbildung für mehrere Zustände X (n, 2) an derselben Phasenkonfiguration."""
    n = X.shape[0]
    r = eng.integrate(np.full(n, phi2), np.full(n, phi3), X[:, 0], X[:, 1], t0=t0, dt=dt, n_cyc=p, i0=i0)
    return np.stack([r['PZ'][p], r['PV'][p]], 1), r


def newton_orbit(phi2, phi3, x0, t0=0.0, dt=eng.DT, p=1, iters=8, h=(1e-9, 1e-7), tol=1e-13):
    x = np.asarray(x0, float).copy()
    hist = []
    J = None
    for it in range(iters):
        X = np.array([x, x + [h[0], 0.0], x + [0.0, h[1]], x - [h[0], 0.0], x - [0.0, h[1]]])
        Y, _ = pmap(phi2, phi3, X, t0, dt, p)
        Fx = Y[0] - x
        J = np.column_stack([(Y[1] - Y[3]) / (2 * h[0]), (Y[2] - Y[4]) / (2 * h[1])])
        res = float(np.max(np.abs(Fx / [1e-3, 1e-1])))      # skaliert: z ~ mm, ż ~ 0,1 m/s
        hist.append(dict(it=it, z=x[0], zd=x[1], res_z=Fx[0], res_v=Fx[1]))
        if np.max(np.abs(Fx)) < tol:
            break
        dx = np.linalg.solve(J - np.eye(2), -Fx)
        x = x + dx
    mult = np.linalg.eigvals(J)
    return x, mult, hist


if __name__ == '__main__':
    import linear_solver as ls
    for (a, b) in [(120.0, 240.0), (113.684, 227.368), (100.0, 240.0), (35.0, 116.0)]:
        lin = np.array(ls.orbit_state(a, b))
        for dt in (eng.DT, eng.DT / 2):
            x, mult, hist = newton_orbit(a, b, lin, dt=dt, iters=4)
            print(f'({a},{b}) dt={dt * 1e6:.0f} µs: Fixpunkt z*={x[0]:.12e} ż*={x[1]:.12e}; linear z={lin[0]:.12e} '
                  f'ż={lin[1]:.12e}; Diff {x[0] - lin[0]:.2e} m, {x[1] - lin[1]:.2e} m/s; |µ| = '
                  + ', '.join(f'{abs(m):.4f}' for m in mult) + f'; Residuen ' +
                  ' '.join(f'{max(abs(hh["res_z"]), abs(hh["res_v"])):.1e}' for hh in hist))
