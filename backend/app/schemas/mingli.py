# app/schemas/mingli.py
from pydantic import BaseModel, Field
from typing import Optional, List


class CityInfo(BaseModel):
    """城市信息"""
    id: int
    name: str = Field(..., description="城市名称（中文优先）")
    name_en: Optional[str] = Field(None, description="城市英文名称")
    province: Optional[str] = None
    country: Optional[str] = Field(None, description="国家")
    longitude: float
    latitude: float
    timezone: str = "Asia/Shanghai"
    population: Optional[int] = Field(None, description="人口")
    capital: Optional[str] = Field(None, description="首都/首府标识")


class GeoQueryRequest(BaseModel):
    """地理查询请求"""
    city_name: str = Field(..., description="城市名称（支持模糊查询）")


class GeoQueryResponse(BaseModel):
    """地理查询响应"""
    success: bool
    data: Optional[List[CityInfo]] = None
    message: Optional[str] = None


class TrueSolarRequest(BaseModel):
    """真太阳时计算请求"""
    date: str = Field(..., description="日期 YYYY-MM-DD")
    time: str = Field(..., description="时间 HH:MM")
    longitude: float = Field(..., ge=-180, le=180, description="经度")
    latitude: float = Field(..., ge=-90, le=90, description="纬度")


class TrueSolarResponse(BaseModel):
    """真太阳时计算响应"""
    success: bool
    local_time: str = Field(..., description="地方平时")
    true_solar_time: str = Field(..., description="真太阳时")
    adjustment_minutes: int = Field(..., description="调整分钟数（正值表示加，负值表示减）")


class MingLiInterpretationRequest(BaseModel):
    """命理解读请求"""
    bazi_result: dict = Field(..., description="八字排盘结果")
    include_geshi: bool = Field(True, description="是否分析格局")
    include_yongshen: bool = Field(True, description="是否分析用神")
    source_books: Optional[List[str]] = Field(
        None, description="参考书籍列表"
    )


class MingLiInterpretationResponse(BaseModel):
    """命理解读响应"""
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None
