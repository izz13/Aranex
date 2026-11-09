import time
from servo import Servo

my_servo = Servo()

# (coxa/hip, femur, tibia) channels for each leg
legs = {
    'leg1': (15, 14, 13),
    'leg2': (12, 11, 10),
    'leg3': (9, 8, 31),
    'leg4': (16, 17, 18),
    'leg5': (19, 20, 21),
    'leg6': (22, 23, 27)
}

# ---------------- Settings you may need to tweak ----------------
LEFT_SIDE = ('leg1', 'leg2', 'leg3')   # stand at femur/tibia = 150
RIGHT_SIDE = ('leg4', 'leg5', 'leg6')  # stand at femur/tibia = 45

# Tripod gait groups: one group is in the air while the other pushes on the ground
GROUP_A = ('leg1', 'leg3', 'leg5')
GROUP_B = ('leg2', 'leg4', 'leg6')

SWING = 20          # degrees the hip moves forward/back from center (90)
LIFT = 25           # degrees the femur lifts a foot off the ground
STEP_DELAY = 0.02   # seconds between interpolation steps (lower = faster)
STEPS = 10          # interpolation steps per movement

# +1 / -1: which way the hip angle moves the leg "forward" on each side.
# If the robot walks backward, set FORWARD_DIR = -1.
# If it wobbles/twists instead of walking, flip one of the SIDE values.
FORWARD_DIR = 1
LEFT_HIP_SIGN = 1
RIGHT_HIP_SIGN = -1

# Which way the femur moves to lift the foot (left stands at 150, right at 45).
# If the feet push into the ground instead of lifting, flip these.
LEFT_LIFT_SIGN = -1    # 150 -> 125
RIGHT_LIFT_SIGN = 1    # 45  -> 70
# -----------------------------------------------------------------


def clamp(angle):
    return max(0, min(180, angle))


def stand_angles(leg):
    if leg in LEFT_SIDE:
        return 90, 135, 135
    return 90, 45, 45


# Track current commanded angles so movements can be interpolated smoothly
current = {}


def set_leg_joint(leg, joint, angle):
    angle = clamp(angle)
    my_servo.set_servo_angle(legs[leg][joint], angle)
    current[(leg, joint)] = angle


def move(targets):
    """targets: {(leg, joint): angle}. Moves all of them together, smoothly."""
    start = {k: current[k] for k in targets}
    for i in range(1, STEPS + 1):
        t = i / STEPS
        for (leg, joint), end in targets.items():
            set_leg_joint(leg, joint, start[(leg, joint)] + (end - start[(leg, joint)]) * t)
        time.sleep(STEP_DELAY)


def hip_angle(leg, offset):
    sign = LEFT_HIP_SIGN if leg in LEFT_SIDE else RIGHT_HIP_SIGN
    return 90 + sign * FORWARD_DIR * offset


def lifted_femur(leg):
    if leg in LEFT_SIDE:
        return stand_angles(leg)[1] + LEFT_LIFT_SIGN * LIFT
    return stand_angles(leg)[1] + RIGHT_LIFT_SIGN * LIFT


def stand():
    for leg in legs:
        hip, femur, tibia = stand_angles(leg)
        set_leg_joint(leg, 0, hip)
        set_leg_joint(leg, 1, femur)
        set_leg_joint(leg, 2, tibia)
        time.sleep(0.2)


def lift(group):
    move({(leg, 1): lifted_femur(leg) for leg in group})


def lower(group):
    move({(leg, 1): stand_angles(leg)[1] for leg in group})


def swing(forward_group, back_group):
    """Swing one group forward (in the air) while the other pushes back (on the ground)."""
    targets = {}
    for leg in forward_group:
        targets[(leg, 0)] = hip_angle(leg, +SWING)
    for leg in back_group:
        targets[(leg, 0)] = hip_angle(leg, -SWING)
    move(targets)


def step_cycle():
    # Group A in the air, group B on the ground
    lift(GROUP_A)
    swing(GROUP_A, GROUP_B)
    lower(GROUP_A)
    # Group B in the air, group A on the ground
    lift(GROUP_B)
    swing(GROUP_B, GROUP_A)
    lower(GROUP_B)


def walk(cycles=4):
    for _ in range(cycles):
        step_cycle()


if __name__ == '__main__':
    try:
        stand()
        time.sleep(1)
        walk(cycles=4)
    finally:
        # Return to the standing pose when done or if you press Ctrl+C
        stand()
