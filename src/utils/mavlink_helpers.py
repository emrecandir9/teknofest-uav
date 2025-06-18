import time
import logging
from dronekit import Vehicle
from pymavlink import mavutil

def condition_yaw(vehicle: Vehicle, heading: float, relative: bool = False):
    """
    Commands the vehicle to point to a specific heading.
    `heading`: The target heading in degrees (0-360).
    `relative`: If True, the heading is relative to the current direction.
    """
    if relative:
        is_relative = 1  # Yaw relative to direction of travel
    else:
        is_relative = 0  # Yaw is an absolute angle

    msg = vehicle.message_factory.command_long_encode(
        0, 0,  # target system, target component
        mavutil.mavlink.MAV_CMD_CONDITION_YAW,  # command
        0,  # confirmation
        heading,    # param 1, yaw in degrees
        0,          # param 2, yaw speed deg/s
        1,          # param 3, direction (-1 ccw, 1 cw)
        is_relative,# param 4, relative offset (1) or absolute angle (0)
        0, 0, 0)   # params 5-7 not used
    
    vehicle.send_mavlink(msg)

def send_local_velocity(vehicle: Vehicle, velocity_x: float, velocity_y: float, velocity_z: float, duration: float):
    """
    Moves the vehicle in a direction based on velocity vectors.
    This uses the NED (North-East-Down) frame relative to the vehicle's heading.
    `velocity_x`: North velocity in m/s.
    `velocity_y`: East velocity in m/s.
    `velocity_z`: Down velocity in m/s.
    `duration`: How long to send the command.
    """
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, # Frame relative to vehicle body
        0b0000111111000111, # type_mask (only speeds enabled)
        0, 0, 0, # x, y, z positions (not used)
        velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored)
        0, 0)    # yaw, yaw_rate (not used)
    
    # Send the command for the specified duration
    for _ in range(int(duration * 100)): # Send at 100Hz
        vehicle.send_mavlink(msg)
        time.sleep(0.01)

def set_servo(vehicle: Vehicle, channel: int, pwm_value: int):
    """
    Sets a servo to a specific PWM value.
    `channel`: The servo channel (e.g., 6).
    `pwm_value`: The PWM value.
    """
    msg = vehicle.message_factory.command_long_encode(
        0, 0,  # target_system, target_component
        mavutil.mavlink.MAV_CMD_DO_SET_SERVO, # command
        0,  # confirmation
        channel,
        pwm_value,
        0, 0, 0, 0, 0) # params 3-7 not used

    vehicle.send_mavlink(msg)
    logging.info(f"Setting servo {channel} to PWM {pwm_value}")