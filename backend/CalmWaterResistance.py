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

def getLWL(LPP):
    # An alternative for realistic data
    return LPP * 0.95

def CBForLWL(LWL, LPP, CB):
    return LPP*CB/LWL

def CPForLWL(LWL, LPP, CP):
    return LPP*CP/LWL

def LR(L, CP, lcb):
    # LR = length of run = L(1 − CP + (0.06 · CP · lcb) / (4CP − 1))
    return L * (1 - CP + (0.06 * CP * lcb) / (4 * CP - 1))

def Fn(V, L):
    return V/(math.sqrt(9.81*L))

def wettedSurfaceArea(draft, B, CM, CB, CWP, ABT, L):
    # S = L(2T + B) · CM^0.5 · (0.453 + 0.4425CB − 0.2862CM − 0.003467(B/T) + 0.3696CWP) + 2.38ABT / CB
    # LWL = length of the ship
    # T = draft
    # B = breadth of the ship
    # CM = midship coefficient
    # CB = block coefficient
    # CWP = waterplane area coefficient
    # ABT = transverse area of bulbous bow (m²); zero if no bulb present
    return L * (2 * draft + B) * CM**0.5 * (0.453 + 0.4425 * CB - 0.2862 * CM - 0.003467 * (B/draft) + 0.3696 * CWP) + 2.38 * ABT / CB

def KinematicViscosity(T):
    # ν = 1.793 × 10^-6 * (1 + 0.0337 * T + 0.000221 * T^2)
    # T = temperature of water
    return 1.793 * 10**-6 * (1 + 0.0337 * T + 0.000221 * T**2)

def Density(T):
    # ρ = 1000 * (1 - 0.003 * T + 0.00004 * T^2)
    # T = temperature of water
    return 1000 * (1 - 0.003 * T + 0.00004 * T**2)

def ReynoldsNumber(V, L, nu):
    return V * L / nu

def frictionalResistance(V, S, rho, Rn):
    # RF = 0.075 / (log₁₀(Rn) − 2)² · ½ρV².S
    # Rn = Reynolds number
    # ρ = density of water
    # V = speed of the ship
    # S = wetted surface area
    CF = 0.075 / (math.log10(Rn) - 2)**2
    return CF * 0.5 * rho * V**2 * S

def formFactor(draft, B, CP, lcb, Cstern, L, LR):
    # 1 + k₁ = c₁₃ · [0.93 + c₁₂(B/LR)^0.92497 ·
    # (0.95 − CP)^{-0.521448} · (1 − CP + 0.0225 · lcb)^{0.6906}]
    # where:
    # c₁₂ = (T/L)^0.2228446 if T/L ≥ 0.05; c₁₂ = 48.20(T/L − 0.02)^2.078 + 0.479948
    # if T/L < 0.05
    # c₁₃ = 1 + 0.003 · Cstern
    # Cstern (stern shape coefficient): 0 for most ships, -10 for V-shaped sterns, 10 for U-shaped sterns
    # CP = prismatic coefficient
    # lcb = longitudinal centre of buoyancy as % of L from midships, positive forward
    # LR = length of run
    c12 = (draft/L)**0.2228446 if draft/L >= 0.05 else 48.20 * (draft/L - 0.02)**2.078 + 0.479948
    c13 = 1 + 0.003 * Cstern

    return c13 * (0.93 + c12 * (B/LR)**0.92497 * (0.95 - CP)**(-0.521448) * (1 - CP + 0.0225 * lcb)**0.6906)

def appendageResistance(V, rho, Rn):
    # RAPP = ½ρV² · SAPP · (1 + k₂) · CF
    # SAPP = appendage wetted surface area (m²)
    SAPP=70
    weightedAverage=(1.5*50+1.4*20)/SAPP
    CF=0.075/(math.log10(Rn)-2)**2
    return 0.5 * rho * V**2 * SAPP * weightedAverage * CF

def iE(L, B, CWP, CP, lcb, LR, displacement):
    # iE = half-angle of entrance of waterline at bow (degrees)
    # iE = 1 + 89 · exp[−(L/B)^0.80856 · (1 − CWP)^0.30484 · (1 − CP − 0.0225lcb)^0.6367 · (LR/B)^0.34574 · (100∇/L³)^0.16302]
    # displacement = volumetric displacement ∇ (m³)
    return 1 + 89 * math.exp(-(L/B)**0.80856 * (1 - CWP)**0.30484 * (1 - CP - 0.0225 * lcb)**0.6367 * (LR/B)**0.34574 * (100 * displacement/L**3)**0.16302)

