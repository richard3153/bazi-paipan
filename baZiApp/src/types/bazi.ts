// 四柱八字核心类型定义

// 天干
export type TianGan = '甲' | '乙' | '丙' | '丁' | '戊' | '己' | '庚' | '辛' | '壬' | '癸';

// 地支
export type DiZhi = '子' | '丑' | '寅' | '卯' | '辰' | '巳' | '午' | '未' | '申' | '酉' | '戌' | '亥';

// 五行
export type WuXing = '金' | '木' | '水' | '火' | '土';

// 十神
export type ShiShen = '比肩' | '劫财' | '食神' | '伤官' | '正财' | '偏财' | '正官' | '七杀' | '正印' | '偏印' | '日主';

// 阴阳
export type YinYang = '阳' | '阴';

// 单柱（天干+地支）
export interface Zhu {
  tiangan: TianGan;
  dizhi: DiZhi;
  shishen?: ShiShen; // 十神关系
  canggan?: TianGan[]; // 藏干
}

// 四柱八字
export interface SiZhu {
  year: Zhu;  // 年柱
  month: Zhu; // 月柱
  day: Zhu;   // 日柱
  hour: Zhu;  // 时柱
}

// 五行统计
export interface WuXingCount {
  element: WuXing;
  count: number;
  percentage: number;
}

// 排盘输入参数
export interface PaiPanInput {
  name: string;
  gender: '男' | '女';
  birthDate: string; // YYYY-MM-DD
  birthTime: string; // HH:mm
  birthPlace: string; // 出生地
  longitude?: number; // 经度
  latitude?: number;  // 纬度
  paipanMode?: 'simple' | 'full'; // 排盘模式：simple=普通式, full=全排
}

// 排盘结果
export interface PaiPanResult {
  input: PaiPanInput;
  sizhu: SiZhu;
  wuxing: WuXingCount[];
  dayMaster: TianGan; // 日主
  dayMasterStrength: '强' | '弱' | '中和';
  analysis: AnalysisReport;
  // 全排专属字段（普通式为空）
  taiyuan?: { tiangan: TianGan; dizhi: DiZhi };
  minggong?: { tiangan: TianGan; dizhi: DiZhi };
  shengong?: { tiangan: TianGan; dizhi: DiZhi };
  dayun?: DaYun[];
  liunian?: LiuNian[];
  xiaoyun?: XiaoYun;
  tongyun?: TongYun[];
  shensha?: ShenShaResult;
  emptyPosition?: string[];
  // 起运信息（扩展字段）
  qiyun?: QiYunInfo;
}

// 起运信息
export interface QiYunInfo {
  forward: boolean;
  direction: string;  // 顺行/逆行
  startAge: number;    // 实岁
  startAgeXu: number;  // 虚岁
  qiyunDays: number;   // 起运天数
  qiyunMonths: number; // 起运月数
  refTerm: string;     // 参考节气
  jiaoyunYear: number; // 交运年份
  jiaoyunMonth: number; // 交运月份
}

// 分析解读报告
export interface AnalysisReport {
  overview: string; // 总体概述
  dayMasterAnalysis: string; // 日主分析
  wuxingAnalysis: string; // 五行分析
  shishenAnalysis: string; // 十神分析
  wealth: string; // 财运
  career: string; // 事业
  health: string; // 健康
  marriage: string; // 婚姻
  education: string; // 学业
  suggestions: string[]; // 建议
}

// 大运
export interface DaYun {
  index: number; // 第几步大运（从0开始）
  startAge: number; // 起运年龄
  endAge: number; // 截止年龄
  tiangan: TianGan; // 天干
  dizhi: DiZhi; // 地支
  shishen: ShiShen; // 十神
  startYear: number; // 起始年份
  endYear: number; // 结束年份
}

// 流年
export interface LiuNian {
  year: number; // 年份
  tiangan: TianGan; // 天干
  dizhi: DiZhi; // 地支
  shishen: ShiShen; // 十神（相对于日主）
  dayMasterRelation: string; // 与日主的关系
}

// 小运
export interface XiaoYun {
  year: number;
  tiangan: TianGan;
  dizhi: DiZhi;
}

// 童运
export interface TongYun {
  age: number; // 年龄（1-12岁）
  tiangan: TianGan;
  dizhi: DiZhi;
  shishen: ShiShen;
}

// 神煞
export interface ShenSha {
  name: string; // 神煞名称
  position: '年柱' | '月柱' | '日柱' | '时柱' | '年干' | '月干' | '日干' | '时干' | '年支' | '月支' | '日支' | '时支';
  description?: string;
}

// 神煞结果
export interface ShenShaResult {
  yearPillar: ShenSha[]; // 年柱神煞
  monthPillar: ShenSha[]; // 月柱神煞
  dayPillar: ShenSha[]; // 日柱神煞
  hourPillar: ShenSha[]; // 时柱神煞
  all: ShenSha[]; // 所有神煞
}

// 旺衰
export type WangShuai = '长生' | '沐浴' | '冠带' | '临官' | '帝旺' | '衰' | '病' | '死' | '墓' | '绝' | '胎' | '养';

// 纳音
export interface NaYin {
  element: string; // 纳音五行
  description: string; // 纳音描述
}

// 扩展的四柱（包含更多信息）
export interface ZhuDetail extends Zhu {
  wangShuai?: WangShuai; // 旺衰
  nayin?: string; // 纳音
  shishenDetail?: {
    tiangan: ShiShen;
    dizhi: ShiShen;
  };
}

// 扩展的排盘结果
export interface PaiPanResultExtended extends PaiPanResult {
  sizhuDetail: {
    year: ZhuDetail;
    month: ZhuDetail;
    day: ZhuDetail;
    hour: ZhuDetail;
  };
  dayun: DaYun[]; // 大运
  shenSha: ShenShaResult; // 神煞
  xiaoYun?: XiaoYun; // 当前小运
  tongYun?: TongYun[]; // 童运
  emptyPosition: string[]; // 空亡位置
}

// API响应
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
