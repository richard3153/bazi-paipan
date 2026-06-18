# 八字排盘系统 / Chinese Bazi (Four Pillars) Calculator

[English](#english) | [中文](#中文)

---

<a name="english"></a>
## English

### 📖 Introduction

A professional full-stack web application for Chinese Bazi (八字, Four Pillars of Destiny) calculation and fortune analysis. This system provides accurate calculation based on traditional Chinese almanac algorithms and integrates interpretations from five classical texts.

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| **Four Pillars Calculation** | Accurate 年柱/月柱/日柱/时柱 based on solar terms |
| **Hidden Stems (藏干)** | Complete with weight analysis (本气/中气/余气) |
| **Ten Gods (十神)** | Complete mapping with 枭神夺食 detection |
| **Shen Sha (神煞)** | 20+ deity/spirit calculations with position tracking |
| **Twelve Life Stages (十二长生)** | 长生/沐浴/冠带/临官/帝旺/衰/病/死/墓/绝/胎/养 |
| **Dayun (大运)** | Fortune cycles with起运/交运 timing |
| **Pattern Analysis (格局)** | 8 正格 + 建禄/月刃格 |
| **YongShen/JiShen (用神/忌神)** | Useful/harmful elements analysis |
| **TiaoHou (调候)** | Climate adjustment based on 《穷通宝鉴》 120 rules |
| **Human-readable Reports** | Plain Chinese interpretation (no classical jargon) |

### 🏗️ Project Structure

```
bazi-paipan/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── core/              # Interpretation engines
│   │   │   ├── constants.py         # Heavenly/Earthly stems, 十神, 神煞 tables
│   │   │   ├── interpretation_engine_v2.py  # Five classics interpretation
│   │   │   ├── dayun_interpreter.py        # 大运解读
│   │   │   ├── liunian_interpreter.py      # 流年解读
│   │   │   └── shensha_interpreter.py      # 神煞解读
│   │   ├── models/            # SQLAlchemy models
│   │   ├── routers/           # FastAPI routes
│   │   │   └── bazi.py              # Main calculation endpoint
│   │   ├── schemas/           # Pydantic request/response models
│   │   └── services/          # Business logic
│   │       └── bazi_calc.py         # Core calculation engine (2000+ lines)
│   ├── data/
│   │   └── cities.csv         # 50+ Chinese cities with coordinates
│   └── docs/                  # API & database documentation
├── baZiApp/                   # React + TypeScript frontend
│   ├── src/
│   │   ├── components/        # UI components
│   │   │   ├── SiZhuDisplay.tsx     # 四柱展示
│   │   │   ├── WuXingDistribution.tsx  # 五行分布图
│   │   │   └── AnalysisReport.tsx   # 分析报告
│   │   ├── pages/
│   │   │   └── ResultPage.tsx       # 结果页面
│   │   ├── services/
│   │   │   └── baziService.ts       # API integration
│   │   └── store/
│   │       └── appStore.ts          # Zustand state management
│   └── package.json
├── knowledge_base/            # JSON knowledge graphs (命理知识图谱)
│   ├── shensha_knowledge.json       # 神煞知识
│   ├── wuxing_knowledge.json        # 五行知识
│   ├── yongshen_knowledge.json      # 用神知识
│   └── tiaohou_knowledge.json       # 调候知识
├── true-solar-time/           # True solar time calculation module
└── geo_location_module/       # Geographic location utilities
```

### 🚀 Quick Start

#### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

#### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Initialize database (optional, for city search)
python data/init_db.py

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup

```bash
cd baZiApp

# Install dependencies
npm install

# Start development server
npm run dev
```

#### Access

- **Frontend**: http://localhost:3000 (or next available port)
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs

### 📚 API Reference

#### Calculate Bazi

```http
POST /api/bazi/calculate
Content-Type: application/json

{
  "birth_info": {
    "birth_date": "1988-02-22",
    "birth_time": "21:20",
    "gender": "male",
    "latitude": 39.904,
    "longitude": 116.407
  }
}
```

#### Response Fields

| Field | Description |
|-------|-------------|
| `four_pillars` | 年柱/月柱/日柱/时柱 with 天干/地支/藏干 |
| `shishen` | Ten Gods mapping for each pillar |
| `shensha` | Shen Sha list with positions |
| `twelve_life_stages` | 十二长生 for each earthly branch |
| `dayun` | 大运 cycles with timing |
| `geju` | Pattern (格局) determination |
| `yongshen/jishen` | Useful/harmful elements |
| `tiaohou` | Climate adjustment (调候用神) |
| `analysis_report` | Human-readable interpretation (10 sections) |

#### City Search

```http
GET /api/geo/search?name=北京
```

### 🧪 Verification

Verified against china95.net reference calculations with 1988-02-22 21:20 乾造 test case:

| Item | Result |
|------|--------|
| Four Pillars | ✅ 戊辰 甲寅 丁未 辛亥 |
| Hidden Stems | ✅ 乙己丁 / 甲丙戊 / 乙己丁 / 壬甲 |
| Shen Sha Positions | ✅ 8/8 match |
| Dayun Direction | ✅ 顺行 (阳男) |
| Starting Age | ✅ 4岁起运 |
| Tongyun | ✅ 1岁甲寅 |

### 📖 Classical Texts Integration

This system implements algorithms from five classical Chinese fortune-telling texts:

| Text | Application |
|------|-------------|
| 《滴天髓》 | Ten Gods strength analysis, pattern determination |
| 《子平真诠》| 格局 classification, 用神 selection |
| 《三命通会》| 神煞 calculation, 十二长生 (火土同论) |
| 《穷通宝鉴》| 调候用神 (120 rules) |
| 《渊海子平》| 纳音, 神煞 supplementary |

### 🛠️ Tech Stack

**Backend:**
- FastAPI 0.104+
- SQLAlchemy 2.0
- Pydantic 2.0
- SQLite (city database)

**Frontend:**
- React 18
- TypeScript 5
- Vite 5
- Zustand (state management)
- Ant Design (UI components)

---

<a name="中文"></a>
## 中文

### 📖 项目简介

一个专业的全栈八字排盘与命理分析Web应用。本系统基于传统历法算法，实现精准的四柱八字计算，并融合五本命理经典的解读体系。

### ✨ 核心功能

| 功能 | 说明 |
|------|------|
| **四柱排盘** | 基于节气精准计算年柱/月柱/日柱/时柱 |
| **藏干分析** | 含本气/中气/余气权重分析 |
| **十神映射** | 完整十神关系，含枭神夺食检测 |
| **神煞推算** | 20+种神煞，标注归属位置 |
| **十二长生** | 长生/沐浴/冠带/临官/帝旺/衰/病/死/墓/绝/胎/养 |
| **大运计算** | 起运年龄、交运年份、顺逆方向 |
| **格局判定** | 8正格 + 建禄/月刃格 |
| **用神/忌神** | 喜用神与忌神分析 |
| **调候用神** | 基于《穷通宝鉴》120条调候规则 |
| **白话解读** | 通俗易懂的命理解读报告（无文言文） |

### 🏗️ 项目结构

```
bazi-paipan/
├── backend/                    # Python FastAPI 后端
│   ├── app/
│   │   ├── core/              # 解读引擎
│   │   │   ├── constants.py         # 天干地支、十神、神煞常量表
│   │   │   ├── interpretation_engine_v2.py  # 五书深度解读
│   │   │   └── *_interpreter.py     # 大运/流年/神煞解读
│   │   ├── models/            # SQLAlchemy 数据模型
│   │   ├── routers/           # FastAPI 路由
│   │   │   └── bazi.py              # 主排盘接口
│   │   ├── schemas/           # Pydantic 请求/响应模型
│   │   └── services/          # 业务逻辑
│   │       └── bazi_calc.py         # 核心排盘引擎 (2000+ 行)
│   ├── data/
│   │   └── cities.csv         # 50+ 中国城市经纬度数据
│   └── docs/                  # API 与数据库文档
├── baZiApp/                   # React + TypeScript 前端
│   ├── src/
│   │   ├── components/        # UI 组件
│   │   │   ├── SiZhuDisplay.tsx     # 四柱展示
│   │   │   ├── WuXingDistribution.tsx  # 五行分布图
│   │   │   └── AnalysisReport.tsx   # 分析报告
│   │   ├── pages/
│   │   │   └── ResultPage.tsx       # 结果页面
│   │   ├── services/
│   │   │   └── baziService.ts       # API 集成
│   │   └── store/
│   │       └── appStore.ts          # Zustand 状态管理
├── knowledge_base/            # 命理知识图谱 (JSON)
│   ├── shensha_knowledge.json       # 神煞知识
│   ├── wuxing_knowledge.json        # 五行知识
│   ├── yongshen_knowledge.json      # 用神知识
│   └── tiaohou_knowledge.json       # 调候知识
├── true-solar-time/           # 真太阳时计算模块
└── geo_location_module/       # 地理位置工具
```

### 🚀 快速开始

#### 环境要求

- Python 3.10+
- Node.js 18+
- npm 或 yarn

#### 后端启动

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（可选，用于城市搜索）
python data/init_db.py

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 前端启动

```bash
cd baZiApp

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 访问地址

- **前端**: http://localhost:3000 (或下一个可用端口)
- **后端 API**: http://localhost:8000
- **API 文档 (Swagger)**: http://localhost:8000/docs

### 📚 API 接口

#### 排盘计算

```http
POST /api/bazi/calculate
Content-Type: application/json

{
  "birth_info": {
    "birth_date": "1988-02-22",
    "birth_time": "21:20",
    "gender": "male",
    "latitude": 39.904,
    "longitude": 116.407
  }
}
```

#### 返回字段

| 字段 | 说明 |
|------|------|
| `four_pillars` | 年柱/月柱/日柱/时柱 含天干/地支/藏干 |
| `shishen` | 四柱十神映射 |
| `shensha` | 神煞列表及归属位置 |
| `twelve_life_stages` | 四支十二长生 |
| `dayun` | 大运周期及时间 |
| `geju` | 格局判定 |
| `yongshen/jishen` | 用神/忌神 |
| `tiaohou` | 调候用神 |
| `analysis_report` | 白话文解读报告 (10个板块) |

#### 城市搜索

```http
GET /api/geo/search?name=北京
```

### 🧪 验证结果

以 1988-02-22 21:20 乾造为验收标准，对比 china95.net 参考排盘：

| 项目 | 结果 |
|------|------|
| 四柱 | ✅ 戊辰 甲寅 丁未 辛亥 |
| 藏干 | ✅ 乙己丁 / 甲丙戊 / 乙己丁 / 壬甲 |
| 神煞位置 | ✅ 8/8 全部匹配 |
| 大运方向 | ✅ 顺行 (阳男) |
| 起运年龄 | ✅ 4岁起运 |
| 童运 | ✅ 1岁甲寅 |

### 📖 经典参考

本系统融合五本命理经典的算法实现：

| 经典 | 应用 |
|------|------|
| 《滴天髓》 | 十神强弱分析、格局判定 |
| 《子平真诠》| 格局分类、用神选取 |
| 《三命通会》| 神煞推算、十二长生 (火土同论) |
| 《穷通宝鉴》| 调候用神 (120条规则) |
| 《渊海子平》| 纳音、神煞补充 |

### 🛠️ 技术栈

**后端:**
- FastAPI 0.104+
- SQLAlchemy 2.0
- Pydantic 2.0
- SQLite (城市数据库)

**前端:**
- React 18
- TypeScript 5
- Vite 5
- Zustand (状态管理)
- Ant Design (UI 组件)

### 📄 开源协议

MIT License

---

## 👨‍💻 Author / 作者

**风水 (Feng Shui)**

- GitHub: [richard3153](https://github.com/richard3153)
- Project: [bazi-paipan](https://github.com/richard3153/bazi-paipan)

## 🤝 Contributing / 贡献

Contributions are welcome! Please feel free to submit a Pull Request.

欢迎贡献代码！请提交 Pull Request。
