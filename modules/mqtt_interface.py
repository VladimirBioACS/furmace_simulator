from enum import Enum
from modules.log_manager import logger
try:
    import paho.mqtt.client as mqtt
    import paho.mqtt.publish as pub
except ImportError:
    logger.error("Module paho-mqtt not found. Please use pip install -r requirements.txt")
    raise


class MqttStatusCodes(Enum):
    """
    MQTT status codes

    Args:
        Enum (_type_): mqtt status codes enum
    """
    MQTT_NORMAL_DISCONNECT = 0x00
    MQTT_CONNECTED = 0x01
    MQTT_SUBSCRIBED = 0x02
    MQTT_UNSUBSCRIBED = 0x03
    MQTT_UNEXPECTED_DISCONNECT = 0xFF


class MqttStatusRetCodes(Enum):
    """
    MQTT status return codes

    Args:
        Enum (_type_): mqtt return codes enum
    """

    MQTT_RET_SUCCESS = 0
    MQTT_RET_FAILED = 1


# MQTT interface main class
class MqttInterface:
    """
    MQTT interface class
    """

    def __init__(self,
                 broker: str,
                 port: int,
                 username: str,
                 password: str,
                 alias: str,
                 service_topic) -> None:

        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.alias = alias
        self.client = None
        self.service_topic = service_topic


    # Private methods
    def __single_pub(self, message: str) -> None:
        """
        Single publish MQTT message

        Args:
            message (str): _description_
        """

        pub.single(topic=self.service_topic,
                   payload=str(message),
                   hostname=self.broker,
                   port=self.port,
                   retain=False,
                   qos=1,
                   keepalive=60,
                   auth=None,
                   tls=None,
                   protocol=mqtt.MQTTv311,
                   transport="tcp")


    def __on_connect(self, client, userdata, flags, rc: int) -> None:
        """
        On connect callback
        """

        if rc == 0:
            message_on_connect = {
                "status":MqttStatusCodes.MQTT_CONNECTED.value
            }
            self.__single_pub(message_on_connect)
            logger.info(f"conncted to: {self.broker} on port: {self.port}")
        else:
            logger.info(f"Error occured during connection to the: {self.broker}")


    def __on_disconnect(self, client, userdata, rc: int) -> None:
        """
        On disconnect callback

        Args:
            client (_type_): mqtt client
            userdata (_type_): mqtt user data
            rc (int): mqtt return code
        """

        status = None
        if rc != 0:
            status = MqttStatusCodes.MQTT_UNEXPECTED_DISCONNECT.value
        else:
            status = MqttStatusCodes.MQTT_NORMAL_DISCONNECT.value

        message_on_disconnect = {
            "status":status,
        }

        self.__single_pub(message_on_disconnect)
        logger.info(f"Disconnected from {self.broker} with code: {rc}")


    def __on_subscribe(self, client, userdata, mid, granted_qos: int) -> None:
        """
        On subscribe callback

        Args:
            client (_type_): mqtt client
            userdata (_type_): mqtt user data
            mid (_type_): mqtt message id
            granted_qos (int): mqtt granted qos
        """

        logger.info("Client successfully subscribed to the topic")
        logger.info(f"Granded QoS: {granted_qos}")
        logger.info(f"Userdata: {userdata}")


    def __on_unsubscribe(self, client, userdata, mid) -> None:
        """
        On unsubscribe callback

        Args:
            client (_type_): mqtt client
            userdata (_type_): mqtt user data
            mid (_type_): mqtt message id
        """

        message_on_unsub = {
            "status": MqttStatusCodes.MQTT_UNSUBSCRIBED.value
        }
        self.__single_pub(message=message_on_unsub)

        logger.info("Client successfully unsubscribed from the topic")
        logger.info(f"Userdata: {userdata}")


    # Public methods
    def init_client(self, topic: list, callback_func) -> None:
        """
        Init MQTT client

        Args:
            topic (list): MQTT topic
            callback_func (_type_): MQTT callback function
        """

        self.client = mqtt.Client(self.alias)
        self.client.on_connect = self.__on_connect
        self.client.on_disconnect = self.__on_disconnect
        self.client.on_subscribe = self.__on_subscribe
        self.client.on_unsubscribe = self.__on_unsubscribe

        logger.info(f"Connecting to broker: {self.broker}")

        self.client.username_pw_set(username=self.username,
                                    password=self.password)

        self.client.connect(host=self.broker, port=self.port)
        self.client.subscribe(topic=topic, qos=1)
        self.client.message_callback_add(sub=topic, callback=callback_func)

        logger.info("Connected")
        logger.info("Init client infinite loop")

        self.client.loop_start()


    def send_message(self, msg: str, topic: str) -> None:
        """
        Send MQTT message

        Args:
            msg (str): message
            topic (str): MQTT topic
        """

        self.client.publish(topic=topic,
                            payload=msg,
                            qos=1,
                            retain=False)


    def unsub_from_topic(self, topic: list) -> int:
        """
        Unsubscribe from the MQTT topic

        Args:
            topic (list): MQTT topic

        Returns:
            int: status
        """

        logger.info(f"Unsub from topics: {topic}")
        ret = self.client.unsubscribe(topic=topic)
        if ret[0] == mqtt.MQTT_ERR_SUCCESS:
            return MqttStatusRetCodes.MQTT_RET_SUCCESS.value

        return MqttStatusRetCodes.MQTT_RET_FAILED.value


    def close(self) -> None:
        """
        Close MQTT connection
        """

        self.client.loop_stop()
        self.client.disconnect()
