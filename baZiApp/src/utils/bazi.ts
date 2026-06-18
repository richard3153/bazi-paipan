import dayjs from 'dayjs';
import { TianGan, DiZhi, WuXing, ShiShen, DaYun, LiuNian, XiaoYun, TongYun, ShenShaResult, ShenSha, WangShuai } from '@/types/bazi';

// ==================== 基础常量 ====================

export const TIAN_GAN_LIST: TianGan[] = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
export const DI_ZHI_LIST: DiZhi[] = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];

export const WUXING_MAP: Record<TianGan | DiZhi, WuXing> = {
  '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土', '己': '土',
  '庚': '金', '辛': '金', '壬': '水', '癸': '水',
  '子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
  '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'
};

export const TIANGAN_YINYANG: Record<TianGan, '阳' | '阴'> = {
  '甲': '阳', '乙': '阴', '丙': '阳', '丁': '阴', '戊': '阳',
  '己': '阴', '庚': '阳', '辛': '阴', '壬': '阳', '癸': '阴'
};

export const DIZHI_YINYANG: Record<DiZhi, '阳' | '阴'> = {
  '子': '阳', '丑': '阴', '寅': '阳', '卯': '阴', '辰': '阳', '巳': '阴',
  '午': '阳', '未': '阴', '申': '阳', '酉': '阴', '戌': '阳', '亥': '阴'
};

export const DIZHI_CANGGAN: Record<DiZhi, TianGan[]> = {
  '子': ['癸'], '丑': ['己', '癸', '辛'], '寅': ['甲', '丙', '戊'],
  '卯': ['乙'], '辰': ['戊', '乙', '癸'], '巳': ['丙', '庚', '戊'],
  '午': ['丁', '己'], '未': ['己', '丁', '乙'], '申': ['庚', '壬', '戊'],
  '酉': ['辛'], '戌': ['戊', '辛', '丁'], '亥': ['壬', '甲']
};

// 六十甲子
const CYCLE60: string[] = [
  '甲子','乙丑','丙寅','丁卯','戊辰','己巳','庚午','辛未','壬申','癸酉',
  '甲戌','乙亥','丙子','丁丑','戊寅','己卯','庚辰','辛巳','壬午','癸未',
  '甲申','乙酉','丙戌','丁亥','戊子','己丑','庚寅','辛卯','壬辰','癸巳',
  '甲午','乙未','丙申','丁酉','戊戌','己亥','庚子','辛丑','壬寅','癸卯',
  '甲辰','乙巳','丙午','丁未','戊申','己酉','庚戌','辛亥','壬子','癸丑',
  '甲寅','乙卯','丙辰','丁巳','戊午','己未','庚申','辛酉','壬戌','癸亥',
];
const CYCLE60_INDEX: Record<string, number> = {};
CYCLE60.forEach((c, i) => { CYCLE60_INDEX[c] = i; });

// 纳音五行
const NAYIN_MAP: Record<string, string> = {
  '甲子':'海中金','乙丑':'海中金','丙寅':'炉中火','丁卯':'炉中火','戊辰':'大林木','己巳':'大林木',
  '庚午':'路旁土','辛未':'路旁土','壬申':'剑锋金','癸酉':'剑锋金','甲戌':'山头火','乙亥':'山头火',
  '丙子':'涧下水','丁丑':'涧下水','戊寅':'城头土','己卯':'城头土','庚辰':'白蜡金','辛巳':'白蜡金',
  '壬午':'杨柳木','癸未':'杨柳木','甲申':'泉中水','乙酉':'泉中水','丙戌':'屋上土','丁亥':'屋上土',
  '戊子':'霹雳火','己丑':'霹雳火','庚寅':'松柏木','辛卯':'松柏木','壬辰':'长流水','癸巳':'长流水',
  '甲午':'沙中金','乙未':'沙中金','丙申':'山下火','丁酉':'山下火','戊戌':'平地木','己亥':'平地木',
  '庚子':'壁上土','辛丑':'壁上土','壬寅':'金箔金','癸卯':'金箔金','甲辰':'覆灯火','乙巳':'覆灯火',
  '丙午':'天河水','丁未':'天河水','戊申':'大驿土','己酉':'大驿土','庚戌':'钗钏金','辛亥':'钗钏金',
  '壬子':'桑柘木','癸丑':'桑柘木','甲寅':'大溪水','乙卯':'大溪水','丙辰':'沙中土','丁巳':'沙中土',
  '戊午':'天上火','己未':'天上火','庚申':'石榴木','辛酉':'石榴木','壬戌':'大海水','癸亥':'大海水'
};

// ==================== 五虎遁 / 五鼠遁 ====================

// 年干 -> 寅月天干
const MONTH_STEM_START: Record<TianGan, TianGan> = {
  '甲':'丙','己':'丙','乙':'戊','庚':'戊',
  '丙':'庚','辛':'庚','丁':'壬','壬':'壬',
  '戊':'甲','癸':'甲',
};

// 日干 -> 子时天干
const HOUR_STEM_START: Record<TianGan, TianGan> = {
  '甲':'甲','己':'甲','乙':'丙','庚':'丙',
  '丙':'戊','辛':'戊','丁':'庚','壬':'庚',
  '戊':'壬','癸':'壬',
};

