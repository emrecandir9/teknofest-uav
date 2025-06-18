import argparse
import logging
import time
from threading import Event

from src.drone.connection import connect_vehicle
from src.drone.actions import arm_and_takeoff, land
from src.vision.target_detector import TargetDetector
from src.missions.mission_control import run_mission_2
import src.config as config

def main():
    """
    The main entry point for the autonomous drone mission.
    """
    parser = argparse.ArgumentParser(description='Main controller for the Teknofest Drone.')
    parser.add_argument('--connect', default=config.CONNECTION_STRING,
                        help="Vehicle connection string. Use 'tcp:127.0.0.1:5762' for SITL.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    vehicle = connect_vehicle(args.connect, config.BAUDRATE)
    if not vehicle:
        return

    stop_event = Event()

    try:
        detector = TargetDetector(config, stop_event)
        detector.start()
        
        arm_and_takeoff(vehicle, config.TARGET_ALTITUDE)
        
        run_mission_2(vehicle, detector, config)

        land(vehicle)

    except KeyboardInterrupt:
        logging.warning("Keyboard interrupt detected. Initiating landing.")
        land(vehicle)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        land(vehicle)
    finally:
        logging.info("Shutting down...")
        stop_event.set()
        if vehicle:
            vehicle.close()
        logging.info("Vehicle disconnected. Program finished.")

if __name__ == "__main__":
    main()