# app/services/true_solar_time.py
"""
真太阳时计算服务
真太阳时 = 地方平时 + 均时差
均时差由太阳视运动不均匀性引起，最大约±16分钟
"""
import math
from datetime import datetime, timezone, timedelta
from typing import Tuple


def julian_day(year: int, month: int, day: int, hour: float) -> float:
    """
    计算儒略日（Julian Day）
    year, month, day: 公历日期
    hour: 小时（含小数）
    """
    if month <= 2:
        year -= 1
        month += 12
    A = int(year / 100)
    B = 2 - A + int(A / 4)
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + hour / 24.0 + B - 1524.5
    return jd


def equation_of_time(jd: float) -> float:
    """
    计算均时差（Equation of Time），单位：分钟
    均时差 = 真太阳时 - 地方平时
    返回值 > 0 表示真太阳时快于地方平时
    """
    # 儒略世纪数
    n = jd - 2451545.0
    L = (280.460 + 0.9856474 * n) % 360
    g = (357.528 + 0.9856003 * n) % 360
    g_rad = math.radians(g)
    lambda_sun = L + 1.915 * math.sin(g_rad) + 0.020 * math.sin(2 * g_rad)
    lambda_rad = math.radians(lambda_sun)
    epsilon = 23.439 - 0.0000004 * n
    epsilon_rad = math.radians(epsilon)
    # 太阳赤纬
    delta = math.degrees(math.asin(math.sin(epsilon_rad) * math.sin(lambda_rad)))
    # 均时差计算
    y = math.tan(epsilon_rad / 2) ** 2
    L_rad = math.radians(L)
    eot = 4 * (
        y * math.sin(2 * L_rad)
        - 2 * math.sin(g_rad)
        + 4 * y * math.sin(g_rad) * math.cos(2 * L_rad)
        - 0.5 * y * y * math.sin(4 * L_rad)
        - 1.25 * math.sin(2 * g_rad)
    )
    return eot  # 分钟


def true_solar_time(
    year: int, month: int, day: int, hour: float,
    longitude: float, timezone_offset: float = 8.0
) -> Tuple[str, int]:
    """
    计算真太阳时
    
    参数:
        year, month, day: 公历日期
        hour: 小时（北京时间，地方平时）
        longitude: 经度（度，东经为正）
        timezone_offset: 时区（默认8，即北京时间UTC+8）
    
    返回:
        (true_solar_time_str, adjustment_minutes)
        true_solar_time_str: 真太阳时 HH:MM
        adjustment_minutes: 调整分钟数（正=加，负=减）
    """
    jd = julian_day(year, month, day, hour)
    eot = equation_of_time(jd)
    
    # 经度差修正（每度4分钟）
    # 标准经度 = 时区 * 15（如UTC+8对应东经120度）
    standard_longitude = timezone_offset * 15.0
    longitude_correction = (longitude - standard_longitude) * 4.0  # 分钟
    
    # 总调整 = 均时差 + 经度差修正
    total_adjustment = eot + longitude_correction  # 分钟
    total_adjustment = round(total_adjustment)
    
    # 将北京时间转为真太阳时
    # 真太阳时 = 北京时间 + 总调整
    # 先转为分钟
    local_minutes = int(hour * 60)  # hour 传入的是小数分钟
    # hour在这里实际上是 minutes，我们需要重新设计接口
    # 其实hour是小时小数，但我们已经转为分钟了
    # 重新整理：
    
    # hour 参数：传入的北京时间已转为 "hour_decimal"，即小时小数
    # 我们需要从hour参数是 "HH:MM" 字符串再解析
    # 但实际上调用方传入的hour应该是小数
    # 修正：hour是小数小时
    true_solar_minutes = round(hour * 60 + total_adjustment)
    
    # 处理跨天
    while true_solar_minutes < 0:
        true_solar_minutes += 1440
    while true_solar_minutes >= 1440:
        true_solar_minutes -= 1440
    
    th = true_solar_minutes // 60
    tm = true_solar_minutes % 60
    
    return f"{th:02d}:{tm:02d}", total_adjustment


def true_solar_time_v2(
    dt: datetime,
    longitude: float,
    timezone_offset: float = 8.0
) -> Tuple[str, int]:
    """
    真太阳时计算（简化版，基于近似公式）
    dt: datetime对象（北京时间，地方平时）
    longitude: 经度（度）
    timezone_offset: 时区偏移（默认8）
    
    返回: (true_solar_time_str, adjustment_minutes)
    """
    hour_decimal = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
    return true_solar_time(dt.year, dt.month, dt.day, hour_decimal, longitude, timezone_offset)
