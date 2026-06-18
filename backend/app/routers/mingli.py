# app/routers/mingli.py
"""
命理解读API路由
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.mingli import MingLiInterpretationRequest, MingLiInterpretationResponse
from app.services.interpretation import interpret_bazi

router = APIRouter(prefix="/api/mingli", tags=["命理解读"])


@router.post("/interpret", response_model=MingLiInterpretationResponse)
def interpret(req: MingLiInterpretationRequest, db: Session = Depends(get_db)):
    """
    命理解读接口
    
    基于八字排盘结果，返回命理解读分析：
    - 十神分析
    - 格局判断
    - 用神分析
    - 综合评断
    
    source_books参数可指定参考书籍：
    - 《三命通会》
    - 《滴天髓》
    - 《穷通宝鉴》
    - 《子平真诠》
    - 《渊海子平》
    """
    if not req.bazi_result:
        return MingLiInterpretationResponse(
            success=False, message="缺少八字排盘结果"
        )
    
    try:
        result = interpret_bazi(
            bazi_result=req.bazi_result,
            db=db,
            include_geshi=req.include_geshi,
            include_yongshen=req.include_yongshen,
            source_books=req.source_books,
        )
        return MingLiInterpretationResponse(success=True, data=result)
    except Exception as e:
        return MingLiInterpretationResponse(
            success=False, message=f"解读失败: {str(e)}"
        )
