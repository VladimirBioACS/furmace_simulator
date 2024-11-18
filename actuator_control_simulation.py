# General python imports
import json
import sys
import random
from enum import Enum
from time import sleep

# Local module imports
import modules.actuator as act
import modules.mqtt_interface as mqtt_interface
# from modules.mqtt_interface import MqttStatusRetCodes as retCodes
from modules.log_manager import log_manager
from modules.log_manager import logger

# 3d party imports
from pyfiglet import Figlet

# Enums
class AlloyStatus(Enum):
    """
    Alloy status enum

    Args:
        Enum (enum): status enums
    """

    EMPTY = 0
    FILLED = 1
    READY = 2


# MQTT topics
mqtt_service_topic = 'simulator/actuator/service'
mqtt_actuator_topic = 'furnace/set_actuator_pos'
mqtt_actuator_animation = 'furnace/set_element'
mqtt_allot_temp_simulation = 'furnace/alloy_temp'
mqtt_actuator_reset_topic = 'furnace/reset_scheme'

mqtt_actuator_status = 'furnace/act/status'
mqtt_actuator_alloy_temp = 'furnace/alloy_temp'

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


def mqtt_callback(client, userdata, message) -> None:
    """
    MQTT callback function

    Args:
        client (_type_): MQTT client
        userdata (_type_): MQTT userdata
        message (_type_): MQTT message
    """

    logger.info("Callback occured")


def reset_sheme(mqtt_client) -> None:
    data = "reset"
    mqtt_client.send_message(msg=data, topic=mqtt_actuator_reset_topic)


def generate_alloy_temp() -> int:
    return random.randint(1560, 1570)


def generate_alloy_cool_temp(temp: int) -> int:
    random_value_degree = random.randint(0, 10)
    return temp - random_value_degree


def set_alloy_state(mqtt_client, alloy_state: int) -> None:

    if AlloyStatus.EMPTY.value == alloy_state:
        json_data = [
                {
                    "command": "set_attribute",
                    "selector": "#FormOne",
                    "attributeName": "fill",
                    "attributeValue": "grey"
                },
                {
                    "command": "set_attribute",
                    "selector": "#FormTwo",
                    "attributeName": "fill",
                    "attributeValue": "grey"
                },
                {
                    "command": "update_style",
                    "selector": "#metalInPot",
                    "attributeName": "visibility",
                    "attributeValue": "visible"
                }
            ]
        data = json.dumps(json_data)
        mqtt_client.send_message(msg=data, topic=mqtt_actuator_animation)

    if AlloyStatus.FILLED.value == alloy_state:
        json_data = [
                {
                    "command": "set_attribute",
                    "selector": "#FormOne",
                    "attributeName": "fill",
                    "attributeValue": "orange"
                },
                {
                    "command": "set_attribute",
                    "selector": "#FormTwo",
                    "attributeName": "fill",
                    "attributeValue": "orange"
                },
                {
                    "command": "update_style",
                    "selector": "#metalInPot",
                    "attributeName": "visibility",
                    "attributeValue": "hidden"
                }
            ]
        data = json.dumps(json_data)
        mqtt_client.send_message(msg=data, topic=mqtt_actuator_animation)

    if AlloyStatus.READY.value == alloy_state:
        json_data = [
                {
                    "command": "set_attribute",
                    "selector": "#FormOne",
                    "attributeName": "fill",
                    "attributeValue": "blue"
                },
                {
                    "command": "set_attribute",
                    "selector": "#FormTwo",
                    "attributeName": "fill",
                    "attributeValue": "blue"
                },
                {
                    "command": "update_style",
                    "selector": "#metalInPot",
                    "attributeName": "visibility",
                    "attributeValue": "hidden"
                }
            ]
        data = json.dumps(json_data)
        mqtt_client.send_message(msg=data, topic=mqtt_actuator_animation)

    else:
        return 0


