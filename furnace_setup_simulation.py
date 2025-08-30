#    ______  _____  _  _____  _________   __________  _____  ____   ___ __________  ___
#   / __/ / / / _ \/ |/ / _ |/ ___/ __/  / __/  _/  |/  / / / / /  / _ /_  __/ __ \/ _ \
#  / _// /_/ / , _/    / __ / /__/ _/   _\ \_/ // /|_/ / /_/ / /__/ __ |/ / / /_/ / , _/
# /_/  \____/_/|_/_/|_/_/ |_\___/___/__/___/___/_/  /_/\____/____/_/ |_/_/  \____/_/|_|
#                                  /___/
#
#

# General python imports
import json
from time import sleep
import random
import sys
from enum import Enum

# Project local imports
from modules.mqtt_interface import MqttInterface
from modules.sensors import SensorDirections, Sensor
from modules.log_manager import LogManager
from modules.log_manager import logger

# 3d party imports
try:
    from pyfiglet import Figlet
except ImportError:
    print("Module pyfiglet not found. Please use pip install -r requirements.txt")
    sys.exit(1)


CONFIG_PATH = 'config/mqtt_conf.json'

# Log settings
LOG_FILE_PATH = 'logs/log.log'
LOG_FILTER_NAME = 'simulator_log'
LOG_LEVEL = 'INFO'
LOG_ROTATION_SIZE = '10 MB'
LOG_COMPRESSION_METHOD = 'tar.gz'
LOG_RETENTION = 3

# MQTT service topic
MQTT_SERVICE_TOPIC = 'simulator/status'

# Global flags
calibration_process_start_flag = 0
manufacturing_process_start_flag = 0

sensor_mqtt_topic_send_list = {
    'thermal_sensor':'sensors/thremal/send',
    'voltage_sensor':'sensor/voltage/send',
    'actuator_sensor':'actuator/send'
}

sensor_mqtt_topic_recv_list = {
    'actuator':'actuator/receive'
}

# Load config file
try:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as config_file:
        config = json.loads(config_file.read())
        config_file.close()
except FileNotFoundError:
    print(f"Config file {CONFIG_PATH} not found!")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Config file {CONFIG_PATH} is not valid JSON!")
    sys.exit(1)

# Enums
class ProcessStatus(Enum):
    """
    Process status ENUM

    Args:
        Enum (enum): status codes
    """

    CALIBRATION_PROCESS_BEGIN       = 0x0B
    CALIBRATION_PROCESS_FINISHED    = 0x0C
    CALIBRATION_PROCESS_ERROR       = 0xF1
    MANUFACTURING_PROCESS_BEGIN     = 0xB0
    MANUFACTURING_PROCESS_FINISHED  = 0xC0
    MANUFACTURING_PROCESS_ERROR     = 0xF2

# Classes
# logger object configuration
log_manager_obj = LogManager(
    log_file_path=LOG_FILE_PATH,
    log_filter_name=LOG_FILTER_NAME,
    log_level=LOG_LEVEL,
    log_rotation_size=LOG_ROTATION_SIZE,
    log_compression_method=LOG_COMPRESSION_METHOD,
    log_retention=LOG_RETENTION
)

mqtt_client = MqttInterface(
    broker=config['broker'],
    port=config['port'],
    username=config['username'],
    password=config['password'],
    alias=config['alias'],
    service_topic=MQTT_SERVICE_TOPIC
)

pot_temp_sensor = Sensor(
    sensor_label="pot_thermal_couple",
    sensor_number=1,
    sensor_bot_boundry=25,
    sensor_top_boundry=1700
)

alloy_temp_sensor = Sensor(
    sensor_label="alloy_thermal_couple",
    sensor_number=1,
    sensor_bot_boundry=25,
    sensor_top_boundry=1650
)

coolant_temp_sensor = Sensor(
    sensor_label="coolant_thermal_couple",
    sensor_number=1,
    sensor_bot_boundry=25,
    sensor_top_boundry=750
)

cold_weld_thermalcouple_sensor = Sensor(
    sensor_label="cold_weld_thermalcouple_sensor",
    sensor_number=1,
    sensor_bot_boundry=15,
    sensor_top_boundry=25
)

room_temp_sensor = Sensor(
    sensor_label="room_temp",
    sensor_number=1,
    sensor_bot_boundry=15,
    sensor_top_boundry=25
)

ppf_one_sensor = Sensor(
    sensor_label="ppf_one_sensor",
    sensor_number=1,
    sensor_bot_boundry=20,
    sensor_top_boundry=1623
)

ppf_two_sensor = Sensor(
    sensor_label="ppf_two_sensor",
    sensor_number=1,
    sensor_bot_boundry=20,
    sensor_top_boundry=1624
)

ppf_three_sensor = Sensor(
    sensor_label="ppf_three_sensor",
    sensor_number=1,
    sensor_bot_boundry=20,
    sensor_top_boundry=1625
)

