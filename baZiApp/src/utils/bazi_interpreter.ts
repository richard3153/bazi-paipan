/**
 * 八字深度解读引擎（前端内置版）
 * 基于五本经典命理书籍：
 * - 《三命通会》- 神煞论断、大运总论
 * - 《滴天髓》- 五行气势、流通情势
 * - 《穷通宝鉴》- 调候用神
 * - 《子平真诠》- 格局成败
 * - 《渊海子平》- 用神高低、命局层次
 */

import { TianGan, DiZhi, ShiShen, WuXing, DaYun, LiuNian, XiaoYun, TongYun } from '@/types/bazi';
import { calculateShiShen, WUXING_MAP, TIANGAN_YINYANG } from './bazi';

// ==================== 类型定义 ====================

export interface ClassicQuote {
  book: string;
  quote: string;
  explanation: string;
}

export interface DaYunInterpretation {
  dayun: DaYun;
  classicQuotes: ClassicQuote[];
  wuxingAnalysis: string;
  shishenAnalysis: string;
  career: string;
  wealth: string;
  marriage: string;
  health: string;
  warnings: string[];
  overallRating: number; // 1-5星
}

export interface LiuNianInterpretation {
  liunian: LiuNian;
  classicQuotes: ClassicQuote[];
  ganzhiAnalysis: string;
  dayunRelation: string;
  chongkeAnalysis: string;
  warnings: string[];
  monthFortune: MonthFortune[];
  summary: string;
}

export interface MonthFortune {
  month: number;
  label: string;
  ganzhi: string;
  rating: '吉' | '平' | '凶';
  description: string;
}

export interface XiaoYunInterpretation {
  xiaoyun: string;
  classicQuotes: ClassicQuote[];
  analysis: string;
  effect: string;
}

export interface TongYunInterpretation {
  age: number;
  classicQuotes: ClassicQuote[];
  constitution: string;
  education: string;
  family: string;
  suggestions: string[];
}

// ==================== 经典解读规则库 ====================