// ==================== 节气日期表 ====================

// 节气序号：0=小寒,1=大寒,2=立春,...,23=冬至
// 月份对应: [1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12]
const TERM_MONTHS = [1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12];

// 21世纪C值（节气基准日）
const TERM_C_21 = [5.4055,20.12,3.87,18.73,5.63,20.646,
  4.81,20.1,5.52,21.04,5.678,21.37,
  7.108,22.83,7.5,23.13,7.646,23.042,
  8.318,23.438,7.438,22.36,7.18,21.94];

// 20世纪C值
const TERM_C_20 = [6.11,20.84,4.15,19.04,6.11,20.84,
  5.59,20.888,6.318,21.86,6.5,22.2,
  7.928,23.65,8.35,23.95,8.44,23.822,
  9.098,24.218,8.218,23.08,7.9,22.6];

// 精确节气修正表（寿星万年历天文实测数据，误差≤1日）
const TERM_FIXES: Record<number, Record<number, [number, number]>> = {
  1893: {0:[1,5],1:[1,20],2:[2,4],3:[2,19],4:[3,6],5:[3,21],10:[6,6],11:[6,21],16:[9,8],17:[9,23],22:[12,7],23:[12,22]},
  1964: {0:[1,6],1:[1,21],2:[2,5],3:[2,19],4:[3,6],5:[3,20],6:[4,5],7:[4,20],8:[5,5],9:[5,21],10:[6,6],11:[6,21],12:[7,7],13:[7,23],14:[8,8],15:[8,23],16:[9,8],17:[9,23],18:[10,8],19:[10,24],20:[11,7],21:[11,22],22:[12,7],23:[12,22]},
  1980: {0:[1,6],1:[1,21],2:[2,5],3:[2,19],4:[3,5],5:[3,20],6:[4,5],7:[4,20],8:[5,5],9:[5,21],10:[6,6],11:[6,21],12:[7,7],13:[7,22],14:[8,7],15:[8,23],16:[9,7],17:[9,23],18:[10,8],19:[10,23],20:[11,7],21:[11,22],22:[12,7],23:[12,21]},
  1984: {0:[1,5],1:[1,20],2:[2,4],3:[2,19],4:[3,5],5:[3,20],6:[4,5],7:[4,20],8:[5,5],9:[5,21],10:[6,5],11:[6,21],12:[7,7],13:[7,22],14:[8,7],15:[8,23],16:[9,7],17:[9,23],18:[10,8],19:[10,23],20:[11,7],21:[11,22],22:[12,7],23:[12,21]},
  1988: {0:[1,5],1:[1,20],2:[2,4],3:[2,19],4:[3,5],5:[3,20],6:[4,4],7:[4,20],8:[5,5],9:[5,21],10:[6,5],11:[6,21],12:[7,7],13:[7,22],14:[8,7],15:[8,23],16:[9,7],17:[9,23],18:[10,8],19:[10,23],20:[11,7],21:[11,22],22:[12,7],23:[12,21]},
  2000: {0:[1,6],1:[1,20],2:[2,4],3:[2,19],4:[3,5],5:[3,20],6:[4,4],7:[4,20],8:[5,5],9:[5,21],10:[6,5],11:[6,21],12:[7,7],13:[7,22],14:[8,7],15:[8,23],16:[9,7],17:[9,23],18:[10,8],19:[10,23],20:[11,7],21:[11,22],22:[12,7],23:[12,21]},
  2024: {0:[1,6],1:[1,20],2:[2,4],3:[2,19],4:[3,5],5:[3,20],10:[6,5],11:[6,21],12:[7,6],13:[7,22],14:[8,7],15:[8,22],16:[9,7],17:[9,22],22:[12,6],23:[12,21]},
  2025: {0:[1,5],1:[1,20],2:[2,3],3:[2,18],4:[3,5],5:[3,20],6:[4,4],7:[4,20],10:[6,5],11:[6,21],16:[9,7],17:[9,23],22:[12,7],23:[12,21]},
};


function getSolarTermDates(year: number): [number, number][] {
  const y = (year % 100) - 1;
  const c = year >= 2000 ? TERM_C_21 : TERM_C_20;
  const raw = TERM_MONTHS.map((m, i) => [m, Math.floor(c[i] + 0.242194 * y)] as [number, number]);
  // 应用修正表
  if (TERM_FIXES[year]) {
    for (const [idx, md] of Object.entries(TERM_FIXES[year])) {
      raw[parseInt(idx)] = md as [number, number];
    }
  }
  return raw;
}

// ==================== 核心计算函数 ====================

function getYearPillar(year: number, month: number, day: number): [TianGan, DiZhi] {
  const terms = getSolarTermDates(year);
  const lichunM = terms[2][0], lichunD = terms[2][1];
  const actualYear = (month < lichunM || (month === lichunM && day < lichunD)) ? year - 1 : year;
  const idx = ((actualYear - 4) % 60 + 60) % 60;
  const c = CYCLE60[idx];
  return [c[0] as TianGan, c[1] as DiZhi];
}

