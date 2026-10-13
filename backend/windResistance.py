# Park et al. 2024, J. Mar. Sci. Eng. 12, 1694, Eq. (9)
# R_AA = ½ρA · C'X(ψR) · AT · VR²  −  ½ρA · CX(0) · AT · VS²
# where:
# first term  = wind force from the relative wind; C'X is the coefficient under the sea wind profile (reference height 10 m)
# second term = still-air resistance from the ship's own speed; CX(0) is the head-on coefficient under a uniform profile.
#               Subtracted because calm-water resistance already contains it (Holtrop RA covers still-air drag)
# ψR = relative wind direction, 0 = head wind; VR = relative wind speed; VS = ship speed; AT = frontal projected area
# Sign: resistance positive (the paper plots CX force-positive-forward, so C here = −CX of Fig. 7)

import math

import numpy as np

RHO_AIR = 1.225  # kg/m³ at 15 °C

PSI = np.arange(0, 181, 10)
CX_PROFILE = np.array([1.13, 1.16, 1.12, 1.04, 0.85, 0.65, 0.44, 0.22, 0.02, -0.15,
                       -0.22, -0.31, -0.44, -0.58, -0.74, -0.89, -0.98, -0.98, -0.87])
# CX(0) uniform / C'X(0) profile = 0.679 / 0.930 (Fig. 15, the paper's only uniform-profile tanker value, ballast draught)
CX0_UNIFORM = 0.679 / 0.930 * float(CX_PROFILE[0])


def windResistance(vessel, windSpeedMs, windDirFrom, headingDeg, speedMs):
    """Added resistance due to wind [N]; negative for a tailwind faster than the ship. windDirFrom in deg true, wind at 10 m."""
    rel = math.radians(windDirFrom - headingDeg)
    ahead = speedMs + windSpeedMs * math.cos(rel)  
    beam = windSpeedMs * math.sin(rel)
    psiR = abs(math.degrees(math.atan2(beam, ahead)))  #relative wind direction
    CX = float(np.interp(psiR, PSI, CX_PROFILE))
    return 0.5 * RHO_AIR * vessel.frontalWindageArea * (CX * (ahead**2 + beam**2) - CX0_UNIFORM * speedMs**2)