def c7(B,L):
    if B/L<=0.11:
        return 0.229577*(B/L)**(1/3)
    elif B/L>0.11 and B/L<=0.25:
        return B/L
    else:
        return 0.5-0.0625*L/B

def c1(draft,B,c7,iE):
    # c₁ = 2223105 · c₇^3.78613 · (T/B)^1.07961 · (90 − iE)^{-1.37565}
    return 2223105 * c7**3.78613 * (draft/B)**1.07961 * (90 - iE)**(-1.37565)

def c3(ABT,B,draft,TF,hB):
    #  c₃ = 0.56 · ABT^1.5 / [B · T · (0.31√ABT + TF − hB)]
    return 0.56 * ABT**1.5 / (B * draft * (0.31 * math.sqrt(ABT) + TF - hB))

def c2(c3):
    # c₂ = exp(−1.89 · √c₃)
    return math.exp(-1.89 * math.sqrt(c3))

def c4(TF,L):
    return TF/L if TF/L <= 0.04 else 0.04

def c5(AT,B,draft,CM):
    # c₅ = 1 − 0.8 · AT / (B · T · CM)
    return 1 - 0.8 * AT / (B * draft * CM)

def c6(AT,B,CWP,V,g):
    if AT == 0:
        return 0
    FnT = V / math.sqrt(2 * g * AT / (B + B * CWP))
    return 0.2 * (1 - 0.2 * FnT) if FnT < 5 else 0

def c16(CP):
#     c₁₆ = 8.07981·CP − 13.8673·CP² + 6.984388·CP³ if CP < 0.8
# c₁₆ = 1.73014 − 0.7067·CP if CP ≥ 0.8
    if CP < 0.8:
        return 8.07981 * CP - 13.8673 * CP**2 + 6.984388 * CP**3
    else:
        return 1.73014 - 0.7067 * CP

def m1(L,draft,displacement,B,CP):
    # m₁ = 0.0140407 · L/T − 1.75254 · ∇^(1/3)/L − 4.79323 · B/L − c₁₆
    return 0.0140407 * L/draft - 1.75254 * displacement**(1/3)/L - 4.79323 * B/L - c16(CP)

def c15(L,displacement):
    # c₁₅ = −1.69385 if L³/∇ < 512
    # c₁₅ = −1.69385 + (L/∇^(1/3) − 8.0)/2.36 if 512 ≤ L³/∇ ≤ 1727
    # c₁₅ = 0 if L³/∇ > 1727
    if L**3/displacement < 512:
        return -1.69385
    elif L**3/displacement >= 512 and L**3/displacement <= 1727:
        return -1.69385 + (L/displacement**(1/3) - 8.0)/2.36
    else:
        return 0

def m4(c15,Fn):
    # m₄ = c₁₅ · 0.4 · exp(−0.034 · Fn^{−3.29})
    return c15 * 0.4 * math.exp(-0.034 * Fn**(-3.29))

def Lambda(CP,L,B):
    # λ = 1.446·CP − 0.03·L/B if L/B < 12 λ = 1.446·CP − 0.36 if L/B ≥ 12
    if L/B < 12:
        return 1.446*CP - 0.03*L/B
    else:
        return 1.446*CP - 0.36

def c17(CM,L,B,displacement):
    # c₁₇ = 6919.3 · CM^{-1.3346} · (∇/L³)^2.00977 · (L/B − 2)^1.40692
    return 6919.3 * CM**(-1.3346) * (displacement/L**3)**2.00977 * (L/B - 2)**1.40692

def m3(B,L,draft):
    # m₃ = −7.2035 · (B/L)^0.326869 · (T/B)^0.605375
    return -7.2035 * (B/L)**0.326869 * (draft/B)**0.605375

def RWa(c1,c2,c5,rho,g,displacement,m1,m4,Lambda,Fn,d):
    return c1 * c2 * c5 * rho * g * displacement * math.exp(m1 * Fn**d + m4 * math.cos(Lambda * Fn**(-2)))

def RWb(c17,c2,c5,rho,g,displacement,m3,m4,Lambda,Fn,d):
    return c17 * c2 * c5 * rho * g * displacement * math.exp(m3 * Fn**d + m4 * math.cos(Lambda * Fn**(-2)))

