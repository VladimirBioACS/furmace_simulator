import sys
import os

class Actuator:
    """
    Actuator class
    """

    def __init__(self,
                 actuator_label: str,
                 actuator_bot_speed: int,
                 actuator_top_speed: int) -> None:

        self.actuator_label = actuator_label
        self.actuator_bot_speed = actuator_bot_speed
        self.actuator_top_speed = actuator_top_speed
        self.actuator_max_position = 150
        self.actuator_min_position = 0
        self.actuator_position = self.actuator_min_position


    # Public methods
    def set_actuator_position(self, speed: int, position: int, dir: int) -> int:
        """
        Sets actuator emulator physical position

        Args:
            speed (int): actuator speed
            position (int): actuator position
            dir (int): actuator direction

        Returns:
            int: _description_
        """

        if self.actuator_position <= self.actuator_max_position and \
        self.actuator_position >= self.actuator_min_position:

            if dir == 0:
                self.actuator_position = self.actuator_position - position
            elif dir == 1:
                self.actuator_position = self.actuator_position + position


            return self.actuator_position


    def reset_actuator_postion(self, position: int) -> None:
        """
        Resets actuator position

        Args:
            position (int): actuator position
        """

        self.actuator_position = self.actuator_min_position


    def get_actuator_label(self) -> str:
        """
        Get actuator name (lable)

        Returns:
            str: actuator lable
        """

        return self.actuator_label
