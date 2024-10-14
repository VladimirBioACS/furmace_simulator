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
import json
from enum import Enum

# Project local imports
import modules.mqtt_interface as mqtt_interface
from modules.mqtt_interface import MqttStatusRetCodes as retCodes
import modules.sensors
import modules.actuator
from modules.log_manager import log_manager
from modules.log_manager import logger

# 3d party imports
from pyfiglet import Figlet

# Variables
LOG_FILE_PATH = 'logs/log.log'
LOG_FILTER_NAME = 'simulator_log'
LOG_LEVEL = 'INFO'
LOG_ROTATION_SIZE = '10 MB'
LOG_COMPRESSION_METHOD = 'tar.gz'
LOG_RETENTION = 3

sensor_readings_delay = 0.2
loop_range = 100
calibration_process_start_flag = 0
manufacturing_process_start_flag = 0

mqtt_service_topic = 'simulator/status'

sensor_mqtt_topic_send_list = {
    'thermal_sensor':'sensors/thremal/send',
    'voltage_sensor':'sensor/voltage/send',
    'actuator_sensor':'actuator/send'
}

sensor_mqtt_topic_recv_list = {
    'actuator':'actuator/receive'
}

# Configurations
config_file = open('config/mqtt_conf.json', 'r')
config = json.loads(config_file.read())
config_file.close()

# Enums
class SensorDirections(Enum):
    sensor_direction_down = 0
    sensor_direction_up = 1
    sensor_direction_reset = 2
    sensor_direction_unknown = 3


class ProcessStatus(Enum):
    calibration_process_begin = 0x0B
    calibration_process_finished = 0x0C
    calibration_process_unexpected_error = 0xF1
    manufacturing_process_begin = 0xB0
    manufacturing_process_finished = 0xC0
    manufacturing_process_unexpected_error = 0xF2

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

pot_temp_sensor = modules.sensors.Sensor(
    sensor_label="pot_thermal_couple",
    sensor_number=1,
    sensor_bot_boundry=25,
    sensor_top_boundry=1700
)

alloy_temp_sensor = modules.sensors.Sensor(
    sensor_label="alloy_thermal_couple",
    sensor_number=1,
    sensor_bot_boundry=25,
    sensor_top_boundry=1650
)

coolant_temp_sensor = modules.sensors.Sensor(
    sensor_label="coolant_thermal_couple",
    sensor_number=1,
    sensor_bot_boundry=25,
    sensor_top_boundry=750
)

cold_weld_thermalcouple_sensor = modules.sensors.Sensor(
    sensor_label="cold_weld_thermalcouple_sensor",
    sensor_number=1,
    sensor_bot_boundry=15,
    sensor_top_boundry=25
)

room_temp_sensor = modules.sensors.Sensor(
    sensor_label="room_temp",
    sensor_number=1,
    sensor_bot_boundry=15,
    sensor_top_boundry=25
)

ppf_one_sensor = modules.sensors.Sensor(
    sensor_label="ppf_one_sensor",
    sensor_number=1,
    sensor_bot_boundry=20,
    sensor_top_boundry=1623
)

ppf_two_sensor = modules.sensors.Sensor(
    sensor_label="ppf_two_sensor",
    sensor_number=1,
    sensor_bot_boundry=20,
    sensor_top_boundry=1624
)

ppf_three_sensor = modules.sensors.Sensor(
    sensor_label="ppf_three_sensor",
    sensor_number=1,
    sensor_bot_boundry=20,
    sensor_top_boundry=1625
)

ppf_four_sensor = modules.sensors.Sensor(
    sensor_label="ppf_four_sensor",
    sensor_number=1,
    sensor_bot_boundry=20,
    sensor_top_boundry=1626
)

ppf_five_sensor = modules.sensors.Sensor(
    sensor_label="ppf_five_sensor",
    sensor_number=1,
    sensor_bot_boundry=20,
    sensor_top_boundry=1625
)


log_manager_obj.create_logger()
figlet = Figlet(font='slant')


def temp_sensor_control(sensor: modules.sensors.Sensor, dir: int, val: int) -> int:

    if dir == SensorDirections.sensor_direction_up.value:
        sensor.set_sensor_value(val)
    elif dir == SensorDirections.sensor_direction_down.value:
        sensor.set_sensor_value(val)
    elif dir == SensorDirections.sensor_direction_reset.value:
        sensor.reset_sensor_value()

    return sensor.read_sensor_value()


def temp_sensor_reset_all() -> None:
    pot_temp_sensor.reset_sensor_value()
    alloy_temp_sensor.reset_sensor_value()
    coolant_temp_sensor.reset_sensor_value()
    cold_weld_thermalcouple_sensor.reset_sensor_value()
    room_temp_sensor.reset_sensor_value()
    ppf_one_sensor.reset_sensor_value()
    ppf_two_sensor.reset_sensor_value()
    ppf_three_sensor.reset_sensor_value()
    ppf_four_sensor.reset_sensor_value()


def calibrate_temp_sensors(value: int, dir: SensorDirections) -> list:
    sensor_data_list = {}

    pot_temp_value = temp_sensor_control(sensor=pot_temp_sensor,
                                         dir=dir,
                                         val=value)

    alloy_temp_value = temp_sensor_control(sensor=alloy_temp_sensor,
                                           dir=dir,
                                           val=value)

    coolant_temp_value = temp_sensor_control(sensor=coolant_temp_sensor,
                                             dir=dir,
                                             val=value)

    sensor_data_list = {
        pot_temp_sensor.sensor_label:pot_temp_value,
        alloy_temp_sensor.sensor_label:alloy_temp_value,
        coolant_temp_sensor.sensor_label:coolant_temp_value
    }

    return sensor_data_list


