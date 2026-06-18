"""
高级命理解读API路由
提供神煞、大运、流年、小运、童运深度解读的接口
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from app.core.advanced_interpretation import AdvancedInterpretationEngine

router = APIRouter(prefix="/api/advanced", tags=["高级命理解读"])

# 全局引擎实例
_engine: Optional[AdvancedInterpretationEngine] = None


def get_engine() -> AdvancedInterpretationEngine:
    """获取解读引擎实例（懒加载）"""
    global _engine
    if _engine is None:
        _engine = AdvancedInterpretationEngine()
    return _engine


# ============ Pydantic 模型 ============

class AdvancedInterpretationRequest(BaseModel):
    """高级解读请求"""
    bazi_result: Dict[str, Any]
    include_shensha: bool = True
    include_dayun: bool = True
    include_liunian: bool = True
    include_xiaoyun: bool = True
    include_tongyun: bool = True


class AdvancedInterpretationResponse(BaseModel):
    """高级解读响应"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class ShenShaQueryRequest(BaseModel):
    """神煞查询请求"""
    bazi_result: Dict[str, Any]


class DaYunQueryRequest(BaseModel):
    """大运解读请求"""
    bazi_result: Dict[str, Any]


class LiuNianQueryRequest(BaseModel):
    """流年解读请求"""
    bazi_result: Dict[str, Any]
    year: Optional[int] = None  # 指定年份，默认为当前年份


# ============ API 接口 ============


@router.post("/full", response_model=AdvancedInterpretationResponse)
def advanced_full_interpretation(req: AdvancedInterpretationRequest):
    """
    完整高级命理解读

    返回包含所有模块的深度解读结果：
    - 神煞深度解读（30+神煞）
    - 大运详细解读（10个维度）
    - 当前流年解读
    - 小运解读
    - 童运解读（12岁以内）
    - 命运层次评估
    - 关键年份
    - 改善建议
    """
    if not req.bazi_result:
        return AdvancedInterpretationResponse(
            success=False,
            message="缺少八字排盘结果"
        )

    try:
        engine = get_engine()
        result = engine.full_interpretation(req.bazi_result)

        output = {}

        if req.include_shensha:
            output["shensha_analysis"] = result.shensha_analysis

        if req.include_dayun:
            output["dayun_analysis"] = result.dayun_analysis

        if req.include_liunian:
            output["current_liunian"] = result.current_liunian

        if req.include_xiaoyun:
            output["xiaoyun_analysis"] = result.xiaoyun_analysis

        if req.include_tongyun:
            output["tongyun_analysis"] = result.tongyun_analysis

        output["overall_fortune"] = result.overall_fortune
        output["key_years"] = result.key_years
        output["suggestions"] = result.suggestions

        return AdvancedInterpretationResponse(
            success=True,
            data=output
        )

    except Exception as e:
        return AdvancedInterpretationResponse(
            success=False,
            message=f"高级解读失败: {str(e)}"
        )


@router.post("/shensha", response_model=AdvancedInterpretationResponse)
def shensha_interpretation(req: ShenShaQueryRequest):
    """
    神煞深度解读

    返回命局中所有神煞的详细解读，包括：
    - 神煞名称、类别
    - 出现位置
    - 经典依据
    - 命理影响
    - 吉凶程度
    - 化解建议
    """
    if not req.bazi_result:
        return AdvancedInterpretationResponse(
            success=False,
            message="缺少八字排盘结果"
        )

    try:
        engine = get_engine()
        chart = engine._build_chart(req.bazi_result)
        shensha_data = engine._interpret_shensha(chart)

        return AdvancedInterpretationResponse(
            success=True,
            data={
                "shensha_count": len(shensha_data),
                "shensha_analysis": shensha_data
            }
        )
    except Exception as e:
        return AdvancedInterpretationResponse(
            success=False,
            message=f"神煞解读失败: {str(e)}"
        )


@router.post("/dayun", response_model=AdvancedInterpretationResponse)
def dayun_interpretation(req: DaYunQueryRequest):
    """
    大运深度解读

    对每步大运进行10个维度的详细解读：
    1. 五行属性与日主关系
    2. 大运与原局作用
    3. 调候得失
    4. 格局成败影响
    5. 用神得失
    6. 总体运势评级
    7. 事业运势详解
    8. 财运走势
    9. 婚姻感情
    10. 健康注意
    """
    if not req.bazi_result:
        return AdvancedInterpretationResponse(
            success=False,
            message="缺少八字排盘结果"
        )

    try:
        engine = get_engine()
        chart = engine._build_chart(req.bazi_result)
        dayun_data = engine._interpret_dayun(chart)

        return AdvancedInterpretationResponse(
            success=True,
            data={
                "dayun_count": len(dayun_data),
                "dayun_analysis": dayun_data
            }
        )
    except Exception as e:
        return AdvancedInterpretationResponse(
            success=False,
            message=f"大运解读失败: {str(e)}"
        )


@router.post("/liunian", response_model=AdvancedInterpretationResponse)
def liunian_interpretation(req: LiuNianQueryRequest):
    """
    流年深度解读

    返回指定年份的流年详细解读：
    - 流年天干地支分析
    - 流年与大运的关系
    - 流年与原局的冲克
    - 重点事项预警
    - 月份运势分布
    """
    if not req.bazi_result:
        return AdvancedInterpretationResponse(
            success=False,
            message="缺少八字排盘结果"
        )

    try:
        # 使用指定年份或当前年份
        target_year = req.year or datetime.now().year

        engine = get_engine()
        chart = engine._build_chart(req.bazi_result)

        # 重新包装为指定年份的流年
        year_cycle = (target_year - 4) % 60
        liunian_stem = engine.tian_gan[year_cycle % 10]
        liunian_branch = engine.di_zhi[year_cycle % 12]
        liunian_ganzhi = liunian_stem + liunian_branch

        current_dayun = chart.get("current_dayun", {})

        result = engine.liunian_interpreter.interpret(
            target_year, liunian_ganzhi, current_dayun, chart
        )

        return AdvancedInterpretationResponse(
            success=True,
            data={
                "year": result.year,
                "ganzhi": result.ganzhi,
                "ganzhi_analysis": result.ganzhi_analysis,
                "dayun_relationship": result.dayun_relationship,
                "chongke_analysis": result.chongke_analysis,
                "warnings": result.warnings,
                "month_fortune": result.month_fortune,
                "summary": result.summary
            }
        )
    except Exception as e:
        return AdvancedInterpretationResponse(
            success=False,
            message=f"流年解读失败: {str(e)}"
        )


@router.get("/health")
def advanced_health():
    """高级解读引擎健康检查"""
    try:
        engine = get_engine()
        shensha_count = len(getattr(engine, 'knowledge', {}).get('shensha', {}))
        return {
            "status": "healthy",
            "engine": "advanced_interpretation_engine",
            "version": "1.0.0",
            "loaded_knowledge": list(engine.knowledge.keys()) if hasattr(engine, 'knowledge') else [],
            "shensha_loaded": shensha_count > 0
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