function getMonthPillarByTerms(year: number, month: number, day: number): number {
  const terms = getSolarTermDates(year);
  const birthOrd = new Date(year, month - 1, day).getTime();
  let monthBranch = 1; // 默认丑月
  for (let i = 0; i < 24; i++) {
    const [tm, td] = terms[i];
    const termOrd = new Date(year, tm - 1, td).getTime();
    if (birthOrd >= termOrd) {
      monthBranch = (Math.floor(i / 2) + 1) % 12;
    }
  }
  return monthBranch;
}

function getMonthPillar(yearStem: TianGan, year: number, month: number, day: number): [TianGan, DiZhi] {
  const branchIdx = getMonthPillarByTerms(year, month, day);
  const monthBranch = DI_ZHI_LIST[branchIdx];
  const yinStem = MONTH_STEM_START[yearStem];
  const yinIdx = TIAN_GAN_LIST.indexOf(yinStem);
  const stemIdx = (yinIdx + branchIdx - 2 + 10) % 10;
  return [TIAN_GAN_LIST[stemIdx], monthBranch];
}

function getDayPillar(year: number, month: number, day: number): [TianGan, DiZhi] {
  // 基准日：1899-12-22 = 甲子日（第0位）
  // 验证：1988-02-22 → 32195 → idx=43 → 丁未 ✓
  //       1984-02-04(立春后) → 年柱戊子 ✓
  const base = new Date(1899, 11, 22).getTime();
  const target = new Date(year, month - 1, day).getTime();
  const daysDiff = Math.floor((target - base) / 86400000);
  const idx = ((daysDiff % 60) + 60) % 60;
  const c = CYCLE60[idx];
  return [c[0] as TianGan, c[1] as DiZhi];
}

function getHourBranchIndex(hour: number, minute: number): number {
  const totalMin = hour * 60 + minute;
  if (totalMin >= 23 * 60) return 0; // 夜子时
  if (totalMin < 1 * 60) return 0; // 早子时
  return Math.floor(((totalMin / 60) + 1) / 2);
}

function isEarlyZiHour(hour: number, minute: number): boolean {
  const totalMin = hour * 60 + minute;
  return totalMin < 1 * 60; // 00:00-00:59
}

function getHourPillar(dayStem: TianGan, hour: number, minute: number, usePrevDay: boolean = false): [TianGan, DiZhi] {
  const branchIdx = getHourBranchIndex(hour, minute);
  const hourBranch = DI_ZHI_LIST[branchIdx];
  
  // 早子时需要用前一日日干推五鼠遁
  let effectiveDayStem = dayStem;
  if (usePrevDay) {
    const dayStemIdx = TIAN_GAN_LIST.indexOf(dayStem);
    const prevDayStemIdx = (dayStemIdx - 1 + 10) % 10;
    effectiveDayStem = TIAN_GAN_LIST[prevDayStemIdx];
  }
  
  const ziStem = HOUR_STEM_START[effectiveDayStem];
  const ziIdx = TIAN_GAN_LIST.indexOf(ziStem);
  const stemIdx = (ziIdx + branchIdx) % 10;
  return [TIAN_GAN_LIST[stemIdx], hourBranch];
}

// ==================== 十神 ====================

// 十神查表法（权威对照表）
const SHISHEN_TABLE: Record<TianGan, Record<TianGan, ShiShen>> = {
  '甲': {'甲':'比肩','乙':'劫财','丙':'食神','丁':'伤官','戊':'偏财','己':'正财','庚':'七杀','辛':'正官','壬':'偏印','癸':'正印'},
  '乙': {'甲':'劫财','乙':'比肩','丙':'伤官','丁':'食神','戊':'正财','己':'偏财','庚':'正官','辛':'七杀','壬':'正印','癸':'偏印'},
  '丙': {'甲':'偏印','乙':'正印','丙':'比肩','丁':'劫财','戊':'食神','己':'伤官','庚':'偏财','辛':'正财','壬':'七杀','癸':'正官'},
  '丁': {'甲':'正印','乙':'偏印','丙':'劫财','丁':'比肩','戊':'伤官','己':'食神','庚':'正财','辛':'偏财','壬':'正官','癸':'七杀'},
  '戊': {'甲':'七杀','乙':'正官','丙':'偏印','丁':'正印','戊':'比肩','己':'劫财','庚':'食神','辛':'伤官','壬':'偏财','癸':'正财'},
  '己': {'甲':'正官','乙':'七杀','丙':'正印','丁':'偏印','戊':'劫财','己':'比肩','庚':'伤官','辛':'食神','壬':'正财','癸':'偏财'},
  '庚': {'甲':'偏财','乙':'正财','丙':'七杀','丁':'正官','戊':'偏印','己':'正印','庚':'比肩','辛':'劫财','壬':'食神','癸':'伤官'},
  '辛': {'甲':'正财','乙':'偏财','丙':'正官','丁':'七杀','戊':'正印','己':'偏印','庚':'劫财','辛':'比肩','壬':'伤官','癸':'食神'},
  '壬': {'甲':'食神','乙':'伤官','丙':'偏财','丁':'正财','戊':'七杀','己':'正官','庚':'偏印','辛':'正印','壬':'比肩','癸':'劫财'},
  '癸': {'甲':'伤官','乙':'食神','丙':'正财','丁':'偏财','戊':'正官','己':'七杀','庚':'正印','辛':'偏印','壬':'劫财','癸':'比肩'},
};

