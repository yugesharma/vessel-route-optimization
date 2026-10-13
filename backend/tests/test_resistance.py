from classes.vessel import Vessel, SternShape, vsl
from calmWaterResistance import calmWaterResistance
from waveAddedResistance import waveAddedResistance
from windResistance import windResistance
import pytest

testVessel = Vessel(
    L=205.0, B=32.0, draft=10, TF=10, TA=10,  
    CB=37500/205/32/10, CM=0.980, lcb=-0.75,
    CWP=0.750, 
    ABT=20, hB=4,  
    AT=16,  
    Cstern=SternShape.U_SHAPED_HOGNER,
    #below values not in the original paper, but are needed for the calculation
    kyy=0.25,
    LE=60.0,  
    eta=0.70,  
    sfoc=175.0,  
    mcrKw=27000.0,  
)

def test_calmWaterResistance():
    print(calmWaterResistance(25*0.5144, 15.0,testVessel))
    assert calmWaterResistance(25*0.5144, 15.0,testVessel) == pytest.approx(1793.26e3,rel=0.01)

    calm = {"Hs": 0, "Tp": 0, "waveDir": 0, "windSpeed": 0, "windDir": 0}
    assert testVessel.legFuel(22, 0, 1, calm) is not None
    assert testVessel.legFuel(24, 0, 1, calm) is None

    w = {**calm, "Hs": 4, "Tp": 8, "waveDir": 150}
    assert waveAddedResistance(testVessel, 4, 8, 150, 6 * 0.5144) < 0   # guards the test itself
    assert testVessel.legFuel(6, 0, 1, w) == testVessel.legFuel(6, 0, 1, {**calm, "Tp": 8})

def test_windResistance():
    V = 12 * 0.5144
    assert windResistance(vsl, 10, 0, 0, V) > 0 > windResistance(vsl, 10, 180, 0, V)
    assert windResistance(vsl, 10, 60, 0, V) == windResistance(vsl, 10, 300, 0, V)

    # a head wind costs fuel; a tailwind is floored, so it costs the same as no wind
    def fuel(windSpeed, windDir):
        return vsl.legFuel(12, 0, 1, {"Hs": 0, "Tp": 0, "waveDir": 0, "windSpeed": windSpeed, "windDir": windDir})
    assert fuel(10, 0) > fuel(0, 0) > fuel(20, 180)
    assert fuel(20, 180) == pytest.approx(vsl.calmWaterFuelPerNM(12) * 12)

if __name__ == "__main__":
    test_calmWaterResistance()
    test_windResistance()
