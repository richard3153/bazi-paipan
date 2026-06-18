# app/routers/bazi.py
"""
八字排盘API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.bazi import BaziRequest, BaziResponse, BaziResult, BirthInfo
from app.schemas.mingli import CityInfo
from app.services import bazi_calc, true_solar_time
from app.services.geo import search_cities, get_city_by_name
from datetime import datetime

router = APIRouter(prefix="/api/bazi", tags=["八字排盘"])


@router.post("/calculate", response_model=BaziResponse)
def calculate_bazi(req: BaziRequest, db: Session = Depends(get_db)):
    """
    八字排盘接口
    
    输入出生信息，自动计算四柱八字
    支持真太阳时自动校正
    """
    birth = req.birth_info
    
    # 解析日期时间
    try:
        dt = datetime.strptime(birth.birth_date, "%Y-%m-%d")
        year, month, day = dt.year, dt.month, dt.day
    except ValueError:
        return BaziResponse(success=False, message="日期格式错误，请使用YYYY-MM-DD格式")
    
    try:
        hour, minute = bazi_calc.parse_birth_time(birth.birth_time)
    except Exception:
        return BaziResponse(success=False, message="时间格式错误，请使用HH:MM格式")
    
    # 地理信息处理
    longitude = birth.longitude
    latitude = birth.latitude
    
    if not longitude or not latitude:
        # 尝试通过城市名查询
        if birth.city:
            cities = search_cities(db, birth.city, limit=1)
            if cities:
                city = cities[0]
                longitude = city.longitude
                latitude = city.latitude
    
    if not longitude or not latitude:
        raise HTTPException(status_code=400, detail="无法确定出生地经纬度，请提供城市名或手动输入经纬度")
    
    # 真太阳时计算
    true_solar_time_str = None
    true_solar_adjustment = 0
    
    if birth.use_true_solar:
        # 创建北京时间datetime对象
        try:
            birth_dt = datetime.strptime(
                f"{birth.birth_date} {birth.birth_time}", "%Y-%m-%d %H:%M"
            )
            true_solar_time_str, true_solar_adjustment = true_solar_time.true_solar_time_v2(
                birth_dt, longitude
            )
        except Exception:
            true_solar_adjustment = 0
    
    # 调用排盘计算
    result = bazi_calc.calculate_bazi(
        year=year, month=month, day=day,
        hour=hour, minute=minute,
        gender=birth.gender or "男",
        use_true_solar=birth.use_true_solar,
        true_solar_adjustment=true_solar_adjustment,
    )
    
    # 添加真太阳时信息
    if birth.use_true_solar:
        result["true_solar_time"] = true_solar_time_str
        result["true_solar_adjustment"] = true_solar_adjustment
    
    # 生成命理解读报告
    try:
        analysis_report = bazi_calc.generate_analysis_report(result)
        result["analysis_report"] = analysis_report
    except Exception as e:
        import logging
        logging.warning(f"生成分析报告失败: {e}")
    
    # 转换为响应模型
    def pillar_to_model(p):
        from app.schemas.bazi import BaziPillar
        return BaziPillar(**p)
    
    def shishen_to_model(s):
        if not s:
            return None
        from app.schemas.bazi import ShishenItem
        return ShishenItem(**s)
    
    bazi_result = BaziResult(
        year_pillar=pillar_to_model(result["year_pillar"]),
        month_pillar=pillar_to_model(result["month_pillar"]),
        day_pillar=pillar_to_model(result["day_pillar"]),
        hour_pillar=pillar_to_model(result["hour_pillar"]),
        day_master=result["day_master"],
        day_master_wuxing=result["day_master_wuxing"],
        day_master_yinyang=result["day_master_yinyang"],
        year_shishen=shishen_to_model(result.get("year_shishen")),
        month_shishen=shishen_to_model(result["month_shishen"]),
        hour_shishen=shishen_to_model(result.get("hour_shishen")),
        year_nayin=result["year_nayin"],
        month_nayin=result["month_nayin"],
        day_nayin=result["day_nayin"],
        hour_nayin=result["hour_nayin"],
        taiyuan=pillar_to_model(result["taiyuan"]),
        mggong=pillar_to_model(result["minggong"]),
        shengong=pillar_to_model(result["shengong"]),
        true_solar_time=result.get("true_solar_time"),
        true_solar_adjustment=result.get("true_solar_adjustment"),
        dayun=result.get("dayun"),
        shensha=result.get("shensha"),
        wangshuai=result.get("wangshuai"),
        geju=result.get("geju"),
        yongshen=result.get("yongshen"),
        tiaohou=result.get("tiaohou"),
        analysis_report=result.get("analysis_report"),
    )
    
    return BaziResponse(success=True, data=bazi_result)
