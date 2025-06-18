import time
import logging
from dronekit import Vehicle, LocationGlobalRelative
from src.vision.target_detector import TargetDetector
from src.missions.mission_2_align import align_and_drop_payload
from src.utils.transformations import get_distance_metres


def wait_for_arrival(vehicle: Vehicle, target_location: LocationGlobalRelative, location_name: str, tolerance: float = 1.0):
    """
    Waits until the vehicle reaches a target location within a given tolerance.
    """    
    while True:
        distance = get_distance_metres(vehicle.location.global_frame, target_location)
        logging.info(f"Moving to {location_name}... Distance: {distance:.2f}m")
        if distance <= tolerance:
            logging.info(f"Arrived at {location_name} (within {tolerance}m).")
            break
        time.sleep(1)

def run_mission_2(vehicle: Vehicle, detector: TargetDetector, config):
    """
    Executes the complete sequence for Mission 2.
    """
    logging.info("--- Starting Mission 2 ---")
    
    pre_mission_point = LocationGlobalRelative(*config.PRE_MISSION_POINT)
    vehicle.simple_goto(pre_mission_point, groundspeed=config.DEFAULT_AIRSPEED)
    wait_for_arrival(vehicle, pre_mission_point, "Staging Point", tolerance=1.0)

    logging.info("Flying search pattern between posts to find target.")
    first_post = LocationGlobalRelative(*config.FIRST_POST_POINT)
    second_post = LocationGlobalRelative(*config.SECOND_POST_POINT)
    
    vehicle.simple_goto(first_post, groundspeed=config.DEFAULT_AIRSPEED)
    wait_for_arrival(vehicle, first_post, "First Post", tolerance=0.5)

    logging.info("Live camera feed enabled.")
    detector.display_feed = True
    
    logging.info("Vision system is active. Starting target search pattern.")
    
    target_location = None
    logging.info("Proceeding to Second Post, searching for target en route.")
    vehicle.simple_goto(second_post, groundspeed=config.SLOW_AIRSPEED)
    
    while True:
        distance_to_post2 = get_distance_metres(vehicle.location.global_frame, second_post)
        if distance_to_post2 <= 0.5:
            logging.info("Reached Second Post.")
            break
        
        if target_location is None:
            detection = detector.latest_detection
            if detection['found']:
                target_location = vehicle.location.global_relative_frame
                logging.info(f"!!! TARGET SPOTTED (First Sighting) at Lat: {target_location.lat}, Lon: {target_location.lon} !!!")

        time.sleep(0.1)

    if not target_location:
        logging.error("Failed to find target during search pattern. Mission aborted.")
        return

    logging.info("Proceeding to pool location.")
    pool_approach = LocationGlobalRelative(*config.POOL_APPROACH_POINT)
    vehicle.simple_goto(pool_approach, groundspeed=config.DEFAULT_AIRSPEED)
    wait_for_arrival(vehicle, pool_approach, "Pool Approach Point", tolerance=1.0)

    pool_loc = LocationGlobalRelative(*config.POOL_LOCATION)
    vehicle.simple_goto(pool_loc, groundspeed=config.SLOW_AIRSPEED)
    wait_for_arrival(vehicle, pool_loc, "Pool Location", tolerance=0.35)
    
    descend_to_pool = LocationGlobalRelative(pool_loc.lat, pool_loc.lon, 2.0)
    vehicle.simple_goto(descend_to_pool)
    while True:
        alt = vehicle.location.global_relative_frame.alt
        logging.info(f"Descending to pool... Current alt: {alt:.2f}m")
        if alt <= 2.5:
            break
        time.sleep(1)
    logging.info("Water payload acquired.")

    ascend_from_pool = LocationGlobalRelative(pool_loc.lat, pool_loc.lon, config.TARGET_ALTITUDE)
    vehicle.simple_goto(ascend_from_pool)
    while True:
        alt = vehicle.location.global_relative_frame.alt
        logging.info(f"Ascending from pool... Current alt: {alt:.2f}m")
        if alt >= config.TARGET_ALTITUDE * 0.95:
            break
        time.sleep(1)
    logging.info("Ascended from pool.")

    logging.info("Proceeding to captured target location.")
    vehicle.simple_goto(target_location, groundspeed=config.SLOW_AIRSPEED)
    wait_for_arrival(vehicle, target_location, "Captured Target Location", tolerance=0.3)

    align_and_drop_payload(vehicle, detector, config)

    logging.info("Ascending slightly to ensure mobility before next waypoint.")
    current_loc = vehicle.location.global_relative_frame
    ascend_point = LocationGlobalRelative(current_loc.lat, current_loc.lon, config.TARGET_ALTITUDE)
    vehicle.simple_goto(ascend_point)
    time.sleep(3)

    logging.info("Payload sequence complete. Returning to Second Post.")
    vehicle.simple_goto(second_post, groundspeed=config.DEFAULT_AIRSPEED)
    wait_for_arrival(vehicle, second_post, "Second Post", tolerance=1.0)

    logging.info("Proceeding to landing zone.")
    landing_zone_loc = LocationGlobalRelative(*config.LANDING_ZONE)
    vehicle.simple_goto(landing_zone_loc, groundspeed=config.DEFAULT_AIRSPEED)
    wait_for_arrival(vehicle, landing_zone_loc, "Landing Zone", tolerance=1.0)
    
    logging.info("--- Mission 2 Complete ---")