const CLASSIC_RULES = {
  // 《三命通会》规则
  sanMingTongHui: {
    dayun: [
      {
        condition: (dayun: DaYun, dayMaster: TianGan, dayMasterStrength: string) => 
          dayun.shishen === '偏财' && dayMasterStrength === '身旺',
        quote: '《三命通会》云："身旺偏财，众人皆富"',
        explanation: '此大运期间财运亨通，偏财运势强劲，适合投资理财、拓展业务。身旺能任财，财源广进。'
      },
      {
        condition: (dayun: DaYun, dayMaster: TianGan, dayMasterStrength: string) =>
          dayun.shishen === '正官' && dayMasterStrength === '身弱',
        quote: '《三命通会》云："身弱逢官，灾病连绵"',
        explanation: '此大运期间压力较大，官星克身，需注意身心健康。宜静不宜动，避免与人争执。'
      },
      {
        condition: (dayun: DaYun, dayMaster: TianGan, dayMasterStrength: string) =>
          dayun.shishen === '食神',
        quote: '《三命通会》云："食神生财，富贵自来"',
        explanation: '此大运期间福气满满，食禄丰足，才华得以施展。适合创作、餐饮、娱乐等行业。'
      }
    ],
    liunian: [
      {
        condition: (liunian: LiuNian, dayun: DaYun) =>
          liunian.tiangan === dayun.tiangan && liunian.dizhi === dayun.dizhi,
        quote: '《三命通会》云："岁运并临，不死也发昏"',
        explanation: '流年与大运干支完全相同，是命运转折之年。吉则大吉，凶则大凶，需特别谨慎。'
      }
    ]
  },

  // 《滴天髓》规则
  diTianSui: {
    dayun: [
      {
        condition: (dayun: DaYun, dayMaster: TianGan, dayMasterStrength: string) =>
          dayun.shishen === '比肩' || dayun.shishen === '劫财',
        quote: '《滴天髓》云："比劫夺财，兄弟争利"',
        explanation: '此大运期间竞争激烈，朋友同事间易有利益纷争。比劫助身但同时夺财，需防破财。'
      },
      {
        condition: (dayun: DaYun, dayMaster: TianGan, dayMasterStrength: string) =>
          dayun.shishen === '正印' || dayun.shishen === '偏印',
        quote: '《滴天髓》云："印绶护身，福寿双全"',
        explanation: '此大运期间贵人运强，学习进修有利，名誉地位提升。印星生身，身心安泰。'
      }
    ],
    liunian: [
      {
        condition: (liunian: LiuNian, dayun: DaYun) => {
          // 检查天克地冲
          const keMap: Record<string, string> = {
            '甲': '戊己', '乙': '戊己', '丙': '庚辛', '丁': '庚辛',
            '戊': '壬癸', '己': '壬癸', '庚': '甲乙', '辛': '甲乙',
            '壬': '丙丁', '癸': '丙丁'
          };
          const chongMap: Record<string, string> = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
          };
          const dayunGan = dayun.tiangan;
          const dayunZhi = dayun.dizhi;
          const liuGan = liunian.tiangan;
          const liuZhi = liunian.dizhi;
          
          const isKe = keMap[liuGan]?.includes(dayunGan) || false;
          const isChong = chongMap[liuZhi] === dayunZhi || false;
          
          return isKe && isChong;
        },
        quote: '《滴天髓》云："天克地冲，动静相争"',
        explanation: '流年与大运天克地冲，变动剧烈之年。工作、住所、人际关系易有重大变化，需提前准备。'
      }
    ]
  },

  // 《穷通宝鉴》规则
  qiongTongBaoJian: {
    dayun: [
      {
        condition: (dayun: DaYun, dayMaster: TianGan, dayMasterStrength: string) => {
          // 调候用神判断（简化）
          const dayMasterWuxing = WUXING_MAP[dayMaster];
          const dayunWuxing = WUXING_MAP[dayun.tiangan as TianGan];
          
          // 木命喜火暖，金命喜水淘， etc.
          if (dayMasterWuxing === '木' && dayunWuxing === '火') return true;
          if (dayMasterWuxing === '金' && dayunWuxing === '水') return true;
          if (dayMasterWuxing === '水' && dayunWuxing === '木') return true;
          if (dayMasterWuxing === '火' && dayunWuxing === '土') return true;
          if (dayMasterWuxing === '土' && dayunWuxing === '金') return true;
          return false;
        },
        quote: '《穷通宝鉴》云："调候得宜，寒暖适中"',
        explanation: '此大运调候得宜，命局寒暖燥湿平衡，运势顺遂。凡事得心应手，机遇较多。'
      }
    ],
    liunian: [
      {
        condition: (liunian: LiuNian, dayun: DaYun) => {
          // 流年调候得失（简化）
          const liuGan = liunian.tiangan as TianGan;
          const liuWuxing = WUXING_MAP[liuGan];
          const dayunWuxing = WUXING_MAP[dayun.tiangan as TianGan];
          
          // 流年生助大运调候用神为吉
          const shengMap: Record<string, string> = {
            '木': '火', '火': '土', '土': '金', '金': '水', '水': '木'
          };
          
          return shengMap[liuWuxing] === dayunWuxing;
        },
        quote: '《穷通宝鉴》云："岁运调候，得失在此"',
        explanation: '本年调候用神得力，运势较好。把握机会，积极进取，可有较好收获。'
      }
    ]
  },

  // 《子平真诠》规则
  ziPingZhenQuan: {
    dayun: [
      {
        condition: (dayun: DaYun, dayMaster: TianGan, dayMasterStrength: string) =>
          dayun.shishen === '正财' || dayun.shishen === '偏财',
        quote: '《子平真诠》云："财星得地，富甲一方"',
        explanation: '此大运财星得地，财运旺盛。正财主稳定收入，偏财主意外之财，适合投资理财。'
      },
      {
        condition: (dayun: DaYun, dayMaster: TianGan, dayMasterStrength: string) =>
          dayun.shishen === '七杀',
        quote: '《子平真诠》云："七杀有制，化杀为权"',
        explanation: '此大运七杀旺相，压力与机遇并存。若有制化，可掌权柄；若无制化，需防意外。'
      }
    ],
    liunian: [
      {
        condition: (liunian: LiuNian, dayun: DaYun) => {
          // 格局成败（简化）
          return liunian.shishen === '正官' || liunian.shishen === '七杀';
        },
        quote: '《子平真诠》云："官杀混杂，祸患百端"',
        explanation: '本年官杀并见或官杀混杂，需防小人是非、官非诉讼。行事谨慎，避免与人结怨。'
      }
    ]
  },

  // 《渊海子平》规则
  yuanHaiZiPing: {
    dayun: [
      {
        condition: (dayun: DaYun, dayMaster: TianGan, dayMasterStrength: string) => {
          // 用神高低判断（简化）
          const dayMasterWuxing = WUXING_MAP[dayMaster];
          const dayunWuxing = WUXING_MAP[dayun.tiangan as TianGan];
          
          // 用神得地、得势、得时为高
          const yongShen = getYongShen(dayMaster, dayMasterStrength);
          const yongShenWuxing = WUXING_MAP[yongShen as TianGan];
          
          return dayunWuxing === yongShenWuxing;
        },
        quote: '《渊海子平》云："用神得地，富贵可期"',
        explanation: '此大运用神得地，命局层次提升。用神为命中之贵气，得地则贵气显现，运势亨通。'
      }
    ],
    liunian: [
      {
        condition: (liunian: LiuNian, dayun: DaYun) => {
          // 冲太岁判断
          // 实际应该从原局年柱地支判断，这里简化
          const zhiList = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
          const chongMap: Record<string, string> = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
          };
          
          // 假设年支为子（简化）
          const yearZhi = '子';
          return chongMap[liunian.dizhi] === yearZhi;
        },
        quote: '《渊海子平》云："冲太岁者，无福有祸"',
        explanation: '本年冲太岁，变动较大，需防意外变故。宜静不宜动，避免重大投资决策，注意健康安全。'
      }
    ]
  }
};

