"""日志模块
"""

import sys
import logging
import logging.handlers


LOGGER_LEVELS = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}


def stdout_handler():
    """基于标准输出的handler
    """
    return logging.StreamHandler(sys.stdout)


def time_rotating_handler(filename, when="D", interval=1, backupCount=0,
                          encoding="utf-8", delay=False):
    """创建基于日期回滚的日志策略"""
    return logging.handlers.TimedRotatingFileHandler(
        filename,
        when="D",
        interval=1,
        backupCount=0,
        encoding="utf-8",
        delay=delay
    )


# 通用的日志格式
LOG_FORMATTER = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def create_logger(logger_name, handlers, level=logging.INFO,
                  formatter=LOG_FORMATTER):
    """创建日志对象
    :param logger_name 日志名称
    :param filename 日志文件路径
    :param level 日志级别
    :param formatter 日志输出格式
    :param handlers 日志处理策略
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    for handler in handlers:
        handler.setFormatter(logging.Formatter(LOG_FORMATTER))
        logger.addHandler(handler)
    return logger


def load_logger_config(config):
    """从配置数据中加载logger对象到模块的namespace
    """
    log_config = config.get("log", {})
    logger_names = ("acolyte", "error", "api", "web")

    for logger_name in logger_names:
        logger_file = log_config.get(logger_name + "_log")
        logger_level = LOGGER_LEVELS[
            log_config.get(logger_name + "_level", "debug")]
        if logger_file is None:
            logger_handler = stdout_handler()
        else:
            logger_handler = time_rotating_handler(logger_file)
        logger = create_logger(logger_name, (logger_handler,))
        logger.setLevel(logger_level)
        globals()[logger_name] = logger
