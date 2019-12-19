import unittest
from motorContl import MotorController, BallStateE

class TestMotorController(unittest.TestCase):

    def setUp(self):
        self.motorC = MotorController()

    def test_get_ball_state_less_than_threshold_int(self):
        expected = BallStateE.HAVE_BALL
        actual = self.motorC.getBallState(MotorController.THRESHOLD_BALL_DETECT - 1)
        self.assertEqual(expected, actual)
    
    def test_get_ball_state_less_than_threshold_float(self):
        expected = BallStateE.HAVE_BALL
        actual = self.motorC.getBallState(MotorController.THRESHOLD_BALL_DETECT - 0.1)
        self.assertEqual(expected, actual)

    def test_get_ball_state_equal_to_threshold(self):
        expected = BallStateE.NOT_HAVE_BALL
        actual = self.motorC.getBallState(MotorController.THRESHOLD_BALL_DETECT)
        self.assertEqual(expected, actual)

    def test_get_ball_state_more_than_threshold_int(self):
        expected = BallStateE.NOT_HAVE_BALL
        actual = self.motorC.getBallState(MotorController.THRESHOLD_BALL_DETECT + 1)
        self.assertEqual(expected, actual)
    
    def test_get_ball_state_more_than_threshold_float(self):
        expected = BallStateE.NOT_HAVE_BALL
        actual = self.motorC.getBallState(MotorController.THRESHOLD_BALL_DETECT + 0.1)
        self.assertEqual(expected, actual)

    def test_calc_motor_powers_have_ball_angle_0(self):
        expected = 30, 30
        actual = self.motorC.calcMotorPowers(BallStateE.HAVE_BALL, 0)
        self.assertEqual(expected, actual)

    def test_calc_motor_powers_have_ball_angle_negative(self):
        expected = 30, 30
        actual = self.motorC.calcMotorPowers(BallStateE.HAVE_BALL, -120)
        self.assertEqual(expected, actual)

    def test_calc_motor_powers_have_ball_angle_positive(self):
        expected = 30, 30
        actual = self.motorC.calcMotorPowers(BallStateE.HAVE_BALL, 120)
        self.assertEqual(expected, actual)

    def test_calc_motor_powers_not_have_ball_angle_0(self):
        expected = 30, 30
        actual = self.motorC.calcMotorPowers(BallStateE.NOT_HAVE_BALL, 0)
        self.assertEqual(expected, actual)

    def test_calc_motor_powers_not_have_ball_angle_negative_over_100(self):
        angle = -120
        expected = (100 / MotorController.CORRECTION_VALUE_SPEED), (-100 / MotorController.CORRECTION_VALUE_SPEED)
        actual = self.motorC.calcMotorPowers(BallStateE.NOT_HAVE_BALL, angle)
        self.assertEqual(expected, actual)

    def test_calc_motor_powers_not_have_ball_angle_negative_100(self):
        angle = -100
        expected = (100 / MotorController.CORRECTION_VALUE_SPEED), (-100 / MotorController.CORRECTION_VALUE_SPEED)
        actual = self.motorC.calcMotorPowers(BallStateE.NOT_HAVE_BALL, angle)
        self.assertEqual(expected, actual)

    def test_calc_motor_powers_not_have_ball_angle_negative_within_100(self):
        angle = -60
        expected = (-angle / MotorController.CORRECTION_VALUE_SPEED), (angle / MotorController.CORRECTION_VALUE_SPEED)
        actual = self.motorC.calcMotorPowers(BallStateE.NOT_HAVE_BALL, angle)
        self.assertEqual(expected, actual)

    def test_calc_motor_powers_not_have_ball_angle_positive_within_100(self):
        angle = 60
        expected = (-angle / MotorController.CORRECTION_VALUE_SPEED), (angle / MotorController.CORRECTION_VALUE_SPEED)
        actual = self.motorC.calcMotorPowers(BallStateE.NOT_HAVE_BALL, angle)
        self.assertEqual(expected, actual)

    def test_calc_motor_powers_not_have_ball_angle_positive_over_100(self):
        angle = 120
        expected = (-100 / MotorController.CORRECTION_VALUE_SPEED), (100 / MotorController.CORRECTION_VALUE_SPEED)
        actual = self.motorC.calcMotorPowers(BallStateE.NOT_HAVE_BALL, angle)
        self.assertEqual(expected, actual)

    def tearDown(self):
        del self.motorC

if __name__ == "__main__":
    unittest.main()