def set_heater(mqtt_client, heater_state: bool) -> None:

    if False == heater_state:
        json_data = [
            {
                "command": "update_style",
                "selector": "#heaterFlame",
                "attributeName": "visibility",
                "attributeValue": "hidden"
            }
        ]
        data = json.dumps(json_data)
        mqtt_client.send_message(msg=data, topic=mqtt_actuator_animation)

    if True == heater_state:
        json_data = [
            {
                "command": "update_style",
                "selector": "#heaterFlame",
                "attributeName": "visibility",
                "attributeValue": "visible"
            }
        ]
        data = json.dumps(json_data)
        mqtt_client.send_message(msg=data, topic=mqtt_actuator_animation)


def control_actuator_up(mqtt_client, temperature: int) -> None:
    """Set act pos

    Args:
        mqtt_client (_type_): MQTT client
    """
    step_amount = 51
    end_possition = -15

    for _ in range(step_amount):
        end_possition = end_possition - 1
        matrix = '1, 0, 0, 1, 39.395883, ' + str(end_possition)
        data_json = [{
            "command": "update_style",
            "selector": "#movingPart",
            "style": { "transform": "matrix(" + matrix + ")" }
        }]
        data = json.dumps(data_json)
        mqtt_client.send_message(msg=data, topic=mqtt_actuator_topic)

        temperature = generate_alloy_cool_temp(temp=temperature)
        mqtt_client.send_message(msg=str(temperature), topic=mqtt_actuator_alloy_temp)
        sleep(1.0)

    return temperature


def control_actuator_down(mqtt_client, temperature: int) -> None:
    """Set act pos

    Args:
        mqtt_client (_type_): MQTT client
    """
    step_amount = 51
    start_possition = -66
    temp = 0

    for _ in range(step_amount):
        start_possition = start_possition + 1
        matrix = '1, 0, 0, 1, 39.395883, ' + str(start_possition)
        data_json = [{
            "command": "update_style",
            "selector": "#movingPart",
            "style": { "transform": "matrix(" + matrix + ")" }
        }]
        data = json.dumps(data_json)

        mqtt_client.send_message(msg=data, topic=mqtt_actuator_topic)

        temp = generate_alloy_temp()
        mqtt_client.send_message(msg=str(temp), topic=mqtt_actuator_alloy_temp)
        sleep(1.0)

    return temp


def main() -> None:
    """
    main function
    """

    mqtt_client.init_client(topic=mqtt_service_topic,
                            callback_func=mqtt_callback)
    temperature = 0

    # Reset sheme
    # reset_sheme(mqtt_client=mqtt_client)
    # sleep(5.0)

    mqtt_client.send_message(msg="Запуск процесу", topic=mqtt_actuator_status)
    sleep(5.0)

    # Enable heater
    # mqtt_client.send_message(msg="Включено нагрівач охолоджувача", topic=mqtt_actuator_status)
    # set_heater(mqtt_client=mqtt_client, heater_state=True)
    # sleep(5.0)

    # # Set alloy state to EMPTY
    # set_alloy_state(mqtt_client=mqtt_client, alloy_state=AlloyStatus.EMPTY.value)
    # sleep(5.0)

    # # Set alloy state to FILLED
    # mqtt_client.send_message(msg="Включено підігрівач ємності охолоджувача", topic=mqtt_actuator_status)
    # set_alloy_state(mqtt_client=mqtt_client, alloy_state=AlloyStatus.FILLED.value)
    # sleep(5.0)

    # Set actuator positions DOWN
    mqtt_client.send_message(msg="Опускання механізму", topic=mqtt_actuator_status)
    temp_start = control_actuator_down(mqtt_client=mqtt_client, temperature=temperature)
    sleep(5.0)

    # Set alloy state to READY
    mqtt_client.send_message(msg="Процес завершено. Повернення установки в початковий стан", topic=mqtt_actuator_status)
    set_alloy_state(mqtt_client=mqtt_client, alloy_state=AlloyStatus.READY.value)
    # Enable heater
    set_heater(mqtt_client=mqtt_client, heater_state=False)
    sleep(5.0)

    # Set actuator positions UP
    temp_end = control_actuator_up(mqtt_client=mqtt_client, temperature=temp_start)
    sleep(5.0)

    # Reset sheme
    reset_sheme(mqtt_client=mqtt_client)

    print(f"Temp_start: {temp_start}")
    print(f"Temp end: {temp_end}")


if __name__ == "__main__":
    main()
