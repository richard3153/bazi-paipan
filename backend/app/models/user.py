# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey
from datetime import datetime
from app.database import Base


class User(Base):
    """
    用户表（可选）
    用于保存排盘记录和用户信息
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # 用户名/昵称
    username = Column(String(64), unique=True, nullable=True, index=True)
    # 性别
    gender = Column(String(4), nullable=True)
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow)
    # 是否活跃
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<User(username={self.username})>"


class BaziRecord(Base):
    """
    八字排盘记录表
    存储用户每次排盘的结果
    """
    __tablename__ = "bazi_records"

    id = Column(Integer, primary_key=True, index=True)
    # 用户ID（可选，匿名用户为NULL）
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # 姓名
    name = Column(String(64), nullable=True)
    # 性别
    gender = Column(String(4), nullable=True)
    # 出生日期（YYYY-MM-DD）
    birth_date = Column(String(10), nullable=False)
    # 出生时间（HH:MM）
    birth_time = Column(String(5), nullable=False)
    # 出生地城市ID
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
    # 经度（手动输入）
    longitude = Column(Float, nullable=True)
    # 纬度（手动输入）
    latitude = Column(Float, nullable=True)
    # 是否使用真太阳时
    use_true_solar = Column(Boolean, default=False)
    # 时区偏移（分钟，如480代表UTC+8）
    timezone_offset = Column(Integer, default=480)
    # 原始时柱地支
    raw_hour_branch = Column(String(4), nullable=True)
    # 真太阳时调整（分钟）
    true_solar_adjustment = Column(Integer, nullable=True)
    # 四柱结果（JSON）
    bazi_result = Column(Text, nullable=False)
    # 解读结果（JSON，可选）
    interpretation = Column(Text, nullable=True)
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<BaziRecord(name={self.name}, birth={self.birth_date} {self.birth_time})>"
