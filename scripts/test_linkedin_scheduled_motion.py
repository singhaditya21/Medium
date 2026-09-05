#!/usr/bin/env python3
"""Fast content and layout checks; media validation lives in the renderer."""
import math
import unittest

import build_linkedin_scheduled_motion as motion


class ScheduledMotionTests(unittest.TestCase):
    def test_exact_audited_schedule(self):
        posts = motion.posts()
        self.assertEqual(len(posts), 14)
        self.assertEqual([p["id"] for p in posts], [f"S{i:02d}" for i in range(1,15)])
        self.assertEqual(len({p["slug"] for p in posts}), 14)
        self.assertEqual([p["schedule"] for p in posts], sorted(p["schedule"] for p in posts))
        self.assertEqual(posts[0]["schedule"], "2026-09-07T08:45:00+05:30")
        self.assertEqual(posts[-1]["schedule"], "2026-10-09T14:00:00+05:30")
        self.assertEqual(sum(p["media"] == "3-page PDF" for p in posts),10)

    def test_each_topic_has_its_own_control_contract(self):
        posts=motion.posts()
        self.assertEqual(len({tuple(p["contract"]) for p in posts}),14)
        self.assertEqual(len({tuple(p["failure"]) for p in posts}),14)
        for p in posts:
            self.assertEqual(len(p["contract"]),6)
            self.assertEqual(len(p["failure"]),3)
            self.assertTrue(p["note"])
            self.assertTrue(p["question"].endswith("?"))
            if p["chart"]:
                self.assertTrue(p["unit"])
                self.assertTrue(all(0 <= v <= p["domain"] for _,v in p["chart"]))

    def test_derived_values(self):
        c, mu, arrival=5,10,42
        a=arrival/mu
        rho=arrival/(c*mu)
        tail=a**c/math.factorial(c)/(1-rho)
        wait_probability=tail/(sum(a**k/math.factorial(k) for k in range(c))+tail)
        wait_minutes=wait_probability/(c*mu-arrival)*60
        self.assertAlmostEqual(rho,.84)
        self.assertEqual(round(wait_minutes,1),4.8)
        self.assertEqual(52-50,2)
        self.assertEqual(52-42,10)
        self.assertEqual(round((.018-.004)*42000-18-65),505)
        self.assertAlmostEqual(2400000*.12,288000)
        self.assertAlmostEqual(2400000*.08,192000)
        self.assertEqual(80*180000/8,1800000)
        self.assertEqual(round(.9502/.837,3),1.135)

    def test_all_scenes_fit(self):
        motion.OVERFLOWS.clear()
        for p in motion.posts():
            for scene in range(6):
                for offset in (0.,.15,2.4,5.8):
                    image=motion.render(p,scene*6+offset)
                    self.assertEqual(image.size,(1080,1350))
        self.assertEqual(motion.OVERFLOWS,set())


if __name__=="__main__":unittest.main()
