from servo import Servo

if __name__ == "__main__":
    servo = Servo(4)
    servo.write(12, 5, 0.1)
    servo.write(7.25, 5, 0.1)
