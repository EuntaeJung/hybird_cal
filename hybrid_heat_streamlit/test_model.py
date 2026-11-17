import unittest
from model import DEFAULTS, COP, optimum, cost, validate

class ModelTests(unittest.TestCase):
    def test_excel_reference(self):
        s=dict(DEFAULTS,keep=True,w2=40.,w3=20.)
        expected=[101409.07585862462,109865.0998048927,113453.48077442592]
        for k,v in enumerate(expected):
            self.assertAlmostEqual(optimum(k,0,s)['total'],v,places=6)
        self.assertAlmostEqual(optimum(0,0,s)['hpPercent'],.06550049369291315)

    def test_optimum_beats_dense_grid(self):
        for s in [DEFAULTS,dict(DEFAULTS,keep=True,w2=40.,w3=20.),dict(DEFAULTS,b=350.,q=2000.)]:
            for t in [-20,-10,0,10,20]:
                for k in range(3):
                    best=optimum(k,t,s)
                    for i in range(1001):
                        self.assertLessEqual(best['total'],cost(k,i/1000,COP[t],s)['total']+1e-7)

    def test_zero_baseline_and_invalid_weights(self):
        s=dict(DEFAULTS,p=0.,f=0.)
        self.assertIsNone(optimum(1,0,s)['hpPercent'])
        with self.assertRaises(ValueError):
            validate(dict(DEFAULTS,w1=50.))

if __name__=='__main__':
    unittest.main()
