import time
import logging
from dronekit import Vehicle, LocationGlobalRelative, VehicleMode
from src.vision.target_detector import TargetDetector
from src.utils.mavlink_helpers import condition_yaw, send_local_velocity, set_servo

def align_and_drop_payload(vehicle: Vehicle, detector: TargetDetector, config):
    logging.info("Starting final alignment and payload drop sequence.")

    logging.info("Performing first alignment...")
    if not perform_alignment(vehicle, detector, config.FIRST_ALIGN_TOLERANCE, config.ALIGN_AIRSPEED):
        logging.error("First alignment failed. Aborting drop.")
        return

    logging.info("First alignment successful. Descending for final alignment.")
    
    current_loc = vehicle.location.global_relative_frame
    descend_point = LocationGlobalRelative(current_loc.lat, current_loc.lon, config.ALIGN_DESCEND_ALTITUDE)
    vehicle.simple_goto(descend_point, groundspeed=config.SLOW_AIRSPEED)
    
    while True:
        alt = vehicle.location.global_relative_frame.alt
        if alt <= config.ALIGN_DESCEND_ALTITUDE + 0.5:
            break
        time.sleep(1)
    
    logging.info(f"Reached final alignment altitude of {config.ALIGN_DESCEND_ALTITUDE}m.")

    logging.info("Performing final, high-precision alignment...")
    if not perform_alignment(vehicle, detector, config.FINAL_ALIGN_TOLERANCE, config.FINAL_ALIGN_AIRSPEED):
        logging.error("Final alignment failed. Aborting drop.")
        return

    logging.info("Final alignment successful. Switching to LOITER and dropping payload.")

    vehicle.mode = VehicleMode("LOITER")
    while vehicle.mode.name != "LOITER":
        time.sleep(0.5)

    logging.info("Mode switched to LOITER. Dropping payload now.")
    set_servo(vehicle, config.SERVO_CHANNEL, config.SERVO_OPEN_PWM)
    time.sleep(3)
    set_servo(vehicle, config.SERVO_CHANNEL, config.SERVO_CLOSE_PWM)
    logging.info("Payload dropped. Servo closed.")

    vehicle.mode = VehicleMode("GUIDED")
    while vehicle.mode.name != "GUIDED":
        time.sleep(0.5)

def perform_alignment(vehicle: Vehicle, detector: TargetDetector, tolerance: int, speed: float) -> bool:
    timeout_seconds = 180
    start_time = time.time()

    logging.info("Aligning vehicle to North (0 degrees).")
    condition_yaw(vehicle, 0)
    time.sleep(2)
    
    while time.time() - start_time < timeout_seconds:
        detection = detector.latest_detection
            
        if not detection['found']:
            logging.warning("Target lost during alignment.")
            send_local_velocity(vehicle, 0, 0, 0, 0.5)
            time.sleep(0.1)
            continue
        
        cx, cy = detection['cx'], detection['cy']
        center_x, center_y = detector.center_x, detector.center_y

        if abs(cx - center_x) < tolerance and abs(cy - center_y) < tolerance:
            logging.info(f"Alignment successful within tolerance of {tolerance}px.")
            send_local_velocity(vehicle, 0, 0, 0, 1)
            return True

        error_x = cx - center_x
        error_y = cy - center_y

        vel_y = (error_x / center_x) * speed
        vel_x = -(error_y / center_y) * speed

        logging.info(f"Aligning... Pos:({cx},{cy}), Err:({error_x},{error_y}), Vel:({vel_x:.2f},{vel_y:.2f})")
        send_local_velocity(vehicle, vel_x, vel_y, 0, 0.2)

    logging.error("Alignment timed out.")
    return False