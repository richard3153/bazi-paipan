# app/services/geo.py
"""
地理查询服务
通过城市名称查询经纬度
"""
from sqlalchemy.orm import Session
from app.models.city import City
from typing import List, Optional


def search_cities(db: Session, query: str, limit: int = 20) -> List[City]:
    """
    模糊搜索城市（支持中文名和英文名）
    
    参数:
        db: 数据库会话
        query: 城市名称（支持模糊匹配）
        limit: 返回数量限制
    
    返回:
        匹配的城市列表
    """
    pattern = f"%{query}%"
    cities = (
        db.query(City)
        .filter(
            City.name.like(pattern) |
            City.name_en.like(pattern) |
            City.province.like(pattern)
        )
        .order_by(City.population.desc().nullslast())
        .limit(limit)
        .all()
    )
    return cities


def get_city_by_name(db: Session, name: str) -> Optional[City]:
    """
    精确查找城市
    """
    return db.query(City).filter(City.name == name).first()


def get_city_by_id(db: Session, city_id: int) -> Optional[City]:
    """
    通过ID获取城市
    """
    return db.query(City).filter(City.id == city_id).first()


def get_provinces(db: Session) -> List[str]:
    """
    获取中国所有省份列表（去重、排序）
    """
    results = (
        db.query(City.province)
        .filter(City.country == 'China')
        .filter(City.province.isnot(None))
        .filter(City.province != '')
        .distinct()
        .order_by(City.province)
        .all()
    )
    return [r[0] for r in results]


def get_cities_by_province(db: Session, province: str) -> List[City]:
    """
    获取某省份下的所有城市
    """
    cities = (
        db.query(City)
        .filter(City.country == 'China')
        .filter(City.province == province)
        .order_by(City.name)
        .all()
    )
    return cities
