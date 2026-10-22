from classes.vessel import Vessel, SternShape, vsl
from calmWaterResistance import calmWaterResistance
from waveAddedResistance import waveAddedResistance, jonswap, snnmTransfer, g, RHO
from windResistance import windResistance
import pytest
import numpy as np

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
    assert testVessel.legFuel(6, 0, 1, w) == testVessel.legFuel(6, 0, 1, {**calm, "Tp": 8})

def test_jonswap():
    w=np.linspace(0.01, 40, 400_000)
    Hs=1.0
    Tp=10.0
    gamma=3.3
    S=jonswap(w, Hs, Tp, gamma)
    m0,m1=(np.trapezoid(S*w**k,w) for k in range(2))
    assert 2*np.pi*m0/m1==pytest.approx(Tp*(0.7303 + 0.04936*gamma - 0.006556*gamma**2 + 0.0003610*gamma**3), rel=0.005)

#Based on Kim et al. 2017. The expriments themselves vary by almost 30% so the range is wide
def test_snnmTransfer():
    lamL=1.2
    expected=7.8
    w=np.sqrt(2*np.pi*g/(lamL*vsl.L))
    omega=np.array([w])
    sigma=snnmTransfer(omega, 0.0, vsl, 7.9739)[0]/(RHO*g*vsl.B**2/vsl.L)
    assert 0.7<sigma/expected<1.3, f"λ/L={lamL}: SNNM {sigma:.2f} vs exp {expected}"

def test_waveAddedResistance():
    V = 12 * 0.5144
    def R(Hs=3.0, Tp=9.0, rel=0):
        return waveAddedResistance(vsl, Hs, Tp, rel, V)

    assert R(Hs=0) == 0 and R(Tp=0) == 0
    assert R(rel=60) == R(rel=-60) == R(rel=300) == R(rel=420)   
    assert R(rel=180) == R(rel=-180)
    assert R(Hs=6) == pytest.approx(4 * R())                     
    assert R(rel=0) > R(rel=90) > R(rel=180)                     

    # 2∫R(ω)S(ω)dω on a wide, fine grid; OMEGA (0.1–3.0) loses <2% for Tp ≥ 7 s
    w = np.linspace(0.05, 8, 20_000)
    ref = 2 * np.trapezoid(snnmTransfer(w, 0.0, vsl, V) * jonswap(w, 3.0, 9.0), w)
    assert R() == pytest.approx(ref, rel=0.02)

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