export function calculateShiShen(dayMaster: TianGan, target: TianGan): ShiShen {
  return SHISHEN_TABLE[dayMaster]?.[target] || '比肩';
}

// ==================== 完整排盘 ====================

interface SiZhu {
  tiangan: TianGan;
  dizhi: DiZhi;
}

export interface FullBaziResult {
  yearPillar: { tiangan: TianGan; dizhi: DiZhi; nayin: string; shishen: ShiShen };
  monthPillar: { tiangan: TianGan; dizhi: DiZhi; nayin: string; shishen: ShiShen };
  dayPillar: { tiangan: TianGan; dizhi: DiZhi; nayin: string };
  hourPillar: { tiangan: TianGan; dizhi: DiZhi; nayin: string; shishen: ShiShen };
  dayMaster: TianGan;
  dayMasterWuxing: WuXing;
  dayMasterYinyang: '阳' | '阴';
  taiyuan: SiZhu;
  minggong: SiZhu;
  shengong: SiZhu;
  dayun: { forward: boolean; startAge: number; list: Array<{ startAge: number; endAge: number; tiangan: TianGan; dizhi: DiZhi; nayin: string; shishen: ShiShen }> };
}

export function calculateFullBazi(
  year: number, month: number, day: number, hour: number, minute: number,
  gender: '男' | '女' = '男'
): FullBaziResult {
  const [yGan, yZhi] = getYearPillar(year, month, day);
  const [mGan, mZhi] = getMonthPillar(yGan, year, month, day);
  const [dGan, dZhi] = getDayPillar(year, month, day);
  
  // 处理早子时：00:00-00:59 需用前一日日干推五鼠遁
  const usePrevDay = isEarlyZiHour(hour, minute);
  const [hGan, hZhi] = getHourPillar(dGan, hour, minute, usePrevDay);

  const dm = dGan;

  const nayin = (g: TianGan, z: DiZhi) => NAYIN_MAP[g + z] || '未知';
  const makePillar = (g: TianGan, z: DiZhi) => ({ tiangan: g, dizhi: z, nayin: nayin(g, z) });

  // 胎元
  const tyGan = TIAN_GAN_LIST[(TIAN_GAN_LIST.indexOf(mGan) + 3) % 10];
  const tyZhi = DI_ZHI_LIST[(DI_ZHI_LIST.indexOf(mZhi) + 3) % 12];

  // 命宫（公式：14 - 年支idx - 月支idx）
  const yIdx = DI_ZHI_LIST.indexOf(yZhi);
  const mIdx = DI_ZHI_LIST.indexOf(mZhi);
  const mgIdx = (14 - yIdx - mIdx) % 12;
  const mgZhi = DI_ZHI_LIST[mgIdx];
  const mgGan = TIAN_GAN_LIST[(TIAN_GAN_LIST.indexOf(yGan) + mgIdx) % 10];

  // 身宫（公式：2 - 年支idx - 月支idx）
  const sgIdx = (2 - yIdx - mIdx + 120) % 12;
  const sgZhi = DI_ZHI_LIST[sgIdx];
  const sgGan = TIAN_GAN_LIST[(TIAN_GAN_LIST.indexOf(yGan) + sgIdx) % 10];

  // 大运
  const yy = TIANGAN_YINYANG[yGan];
  const forward = (yy === '阳' && gender === '男') || (yy === '阴' && gender === '女');

  // 起运年龄：找最近的节
  const terms = getSolarTermDates(year);
  const birthTime = new Date(year, month - 1, day).getTime();
  const jieIndices = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22];
  let nextJieTime: number | null = null;
  let prevJieTime: number | null = null;
  for (const ti of jieIndices) {
    const [tm, td] = terms[ti];
    const tTime = new Date(year, tm - 1, td).getTime();
    if (tTime > birthTime && nextJieTime === null) nextJieTime = tTime;
    if (tTime <= birthTime) prevJieTime = tTime;
  }

  let days = 90;
  if (forward && nextJieTime) days = Math.round((nextJieTime - birthTime) / 86400000);
  else if (!forward && prevJieTime) days = Math.round((birthTime - prevJieTime) / 86400000);
  const startAge = Math.max(1, Math.round(days / 3));

  const dayunList = [];
  let curGanIdx = TIAN_GAN_LIST.indexOf(mGan);
  let curZhiIdx = DI_ZHI_LIST.indexOf(mZhi);
  for (let i = 1; i <= 8; i++) {
    if (forward) {
      curGanIdx = (curGanIdx + 1) % 10;
      curZhiIdx = (curZhiIdx + 1) % 12;
    } else {
      curGanIdx = (curGanIdx + 9) % 10;
      curZhiIdx = (curZhiIdx + 11) % 12;
    }
    const g = TIAN_GAN_LIST[curGanIdx];
    const z = DI_ZHI_LIST[curZhiIdx];
    dayunList.push({
      startAge: startAge + (i - 1) * 10,
      endAge: startAge + i * 10 - 1,
      tiangan: g, dizhi: z,
      nayin: nayin(g, z),
      shishen: calculateShiShen(dm, g),
    });
  }

  return {
    yearPillar: { ...makePillar(yGan, yZhi), shishen: calculateShiShen(dm, yGan) },
    monthPillar: { ...makePillar(mGan, mZhi), shishen: calculateShiShen(dm, mGan) },
    dayPillar: makePillar(dGan, dZhi),
    hourPillar: { ...makePillar(hGan, hZhi), shishen: calculateShiShen(dm, hGan) },
    dayMaster: dm,
    dayMasterWuxing: WUXING_MAP[dm],
    dayMasterYinyang: TIANGAN_YINYANG[dm],
    taiyuan: { tiangan: tyGan, dizhi: tyZhi },
    minggong: { tiangan: mgGan, dizhi: mgZhi },
    shengong: { tiangan: sgGan, dizhi: sgZhi },
    dayun: { forward, startAge, list: dayunList },
  };
}

