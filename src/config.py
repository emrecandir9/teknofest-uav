import numpy as np

# --- Vehicle Connection ---
# Use 'tcp:127.0.0.1:5762' for SITL simulation in Mission Planner
# Use '/dev/ttyACM0' for a real vehicle
CONNECTION_STRING = 'tcp:127.0.0.1:5762'
BAUDRATE = 57600

# --- Mission Parameters ---
TARGET_ALTITUDE = 10.0  # meters
DEFAULT_AIRSPEED = 12   # m/s
SLOW_AIRSPEED = 3       # m/s
ALIGN_AIRSPEED = 0.35   # m/s
FINAL_ALIGN_AIRSPEED = 0.15 # m/s

# --- Mission 2 Waypoints & Locations ---
PRE_MISSION_POINT = (40.2302201, 29.0096884, 14)
FIRST_POST_POINT = (40.2305318, 29.0091191, 14)
SECOND_POST_POINT = (40.2297490, 29.0091216, 14)
POOL_APPROACH_POINT = (40.2305677, 29.0094598, 14)
POOL_LOCATION = (40.2303995, 29.0095540, 10)
LANDING_ZONE = (40.2302395, 29.0098007, 12)

# --- Vision / Target Detection ---
CAMERA_INDEX = 0
# HSV color range for the red target
LOWER_HSV_BOUND = np.array([140, 50, 50])
UPPER_HSV_BOUND = np.array([179, 255, 255])
MIN_CONTOUR_AREA = 1400  # Minimum pixel area to be considered a target

# --- Alignment Parameters ---
# Tolerance for considering the target centered (in pixels)
FIRST_ALIGN_TOLERANCE = 40
FINAL_ALIGN_TOLERANCE = 25
ALIGN_DESCEND_ALTITUDE = 5.0

# --- Servo / Payload ---
SERVO_CHANNEL = 6
SERVO_OPEN_PWM = 2000
SERVO_CLOSE_PWM = 1470