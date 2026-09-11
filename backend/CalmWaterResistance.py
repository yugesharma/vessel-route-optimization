# Holtrop and Mennen method
# RT = RF(1 + k₁) + RAPP + RW + RB + RTR + RA
# where:
# RF = frictional resistance (ITTC-1957 line) (1 + k₁) = form factor accounting for viscous pressure resistance 
# RAPP = appendage resistance RW = wave-making resistance 
# RB = additional pressure resistance due to bulbous bow near waterline 
# RTR = additional pressure resistance due to submerged transom stern 
# RA = model–ship correlation (roughness) allowance 

import math
import numpy as np

def getLWL(draft):
    return draft * 0.95

def wettedSurfaceArea(draft, B, CM, CB, CWP, ABT):
    # S = L(2T + B) · CM^0.5 · (0.453 + 0.4425CB − 0.2862CM − 0.003467(B/T) + 0.3696CWP) + 2.38ABT / CB
    # LWL = length of the ship
    # T = draft
    # B = breadth of the ship
    # CM = midship coefficient
    # CB = block coefficient
    # CWP = waterplane area coefficient
    # ABT = transverse area of bulbous bow (m²); zero if no bulb present
    LWL = getLWL(draft)
    return LWL * (2 * draft + B) * CM**0.5 * (0.453 + 0.4425 * CB - 0.2862 * CM - 0.003467 * (B/draft) + 0.3696 * CWP) + 2.38 * ABT / CB

def KinematicViscosity(T):
    # ν = 1.793 × 10^-6 * (1 + 0.0337 * T + 0.000221 * T^2)
    # T = temperature of water
    return 1.793 * 10**-6 * (1 + 0.0337 * T + 0.000221 * T**2)

def Density(T):
    # ρ = 1000 * (1 - 0.003 * T + 0.00004 * T^2)
    # T = temperature of water
    return 1000 * (1 - 0.003 * T + 0.00004 * T**2)

def ReynoldsNumber(V, LWL, nu):
    return V * LWL / nu

def fritionalResistance(V, S, T, draft):
    # RF = 0.075 / (log₁₀(Rn) − 2)² · ½ρV².S
    # Rn = Reynolds number
    # ρ = density of water
    # V = speed of the ship
    # S = wetted surface area
    nu = KinematicViscosity(T)
    LWL = getLWL(draft)
    Rn = ReynoldsNumber(V, LWL, nu)
    return 0.075 / (math.log10(Rn) - 2)**2 * 0.5 * Density(T) * V**2 * S

def formFactor(T, B, CP, lcb, Cstern, draft):
    # 1 + k₁ = c₁₃ · [0.93 + c₁₂(B/LR)^0.92497 · 
    # (0.95 − CP)^{-0.521448} · (1 − CP + 0.0225 · lcb)^{0.6906}]
    # where:
    # c₁₂ = (T/L)^0.2228446 if T/L ≥ 0.05; c₁₂ = 48.20(T/L − 0.02)^2.078 + 0.479948
    # if T/L < 0.05
    # c₁₃ = 1 + 0.003
    # Cstern (stern shape coefficient)
    # CP = prismatic coefficient
    # lcb = longitudinal centre of buoyancy as % of L from midships, positive forward
    # LR = length of run = L(1 − CP + (0.06 · CP · lcb) / (4CP − 1))
    L = getLWL(draft)
    c12 = (T/L)**0.2228446 if T/L >= 0.05 else 48.20 * (T/L - 0.02)**2.078 + 0.479948
    c13 = 1 #Cstern=0 for most ships, -10 for V-shaped sterns
    LR = getLWL(draft) * (1 - CP + (0.06 * CP * lcb) / (4 * CP - 1))

    return c13 * (0.93 + c12 * (B/LR)**0.92497 * (0.95 - CP)**(-0.521448) * (1 - CP + 0.0225 * lcb)**0.6906)

def appendageResistance(V, LWL, T):
    # RAPP = ½ρV² · SAPP · (1 + k₂) · CF
    # SAPP = appendage wetted surface area (m²)
    SAPP=70
    weightedAverage=(1.5*50+1.4*20)/SAPP
    nu = KinematicViscosity(T)
    Rn = ReynoldsNumber(V, LWL, nu)
    CF=0.075/(math.log10(Rn)-2)**2
    return 0.5 * Density(T) * V**2 * SAPP * weightedAverage * CF