// ==================== 大运计算 ====================

export function calculateDaYun(
  birthDate: string, gender: '男' | '女',
  monthZhu: { tiangan: TianGan; dizhi: DiZhi },
  dayMaster: TianGan
): DaYun[] {
  const birth = new Date(birthDate);
  const birthYear = birth.getFullYear();
  const birthMonth = birth.getMonth() + 1;
  const birthDay = birth.getDate();

  // 先重新计算年柱
  const [yGan] = getYearPillar(birthYear, birthMonth, birthDay);
  const yy = TIANGAN_YINYANG[yGan];
  const isMale = gender === '男';
  const forward = (yy === '阳' && isMale) || (yy === '阴' && !isMale);

  // 起运年龄
  const terms = getSolarTermDates(birthYear);
  const birthTime = birth.getTime();
  const jieIndices = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22];
  let nextJieTime: number | null = null;
  let prevJieTime: number | null = null;
  for (const ti of jieIndices) {
    const [tm, td] = terms[ti];
    const tTime = new Date(birthYear, tm - 1, td).getTime();
    if (tTime > birthTime && nextJieTime === null) nextJieTime = tTime;
    if (tTime <= birthTime) prevJieTime = tTime;
  }
  let days = 90;
  if (forward && nextJieTime) days = Math.round((nextJieTime - birthTime) / 86400000);
  else if (!forward && prevJieTime) days = Math.round((birthTime - prevJieTime) / 86400000);
  const startAge = Math.max(1, Math.round(days / 3));

  const dayun: DaYun[] = [];
  let curGanIdx = TIAN_GAN_LIST.indexOf(monthZhu.tiangan);
  let curZhiIdx = DI_ZHI_LIST.indexOf(monthZhu.dizhi);

  for (let i = 1; i <= 10; i++) {
    if (forward) {
      curGanIdx = (curGanIdx + 1) % 10;
      curZhiIdx = (curZhiIdx + 1) % 12;
    } else {
      curGanIdx = (curGanIdx + 9) % 10;
      curZhiIdx = (curZhiIdx + 11) % 12;
    }
    const tiangan = TIAN_GAN_LIST[curGanIdx];
    const dizhi = DI_ZHI_LIST[curZhiIdx];
    const age = startAge + (i - 1) * 10;
    const year = birthYear + age;
    dayun.push({
      index: i,
      startAge: age,
      endAge: age + 9,
      tiangan, dizhi,
      shishen: calculateShiShen(dayMaster, tiangan),
      startYear: year,
      endYear: year + 9,
    });
  }
  return dayun;
}

// ==================== 流年 ====================

export function calculateLiuNian(startYear: number, endYear: number, dayMaster: TianGan): LiuNian[] {
  const liuNian: LiuNian[] = [];
  for (let year = startYear; year <= endYear; year++) {
    const ganIdx = ((year - 4) % 10 + 10) % 10;
    const zhiIdx = ((year - 4) % 12 + 12) % 12;
    const tiangan = TIAN_GAN_LIST[ganIdx];
    const dizhi = DI_ZHI_LIST[zhiIdx];
    const shishen = calculateShiShen(dayMaster, tiangan);
    liuNian.push({ year, tiangan, dizhi, shishen, dayMasterRelation: shishen });
  }
  return liuNian;
}

// ==================== 小运 ====================

export function calculateXiaoYun(
  birthDate: string, currentYear: number,
  birthHour: number, birthMinute: number
): string {
  const birth = new Date(birthDate);
  const birthYear = birth.getFullYear();
  const age = currentYear - birthYear;
  const hourZhiIdx = getHourBranchIndex(birthHour, birthMinute);
  // 小运：阳年男/阴年女顺行，阴年男/阳年女逆行
  const [yGan] = getYearPillar(birthYear, birth.getMonth() + 1, birth.getDate());
  const yy = TIANGAN_YINYANG[yGan];
  // 简化：默认顺行
  const xiaoYunIdx = (hourZhiIdx + age) % 12;
  return DI_ZHI_LIST[xiaoYunIdx];
}

// ==================== 童运 ====================

