# app/routers/geo.py
"""
地理查询API路由
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.mingli import GeoQueryRequest, GeoQueryResponse, CityInfo, TrueSolarRequest, TrueSolarResponse
from app.services.geo import search_cities
from app.services.true_solar_time import true_solar_time_v2
from datetime import datetime

router = APIRouter(prefix="/api/geo", tags=["地理查询"])


@router.post("/search", response_model=GeoQueryResponse)
def search_city(req: GeoQueryRequest, db: Session = Depends(get_db)):
    """
    城市名称模糊搜索
    返回匹配的城市列表及其经纬度
    """
    if len(req.city_name) < 2:
        return GeoQueryResponse(success=False, message="城市名称至少2个字符")
    
    cities = search_cities(db, req.city_name)
    
    if not cities:
        return GeoQueryResponse(success=True, data=[], message="未找到匹配城市")
    
    city_list = [
        CityInfo(
            id=c.id,
            name=c.name,
            province=c.province,
            longitude=c.longitude,
            latitude=c.latitude,
            timezone=c.timezone,
        )
        for c in cities
    ]
    
    return GeoQueryResponse(success=True, data=city_list)


@router.post("/true-solar-time", response_model=TrueSolarResponse)
def calc_true_solar_time(req: TrueSolarRequest):
    """
    真太阳时计算
    
    将北京时间（地方平时）转换为真太阳时
    参数:
        date: 日期 YYYY-MM-DD
        time: 时间 HH:MM
        longitude: 经度
        latitude: 纬度（此参数在均时差计算中非必需，但保留作为参考）
    """
    try:
        dt = datetime.strptime(f"{req.date} {req.time}", "%Y-%m-%d %H:%M")
    except ValueError:
        return TrueSolarResponse(
            success=False,
            local_time=req.time,
            true_solar_time=req.time,
            adjustment_minutes=0,
        )
    
    true_solar_str, adjustment = true_solar_time_v2(dt, req.longitude)
    
    return TrueSolarResponse(
        success=True,
        local_time=req.time,
        true_solar_time=true_solar_str,
        adjustment_minutes=adjustment,
    )