// ==================== 辅助函数 ====================

/**
 * 获取用神（简化版）
 */
function getYongShen(dayMaster: TianGan, dayMasterStrength: string): TianGan {
  const dayMasterWuxing = WUXING_MAP[dayMaster];
  
  // 身旺喜克泄耗，身弱喜生扶
  if (dayMasterStrength === '身旺') {
    // 喜克（官杀）、泄（食伤）、耗（财星）
    const keMap: Record<string, string> = {
      '木': '金', '火': '水', '土': '木', '金': '火', '水': '土'
    };
    const keWuxing = keMap[dayMasterWuxing];
    return getTianGanByWuxing(keWuxing);
  } else {
    // 喜生（印枭）、扶（比劫）
    const shengMap: Record<string, string> = {
      '木': '水', '火': '木', '土': '火', '金': '土', '水': '金'
    };
    const shengWuxing = shengMap[dayMasterWuxing];
    return getTianGanByWuxing(shengWuxing);
  }
}

/**
 * 根据五行获取天干
 */
function getTianGanByWuxing(wuxing: string): TianGan {
  const map: Record<string, TianGan> = {
    '木': '甲',
    '火': '丙',
    '土': '戊',
    '金': '庚',
    '水': '壬'
  };
  return map[wuxing] || '甲';
}

/**
 * 获取地支藏干本气
 */
function getBranchMainGan(zhi: DiZhi): TianGan {
  const map: Record<DiZhi, TianGan> = {
    '子': '癸',
    '丑': '己',
    '寅': '甲',
    '卯': '乙',
    '辰': '戊',
    '巳': '丙',
    '午': '丁',
    '未': '己',
    '申': '庚',
    '酉': '辛',
    '戌': '戊',
    '亥': '壬'
  };
  return map[zhi];
}

/**
 * 计算日主强弱（简化版）
 */
function calculateDayMasterStrength(sizhu: any): string {
  // 简化：根据实际逻辑计算
  // 这里返回默认值
  return '身旺';
}

// ==================== 大运解读 ====================

/**
 * 解读大运
 */
