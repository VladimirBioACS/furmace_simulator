# General python imports
import json
import sys
from time import sleep

# Local module imports
import modules.actuator as act
import modules.mqtt_interface as mqtt_interface
# from modules.mqtt_interface import MqttStatusRetCodes as retCodes
from modules.log_manager import log_manager
from modules.log_manager import logger

# 3d party imports
from pyfiglet import Figlet

# MQTT topics
mqtt_service_topic = 'simulator/water_level/service'
mqtt_tank_topic = 'simulator/water_level/tank'
mqtt_tank_valve_status_ctrl_topic = 'simulator/water_level/status_control'

# Configurations
config_file = open('config/mqtt_conf.json', 'r', encoding='utf-8')
config = json.loads(config_file.read())
config_file.close()

# Variables
LOG_FILE_PATH = 'logs/tank_sim_log.log'
LOG_FILTER_NAME = 'tank_simulator_log'
LOG_LEVEL = 'INFO'
LOG_ROTATION_SIZE = '10 MB'
LOG_COMPRESSION_METHOD = 'tar.gz'
LOG_RETENTION = 3

# Classes
# logger object configuration
log_manager_obj = log_manager(
    log_file_path=LOG_FILE_PATH,
    log_filter_name=LOG_FILTER_NAME,
    log_level=LOG_LEVEL,
    log_rotation_size=LOG_ROTATION_SIZE,
    log_compression_method=LOG_COMPRESSION_METHOD,
    log_retention=LOG_RETENTION
)


mqtt_client = mqtt_interface.MQTT_interface(
    broker=config['broker'],
    port=config['port'],
    username=config['username'],
    password=config['password'],
    alias=config['alias'],
    service_topic=mqtt_service_topic
)


actuator = act.Actuator(
    actuator_label="Water_Level",
    actuator_bot_speed=0,
    actuator_top_speed=100
)


log_manager_obj.create_logger()
figlet = Figlet(font='slant')


def actuator_dir_up(level: int) -> int:
    """
    Increase actuator value

    Args:
        level (int): level of the actuator

    Returns:
        int: actuator position
    """

    pos = actuator.set_actuator_position(speed=0,
                                        position=level,
                                        dir=1)
    return pos


def actuator_dir_down(level: int) -> int:
    """
    Decrease actuator value

    Args:
        level (int): level of the actuator

    Returns:
        int: actuator position
    """

    pos = actuator.set_actuator_position(speed=0,
                                        position=level,
                                        dir=0)
    return pos


def reset_simulation() -> None:
    """
    Reset simulation parameters
    """

    mqtt_client.send_message(msg="0",
                            topic=mqtt_tank_topic)
    mqtt_client.send_message(msg="Disabled",
                            topic=mqtt_tank_valve_status_ctrl_topic)


def mqtt_callback(client, userdata, message) -> None:
    """
    MQTT callback function

    Args:
        client (_type_): MQTT client
        userdata (_type_): MQTT userdata
        message (_type_): MQTT message
    """

    logger.info("Callback occured")


def main():
    """
    Main function
    """

    print(figlet.renderText('Tank filling Simulator'))

    mqtt_client.init_client(topic=mqtt_service_topic,
                            callback_func=mqtt_callback)
    logger.info("MQTT brocker connected!")

    user_input = input("Do you want to start the tank filling simulation? (y/n): ")

    if user_input == 'y':
        logger.info("[PROCESS STARTED]")
        logger.info("[RESET THE SIMULATION]")
        reset_simulation()
        sleep(2)

        logger.info("The process of filling the tank with liquid has begun")
        logger.info("Open the valve")
        logger.info("Set operation status as: [ENABLED]")
        mqtt_client.send_message(msg="Enabled",
                            topic=mqtt_tank_valve_status_ctrl_topic)

        for _ in range (125):
            level = actuator_dir_up(1)
            logger.info(f"Process started. Liquid level: {level} L")
            mqtt_client.send_message(msg=str(level),
                            topic=mqtt_tank_topic)
            sleep(0.3)

        logger.info("Tank filled with liquid")
        logger.info(f"Liquid level: {level}")
        logger.info(2)

        logger.info("The process of draining the liquid has begun")

        for _ in range (125):
            level = actuator_dir_down(1)
            logger.info(f"Process started. Liquid level: {level} L")
            mqtt_client.send_message(msg=str(level),
                            topic=mqtt_tank_topic)
            sleep(0.3)

        logger.info("Tank drained")
        logger.info(f"Liquid level: {level}")

        logger.info("[PROCESS COMPLETED]")
        logger.info("Close the valve")
        logger.info("Set operation status as: [DISABLED]")
        mqtt_client.send_message(msg="Disabled",
                            topic=mqtt_tank_valve_status_ctrl_topic)
        mqtt_client.close()

    else:
        logger.info("Process terminated")
        mqtt_client.close()
        sys.exit(0)

if __name__ == "__main__":
    main()
