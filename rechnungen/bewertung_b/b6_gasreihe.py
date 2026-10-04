"""P3 bewertung_b, Kandidat 75 (B12): Gasaustausch He/Luft/Ar/CO2.
Prueft das Dichteverhaeltnis (Quelle: 11, nachgerechnet 11,07) und zeigt [E], dass ein Gaswechsel
neben rho auch die kinematische Viskositaet nu, die Stokes-Schicht delta = sqrt(2 nu/omega) und
den viskosen Kraftmassstab sqrt(rho*mu) veraendert. Stoffwerte 20 Grad C, 1 atm sind ANNAHMEN
(Tabellenwerte aus Allgemeinwissen, nicht im Bestand geprueft).
"""
import numpy as np

gas = {  # rho [kg/m^3], mu [Pa s]
    "He":   (0.1664, 1.96e-5),
    "Luft": (1.204, 1.81e-5),
    "Ar":   (1.661, 2.23e-5),
    "CO2":  (1.842, 1.47e-5),
}
omega = 2 * np.pi * 10.0
print("Gas    rho     nu [m^2/s]   delta(10 Hz) [mm]   sqrt(rho*mu)")
for k, (rho, mu) in gas.items():
    nu = mu / rho
    print(f"{k:5s} {rho:6.3f}   {nu:.3e}      {1e3*np.sqrt(2*nu/omega):.2f}              {np.sqrt(rho*mu):.3e}")
r = gas["CO2"][0] / gas["He"][0]
nur = (gas["He"][1] / gas["He"][0]) / (gas["CO2"][1] / gas["CO2"][0])
sr = np.sqrt(gas["CO2"][0] * gas["CO2"][1]) / np.sqrt(gas["He"][0] * gas["He"][1])
print(f"CO2/He: rho-Verhaeltnis {r:.2f}; nu(He)/nu(CO2) {nur:.1f}; sqrt(rho mu)-Verhaeltnis {sr:.2f}")
print("Druckreihe (gleiches Gas): rho ~ p, mu ~ konst. -> rho- und mu-Abhaengigkeit sind nur mit Gas- UND Druckreihe trennbar.")
