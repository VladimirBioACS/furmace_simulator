import sys

try:
    from loguru import logger
except ImportError:
    print("Module loguru not found. Please use pip install -r requirements.txt")
    sys.exit(1)


class LogManager():
    """
    log_manager class
    """

    def __init__(self,
                 log_file_path: str,
                 log_filter_name: str,
                 log_level: str,
                 log_rotation_size: str,
                 log_compression_method: str,
                 log_retention: int) -> None:
        """log_manager class constructor

        Args:
            log_file_path (str): path to log file
            log_filter_name (str): log filtering name
            log_level (str): log level (DEBUG, INFO, TRACE, SUCCESS, WARNING, ERROR, CRITICAL)
            log_rotation_size (str): size for log file rotation
            log_compression_method (str): method of log file compression
            log_retention (int): number of log file retention
        """

        self.log_file_path = log_file_path
        self.log_filter_name = log_filter_name
        self.log_level = log_level
        self.log_rotation_size = log_rotation_size
        self.log_compression_method = log_compression_method
        self.log_retention = log_retention


    def create_logger(self) -> None:
        """ creates loguru logger instance

        Args:
            None
        """

        logger.add(sys.stderr, format="{time} {level} {message}",
           filter=self.log_filter_name,
           level=self.log_level)

        logger.add(self.log_file_path,
                rotation=self.log_rotation_size,
                compression=self.log_compression_method,
                retention=self.log_retention)