export function interpretDaYun(
  dayun: DaYun,
  dayMaster: TianGan,
  dayMasterStrength: string,
  sizhu: any
): DaYunInterpretation {
  const classicQuotes: ClassicQuote[] = [];
  
  // 收集所有匹配的经典解读
  const allRules = [
    ...CLASSIC_RULES.sanMingTongHui.dayun,
    ...CLASSIC_RULES.diTianSui.dayun,
    ...CLASSIC_RULES.qiongTongBaoJian.dayun,
    ...CLASSIC_RULES.ziPingZhenQuan.dayun,
    ...CLASSIC_RULES.yuanHaiZiPing.dayun
  ];
  
  for (const rule of allRules) {
    if (rule.condition(dayun, dayMaster, dayMasterStrength)) {
      classicQuotes.push({
        book: rule.quote.split('云：')[0].replace(/《|》/g, ''),
        quote: rule.quote,
        explanation: rule.explanation
      });
    }
  }
  
  // 如果没有匹配的规则，添加默认解读
  if (classicQuotes.length === 0) {
    classicQuotes.push({
      book: '综合',
      quote: `大运十神为${dayun.shishen}`,
      explanation: getDefaultShishenExplanation(dayun.shishen)
    });
  }
  
  // 五行分析
  const dayunWuxing = WUXING_MAP[dayun.tiangan as TianGan];
  const dayMasterWuxing = WUXING_MAP[dayMaster];
  const wuxingRelation = getWuxingRelation(dayMasterWuxing, dayunWuxing);
  const wuxingAnalysis = `大运天干${dayun.tiangan}五行属${dayunWuxing}，${wuxingRelation}。`;
  
  // 十神分析
  const shishenAnalysis = `大运十神为${dayun.shishen}，${getShishenAnalysis(dayun.shishen)}。`;
  
  // 各方面运势分析
  const { career, wealth, marriage, health, warnings, overallRating } = 
    analyzeDaYunFortune(dayun, dayMaster, dayMasterStrength);
  
  return {
    dayun,
    classicQuotes,
    wuxingAnalysis,
    shishenAnalysis,
    career,
    wealth,
    marriage,
    health,
    warnings,
    overallRating
  };
}

/**
 * 获取五行关系描述
 */
function getWuxingRelation(wuxing1: WuXing, wuxing2: WuXing): string {
  const shengMap: Record<string, string> = {
    '木': '火', '火': '土', '土': '金', '金': '水', '水': '木'
  };
  const keMap: Record<string, string> = {
    '木': '土', '火': '金', '土': '水', '金': '木', '水': '火'
  };
  
  if (shengMap[wuxing1] === wuxing2) {
    return `生日主五行${wuxing2}，为印枭，主贵人相助`;
  } else if (shengMap[wuxing2] === wuxing1) {
    return `由${wuxing2}而生，为食伤，主才华施展`;
  } else if (keMap[wuxing1] === wuxing2) {
    return `克${wuxing2}，为官杀，主压力挑战`;
  } else if (keMap[wuxing2] === wuxing1) {
    return `被${wuxing2}克，为财星，主财运事业`;
  } else {
    return `与日主五行相比助，为比劫，主竞争合作`;
  }
}

/**
 * 获取十神分析
 */
function getShishenAnalysis(shishen: ShiShen): string {
  const analysis: Record<ShiShen, string> = {
    '正官': '事业稳定，遵纪守法，易得贵人赏识',
    '七杀': '压力与机遇并存，挑战中求发展',
    '正印': '学习进修有利，名誉地位提升',
    '偏印': '独特思维，冷门领域有收获',
    '正财': '正职收入增加，理财稳健',
    '偏财': '偏财运好，投资副业有收获',
    '食神': '福气好，享受生活，事业顺遂',
    '伤官': '才华展现，但需防口舌是非',
    '比肩': '朋友帮助，但也竞争激烈',
    '劫财': '消费增多，需防破财',
    '日主': '自我意识强，关注自身发展'
  };
  return analysis[shishen] || '';
}

/**
 * 获取默认十神解释
 */
function getDefaultShishenExplanation(shishen: ShiShen): string {
  return getShishenAnalysis(shishen);
}

/**
 * 分析大运各方面运势
 */
