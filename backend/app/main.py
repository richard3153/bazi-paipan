# app/main.py
"""
风水命理程序 - 后端API服务
基于 FastAPI + SQLAlchemy
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import bazi, geo, mingli, advanced_routes

app = FastAPI(
    title="风水命理API",
    description="""
# 风水命理程序后端API

提供四柱八字排盘、真太阳时计算、地理查询和命理解读服务。

## 核心功能
- **八字排盘**：输入出生信息，返回完整四柱八字
- **真太阳时**：根据经纬度精确计算真太阳时
- **地理查询**：城市名称查询经纬度
- **命理解读**：基于五本经典命理书籍的解读分析

## 参考书籍
- 《三命通会》
- 《滴天髓》
- 《穷通宝鉴》
- 《子平真诠》
- 《渊海子平》
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(bazi.router)
app.include_router(geo.router)
app.include_router(mingli.router)
app.include_router(advanced_routes.router)


@app.on_event("startup")
def startup_event():
    """启动时初始化数据库"""
    init_db()


@app.get("/")
def root():
    return {"message": "风水命理API服务", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
