import time
from servo import Servo

my_servo = Servo()

legs = {
    'leg1': (15, 14, 13),
    'leg2': (12, 11, 10),
    'leg3': (9, 8, 31),
    'leg4': (16, 17, 18),
    'leg5': (19, 20, 21),
    'leg6': (22, 23, 27)
}

def move_servo(channel, angle, delay=0.2):
    angle = max(0, min(180, angle))
    my_servo.set_servo_angle(channel, angle)
    time.sleep(delay)
    


if __name__ == '__main__':
    for leg in legs.keys():
        if leg == 'leg1' or leg == 'leg2' or leg == 'leg3':
            move_servo(legs[leg][0], 90)
            move_servo(legs[leg][1], 130)
            move_servo(legs[leg][2], 130)
        else:
            move_servo(legs[leg][0], 90)
            move_servo(legs[leg][1], 50)
            move_servo(legs[leg][2], 50)