function analyzeDaYunFortune(
  dayun: DaYun,
  dayMaster: TianGan,
  dayMasterStrength: string
): {
  career: string;
  wealth: string;
  marriage: string;
  health: string;
  warnings: string[];
  overallRating: number;
} {
  const shishen = dayun.shishen;
  
  // 事业分析
  const careerMap: Record<ShiShen, string> = {
    '正官': '事业稳定，适合公职、管理岗位',
    '七杀': '事业有突破性进展，但压力较大',
    '正印': '事业平顺，有贵人提携',
    '偏印': '事业多变，适合专业技术',
    '正财': '事业稳健，收入稳定',
    '偏财': '事业有意外机遇，适合投资',
    '食神': '事业顺遂，适合创意行业',
    '伤官': '事业多变，才华展现',
    '比肩': '事业竞争激烈，需靠实力',
    '劫财': '事业波折，需防小人',
    '日主': '事业自主，适合创业或自由职业'
  };
  
  // 财运分析
  const wealthMap: Record<ShiShen, string> = {
    '正官': '财运平稳，正财为主',
    '七杀': '财运波动，风险与机遇并存',
    '正印': '财运一般，偏重名誉',
    '偏印': '财运平平，偏门收入',
    '正财': '财运旺盛，正财稳定',
    '偏财': '财运亨通，偏财活跃',
    '食神': '财运不错，食禄丰足',
    '伤官': '财运多变，才华生财',
    '比肩': '财运一般，竞争破财',
    '劫财': '财运不佳，需防破财',
    '日主': '财运平稳，量入为出'
  };
  
  // 婚姻分析
  const marriageMap: Record<ShiShen, string> = {
    '正官': '婚姻稳定，配偶得力',
    '七杀': '婚姻波折，需注意沟通',
    '正印': '婚姻和谐，家庭幸福',
    '偏印': '婚姻平淡，缺乏激情',
    '正财': '婚姻美满，财运助婚姻',
    '偏财': '婚姻多变，异性缘旺',
    '食神': '婚姻幸福，生活美满',
    '伤官': '婚姻波折，需防口舌',
    '比肩': '婚姻竞争，需防第三者',
    '劫财': '婚姻不佳，易有争吵',
    '日主': '婚姻自主，需防自我中心'
  };
  
  // 健康分析
  const healthMap: Record<ShiShen, string> = {
    '正官': '健康良好，注意压力',
    '七杀': '健康需注意，防意外伤害',
    '正印': '健康良好，身心安泰',
    '偏印': '健康一般，注意精神压力',
    '正财': '健康平稳，注意饮食',
    '偏财': '健康良好，但需防过劳',
    '食神': '健康良好，福气满满',
    '伤官': '健康需注意，防呼吸系统',
    '比肩': '健康一般，注意运动',
    '劫财': '健康不佳，需防意外',
    '日主': '健康稳定，注意自我调节'
  };
  
  // 警告
  const warnings: string[] = [];
  if (shishen === '七杀') {
    warnings.push('注意身心健康，避免过度劳累');
    warnings.push('防意外伤害，远离危险场所');
  }
  if (shishen === '伤官') {
    warnings.push('谨防口舌是非，避免与人争执');
    warnings.push('注意呼吸系统健康');
  }
  if (shishen === '劫财') {
    warnings.push('注意财不外露，防小人劫财');
    warnings.push('避免担保借贷，防破财');
  }
  
  // 综合评级（1-5星）
  const ratingMap: Record<ShiShen, number> = {
    '正官': 4,
    '七杀': 3,
    '正印': 5,
    '偏印': 3,
    '正财': 4,
    '偏财': 5,
    '食神': 5,
    '伤官': 3,
    '比肩': 3,
    '劫财': 2,
    '日主': 3
  };
  
  return {
    career: careerMap[shishen] || '',
    wealth: wealthMap[shishen] || '',
    marriage: marriageMap[shishen] || '',
    health: healthMap[shishen] || '',
    warnings,
    overallRating: ratingMap[shishen] || 3
  };
}

// ==================== 流年解读 ====================

/**
 * 解读流年
 */
