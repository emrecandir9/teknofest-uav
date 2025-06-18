import time
import logging
from dronekit import Vehicle, VehicleMode

def arm_and_takeoff(vehicle: Vehicle, target_altitude: float):
    """
    Arms the vehicle and takes off to a specified altitude.
    """
    logging.info("Performing pre-arm checks...")
    while not vehicle.is_armable:
        logging.info("Waiting for vehicle to become armable...")
        time.sleep(1)
    
    logging.info("Arming motors...")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        logging.info("Waiting for arming...")
        time.sleep(1)

    logging.info(f"Taking off to {target_altitude} meters!")
    vehicle.simple_takeoff(target_altitude)

    # Wait until the vehicle reaches a safe height
    while True:
        current_altitude = vehicle.location.global_relative_frame.alt
        logging.info(f"Altitude: {current_altitude:.2f}m")
        if current_altitude >= target_altitude * 0.90:
            logging.info("Reached target altitude.")
            break
        time.sleep(1)

def land(vehicle: Vehicle):
    """
    Sets the vehicle to LAND mode and waits for it to land.
    """
    logging.info("Setting mode to LAND...")
    vehicle.mode = VehicleMode("LAND")
    
    while True:
        current_altitude = vehicle.location.global_relative_frame.alt
        if current_altitude <= 0.6: # Consider landed if altitude is very low
            logging.info("Vehicle has landed.")
            break
        logging.info(f"Waiting for landing... Current altitude: {current_altitude:.2f}m")
        time.sleep(2)