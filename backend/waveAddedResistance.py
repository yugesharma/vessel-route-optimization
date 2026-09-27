# SNNM 
# Rwave(w, alpha) = R_AWM (motion) + R_AWR (reflection)
# R_AW            = 2 * integral(Rwave/zetaA^2 * S(w) dw)
# Valid: 75 <= Lpp <= 400 m, 5 <= L/B <= 8, 2 <= B/T <= 8, 0.52 <= CB <= 0.88, 0.09 <= Fr <= 0.30.

import math

import numpy as np

g = 9.81
RHO = 1025.0
OMEGA = np.linspace(0.1, 3.0, 300)  # rad/s


def jonswap(omega, Hs, Tp, gamma=3.3):
    # DNV-RP-C205 JONSWAP; gamma=3.3 is the standard North Sea value
    wp = 2 * np.pi / Tp
    sigma = np.where(omega <= wp, 0.07, 0.09)
    peak = gamma ** np.exp(-((omega - wp) ** 2) / (2 * sigma**2 * wp**2))
    return (1 - 0.287 * np.log(gamma)) * 5 / 16 * Hs**2 * wp**4 * omega**-5 * np.exp(-1.25 * (wp / omega) ** 4) * peak


def snnmTransfer(omega, alpha, vessel, V):
    """Rwave / zetaA^2 in regular waves [N/m^2]. alpha in [0, pi], 0 = head waves."""
    L, B, CB, kyy = vessel.L, vessel.B, vessel.CB, vessel.kyy
    E1, E2 = vessel.getEntranceRunAngles()
    Tdeep = max(vessel.TF, vessel.TA)
    trim = math.atan(abs(vessel.TA - vessel.TF) / L)
    lnBT = math.log(B / Tdeep)
    Fr = V / math.sqrt(g * L)
    Vg = g / (2 * omega)
    Frrel = (V - Vg) / math.sqrt(g * L)
    c = math.cos(alpha)

    # Motion-induced part (G-14..G-22)
    wbar = (2.142 * kyy ** (1 / 3) * np.sqrt(L / (2 * np.pi * g)) * (CB / 0.65) ** 0.17
            * (1 - 0.111 / CB * (lnBT - math.log(2.75)))
            * ((-1.377 * Fr**2 + 1.157 * Fr) * abs(c) + 0.618 * (13 + math.cos(2 * alpha)) / 14) * omega)
    a2Head = 0.0072 + 0.1676 * Fr if Fr < 0.12 else Fr**1.5 * math.exp(-3.5 * Fr)
    if alpha <= np.pi / 2:
        a1 = (0.87 / CB) ** ((1 + Fr) * c) / lnBT * (1 + 2 * c) / 3
        a2 = a2Head
    else:  # stern oblique: linear between beam (pi/2) and following (pi)
        FrrelPos = np.maximum(Frrel, 0)
        a1Pi = np.where((V > Vg) & (Frrel >= 0.12), (0.87 / CB) ** (1 + FrrelPos), 0.87 / CB) / lnBT
        a2Pi = np.where(V <= Vg, 0.0072 * (2 * V / Vg - 1),
                        np.where(Frrel < 0.12, 0.0072 + 0.1676 * Frrel, FrrelPos**1.5 * np.exp(-3.5 * FrrelPos)))
        t = (alpha - np.pi / 2) / (np.pi / 2)
        a1 = (1 - t) / (3 * lnBT) + t * a1Pi
        a2 = (1 - t) * a2Head + t * a2Pi
    a3 = 1 + 28.7 * trim
    b1 = np.where(wbar < 1, 11.0, -8.5)
    d1 = np.where(wbar < 1, 566 * (L * CB / B) ** -2.66, -566 * (L / B) ** -2.66 * (4 - 125 * trim))
    R_AWM = (3859.2 * RHO * g * B**2 / L * CB**1.34 * kyy**2
             * a1 * a2 * a3 * wbar**b1 * np.exp(b1 / d1 * (1 - wbar**d1)))

    # Reflection part (G-23..G-31)
    lam = 2 * np.pi * g / omega**2
    k = 2 * omega * V / g

    def alphaT(Ts):
        return np.where(lam / L <= 2.5, 1 - np.exp(-4 * np.pi * (Ts / lam - Ts / (2.5 * L))), 0)

    def bracket(E, a):
        return np.sin(E + a) ** 2 + k * (c - math.cos(E) * math.cos(E + a))

    base = 2.25 / 4 * RHO * g * B
    bow = (0.87 / CB) ** ((1 + 4 * math.sqrt(Fr)) * (c if alpha <= E1 else 0))
    Tstern = Tdeep * (4 + math.sqrt(abs(c))) / 5 if CB <= 0.75 else Tdeep * (2 + math.sqrt(abs(c))) / 3
    R_AWR = 0
    if alpha <= np.pi - E1:
        R_AWR += base * alphaT(Tdeep) * bracket(E1, alpha) * bow
    if alpha <= E1:
        R_AWR += base * alphaT(Tdeep) * bracket(E1, -alpha) * bow
    if alpha >= E2:
        R_AWR -= base * alphaT(Tstern) * bracket(E2, -alpha)
    if alpha >= np.pi - E2:
        R_AWR -= base * alphaT(Tstern) * bracket(E2, alpha)

    return R_AWM + R_AWR


