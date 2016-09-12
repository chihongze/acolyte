COMMON_DATE_FORMAT = "%Y-%m-%d"
COMMON_DATETIME_FORMAT = "{date_fmt} %H:%M:%S".format(
    date_fmt=COMMON_DATE_FORMAT)


def common_fmt_dt(dt):
    """按常规格式获取datetime对象的字符串表示
    """
    return dt.strftime(COMMON_DATETIME_FORMAT)