ppf_four_sensor = Sensor(
    sensor_label="ppf_four_sensor",
    sensor_number=1,
    sensor_bot_boundry=20,
    sensor_top_boundry=1626
)

ppf_five_sensor = Sensor(
    sensor_label="ppf_five_sensor",
    sensor_number=1,
    sensor_bot_boundry=20,
    sensor_top_boundry=1625
)


log_manager_obj.create_logger()
figlet = Figlet(font='slant')


def temp_sensor_control(sensor: Sensor, direction: int, val: int) -> int:
    """
    Controls temperature sensor emulator

    Args:
        sensor (modules.sensors.Sensor): sensor class
        dir (int): sensor value direction
        val (int): sensor value

    Returns:
        int: value
    """

    if direction == SensorDirections.SENSOR_VALUE_INCREASE.value:
        sensor.set_sensor_value(val)
    elif direction == SensorDirections.SENSOR_VALUE_DECREASE.value:
        sensor.set_sensor_value(val)
    elif direction == SensorDirections.SENSOR_VALUE_RESET.value:
        sensor.reset_sensor_value()

    return sensor.read_sensor_value()


def temp_sensor_reset_all() -> None:
    """
    Reset sensor emulator
    """

    pot_temp_sensor.reset_sensor_value()
    alloy_temp_sensor.reset_sensor_value()
    coolant_temp_sensor.reset_sensor_value()
    cold_weld_thermalcouple_sensor.reset_sensor_value()
    room_temp_sensor.reset_sensor_value()
    ppf_one_sensor.reset_sensor_value()
    ppf_two_sensor.reset_sensor_value()
    ppf_three_sensor.reset_sensor_value()
    ppf_four_sensor.reset_sensor_value()


def calibrate_temp_sensors(value: int, direction: SensorDirections) -> list:
    """
    Calibration of the temperature sensor emulator

    Args:
        value (int): sensor value
        dir (SensorDirections): sensor direction

    Returns:
        list: list of sensor data
    """

    sensor_data_list = {}

    pot_temp_value = temp_sensor_control(sensor=pot_temp_sensor,
                                        direction=direction,
                                        val=value)

    alloy_temp_value = temp_sensor_control(sensor=alloy_temp_sensor,
                                           direction=direction,
                                           val=value)

    coolant_temp_value = temp_sensor_control(sensor=coolant_temp_sensor,
                                            direction=direction,
                                            val=value)

    sensor_data_list = {
        pot_temp_sensor.sensor_label:pot_temp_value,
        alloy_temp_sensor.sensor_label:alloy_temp_value,
        coolant_temp_sensor.sensor_label:coolant_temp_value
    }

    return sensor_data_list


def temp_sensors_mock() -> None:
    """
    Create sensor mock
    """

    pot_thermal_couple_val = random.randint(1700, 1715)
    alloy_thermal_couple_val = random.randint(1611, 1630)
    coolant_thermal_couple_val = random.randint(740, 751)
    cold_weld_therm_sensor_val = random.randint(24, 26)
    room_temp_val = random.randint(24, 26)
    ppf_one_sensor_val = random.randint(1620, 1640)
    ppf_two_sensor_val = random.randint(1620, 1640)
    ppf_three_sensor_val = random.randint(1620, 1640)
    ppf_four_sensor_val = random.randint(1620, 1640)
    ppf_five_sensor_val = random.randint(1620, 1640)

    sensor_data_list = {
        "pot_thermal_couple":pot_thermal_couple_val,
        "alloy_thermal_couple":alloy_thermal_couple_val,
        "coolant_thermal_couple":coolant_thermal_couple_val,
        "cold_weld_thermalcouple_sensor":cold_weld_therm_sensor_val,
        "room_temp":room_temp_val,
        "ppf_one_sensor":ppf_one_sensor_val,
        "ppf_two_sensor":ppf_two_sensor_val,
        "ppf_three_sensor":ppf_three_sensor_val,
        "ppf_four_sensor":ppf_four_sensor_val,
        "ppf_five_sensor":ppf_five_sensor_val
    }

    data = json.dumps(sensor_data_list)
    mqtt_client.send_message(topic=sensor_mqtt_topic_send_list['thermal_sensor'],
                                msg=str(data))
    sleep(1)


