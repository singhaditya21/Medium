import math
import unittest
from analytics import wilson, recovery_hours, planning_cap, mmc, fluid_backlog, results


class Calculations(unittest.TestCase):
    def test_baseline_by_independent_units(self):
        self.assertEqual(recovery_hours(10000,.01,12), 100 * (12/60))
    def test_recovery_sensitivity(self):
        self.assertEqual([recovery_hours(10000,p,12) for p in [.002,.01,.02]], [4,20,40])
    def test_cap_point(self):
        self.assertEqual(planning_cap(16,.75,.01,12), 6000)
    def test_cap_upper(self):
        self.assertEqual(planning_cap(16,.75,wilson(100,10000)[1],12), 4939)
    def test_wilson_score_roots(self):
        for p in wilson(100,10000):
            self.assertAlmostEqual(abs((.01-p)/math.sqrt(p*(1-p)/10000)), 1.959963984540054)
    def test_wilson_boundary(self):
        self.assertAlmostEqual(wilson(0,100)[0],0)
        self.assertAlmostEqual(wilson(100,100)[1],1)
    def test_wilson_width(self):
        a,b=wilson(10,1000);c,d=wilson(100,10000)
        self.assertGreater(b-a,d-c)
    def test_invalid_wilson(self):
        for k,n in [(0,0),(-1,2),(3,2)]:
            with self.assertRaises(ValueError):wilson(k,n)
    def test_fluid_conservation(self):
        self.assertEqual(fluid_backlog(5,10000,.01,80),[0,20,40,60,80,100])
    def test_stress_backlog(self):
        self.assertEqual(fluid_backlog(5,10000,.02,80)[-1],600)
    def test_no_negative_queue(self):
        self.assertEqual(fluid_backlog(5,10000,.002,80),[0]*6)
    def test_existing_backlog(self):
        self.assertEqual(fluid_backlog(2,10000,.002,80,100),[100,40,0])
    def test_mmc_reduces_to_mm1(self):
        q=mmc(8,10,1)
        self.assertAlmostEqual(q['p_wait'],.8)
        self.assertAlmostEqual(q['mean_wait_min'],24)
    def test_mmc_two_server_anchor(self):
        q=mmc(3,2,2)
        self.assertAlmostEqual(q['p_wait'],9/14)
        self.assertAlmostEqual(q['mean_wait_min'],(9/14)*60)
    def test_erlang_b_independent_recursion(self):
        for rho in [.5,.75,.9,.95,.98]:
            a=rho*4;b=1
            for k in range(1,5): b=a*b/(k+a*b)
            c=b/(1-rho+rho*b)
            self.assertAlmostEqual(mmc(rho*20)['p_wait'],c)
    def test_quantile_inverts_tail(self):
        for rho in [.5,.75,.9,.95,.98]:
            q=mmc(rho*20)
            self.assertAlmostEqual(q['p_wait']*math.exp(-20*(1-rho)*q['p95_wait_min']/60),.05)
    def test_zero_arrivals(self):
        q=mmc(0)
        self.assertEqual([q['p_wait'],q['mean_wait_min'],q['p95_wait_min']],[0,0,0])
    def test_unstable_has_no_fake_wait(self):
        for arrival in [20,25]:
            q=mmc(arrival)
            self.assertFalse(q['stable']);self.assertIsNone(q['mean_wait_min'])
    def test_wait_increases(self):
        waits=[mmc(r*20)['mean_wait_min'] for r in [.5,.75,.9,.95,.98]]
        self.assertEqual(waits,sorted(waits))
    def test_more_servers_reduce_wait(self):
        self.assertLess(mmc(15,5,5)['mean_wait_min'],mmc(15,5,4)['mean_wait_min'])
    def test_invalid_inputs(self):
        for fn,args in [(mmc,(-1,)),(mmc,(1,0)),(mmc,(1,5,0)),(planning_cap,(16,.75,0,12)),(recovery_hours,(10,2,12))]:
            with self.assertRaises(ValueError):fn(*args)
    def test_economic_units(self):
        x=results()['economics']
        self.assertEqual(10000*3/60-20-30-40,x['net_capacity_hours'])


if __name__ == '__main__':unittest.main()
