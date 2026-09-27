import math
from enum import IntEnum

from calmWaterResistance import LR as holtropLR


class SternShape(IntEnum):
    PRAM_WITH_GONDOLA = -25
    V_SHAPED = -10
    NORMAL = 0
    U_SHAPED_HOGNER = 10


class Vessel:
    def __init__(self, L, B, draft, TF, CM, CB, CWP, ABT, hB, AT, lcb, Cstern=SternShape.NORMAL, kyy=0.25, TA=None, LE=None, LR=None):
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
        self.displacement = 0
        self.wettedSurfaceArea = 0

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