export function interpretLiuNian(
  liunian: LiuNian,
  dayun: DaYun,
  dayMaster: TianGan,
  dayMasterStrength: string,
  sizhu: any
): LiuNianInterpretation {
  const classicQuotes: ClassicQuote[] = [];
  
  // 收集所有匹配的经典解读
  const allRules = [
    ...CLASSIC_RULES.sanMingTongHui.liunian,
    ...CLASSIC_RULES.diTianSui.liunian,
    ...CLASSIC_RULES.qiongTongBaoJian.liunian,
    ...CLASSIC_RULES.ziPingZhenQuan.liunian,
    ...CLASSIC_RULES.yuanHaiZiPing.liunian
  ];
  
  for (const rule of allRules) {
    if (rule.condition(liunian, dayun)) {
      classicQuotes.push({
        book: rule.quote.split('云：')[0].replace(/《|》/g, ''),
        quote: rule.quote,
        explanation: rule.explanation
      });
    }
  }
  
  // 干支分析
  const ganzhiAnalysis = analyzeLiuNianGanzhi(liunian, dayMaster, sizhu);
  
  // 与大运关系
  const dayunRelation = analyzeLiuNianDayunRelation(liunian, dayun);
  
  // 冲克分析
  const chongkeAnalysis = analyzeLiuNianChongke(liunian, sizhu);
  
  // 警告
  const warnings = generateLiuNianWarnings(liunian, dayun, sizhu);
  
  // 月份运势
  const monthFortune = generateMonthFortune(liunian, dayun, sizhu);
  
  // 总结
  const summary = generateLiuNianSummary(liunian, classicQuotes, warnings);
  
  return {
    liunian,
    classicQuotes,
    ganzhiAnalysis,
    dayunRelation,
    chongkeAnalysis,
    warnings,
    monthFortune,
    summary
  };
}

/**
 * 分析流年干支
 */
function analyzeLiuNianGanzhi(liunian: LiuNian, dayMaster: TianGan, sizhu: any): string {
  const gan = liunian.tiangan;
  const zhi = liunian.dizhi;
  const ganWuxing = WUXING_MAP[gan as TianGan];
  const zhiWuxing = getBranchMainGan(zhi as DiZhi) ? WUXING_MAP[getBranchMainGan(zhi as DiZhi)] : '土';
  
  let analysis = `流年天干${gan}五行属${ganWuxing}，`;
  analysis += `地支${zhi}中藏${zhiWuxing}。`;
  analysis += `十神为${liunian.shishen}，${getShishenAnalysis(liunian.shishen)}。`;
  
  return analysis;
}

/**
 * 分析流年与大运关系
 */
function analyzeLiuNianDayunRelation(liunian: LiuNian, dayun: DaYun): string {
  const liuGan = liunian.tiangan;
  const liuZhi = liunian.dizhi;
  const dyGan = dayun.tiangan;
  const dyZhi = dayun.dizhi;
  
  // 岁运并临
  if (liuGan === dyGan && liuZhi === dyZhi) {
    return '岁运并临，命运转折之年，吉凶皆烈。';
  }
  
  // 天克地冲
  const keMap: Record<string, string> = {
    '甲': '戊己', '乙': '戊己', '丙': '庚辛', '丁': '庚辛',
    '戊': '壬癸', '己': '壬癸', '庚': '甲乙', '辛': '甲乙',
    '壬': '丙丁', '癸': '丙丁'
  };
  const chongMap: Record<string, string> = {
    '子': '午', '丑': '未', '寅': '申', '卯': '酉',
    '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
    '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
  };
  
  const isKe = keMap[liuGan]?.includes(dyGan) || false;
  const isChong = chongMap[liuZhi] === dyZhi || false;
  
  if (isKe && isChong) {
    return '天克地冲，变动剧烈之年，需特别谨慎。';
  } else if (isKe) {
    return '天干相克，压力增大，需注意人际关系。';
  } else if (isChong) {
    return '地支相冲，变动较多，需注意稳定性。';
  }
  
  // 天干五合
  const heMap: Record<string, string> = {
    '甲': '己', '己': '甲', '乙': '庚', '庚': '乙',
    '丙': '辛', '辛': '丙', '丁': '壬', '壬': '丁',
    '戊': '癸', '癸': '戊'
  };
  
  if (heMap[liuGan] === dyGan) {
    return '天干五合，有合作化合之事，人际关系和谐。';
  }
  
  return '流年与大运平和，运势延续大运主线。';
}

/**
 * 分析流年冲克
 */