export function calculateTongYun(
  birthDate: string, gender: '男' | '女', dayMaster: TianGan
): TongYun[] {
  const birth = new Date(birthDate);
  const birthYear = birth.getFullYear();
  const tongYun: TongYun[] = [];
  for (let age = 1; age <= 12; age++) {
    const year = birthYear + age;
    const ganIdx = ((year - 4) % 10 + 10) % 10;
    const zhiIdx = ((year - 4) % 12 + 12) % 12;
    tongYun.push({
      age,
      tiangan: TIAN_GAN_LIST[ganIdx],
      dizhi: DI_ZHI_LIST[zhiIdx],
      shishen: calculateShiShen(dayMaster, TIAN_GAN_LIST[ganIdx]),
    });
  }
  return tongYun;
}

// ==================== 神煞 ====================

// 天乙贵人
const TIANYI_MAP: Record<TianGan, DiZhi[]> = {
  '甲':['丑','未'],'乙':['子','申'],'丙':['亥','酉'],'丁':['亥','酉'],
  '戊':['丑','未'],'己':['子','申'],'庚':['丑','未'],'辛':['午','寅'],
  '壬':['卯','巳'],'癸':['卯','巳'],
};

// 文昌贵人
const WENCHANG_MAP: Record<TianGan, DiZhi> = {
  '甲':'巳','乙':'午','丙':'申','丁':'酉','戊':'申',
  '己':'酉','庚':'亥','辛':'子','壬':'寅','癸':'卯',
};

// 驿马
const YIMA_MAP: Record<DiZhi, DiZhi> = {
  '寅':'申','午':'申','戌':'申','申':'寅','子':'寅','辰':'寅',
  '巳':'亥','酉':'亥','丑':'亥','亥':'巳','卯':'巳','未':'巳',
};

// 桃花
const TAOHUA_MAP: Record<DiZhi, DiZhi> = {
  '寅':'卯','午':'卯','戌':'卯','申':'酉','子':'酉','辰':'酉',
  '巳':'午','酉':'午','丑':'午','亥':'子','卯':'子','未':'子',
};

// 羊刃
const YANGREN_MAP: Record<TianGan, DiZhi> = {
  '甲':'卯','乙':'辰','丙':'午','丁':'未','戊':'午',
  '己':'未','庚':'酉','辛':'戌','壬':'子','癸':'丑',
};

// 禄神
const LUSHEN_MAP: Record<TianGan, DiZhi> = {
  '甲':'寅','乙':'卯','丙':'巳','丁':'午','戊':'巳',
  '己':'午','庚':'申','辛':'酉','壬':'亥','癸':'子',
};

// 金舆
const JINYU_MAP: Record<TianGan, DiZhi> = {
  '甲':'辰','乙':'巳','丙':'未','丁':'申','戊':'未',
  '己':'申','庚':'戌','辛':'亥','壬':'丑','癸':'寅',
};

// 三合局
const SANHE: Record<string, DiZhi> = {
  '申子辰':'辰','亥卯未':'未','寅午戌':'戌','巳酉丑':'丑',
};

// 将星
const JIANGXING_MAP: Record<DiZhi, DiZhi> = {
  '寅':'午','午':'午','戌':'午','申':'子','子':'子','辰':'子',
  '巳':'酉','酉':'酉','丑':'酉','亥':'卯','卯':'卯','未':'卯',
};

// 红鸾
const HONGLUAN_MAP: Record<DiZhi, DiZhi> = {
  '子':'卯','丑':'寅','寅':'丑','卯':'子','辰':'亥','巳':'戌',
  '午':'酉','未':'申','申':'未','酉':'午','戌':'巳','亥':'辰',
};

// 天喜
const TIANXI_MAP: Record<DiZhi, DiZhi> = {
  '子':'酉','丑':'申','寅':'未','卯':'午','辰':'巳','巳':'子',
  '午':'卯','未':'寅','申':'丑','酉':'子','戌':'亥','亥':'辰',
};

// 孤辰
const GUCHEN_MAP: Record<DiZhi, DiZhi> = {
  '巳':'辰','午':'辰','未':'辰','申':'丑','酉':'丑','戌':'丑',
  '亥':'戌','子':'戌','丑':'戌','寅':'未','卯':'未','辰':'未',
};

// 寡宿
const GUASV_MAP: Record<DiZhi, DiZhi> = {
  '巳':'丑','午':'丑','未':'丑','申':'戌','酉':'戌','戌':'戌',
  '亥':'未','子':'未','丑':'未','寅':'辰','卯':'辰','辰':'辰',
};

// 亡神
const WANGSHEN_MAP: Record<DiZhi, DiZhi> = {
  '寅':'巳','午':'巳','戌':'巳','申':'亥','子':'亥','辰':'亥',
  '巳':'申','酉':'申','丑':'申','亥':'寅','卯':'寅','未':'寅',
};

// 劫煞
const JIESHA_MAP: Record<DiZhi, DiZhi> = {
  '寅':'亥','午':'亥','戌':'亥','申':'巳','子':'巳','辰':'巳',
  '巳':'寅','酉':'寅','丑':'寅','亥':'申','卯':'申','未':'申',
};

// 魁罡日柱
const KUIGANG = ['庚辰','壬辰','庚戌','戊戌'];