def waveResistance(Fn,d,c1,c2,c5,rho,g,displacement,m1,m4,Lambda,c17,m3):
    if Fn <= 0.4:
        return RWa(c1,c2,c5,rho,g,displacement,m1,m4,Lambda,Fn,d)
    elif Fn <= 0.55:
        RWa04 = RWa(c1,c2,c5,rho,g,displacement,m1,m4,Lambda,0.4,d)
        RWb055 = RWb(c17,c2,c5,rho,g,displacement,m3,m4,Lambda,0.55,d)
        return RWa04 + (20 * Fn - 8) / 3 * (RWb055 - RWa04)
    else:
        return RWb(c17,c2,c5,rho,g,displacement,m3,m4,Lambda,Fn,d)

def bulbousBowResistance(ABT,TF,hB,V,rho,g):
    if ABT == 0:
        return 0
    PB = 0.56 * math.sqrt(ABT) / (TF - 1.5 * hB)
    Fni = V / math.sqrt(g * (TF - hB - 0.25 * math.sqrt(ABT)) + 0.15 * V**2)
    return 0.11 * math.exp(-3 * PB**(-2)) * Fni**3 * ABT**1.5 * rho * g / (1 + Fni**2)

def transomSternResistance(AT,rho,V,c6):
    return 0.5 * rho * V**2 * AT * c6

def roughnessResistance(V,rho,L,S,CB,c2,c4):
#     RA = ½ρV² · S · CA
# CA = 0.006 · (L + 100)^{−0.16} − 0.00205
# + 0.003 · √(L/7.5) · CB⁴ · c₂ · (0.04 − c₄)
    return 0.5 * rho * V**2 * S * (0.006 * (L + 100)**(-0.16) - 0.00205 + 0.003 * math.sqrt(L/7.5) * CB**4 * c2 * (0.04 - c4))

# Total Resistance
# RT = RF(1 + k₁) + RAPP + RW + RB + RTR + RA
# where:
# RF = frictional resistance (ITTC-1957 line) (1 + k₁) = form factor accounting for viscous pressure resistance RAPP = appendage resistance RW = wave-making resistance RB = additional pressure resistance due to bulbous bow near waterline RTR = additional pressure resistance due to submerged transom stern RA = model–ship correlation (roughness) allowance
def totalResistance(V,draft,B,CM,CB,CWP,ABT,TF,hB,AT,L,CP,lcb,waterTemp,Cstern=0,g=9.81):
    displacement = CB * L * B * draft
    S = wettedSurfaceArea(draft,B,CM,CB,CWP,ABT,L)
    rho = Density(waterTemp)
    nu = KinematicViscosity(waterTemp)
    Rn = ReynoldsNumber(V,L,nu)
    fn = Fn(V,L)
    d = -0.9

    LRVal = LR(L,CP,lcb)
    c7Val = c7(B,L)
    iEVal = iE(L,B,CWP,CP,lcb,LRVal,displacement)
    c1Val = c1(draft,B,c7Val,iEVal)
    c3Val = c3(ABT,B,draft,TF,hB)
    c2Val = c2(c3Val)
    c4Val = c4(TF,L)
    c5Val = c5(AT,B,draft,CM)
    c6Val = c6(AT,B,CWP,V,g)
    c15Val = c15(L,displacement)
    m1Val = m1(L,draft,displacement,B,CP)
    m4Val = m4(c15Val,fn)
    m3Val = m3(B,L,draft)
    lambdaVal = Lambda(CP,L,B)
    c17Val = c17(CM,L,B,displacement)
    formFactorVal = formFactor(draft,B,CP,lcb,Cstern,L,LRVal)

    RF = frictionalResistance(V,S,rho,Rn) * formFactorVal
    RAPP = appendageResistance(V,rho,Rn)
    RW = waveResistance(fn,d,c1Val,c2Val,c5Val,rho,g,displacement,m1Val,m4Val,lambdaVal,c17Val,m3Val)
    RB = bulbousBowResistance(ABT,TF,hB,V,rho,g)
    RTR = transomSternResistance(AT,rho,V,c6Val)
    RA = roughnessResistance(V,rho,L,S,CB,c2Val,c4Val)

    return RF + RAPP + RW + RB + RTR + RA
