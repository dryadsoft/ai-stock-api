import logging

class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.my_logger = logging.getLogger(__name__)
            cls._instance.my_logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            cls._instance.my_logger.addHandler(stream_handler)
        return cls._instance

    def get_logger(self, name=__name__):
        self.my_logger.name = name
        return self.my_logger
