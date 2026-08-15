import unittest

from core.state import AssistantState
from gui.orb_geometry import LEFT_SEGMENT, RIGHT_SEGMENT, geometry_for


class OrbGeometryTests(unittest.TestCase):
    def test_ring_keeps_guaranteed_gap_in_every_state_and_animation_phase(self):
        for state in AssistantState:
            for phase in (0.0, 0.5, 1.57, 3.14, 5.8, 12.0):
                geometry = geometry_for(state, phase, 300, 180, 66)
                self.assertGreaterEqual(geometry.separation, geometry.gap)
                self.assertGreater(geometry.gap, 0)

    def test_geometry_remains_centered_after_resize(self):
        geometry = geometry_for(AssistantState.LISTENING, 1.0, 512, 220, 55)
        self.assertEqual(512, geometry.center_x)
        self.assertEqual(220, geometry.center_y)

    def test_segments_are_vertical_and_leave_top_bottom_open(self):
        self.assertEqual(LEFT_SEGMENT[1], RIGHT_SEGMENT[1])
        self.assertEqual(180, (RIGHT_SEGMENT[0] - LEFT_SEGMENT[0]) % 360)
        self.assertLess(LEFT_SEGMENT[0], 180)
        self.assertGreater(RIGHT_SEGMENT[0], 180)