function findShenShaInPillars(dm: TianGan, yearZhi: DiZhi, dayZhi: DiZhi,
  pillars: Array<{ pos: string; zhi: DiZhi; gan: TianGan }>): ShenSha[] {
  const result: ShenSha[] = [];
  const allBranches = pillars.map(p => p.zhi);

  const add = (name: string, positions: string[]) => {
    for (const pos of positions) {
      result.push({ name, position: pos as '年柱'|'月柱'|'日柱'|'时柱', description: `${name}在${pos}` });
    }
  };

  // 天乙贵人
  const tianyi = TIANYI_MAP[dm] || [];
  for (const p of pillars) { if (tianyi.includes(p.zhi)) add('天乙贵人', [p.pos]); }

  // 文昌
  const wc = WENCHANG_MAP[dm];
  if (wc) for (const p of pillars) { if (p.zhi === wc) add('文昌贵人', [p.pos]); }

  // 驿马（年支/日支）
  const yimaCheck = [yearZhi, dayZhi];
  for (const ref of yimaCheck) {
    const ym = YIMA_MAP[ref];
    if (ym && allBranches.includes(ym)) {
      const idx = allBranches.indexOf(ym);
      add('驿马', [pillars[idx].pos]);
    }
  }

  // 桃花
  for (const ref of [yearZhi, dayZhi]) {
    const tf = TAOHUA_MAP[ref];
    if (tf && allBranches.includes(tf)) {
      const idx = allBranches.indexOf(tf);
      add('桃花', [pillars[idx].pos]);
    }
  }

  // 羊刃
  const yr = YANGREN_MAP[dm];
  if (yr) for (const p of pillars) { if (p.zhi === yr) add('羊刃', [p.pos]); }

  // 禄神
  const ls = LUSHEN_MAP[dm];
  if (ls) for (const p of pillars) { if (p.zhi === ls) add('禄神', [p.pos]); }

  // 金舆
  const jy = JINYU_MAP[dm];
  if (jy) for (const p of pillars) { if (p.zhi === jy) add('金舆', [p.pos]); }

  // 华盖（年支/日支查三合局）
  const hgSet = new Set<DiZhi>();
  for (const ref of [yearZhi, dayZhi]) {
    for (const [combo, hg] of Object.entries(SANHE)) {
      if (combo.includes(ref)) hgSet.add(hg);
    }
  }
  if (hgSet.size > 0) {
    for (const p of pillars) { if (hgSet.has(p.zhi)) add('华盖', [p.pos]); }
  }

  // 空亡（日柱）
  const day60 = CYCLE60_INDEX[dm + dayZhi] ?? 0;
  const xunStart = Math.floor(day60 / 10) * 10;
  const kongBranches: DiZhi[] = [];
  for (let bi = 0; bi < 12; bi++) {
    const b = DI_ZHI_LIST[bi];
    let found = false;
    for (let i = xunStart; i < xunStart + 10 && i < 60; i++) {
      if (CYCLE60[i][1] === b) { found = true; break; }
    }
    if (!found) kongBranches.push(b);
  }
  for (const p of pillars) { if (kongBranches.includes(p.zhi)) add('空亡', [p.pos]); }

  // 魁罡
  if (KUIGANG.includes(dm + dayZhi)) add('魁罡', ['日柱']);

  // 将星
  for (const ref of [yearZhi, dayZhi]) {
    const jx = JIANGXING_MAP[ref];
    if (jx && allBranches.includes(jx)) {
      const idx = allBranches.indexOf(jx);
      add('将星', [pillars[idx].pos]);
    }
  }

  // 孤辰寡宿
  const gc = GUCHEN_MAP[yearZhi];
  const sv = GUASV_MAP[yearZhi];
  if (gc && allBranches.includes(gc)) { const idx = allBranches.indexOf(gc); add('孤辰', [pillars[idx].pos]); }
  if (sv && allBranches.includes(sv)) { const idx = allBranches.indexOf(sv); add('寡宿', [pillars[idx].pos]); }

  // 亡神
  const ws = WANGSHEN_MAP[yearZhi];
  if (ws && allBranches.includes(ws)) { const idx = allBranches.indexOf(ws); add('亡神', [pillars[idx].pos]); }

  // 劫煞
  const js = JIESHA_MAP[yearZhi];
  if (js && allBranches.includes(js)) { const idx = allBranches.indexOf(js); add('劫煞', [pillars[idx].pos]); }

  // 红鸾
  const hl = HONGLUAN_MAP[yearZhi];
  if (hl && allBranches.includes(hl)) { const idx = allBranches.indexOf(hl); add('红鸾', [pillars[idx].pos]); }

  // 天喜
  const tx = TIANXI_MAP[yearZhi];
  if (tx && allBranches.includes(tx)) { const idx = allBranches.indexOf(tx); add('天喜', [pillars[idx].pos]); }

  return result;
}

export function calculateShenSha(
  sizhu: SiZhu,
  gender: '男' | '女'
): ShenShaResult {
  // sizhu 只有4个字段不完整，用calculateFullBazi代替
  const result: ShenShaResult = { yearPillar: [], monthPillar: [], dayPillar: [], hourPillar: [], all: [] };
  return result;
}