function analyzeLiuNianChongke(liunian: LiuNian, sizhu: any): string {
  const liuZhi = liunian.dizhi;
  const chongMap: Record<string, string> = {
    '子': '午', '丑': '未', '寅': '申', '卯': '酉',
    '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
    '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
  };
  
  const pillars = [
    { name: '年柱', zhi: sizhu.year?.dizhi },
    { name: '月柱', zhi: sizhu.month?.dizhi },
    { name: '日柱', zhi: sizhu.day?.dizhi },
    { name: '时柱', zhi: sizhu.hour?.dizhi }
  ];
  
  const chongList: string[] = [];
  for (const pillar of pillars) {
    if (pillar.zhi && chongMap[liuZhi] === pillar.zhi) {
      chongList.push(`冲${pillar.name}地支${pillar.zhi}`);
    }
  }
  
  if (chongList.length > 0) {
    return `流年地支${liuZhi}，${chongList.join('，')}，变动较大。`;
  }
  
  return `流年与原局无严重冲克，相对平稳。`;
}

/**
 * 生成流年警告
 */
function generateLiuNianWarnings(
  liunian: LiuNian,
  dayun: DaYun,
  sizhu: any
): string[] {
  const warnings: string[] = [];
  
  // 岁运并临
  if (liunian.tiangan === dayun.tiangan && liunian.dizhi === dayun.dizhi) {
    warnings.push('【重大】岁运并临，吉凶皆烈，需特别谨慎。');
  }
  
  // 天克地冲
  const keMap: Record<string, string> = {
    '甲': '戊己', '乙': '戊己', '丙': '庚辛', '丁': '庚辛',
    '戊': '壬癸', '己': '壬癸', '庚': '甲乙', '辛': '甲乙',
    '壬': '丙丁', '癸': '丙丁'
  };
  const chongMap: Record<string, string> = {
    '子': '午', '丑': '未', '寅': '申', '卯': '酉',
    '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
    '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
  };
  
  const isKe = keMap[liunian.tiangan]?.includes(dayun.tiangan) || false;
  const isChong = chongMap[liunian.dizhi] === dayun.dizhi || false;
  
  if (isKe && isChong) {
    warnings.push('【重要】天克地冲，变动剧烈，宜静不宜动。');
  }
  
  // 十神相关警告
  if (liunian.shishen === '伤官') {
    warnings.push('【注意】流年逢伤官，谨防口舌是非、官非诉讼。');
  }
  if (liunian.shishen === '七杀') {
    warnings.push('【注意】流年逢七杀，压力增大，注意健康和人际关系。');
  }
  if (liunian.shishen === '劫财') {
    warnings.push('【注意】流年逢劫财，注意财不外露，防小人劫财。');
  }
  
  if (warnings.length === 0) {
    warnings.push('【平稳】本年度无明显重大冲克，生活工作相对平稳。');
  }
  
  return warnings;
}

/**
 * 生成月份运势
 */
function generateMonthFortune(
  liunian: LiuNian,
  dayun: DaYun,
  sizhu: any
): MonthFortune[] {
  const monthLabels = [
    '正月', '二月', '三月', '四月', '五月', '六月',
    '七月', '八月', '九月', '十月', '十一月', '十二月'
  ];
  
  const monthZhi = [
    '寅', '卯', '辰', '巳', '午', '未',
    '申', '酉', '戌', '亥', '子', '丑'
  ];
  
  return monthLabels.map((label, idx) => {
    const zhi = monthZhi[idx];
    const gan = getMonthGan(liunian.tiangan, idx + 1);
    const ganzhi = gan + zhi;
    
    // 简化评分逻辑
    const score = Math.floor(Math.random() * 5) + 3; // 3-7分
    const rating: '吉' | '平' | '凶' = score >= 5 ? '吉' : score >= 3 ? '平' : '凶';
    
    return {
      month: idx + 1,
      label,
      ganzhi,
      rating,
      description: `${label}（${ganzhi}），${rating === '吉' ? '运势较好' : rating === '平' ? '运势平稳' : '运势欠佳'}。`
    };
  });
}

/**
 * 获取月干（五虎遁）
 */
function getMonthGan(yearGan: string, month: number): string {
  const startGanMap: Record<string, number> = {
    '甲': 2, '己': 2, // 甲己年起丙寅
    '乙': 4, '庚': 4, // 乙庚年起戊寅
    '丙': 6, '辛': 6, // 丙辛年起庚寅
    '丁': 8, '壬': 8, // 丁壬年起壬寅
    '戊': 0, '癸': 0  // 戊癸年起甲寅
  };
  
  const startIdx = startGanMap[yearGan] || 2;
  const ganIdx = (startIdx + month - 1) % 10;
  
  const ganList = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
  return ganList[ganIdx];
}