def start_calibration_process() -> bool:
    """
    Emulate furnace callibration process

    Returns:
        bool: calibration status
    """

    for _ in range(400):
        sensor_data_list = {}
        value = random.randint(1, 10)
        pot_temp_value = temp_sensor_control(sensor=pot_temp_sensor,
                                        direction=SensorDirections.SENSOR_VALUE_INCREASE.value,
                                        val=value)
        value = random.randint(1, 10)
        alloy_temp_value = temp_sensor_control(sensor=alloy_temp_sensor,
                                        direction=SensorDirections.SENSOR_VALUE_INCREASE.value,
                                        val=value)

        value = random.randint(1, 10)
        coolant_temp_value = temp_sensor_control(sensor=coolant_temp_sensor,
                                        direction=SensorDirections.SENSOR_VALUE_INCREASE.value,
                                        val=value)

        value = random.randint(1, 10)
        cold_weld_sensor_value = temp_sensor_control(sensor=cold_weld_thermalcouple_sensor,
                                        direction=SensorDirections.SENSOR_VALUE_INCREASE,
                                        val=value)

        value = random.randint(1, 10)
        room_temp_sensor_value = temp_sensor_control(sensor=room_temp_sensor,
                                        direction=SensorDirections.SENSOR_VALUE_INCREASE,
                                        val=value)

        value = random.randint(1, 10)
        ppf_one_value = temp_sensor_control(sensor=ppf_one_sensor,
                                        direction=SensorDirections.SENSOR_VALUE_INCREASE,
                                        val=value)

        value = random.randint(1, 10)
        ppf_two_value = temp_sensor_control(sensor=ppf_two_sensor,
                                        direction=SensorDirections.SENSOR_VALUE_INCREASE,
                                        val=value)

        value = random.randint(1, 10)
        ppf_three_value = temp_sensor_control(sensor=ppf_three_sensor,
                                        direction=SensorDirections.SENSOR_VALUE_INCREASE.value,
                                        val=value)

        value = random.randint(1, 10)
        ppf_four_value = temp_sensor_control(sensor=ppf_four_sensor,
                                        direction=SensorDirections.SENSOR_VALUE_INCREASE.value,
                                        val=value)

        value = random.randint(1, 10)
        ppf_five_value = temp_sensor_control(sensor=ppf_five_sensor,
                                        direction=SensorDirections.SENSOR_VALUE_INCREASE.value,
                                        val=value)

        sensor_data_list = {
            pot_temp_sensor.sensor_label:pot_temp_value,
            alloy_temp_sensor.sensor_label:alloy_temp_value,
            coolant_temp_sensor.sensor_label:coolant_temp_value,
            cold_weld_thermalcouple_sensor.sensor_label:cold_weld_sensor_value,
            room_temp_sensor.sensor_label:room_temp_sensor_value,
            ppf_one_sensor.sensor_label:ppf_one_value,
            ppf_two_sensor.sensor_label:ppf_two_value,
            ppf_three_sensor.sensor_label:ppf_three_value,
            ppf_four_sensor.sensor_label:ppf_four_value,
            ppf_five_sensor.sensor_label:ppf_five_value
        }

        data = json.dumps(sensor_data_list)
        mqtt_client.send_message(topic=sensor_mqtt_topic_send_list['thermal_sensor'],
                                msg=str(data))
        sleep(0.1)

    return True


def mqtt_callback_func(_, userdata, message) -> None:
    """
    MQTT callback function

    Args:
        client (_type_): MQTT client
        userdata (_type_): MQTT userdata
        message (_type_): MQTT message
    """

    global calibration_process_start_flag
    global manufacturing_process_start_flag

    recv_message = message.payload.decode()

    logger.info(f"Message Recieved from Server: {recv_message}")
    logger.info(f"Userdata: {userdata}")

    if int(recv_message) == ProcessStatus.CALIBRATION_PROCESS_BEGIN.value:
        logger.info("Calibration Process started")
        mqtt_client.send_message(topic=MQTT_SERVICE_TOPIC,
                                 msg="Calibration process started")
        calibration_process_start_flag = 1

    if int(recv_message) == ProcessStatus.MANUFACTURING_PROCESS_BEGIN.value:
        logger.info("Manufacturing Process started")
        mqtt_client.send_message(topic=MQTT_SERVICE_TOPIC,
                                 msg="Manufacturing process started")
        manufacturing_process_start_flag = 1


def main() -> None:
    """
    Main function
    """

    global calibration_process_start_flag
    global manufacturing_process_start_flag

    try:
        print(figlet.renderText('Furnace Simulator'))

        mqtt_client.init_client(topic=sensor_mqtt_topic_recv_list['actuator'],
                        callback_func=mqtt_callback_func)

        temp_sensor_reset_all()

        calibration_state = False

        while True:
            if calibration_process_start_flag == 1:
                calibration_state = start_calibration_process()
                calibration_process_start_flag = 0
                logger.info("Calibration process finished!")
                mqtt_client.send_message(msg=str(ProcessStatus.CALIBRATION_PROCESS_FINISHED.value),
                                         topic=MQTT_SERVICE_TOPIC)

            if calibration_state:
                temp_sensors_mock()

    except KeyboardInterrupt:
        mqtt_client.close()
        logger.info("Exit through keyboard interrupt")
        sys.exit(0)

    except OSError:
        mqtt_client.close()
        logger.error("OS error occured")
        sys.exit(1)

if __name__ == "__main__":
    main()