def addedWaveResistance(vessel, Hs, Tp, relWaveHeading, speedMs):
    """Mean added resistance in irregular waves [N]. relWaveHeading = waveDirFrom - heading, 0 = head seas."""
    if Hs <= 0 or Tp <= 0:
        return 0.0
    alpha = math.radians(abs((relWaveHeading + 180) % 360 - 180))  # symmetric port/starboard
    # ponytail: long-crested at the peak direction; add directional spreading (G-32) if the weather data has it
    R = snnmTransfer(OMEGA, alpha, vessel, speedMs)
    # may be slightly negative in stern-quarter/following seas (waves push the ship); not clamped, like wind
    return float(2 * np.trapezoid(R * jonswap(OMEGA, Hs, Tp), OMEGA))


if __name__ == "__main__":
    from classes.vessel import Vessel

    # KVLCC2, 15 kn
    ship = Vessel(L=320.0, B=58.0, draft=20.8, TF=20.8, CM=0.998, CB=0.8098, CWP=0.9,
                  ABT=0, hB=0, AT=0, lcb=3.48)
    V = 15 * 0.5144

    E1, E2 = ship.getEntranceRunAngles()
    print(f"LE={ship.LE:.0f} m LR={ship.LR:.0f} m  E1={math.degrees(E1):.1f} deg E2={math.degrees(E2):.1f} deg")
    assert 30 < math.degrees(E1) < 45 and 15 < math.degrees(E2) < 25

    # spectrum integrates to Hs^2/16
    w = np.linspace(0.05, 6, 5000)
    assert abs(np.trapezoid(jonswap(w, 3.0, 10.0), w) - 9 / 16) < 0.02

    print("heading  R_AW (kN)   Hs=3 Tp=9  (STAWAVE-2 head sea was 322 kN)")
    R = {h: addedWaveResistance(ship, 3.0, 9.0, h, V) for h in range(0, 181, 15)}
    for h, r in R.items():
        print(f"{h:5d}  {r / 1e3:8.0f}")
        assert math.isfinite(r)
    assert 20e3 < R[0] < 1e6
    assert R[0] > R[180]
    assert addedWaveResistance(ship, 3.0, 9.0, 60, V) == addedWaveResistance(ship, 3.0, 9.0, -60, V) \
        == addedWaveResistance(ship, 3.0, 9.0, 300, V)
    assert abs(addedWaveResistance(ship, 6.0, 9.0, 0, V) / R[0] - 4) < 1e-9
    print("ok")
