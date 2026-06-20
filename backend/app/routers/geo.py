# app/routers/geo.py
"""
地理查询API路由
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.mingli import (
    GeoQueryRequest, GeoQueryResponse, CityInfo,
    ProvinceListResponse, CitiesByProvinceRequest, CitiesByProvinceResponse,
    TrueSolarRequest, TrueSolarResponse
)
from app.services.geo import search_cities, get_provinces, get_cities_by_province
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
            name_en=c.name_en,
            province=c.province,
            country=c.country,
            longitude=c.longitude,
            latitude=c.latitude,
            timezone=c.timezone,
            population=c.population,
            capital=c.capital,
        )
        for c in cities
    ]
    
    return GeoQueryResponse(success=True, data=city_list)


@router.get("/provinces", response_model=ProvinceListResponse)
def list_provinces(db: Session = Depends(get_db)):
    """
    获取中国所有省份列表
    """
    provinces = get_provinces(db)
    return ProvinceListResponse(
        success=True,
        data=[{"name": p} for p in provinces],
        message=None
    )


@router.post("/cities-by-province", response_model=CitiesByProvinceResponse)
def list_cities_by_province(req: CitiesByProvinceRequest, db: Session = Depends(get_db)):
    """
    根据省份获取城市列表
    """
    if not req.province:
        return CitiesByProvinceResponse(success=False, message="省份不能为空")

    cities = get_cities_by_province(db, req.province)

    if not cities:
        return CitiesByProvinceResponse(success=True, data=[], message="该省份下暂无城市数据")

    city_list = [
        CityInfo(
            id=c.id,
            name=c.name,
            name_en=c.name_en,
            province=c.province,
            country=c.country,
            longitude=c.longitude,
            latitude=c.latitude,
            timezone=c.timezone,
            population=c.population,
            capital=c.capital,
        )
        for c in cities
    ]

    return CitiesByProvinceResponse(success=True, data=city_list)


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
