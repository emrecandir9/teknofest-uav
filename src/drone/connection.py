import logging
from dronekit import connect, Vehicle

def connect_vehicle(connection_string: str, baud: int) -> Vehicle:
    """
    Connects to the vehicle and waits for it to be ready.
    Returns the vehicle object.
    """
    logging.info(f"Connecting to vehicle on: {connection_string}")
    try:
        vehicle = connect(connection_string, baud=baud, wait_ready=False)
        vehicle.wait_ready(True, timeout=60)
        logging.info("Vehicle connected and ready.")
        logging.info(f"Firmware: {vehicle.version}")
        logging.info(f"GPS: {vehicle.gps_0}")
        logging.info(f"Attitude: {vehicle.attitude}")
        return vehicle
    except Exception as e:
        logging.error(f"Failed to connect to vehicle: {e}")
        return None