def temp_sensors_mock() -> None:
    pot_thermal_couple = random.randint(1700, 1715)
    alloy_thermal_couple = random.randint(1611, 1630)
    coolant_thermal_couple = random.randint(740, 751)
    cold_weld_thermalcouple_sensor = random.randint(24, 26)
    room_temp = random.randint(24, 26)
    ppf_one_sensor = random.randint(1620, 1640)
    ppf_two_sensor = random.randint(1620, 1640)
    ppf_three_sensor = random.randint(1620, 1640)
    ppf_four_sensor = random.randint(1620, 1640)
    ppf_five_sensor = random.randint(1620, 1640)

    sensor_data_list = {
        "pot_thermal_couple":pot_thermal_couple,
        "alloy_thermal_couple":alloy_thermal_couple,
        "coolant_thermal_couple":coolant_thermal_couple,
        "cold_weld_thermalcouple_sensor":cold_weld_thermalcouple_sensor,
        "room_temp":room_temp,
        "ppf_one_sensor":ppf_one_sensor,
        "ppf_two_sensor":ppf_two_sensor,
        "ppf_three_sensor":ppf_three_sensor,
        "ppf_four_sensor":ppf_four_sensor,
        "ppf_five_sensor":ppf_five_sensor
    }

    data = json.dumps(sensor_data_list)
    mqtt_client.send_message(topic=sensor_mqtt_topic_send_list['thermal_sensor'],
                                msg=str(data))
    sleep(1)


def start_calibration_process() -> bool:
    for val in range(400):
        sensor_data_list = {}
        value = random.randint(1, 10)
        pot_temp_value = temp_sensor_control(sensor=pot_temp_sensor,
                                        dir=SensorDirections.sensor_direction_up.value,
                                        val=value)
        value = random.randint(1, 10)
        alloy_temp_value = temp_sensor_control(sensor=alloy_temp_sensor,
                                        dir=SensorDirections.sensor_direction_up.value,
                                        val=value)

        value = random.randint(1, 10)
        coolant_temp_value = temp_sensor_control(sensor=coolant_temp_sensor,
                                        dir=SensorDirections.sensor_direction_up.value,
                                        val=value)

        value = random.randint(1, 10)
        cold_weld_sensor_value = temp_sensor_control(sensor=cold_weld_thermalcouple_sensor,
                                        dir=SensorDirections.sensor_direction_up.value,
                                        val=value)

        value = random.randint(1, 10)
        room_temp_sensor_value = temp_sensor_control(sensor=room_temp_sensor,
                                        dir=SensorDirections.sensor_direction_up.value,
                                        val=value)

        value = random.randint(1, 10)
        ppf_one_value = temp_sensor_control(sensor=ppf_one_sensor,
                                        dir=SensorDirections.sensor_direction_up.value,
                                        val=value)

        value = random.randint(1, 10)
        ppf_two_value = temp_sensor_control(sensor=ppf_two_sensor,
                                        dir=SensorDirections.sensor_direction_up.value,
                                        val=value)

        value = random.randint(1, 10)
        ppf_three_value = temp_sensor_control(sensor=ppf_three_sensor,
                                        dir=SensorDirections.sensor_direction_up.value,
                                        val=value)

        value = random.randint(1, 10)
        ppf_four_value = temp_sensor_control(sensor=ppf_four_sensor,
                                        dir=SensorDirections.sensor_direction_up.value,
                                        val=value)

        value = random.randint(1, 10)
        ppf_five_value = temp_sensor_control(sensor=ppf_five_sensor,
                                        dir=SensorDirections.sensor_direction_up.value,
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


def mqtt_callback_func(client, userdata, message) -> None:
    global calibration_process_start_flag
    global manufacturing_process_start_flag

    recv_message = message.payload.decode()

    logger.info(f"Message Recieved from Server: {recv_message}")
    logger.info(f"Userdata: {userdata}")

    if int(recv_message) == ProcessStatus.calibration_process_begin.value:
        logger.info("Calibration Process started")
        mqtt_client.send_message(topic=mqtt_service_topic,
                                 msg="Calibration process started")
        calibration_process_start_flag = 1

    if int(recv_message) == ProcessStatus.manufacturing_process_begin.value:
        logger.info("Manufacturing Process started")
        mqtt_client.send_message(topic=mqtt_service_topic,
                                 msg="Manufacturing process started")
        manufacturing_process_start_flag = 1


def main() -> None:
    # logger.disable("mqtt_interface")
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
                mqtt_client.send_message(msg=str(ProcessStatus.calibration_process_finished.value),
                                         topic=mqtt_service_topic)

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




# Temperature gradient calculation formula (for alloy sample):
# dT/dz = (T2 - T1) / (z2 - z1)
# T1 - temperature at start point
# T2 - temperature at end point
# z1 - distance start point
# z2 - distance end point
# For this case we can assume that we can have many distance points between thermal couple (5 for example), so:
# we should use something like: Gradient = Sum ((T2 - T1) /(z2 - z1), (Tx - Ty) / (zx - zy))

# Same can be used for pot temperature and coolant temperature gradient calculation