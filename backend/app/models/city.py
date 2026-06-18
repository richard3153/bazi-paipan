# app/models/city.py
from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class City(Base):
    """
    城市经纬度数据库
    存储城市名称（支持省/市/区多级）、经纬度、时区、行政区划代码
    """
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    # 城市名称
    name = Column(String(64), nullable=False, index=True)
    # 所属省份
    province = Column(String(32), nullable=True, index=True)
    # 所属城市（地级市，用于区县级查询）
    city = Column(String(32), nullable=True)
    # 经度
    longitude = Column(Float, nullable=False)
    # 纬度
    latitude = Column(Float, nullable=False)
    # 时区（UTC偏移，如8代表UTC+8北京时间）
    timezone = Column(String(32), nullable=False, default="Asia/Shanghai")
    # 行政区划代码
    adcode = Column(String(12), nullable=True)
    # 国家代码
    country = Column(String(8), nullable=True, default="CN")

    def __repr__(self):
        return f"<City(name={self.name}, lng={self.longitude}, lat={self.latitude})>"
