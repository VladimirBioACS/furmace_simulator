from enum import Enum


class SensorDirections(Enum):
    """
    Sensor direction enum

    Args:
        Enum (enum): sensor directions enums
    """

    SENSOR_VALUE_INCREASE   = 0
    SENSOR_VALUE_DECREASE   = 1
    SENSOR_VALUE_RESET      = 2
    SENSOR_VALUE_UNKNOWN    = 3


class Sensor:
    """
    Sensor class
    """

    def __init__(self,
                 sensor_label: str,
                 sensor_number: int,
                 sensor_bot_boundry,
                 sensor_top_boundry) -> None:
        """Sensor class constructor

        Args:
            sensor_label (str): label of the specific sensor
            sensor_number (int): number of the specific sensor
            sensor_bot_boundry (_type_): sensor min value
            sensor_top_boundry (_type_): sensor max value
        """

        self.sensor_label = sensor_label
        self.sensor_number = sensor_number
        self.sensor_bot_boundry = sensor_bot_boundry
        self.sensor_top_boundry = sensor_top_boundry

        self.sensor_readings = sensor_bot_boundry


    # Private methods
    def __filter_sensor_value(self) -> int:
        """
        Filter sensor value to be within the boundries
        """

        return self.sensor_readings


    # Public methods
    def read_sensor_value(self) -> int:
        """
        Read sensor value

        Returns:
            int: sensor value
        """

        return self.__filter_sensor_value()


    def set_sensor_value(self, val: int) -> None:
        """
        Set sensor value

        Args:
            val (int): sensor value
        """

        if  self.sensor_readings >= self.sensor_bot_boundry and  \
            self.sensor_readings <= self.sensor_top_boundry:

            self.sensor_readings = self.sensor_readings + val


    def reset_sensor_value(self) -> None:
        """
        Reset sensor value to the low boundry (default)
        """

        self.sensor_readings = self.sensor_bot_boundry