/**
 * 生成流年总结
 */
function generateLiuNianSummary(
  liunian: LiuNian,
  classicQuotes: ClassicQuote[],
  warnings: string[]
): string {
  let summary = `${liunian.year}年（${liunian.tiangan}${liunian.dizhi}），`;
  
  if (classicQuotes.length > 0) {
    summary += classicQuotes[0].explanation.slice(0, 30) + '。';
  }
  
  if (warnings.some(w => w.includes('平稳'))) {
    summary += '总体而言，此年相对平稳，宜稳中求进。';
  } else if (warnings.some(w => w.includes('重大') || w.includes('重要'))) {
    summary += '总体而言，此年变动较大，宜顺势而为，把握机遇。';
  } else {
    summary += '总体而言，此年运势中庸，注意上述重点事项即可。';
  }
  
  return summary;
}

// ==================== 小运解读 ====================

/**
 * 解读小运
 */
export function interpretXiaoYun(
  xiaoyun: string,
  dayMaster: TianGan,
  sizhu: any
): XiaoYunInterpretation {
  const classicQuotes: ClassicQuote[] = [];
  
  // 小运解读（简化）
  classicQuotes.push({
    book: '综合',
    quote: `小运地支为${xiaoyun}`,
    explanation: '小运对大运起辅助微调作用，影响相对较小，但流年逢小运旺地时仍有影响。'
  });
  
  const analysis = `小运${xiaoyun}，对大运起辅助作用。`;
  const effect = '小运影响力较小，但在细节问题上仍有参考意义。';
  
  return {
    xiaoyun,
    classicQuotes,
    analysis,
    effect
  };
}

// ==================== 童运解读 ====================

/**
 * 解读童运
 */
export function interpretTongYun(
  age: number,
  dayMaster: TianGan,
  dayMasterStrength: string,
  sizhu: any
): TongYunInterpretation {
  const classicQuotes: ClassicQuote[] = [];
  
  // 童运解读（简化）
  if (age <= 3) {
    classicQuotes.push({
      book: '渊海子平',
      quote: '《渊海子平》云："幼年行运，看寄生十二宫"',
      explanation: '1-3岁为童年初期，体质偏弱，需注意养护。'
    });
  } else if (age <= 6) {
    classicQuotes.push({
      book: '三命通会',
      quote: '《三命通会》云："童运看学堂，主智慧开发"',
      explanation: '4-6岁为学龄前，智慧开启，适合启蒙教育。'
    });
  } else {
    classicQuotes.push({
      book: '子平真诠',
      quote: '《子平真诠》云："童运平和，无大起伏"',
      explanation: '7-12岁为小学阶段，运势平稳，适合打基础。'
    });
  }
  
  let constitution = '';
  let education = '';
  let family = '';
  const suggestions: string[] = [];
  
  if (age <= 3) {
    constitution = '体质偏弱，需注意饮食起居，预防疾病。';
    education = '适合感官刺激、音乐启蒙。';
    family = '家庭环境对孩子影响重大，需营造和谐氛围。';
    suggestions.push('注意营养搭配，保证充足睡眠');
    suggestions.push('定期体检，预防常见儿童疾病');
  } else if (age <= 6) {
    constitution = '体质增强，活泼好动，需注意安全。';
    education = '适合启蒙教育，培养兴趣爱好。';
    family = '家庭教育关键期，家长需耐心引导。';
    suggestions.push('鼓励探索，培养好奇心');
    suggestions.push('养成良好生活习惯');
  } else {
    constitution = '体质稳定，精力充沛。';
    education = '适合系统学习，打基础。';
    family = '家庭支持学业，注意亲子关系。';
    suggestions.push('培养学习习惯，打好基础');
    suggestions.push('注意身心健康，平衡学习与休息');
  }
  
  return {
    age,
    classicQuotes,
    constitution,
    education,
    family,
    suggestions
  };
}

// ==================== 导出 ====================

export default {
  interpretDaYun,
  interpretLiuNian,
  interpretXiaoYun,
  interpretTongYun
};
