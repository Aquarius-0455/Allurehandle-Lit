# -*- coding:UTF-8 -*-
import os
import logging.handlers


class Logger:
    """单例日志类"""
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._logger = logging.getLogger('DI_Api')
            self._logger.setLevel(logging.DEBUG)
            
            fmt = "%(asctime)s %(levelname)s [%(name)s] [%(filename)s(%(funcName)s:%(lineno)d)] - %(message)s"
            formatter = logging.Formatter(fmt)
            
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            log_file = os.path.join(project_path, 'log', 'requests.log')
            
            handler = logging.handlers.TimedRotatingFileHandler(
                filename=log_file,
                when='midnight',
                interval=1,
                backupCount=7,
                encoding='utf-8'
            )
            
            def namer(filename):
                dir_name, base_name = os.path.split(filename)
                base_name = base_name.replace('requests.log.', 'requests_')
                return os.path.join(dir_name, base_name)
            
            handler.namer = namer
            handler.suffix = "_%Y-%m-%d.log"
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
    
    def get_logger(self):
        return self._logger


logger = Logger().get_logger()

