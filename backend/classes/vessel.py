import math
from enum import IntEnum

from calmWaterResistance import LR as holtropLR
from calmWaterResistance import calmWaterResistance
from waveAddedResistance import waveAddedResistance

class SternShape(IntEnum):
    PRAM_WITH_GONDOLA = -25
    V_SHAPED = -10
    NORMAL = 0
    U_SHAPED_HOGNER = 10


class Vessel:
    def __init__(self, L, B, draft, TF, CM, CB, CWP, ABT, hB, AT, lcb, Cstern=SternShape.NORMAL, kyy=0.25, TA=None, LE=None, LR=None,
                 eta=0.70, sfoc=175.0, mcrKw=27000.0):
        self.L = L
        self.B = B
        self.draft = draft
        self.TF = TF # forward draught
        self.CM = CM # midship coefficient
        self.CB = CB # block coefficient
        self.CWP = CWP # waterplane coefficient
        self.ABT = ABT # area of bottom transverse
        self.hB = hB # height of bottom transverse
        self.AT = AT # area of transverse
        self.lcb = lcb # longitudinal center of buoyancy
        self.Cstern = Cstern # stern shape
        self.kyy = kyy  # pitch radius of gyration / Lpp, 0.25 typical
        self.TA = TF if TA is None else TA  # aft draught; default even keel
        self.LE = LE  # waterline entrance length (m), bow to 0.495B half-breadth; from hull lines if known
        self.LR = LR  # waterline run length (m), stern to 0.495B half-breadth
        self.E1 = 0 # Bow entrance angle
        self.E2 = 0 # Stern entrance angle
        self.CP = 0 # Prismatic coefficient
        # fuel model
        self.eta = eta  # overall propulsive efficiency: effective power / brake power
        self.sfoc = sfoc  # specific fuel oil consumption (g/kWh)
        self.mcrKw = mcrKw  # engine maximum continuous rating (kW); legs needing more are infeasible

        # derived hull values used by the calm-water model
        self.getCP()
        self.getDisplacement()
        self.getWettedSurfaceArea()

    def getCP(self):
        self.CP = self.CB / self.CM
        return self.CP

    def getEntranceRunAngles(self):
        # SNNM (ITTC G.3, Fig G-3): E = atan(0.495B / length)
        # without hull lines, LR is Holtrop-Mennen and LE its mirror (lcb sign flipped); measured LE/LR beat both
        CP = self.getCP()
        if self.LR is None:
            self.LR = holtropLR(self.L, CP, self.lcb)
        if self.LE is None:
            self.LE = self.L * (1 - CP - 0.06 * CP * self.lcb / (4 * CP - 1))
        self.E1 = math.atan(0.495 * self.B / self.LE)
        self.E2 = math.atan(0.495 * self.B / self.LR)
        return self.E1, self.E2

    def getDisplacement(self):
        self.displacement = self.CB * self.L * self.B * self.draft
        return self.displacement

    def getWettedSurfaceArea(self):
        self.wettedSurfaceArea = (
            self.L * (2 * self.draft + self.B) * self.CM**0.5
            * (0.453 + 0.4425 * self.CB - 0.2862 * self.CM
               - 0.003467 * (self.B / self.draft) + 0.3696 * self.CWP)
            + 2.38 * self.ABT / self.CB
        )
        return self.wettedSurfaceArea
    
    def legFuel(self, speedKn, headingDeg, timeH, weather, waterTemp=15.0):
        #no R_wind yet, add it later
        V = speedKn * 0.5144
        R_calm = calmWaterResistance(V, waterTemp, self)  # N
        R_wave = waveAddedResistance(self, weather["Hs"], weather["Tp"], weather["waveDir"] - headingDeg, V)  # N, may be < 0
        R_total = R_calm + max(0, R_wave)  # floor R_wave at 0 so no leg beats calm water; keeps the A* heuristic admissible
        P_B = R_total * V / 1000 / self.eta  # brake power (kW)
        if P_B > 0.9*self.mcrKw:
            return None
        return P_B * self.sfoc * timeH / 1000  # kW * g/kWh * h = g -> kg
    
    def calmWaterFuelPerNM(self, speedKn, waterTemp=15.0):
        V = speedKn * 0.5144
        R_calm = calmWaterResistance(V, waterTemp, self)  # N
        P_B_calm= R_calm * V / 1000 / self.eta
        return P_B_calm * self.sfoc / 1000 / speedKn  # kW * g/kWh / 1000 = g -> kg/NM


# KVLCC2 (KRISO VLCC), the single ship used for now.
# Published full-scale particulars: SIMMAN 2014 
vsl = Vessel(
    L=320.0, B=58.0, draft=20.8, TF=20.8, TA=20.8,  # even keel, design draught
    CB=0.8098, CM=0.998, lcb=3.48,
    CWP=0.873,  # not published; Schneekluth estimate (1 + 2CB) / 3
    ABT=0, hB=0,  # bulb area/centre not published; 0 ignores the bulb in Holtrop
    AT=0,  # transom not immersed at design draught
    Cstern=SternShape.U_SHAPED_HOGNER,
    kyy=0.25,
    LE=60.0,  # fitted to KVLCC2 added-resistance tests (Kim et al. 2017); Holtrop-mirror estimate gave 36 m
    eta=0.70,  # assumed; typical tanker 0.65-0.75, replace with sea-trial/model-test value
    sfoc=175.0,  # assumed; modern slow-speed two-stroke 170-190 g/kWh
    mcrKw=27000.0,  # assumed; not published for KVLCC2, typical VLCC main engine
)
