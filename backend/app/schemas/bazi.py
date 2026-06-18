# app/schemas/bazi.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, time


class BirthInfo(BaseModel):
    """出生信息输入"""
    name: Optional[str] = Field(None, description="姓名（可选）")
    gender: Optional[str] = Field(None, description="性别：male/female")
    birth_date: str = Field(..., description="出生日期 YYYY-MM-DD")
    birth_time: str = Field(..., description="出生时间 HH:MM（北京时间）")
    city: Optional[str] = Field(None, description="出生城市名称")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="纬度")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="经度")
    use_true_solar: bool = Field(False, description="是否使用真太阳时")


class BaziPillar(BaseModel):
    """单柱信息"""
    stem: str = Field(..., description="天干")
    branch: str = Field(..., description="地支")
    hidden_stems: List[str] = Field(default_factory=list, description="地支藏干")
    wuxing: str = Field(..., description="五行")


class ShishenItem(BaseModel):
    """十神项"""
    stem: str = Field(..., description="天干")
    target: str = Field(..., description="作用天干")
    shishen: str = Field(..., description="十神名称")
    wuxing: str = Field(..., description="五行属性")


class AnalysisReportSchema(BaseModel):
    """命理解读报告"""
    overview: str = Field(..., description="总体概述")
    dayMasterAnalysis: str = Field(..., description="日主分析")
    wuxingAnalysis: str = Field(..., description="五行分析")
    shishenAnalysis: str = Field(..., description="十神分析")
    wealth: str = Field(..., description="财运分析")
    career: str = Field(..., description="事业分析")
    health: str = Field(..., description="健康分析")
    marriage: str = Field(..., description="婚姻分析")
    education: str = Field(..., description="学业分析")
    suggestions: List[str] = Field(default_factory=list, description="改善建议")


class BaziResult(BaseModel):
    """八字排盘结果"""
    year_pillar: BaziPillar = Field(..., description="年柱")
    month_pillar: BaziPillar = Field(..., description="月柱")
    day_pillar: BaziPillar = Field(..., description="日柱")
    hour_pillar: BaziPillar = Field(..., description="时柱")
    day_master: str = Field(..., description="日主（日干）")
    day_master_wuxing: str = Field(..., description="日主五行")
    day_master_yinyang: str = Field(..., description="日主阴阳")
    year_shishen: Optional[ShishenItem] = Field(None, description="年柱十神")
    month_shishen: ShishenItem = Field(..., description="月柱十神")
    hour_shishen: Optional[ShishenItem] = Field(None, description="时柱十神")
    # 纳音
    year_nayin: str = Field(..., description="年柱纳音")
    month_nayin: str = Field(..., description="月柱纳音")
    day_nayin: str = Field(..., description="日柱纳音")
    hour_nayin: str = Field(..., description="时柱纳音")
    # 胎元、命宫、身宫（可选）
    taiyuan: Optional[BaziPillar] = Field(None, description="胎元")
    mggong: Optional[BaziPillar] = Field(None, description="命宫")
    shengong: Optional[BaziPillar] = Field(None, description="身宫")
    # 真太阳时信息
    true_solar_time: Optional[str] = Field(None, description="真太阳时间 HH:MM")
    true_solar_adjustment: Optional[int] = Field(None, description="调整分钟数")
    # 大运
    dayun: Optional[dict] = Field(None, description="大运信息")
    # 神煞
    shensha: Optional[dict] = Field(None, description="神煞信息")
    # 旺衰
    wangshuai: Optional[dict] = Field(None, description="旺衰信息")
    # 格局判定（子平真诠核心）
    geju: Optional[dict] = Field(None, description="格局判定结果（含geju/chengge/desc等）")
    # 用神/忌神
    yongshen: Optional[dict] = Field(None, description="用神/忌神信息（含yongshen/jishen/tiaohou/tongguan/type/strength_auto/desc）")
    # 调候用神（穷通宝鉴）
    tiaohou: Optional[dict] = Field(None, description="调候用神结果（含tiaohou_yongshen/hannuan/zaoshi/desc）")
    # 命理解读报告
    analysis_report: Optional[AnalysisReportSchema] = Field(None, description="命理解读报告")


class BaziRequest(BaseModel):
    """八字排盘请求"""
    birth_info: BirthInfo


class BaziResponse(BaseModel):
    """八字排盘响应"""
    success: bool
    data: Optional[BaziResult] = None
    message: Optional[str] = None
