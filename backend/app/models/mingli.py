# app/models/mingli.py
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class MingLiKnowledge(Base):
    """
    命理知识库
    存储五本经典命理书籍的核心理论
    """
    __tablename__ = "mingli_knowledge"

    id = Column(Integer, primary_key=True, index=True)
    # 来源书籍
    source_book = Column(String(64), nullable=False, index=True)
    # 理论分类：十神/五行/格局/用神/大运/流年/神煞
    category = Column(String(32), nullable=False, index=True)
    # 标题/主题
    title = Column(String(128), nullable=False)
    # 正文内容
    content = Column(Text, nullable=False)
    # 标签（逗号分隔）
    tags = Column(String(256), nullable=True)

    def __repr__(self):
        return f"<MingLiKnowledge(category={self.category}, title={self.title})>"


class ShishenEntry(Base):
    """
    十神释义表
    详细解释每个十神的含义、旺衰、喜忌
    """
    __tablename__ = "shishen_entries"

    id = Column(Integer, primary_key=True, index=True)
    # 十神名称
    name = Column(String(16), nullable=False, index=True)
    # 五行属性
    wuxing = Column(String(8), nullable=False)
    # 阴阳属性（阳/阴）
    yinyang = Column(String(4), nullable=False)
    # 基本定义
    definition = Column(Text, nullable=False)
    # 性格特征
    personality = Column(Text, nullable=True)
    # 旺相休囚死状态描述
    conditions = Column(Text, nullable=True)
    # 喜忌规则
    preferences = Column(Text, nullable=True)
    # 来源书籍
    source_book = Column(String(64), nullable=True)

    def __repr__(self):
        return f"<ShishenEntry(name={self.name}, wuxing={self.wuxing})>"


class WuxingEntry(Base):
    """
    五行释义表
    五行旺相休囚死、各类喜忌
    """
    __tablename__ = "wuxing_entries"

    id = Column(Integer, primary_key=True, index=True)
    # 五行名称
    name = Column(String(8), nullable=False, index=True)
    # 阴阳
    yinyang = Column(String(4), nullable=False)
    # 基本含义
    meaning = Column(Text, nullable=False)
    # 旺相休囚死
    states = Column(Text, nullable=True)
    # 喜忌
    preferences = Column(Text, nullable=True)
    # 五行各季旺衰
    seasonal_strength = Column(Text, nullable=True)

    def __repr__(self):
        return f"<WuxingEntry(name={self.name})>"


class GeshiRule(Base):
    """
    格局判断规则表
    存储各种格局的判断条件和解读
    """
    __tablename__ = "geshi_rules"

    id = Column(Integer, primary_key=True, index=True)
    # 格局名称
    name = Column(String(32), nullable=False, index=True)
    # 格局分类：正格/变格/从格
    category = Column(String(16), nullable=False, index=True)
    # 判断条件（JSON格式）
    conditions = Column(Text, nullable=False)
    # 吉凶判断
    jixiong = Column(String(16), nullable=True)
    # 解读内容
    interpretation = Column(Text, nullable=False)
    # 来源书籍
    source_book = Column(String(64), nullable=True)

    def __repr__(self):
        return f"<GeshiRule(name={self.name}, category={self.category})>"
