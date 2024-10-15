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
mqtt_actuator_topic = 'simulator/furnace_actuator/actuator_one'

# Configurations
config_file = open('config/mqtt_conf.json', 'r', encoding='utf-8')
config = json.loads(config_file.read())
config_file.close()

# Variables
LOG_FILE_PATH = 'logs/furnace_actuator_sim_log.log'
LOG_FILTER_NAME = 'furnace_actuator_simulator_log'
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
    actuator_label="furnace_actuator",
    actuator_bot_speed=0,
    actuator_top_speed=400
)


log_manager_obj.create_logger()
figlet = Figlet(font='slant')


def main() -> None:
    """
    main function
    """

    pass


if __name__ == "__main__":
    main()