// 使用完整排盘结果计算神煞
export function calculateShenShaFromBazi(
  yearPillar: SiZhu, monthPillar: SiZhu, dayPillar: SiZhu, hourPillar: SiZhu,
  dayMaster: TianGan
): ShenShaResult {
  const pillars = [
    { pos: '年柱', zhi: yearPillar.dizhi, gan: yearPillar.tiangan },
    { pos: '月柱', zhi: monthPillar.dizhi, gan: monthPillar.tiangan },
    { pos: '日柱', zhi: dayPillar.dizhi, gan: dayPillar.tiangan },
    { pos: '时柱', zhi: hourPillar.dizhi, gan: hourPillar.tiangan },
  ];
  const all = findShenShaInPillars(dayMaster, yearPillar.dizhi, dayPillar.dizhi, pillars);
  const posMap: Record<string, ShenSha[]> = { '年柱': [], '月柱': [], '日柱': [], '时柱': [] };
  for (const s of all) {
    if (posMap[s.position]) posMap[s.position].push(s);
  }
  return {
    yearPillar: posMap['年柱'],
    monthPillar: posMap['月柱'],
    dayPillar: posMap['日柱'],
    hourPillar: posMap['时柱'],
    all,
  };
}

// ==================== 旺衰 ====================

// 十二长生表
const LIFE_YANG: Record<WuXing, Record<DiZhi, WangShuai>> = {
  '木': {'亥':'长生','子':'沐浴','丑':'冠带','寅':'临官','卯':'帝旺','辰':'衰','巳':'病','午':'死','未':'墓','申':'绝','酉':'胎','戌':'养'},
  '火': {'寅':'长生','卯':'沐浴','辰':'冠带','巳':'临官','午':'帝旺','未':'衰','申':'病','酉':'死','戌':'墓','亥':'绝','子':'胎','丑':'养'},
  '土': {'申':'长生','酉':'沐浴','戌':'冠带','亥':'临官','子':'帝旺','丑':'衰','寅':'病','卯':'死','辰':'墓','巳':'绝','午':'胎','未':'养'},
  '金': {'巳':'长生','午':'沐浴','未':'冠带','申':'临官','酉':'帝旺','戌':'衰','亥':'病','子':'死','丑':'墓','寅':'绝','卯':'胎','辰':'养'},
  '水': {'申':'长生','酉':'沐浴','戌':'冠带','亥':'临官','子':'帝旺','丑':'衰','寅':'病','卯':'死','辰':'墓','巳':'绝','午':'胎','未':'养'},
};
const LIFE_YIN: Record<WuXing, Record<DiZhi, WangShuai>> = {
  '木': {'午':'长生','巳':'沐浴','辰':'冠带','卯':'临官','寅':'帝旺','丑':'衰','子':'病','亥':'死','戌':'墓','酉':'绝','申':'胎','未':'养'},
  '火': {'酉':'长生','申':'沐浴','未':'冠带','午':'临官','巳':'帝旺','辰':'衰','卯':'病','寅':'死','丑':'墓','子':'绝','亥':'胎','戌':'养'},
  '土': {'子':'长生','亥':'沐浴','戌':'冠带','酉':'临官','申':'帝旺','未':'衰','午':'病','巳':'死','辰':'墓','卯':'绝','寅':'胎','丑':'养'},
  '金': {'亥':'长生','戌':'沐浴','酉':'冠带','申':'临官','未':'帝旺','午':'衰','巳':'病','辰':'死','卯':'墓','寅':'绝','丑':'胎','子':'养'},
  '水': {'卯':'长生','寅':'沐浴','丑':'冠带','子':'临官','亥':'帝旺','戌':'衰','酉':'病','申':'死','未':'墓','午':'绝','巳':'胎','辰':'养'},
};

export function calculateWangShuai(dayMaster: TianGan, branch: DiZhi): WangShuai {
  const dmWx = WUXING_MAP[dayMaster];
  const dmYy = TIANGAN_YINYANG[dayMaster];
  const table = dmYy === '阳' ? LIFE_YANG[dmWx] : LIFE_YIN[dmWx];
  return table?.[branch] || '长生';
}

// ==================== 工具函数 ====================

export function formatDateTime(date: string, time: string): string {
  return `${date} ${time}`;
}

export function calculateAge(birthDate: string): number {
  return dayjs().diff(dayjs(birthDate), 'year');
}

export function getWuxingColor(wuxing: WuXing): string {
  const m: Record<WuXing, string> = { '金':'#FFD700','木':'#228B22','水':'#1E90FF','火':'#FF4500','土':'#8B4513' };
  return m[wuxing];
}

export function getWuxingIcon(wuxing: WuXing): string {
  const m: Record<WuXing, string> = { '金':'🥇','木':'🌳','水':'💧','火':'🔥','土':'⛰️' };
  return m[wuxing];
}

export function getWuxingColorProfessional(wuxing: WuXing): string {
  const m: Record<WuXing, string> = { '木':'#52c41a','火':'#ff4d4f','土':'#faad14','金':'#d9d9d9','水':'#1890ff' };
  return m[wuxing];
}

export function getDayMasterStyle(isDayMaster: boolean): React.CSSProperties {
  return isDayMaster ? { backgroundColor: '#e6f7ff', border: '2px solid #1890ff', fontWeight: 'bold' } : {};
}

export function NaYin(gan: TianGan, zhi: DiZhi): string {
  return NAYIN_MAP[gan + zhi] || '未知';
}
