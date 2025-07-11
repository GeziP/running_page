/**
 * Professional Running Analysis Utilities
 * 专业跑步分析工具函数
 * 
 * 基于权威跑步训练理论：
 * - VDOT系统（Jack Daniels）
 * - MAF 180心率训练法（Phil Maffetone）
 * - 训练压力评分（TSS）
 */

// 接口定义
export interface VDOTResult {
  vdot: number;
  fitnessLevel: string;
  trainingPaces: {
    easy: string;
    tempo: string;
    interval: string;
    repetition: string;
  };
  racePredictions: {
    [key: string]: string;
  };
}

export interface MAFResult {
  mafHeartRate: number;
  zones: {
    [key: string]: {
      min_hr: number;
      max_hr: number;
      name: string;
      description: string;
      rpe: string;
    };
  };
  recommendation: string;
}

export interface TSSResult {
  tss: number;
  interpretation: string;
  trainingAdvice: string;
  intensityFactor: number;
}

// VDOT训练配速表 - 基于Jack Daniels Running Formula
const VDOT_TRAINING_PACES: { [key: number]: any } = {
  30: { easy: '12:40', tempo: '10:18', interval: '2:22', repetition: '2:15' },
  32: { easy: '12:04', tempo: '9:47', interval: '2:14', repetition: '2:07' },
  34: { easy: '11:32', tempo: '9:20', interval: '2:08', repetition: '2:00' },
  36: { easy: '11:02', tempo: '8:55', interval: '2:02', repetition: '1:54' },
  38: { easy: '10:35', tempo: '8:33', interval: '1:56', repetition: '1:48' },
  40: { easy: '10:11', tempo: '8:12', interval: '1:52', repetition: '1:43' },
  42: { easy: '9:48', tempo: '7:52', interval: '1:48', repetition: '1:38' },
  44: { easy: '9:27', tempo: '7:33', interval: '1:44', repetition: '1:34' },
  46: { easy: '9:07', tempo: '7:17', interval: '1:40', repetition: '1:30' },
  48: { easy: '8:49', tempo: '7:02', interval: '1:36', repetition: '1:26' },
  50: { easy: '8:32', tempo: '6:51', interval: '1:33', repetition: '1:22' },
  52: { easy: '8:16', tempo: '6:38', interval: '1:31', repetition: '1:19' },
  54: { easy: '8:01', tempo: '6:26', interval: '1:28', repetition: '1:16' },
  56: { easy: '7:48', tempo: '6:15', interval: '1:26', repetition: '1:13' },
  58: { easy: '7:34', tempo: '6:04', interval: '1:23', repetition: '1:11' },
  60: { easy: '7:22', tempo: '5:54', interval: '1:21', repetition: '1:08' },
  62: { easy: '7:11', tempo: '5:45', interval: '1:19', repetition: '1:06' },
  64: { easy: '7:00', tempo: '5:36', interval: '1:17', repetition: '1:04' },
  66: { easy: '6:49', tempo: '5:28', interval: '1:15', repetition: '1:02' },
  68: { easy: '6:39', tempo: '5:20', interval: '1:13', repetition: '1:00' },
  70: { easy: '6:30', tempo: '5:13', interval: '1:11', repetition: '0:58' },
};

// VDOT比赛时间预测表（秒）
const VDOT_RACE_TIMES: { [key: number]: any } = {
  30: { 5: 1840, 10: 3826, 21.1: 8464, 42.2: 17357 },
  35: { 5: 1540, 10: 3200, 21.1: 7020, 42.2: 14400 },
  40: { 5: 1288, 10: 2683, 21.1: 5889, 42.2: 12105 },
  45: { 5: 1095, 10: 2282, 21.1: 5010, 42.2: 10300 },
  50: { 5: 957, 10: 1995, 21.1: 4375, 42.2: 9000 },
  55: { 5: 852, 10: 1776, 21.1: 3900, 42.2: 8025 },
  60: { 5: 771, 10: 1607, 21.1: 3530, 42.2: 7275 },
  65: { 5: 705, 10: 1470, 21.1: 3225, 42.2: 6660 },
  70: { 5: 651, 10: 1356, 21.1: 2975, 42.2: 6150 },
};

/**
 * 计算VDOT值
 */
export function calculateVDOT(distanceKm: number, timeSeconds: number): VDOTResult {
  if (distanceKm <= 0 || timeSeconds <= 0) {
    throw new Error('距离和时间必须大于0');
  }

  // 使用Jack Daniels的VDOT公式
  const velocityMPerMin = (distanceKm * 1000) / (timeSeconds / 60);
  const vdot = Math.max(20, Math.min(85, 
    -4.6 + 0.182258 * velocityMPerMin + 0.000104 * velocityMPerMin ** 2
  ));

  const roundedVDOT = Math.round(vdot * 10) / 10;

  // 获取训练配速
  const trainingPaces = getTrainingPaces(roundedVDOT);
  
  // 获取比赛预测
  const racePredictions = getRacePredictions(roundedVDOT);
  
  // 分类健身水平
  let fitnessLevel = '';
  if (roundedVDOT >= 65) fitnessLevel = '精英级';
  else if (roundedVDOT >= 55) fitnessLevel = '优秀级';
  else if (roundedVDOT >= 45) fitnessLevel = '良好级';
  else if (roundedVDOT >= 35) fitnessLevel = '中等级';
  else fitnessLevel = '初级';

  return {
    vdot: roundedVDOT,
    fitnessLevel,
    trainingPaces,
    racePredictions
  };
}

/**
 * 获取训练配速
 */
function getTrainingPaces(vdot: number) {
  const clampedVdot = Math.max(30, Math.min(70, vdot));
  const closestVdot = Math.round(clampedVdot / 2) * 2;
  
  return VDOT_TRAINING_PACES[closestVdot] || VDOT_TRAINING_PACES[40];
}

/**
 * 获取比赛时间预测
 */
function getRacePredictions(vdot: number) {
  const clampedVdot = Math.max(30, Math.min(70, vdot));
  const lowerVdot = Math.floor(clampedVdot / 5) * 5;
  const upperVdot = Math.ceil(clampedVdot / 5) * 5;
  
  const lowerTimes = VDOT_RACE_TIMES[lowerVdot] || VDOT_RACE_TIMES[40];
  const upperTimes = VDOT_RACE_TIMES[upperVdot] || VDOT_RACE_TIMES[40];
  
  const factor = (clampedVdot - lowerVdot) / (upperVdot - lowerVdot) || 0;
  
  const predictions: { [key: string]: string } = {};
  
  for (const distance of [5, 10, 21.1, 42.2]) {
    const lowerTime = lowerTimes[distance];
    const upperTime = upperTimes[distance];
    const interpolatedTime = lowerTime + (upperTime - lowerTime) * factor;
    
    const distanceName = distance === 5 ? '5公里' :
                        distance === 10 ? '10公里' :
                        distance === 21.1 ? '半程马拉松' : '全程马拉松';
    
    predictions[distanceName] = formatTime(Math.round(interpolatedTime));
  }
  
  return predictions;
}

/**
 * 计算MAF心率
 */
export function calculateMAF(age: number, healthCategory: string): MAFResult {
  if (age <= 0 || age > 100) {
    throw new Error('年龄必须在1-100之间');
  }

  const baseHR = 180 - age;
  
  const adjustments: { [key: string]: number } = {
    'major_illness': -10,  // 重大疾病、服药、康复期
    'minor_issues': -5,    // 受伤、感冒频繁、哮喘、新手
    'healthy': 0,          // 正常健康训练者
    'elite': 5,            // 精英运动员（2年以上训练无伤病）
    'senior': 10           // 65岁以上（需要评估）
  };
  
  const adjustment = adjustments[healthCategory] || 0;
  const mafHeartRate = Math.max(100, Math.min(180, baseHR + adjustment));
  
  // 计算心率区间
  const zones = {
    '区间1': {
      min_hr: Math.round(mafHeartRate * 0.65),
      max_hr: Math.round(mafHeartRate * 0.75),
      name: '恢复区',
      description: '主动恢复，提高脂肪燃烧',
      rpe: '1-2级（很轻松）'
    },
    '区间2': {
      min_hr: Math.round(mafHeartRate * 0.75),
      max_hr: Math.round(mafHeartRate * 0.85),
      name: '有氧基础区',
      description: '建立有氧基础，长距离LSD',
      rpe: '3-4级（轻松）'
    },
    '区间3': {
      min_hr: Math.round(mafHeartRate * 0.85),
      max_hr: mafHeartRate,
      name: 'MAF区间',
      description: '最大有氧功能，提高效率',
      rpe: '5-6级（适中）'
    },
    '区间4': {
      min_hr: mafHeartRate,
      max_hr: Math.round(mafHeartRate * 1.1),
      name: '乳酸阈值区',
      description: '提高乳酸清除能力',
      rpe: '7-8级（困难）'
    },
    '区间5': {
      min_hr: Math.round(mafHeartRate * 1.1),
      max_hr: Math.round(mafHeartRate * 1.2),
      name: '无氧功率区',
      description: '提高VO2max和无氧功率',
      rpe: '9-10级（最大强度）'
    }
  };

  return {
    mafHeartRate,
    zones,
    recommendation: `大部分训练应保持在${mafHeartRate-10}-${mafHeartRate}心率区间`
  };
}

/**
 * 计算训练压力评分（TSS）
 */
export function calculateTSS(durationMinutes: number, avgPaceSeconds: number, thresholdPaceSeconds: number): TSSResult {
  if (durationMinutes <= 0) {
    throw new Error('训练时长必须大于0');
  }
  
  if (avgPaceSeconds <= 0 || thresholdPaceSeconds <= 0) {
    throw new Error('配速值必须大于0');
  }
  
  // 计算强度因子 (IF)
  const intensityFactor = thresholdPaceSeconds / avgPaceSeconds;
  
  // TSS = (duration_hours * IF^2) * 100
  const durationHours = durationMinutes / 60;
  const tss = durationHours * (intensityFactor ** 2) * 100;
  
  let interpretation = '';
  let trainingAdvice = '';
  
  if (tss < 50) {
    interpretation = '轻松训练';
    trainingAdvice = '适合恢复日或技术训练';
  } else if (tss < 100) {
    interpretation = '中等强度训练';
    trainingAdvice = '标准训练强度，可以每天进行';
  } else if (tss < 200) {
    interpretation = '高强度训练';
    trainingAdvice = '需要1-2天恢复时间';
  } else {
    interpretation = '极高强度训练';
    trainingAdvice = '需要2-3天恢复时间，谨慎安排';
  }

  return {
    tss: Math.round(tss * 10) / 10,
    interpretation,
    trainingAdvice,
    intensityFactor: Math.round(intensityFactor * 100) / 100
  };
}

/**
 * 解析时间字符串为秒数
 */
export function parseTimeToSeconds(timeStr: string): number {
  const parts = timeStr.split(':');
  if (parts.length === 2) {
    return parseInt(parts[0]) * 60 + parseInt(parts[1]);
  } else if (parts.length === 3) {
    return parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseInt(parts[2]);
  }
  return 0;
}

/**
 * 格式化时间（秒）为字符串
 */
export function formatTime(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  } else {
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  }
}

/**
 * 生成训练建议
 */
export function generateTrainingAdvice(vdot: number, mafHeartRate: number, age: number): string {
  let advice = '';
  
  // 基于VDOT水平给出建议
  if (vdot < 40) {
    advice = '重点建立有氧基础，80%以上训练应在MAF心率以下。每周3-4次训练，以轻松跑为主。';
  } else if (vdot < 55) {
    advice = '在保持有氧基础的同时，适度增加节奏跑和间歇训练。每周4-5次训练，70%轻松跑，20%节奏跑，10%间歇训练。';
  } else {
    advice = '精英训练：有氧基础+系统化的速度和专项训练。每周6-7次训练，包含多种训练类型的周期化安排。';
  }
  
  // 基于年龄的建议
  if (age >= 50) {
    advice += ' 注意恢复时间，增加力量训练，减少高强度训练频率。';
  } else if (age >= 40) {
    advice += ' 平衡训练强度，重视睡眠和营养恢复。';
  }
  
  return advice;
}

/**
 * 获取理论基础信息
 */
export function getTheoryInfo() {
  return {
    vdot: {
      name: 'VDOT训练系统',
      developer: 'Jack Daniels博士',
      description: '基于VO2max的跑步训练配速计算系统',
      benefits: [
        '精确的训练配速指导',
        '科学的能力评估',
        '比赛成绩预测'
      ]
    },
    maf: {
      name: 'MAF 180心率训练法',
      developer: 'Phil Maffetone博士',
      description: '最大有氧心率训练法，强调有氧基础建设',
      benefits: [
        '提高脂肪燃烧效率',
        '减少受伤风险',
        '建立强大有氧基础'
      ]
    },
    tss: {
      name: '训练压力评分系统',
      developer: 'TrainingPeaks / Dr. Andrew Coggan',
      description: '量化训练负荷和恢复需求的科学系统',
      benefits: [
        '客观量化训练强度',
        '科学安排恢复时间',
        '预防过度训练'
      ]
    }
  };
} 

// 综合分析功能
export const getComprehensiveAnalysis = async () => {
  try {
    // 模拟从活动数据加载
    const activities = await loadActivitiesData();
    
    // 计算训练负荷分析
    const trainingLoad = analyzeTrainingLoad(activities);
    
    // 计算表现分析
    const performance = analyzePerformance(activities);
    
    // 生成个性化建议
    const recommendations = generateRecommendations(activities, trainingLoad, performance);
    
    // 统计近期活动
    const recentActivities = analyzeRecentActivities(activities);
    
    return {
      trainingLoad,
      performance,
      recommendations,
      recentActivities
    };
  } catch (error) {
    console.error('Error in comprehensive analysis:', error);
    throw new Error('无法完成综合分析');
  }
};

// 加载活动数据
const loadActivitiesData = async () => {
  const response = await fetch('/static/activities.json');
  if (!response.ok) {
    throw new Error('Failed to load activities data');
  }
  return response.json();
};

// 分析训练负荷
const analyzeTrainingLoad = (activities: any[]) => {
  const now = new Date();
  const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
  const oneMonthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
  const oneYearAgo = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
  
  // 过滤最近的活动
  const recentActivities = activities.filter((activity: any) => {
    const activityDate = new Date(activity.start_date);
    return activityDate >= oneYearAgo;
  });
  
  let weeklyTSS = 0;
  let monthlyTSS = 0;
  let yearlyTSS = 0;
  
  recentActivities.forEach((activity: any) => {
    const activityDate = new Date(activity.start_date);
    const duration = parseMovingTimeHelper(activity.moving_time);
    const avgSpeed = activity.average_speed || 2.5; // m/s
    const avgPace = 1000 / avgSpeed; // seconds per km
    
    // 估算TSS（简化计算）
    const estimatedTSS = Math.round((duration / 3600) * 100 * (avgPace < 300 ? 1.2 : avgPace < 360 ? 1.0 : 0.8));
    
    if (activityDate >= oneWeekAgo) {
      weeklyTSS += estimatedTSS;
    }
    if (activityDate >= oneMonthAgo) {
      monthlyTSS += estimatedTSS;
    }
    yearlyTSS += estimatedTSS;
  });
  
  // 计算趋势
  const trendDirection: 'increasing' | 'decreasing' | 'stable' = weeklyTSS > 300 ? 'increasing' : weeklyTSS < 150 ? 'decreasing' : 'stable';
  
  // 评估风险
  let riskLevel: 'low' | 'moderate' | 'high' = 'low';
  if (weeklyTSS > 500) riskLevel = 'high';
  else if (weeklyTSS > 350) riskLevel = 'moderate';
  
  return {
    weeklyTSS,
    monthlyTSS,
    yearlyTSS,
    trendDirection,
    riskLevel
  };
};

// 分析表现
const analyzePerformance = (activities: any[]) => {
  const recentActivities = activities.slice(-30); // 最近30次活动
  
  if (recentActivities.length === 0) {
    return {
      avgPace: '5:00',
      paceImprovement: 0,
      avgHeartRate: 150,
      vdotEstimate: 35,
      fitnessLevel: '业余初级'
    };
  }
  
  // 计算平均配速
  const totalDistance = recentActivities.reduce((sum: number, activity: any) => sum + activity.distance, 0);
  const totalTime = recentActivities.reduce((sum: number, activity: any) => sum + parseMovingTimeHelper(activity.moving_time), 0);
  const avgSpeed = totalDistance / totalTime; // m/s
  const avgPaceSeconds = 1000 / avgSpeed; // seconds per km
  const avgPace = formatPaceHelper(avgPaceSeconds);
  
  // 计算配速改善（与前一个月比较）
  const olderActivities = activities.slice(-60, -30);
  let paceImprovement = 0;
  if (olderActivities.length > 0) {
    const oldTotalDistance = olderActivities.reduce((sum: number, activity: any) => sum + activity.distance, 0);
    const oldTotalTime = olderActivities.reduce((sum: number, activity: any) => sum + parseMovingTimeHelper(activity.moving_time), 0);
    const oldAvgSpeed = oldTotalDistance / oldTotalTime;
    const oldAvgPaceSeconds = 1000 / oldAvgSpeed;
    paceImprovement = Math.round(oldAvgPaceSeconds - avgPaceSeconds);
  }
  
  // 计算平均心率
  const activitiesWithHR = recentActivities.filter((activity: any) => activity.average_heartrate);
  const avgHeartRate = activitiesWithHR.length > 0 
    ? Math.round(activitiesWithHR.reduce((sum: number, activity: any) => sum + activity.average_heartrate, 0) / activitiesWithHR.length)
    : 150;
  
  // 估算VDOT值
  const vdotEstimate = estimateVDOTFromPaceHelper(avgPaceSeconds);
  const fitnessLevel = getFitnessLevelHelper(vdotEstimate);
  
  return {
    avgPace,
    paceImprovement,
    avgHeartRate,
    vdotEstimate,
    fitnessLevel
  };
};

// 生成个性化建议
const generateRecommendations = (activities: any[], trainingLoad: any, performance: any) => {
  const vdot = performance.vdotEstimate;
  const weeklyTSS = trainingLoad.weeklyTSS;
  const riskLevel = trainingLoad.riskLevel;
  
  // 训练重点建议
  let trainingFocus = '';
  if (vdot < 35) {
    trainingFocus = '建议以有氧基础训练为主，增加跑量，提高心肺功能。重点进行轻松跑和长距离慢跑。';
  } else if (vdot < 45) {
    trainingFocus = '在保持有氧基础的同时，适当增加节奏跑和间歇训练，提高乳酸阈值和速度耐力。';
  } else {
    trainingFocus = '可以进行更多高质量的间歇训练和速度训练，同时保持足够的有氧基础训练。';
  }
  
  // 周训练结构
  let weeklyStructure = [];
  if (riskLevel === 'high') {
    weeklyStructure = [
      '休息或轻度交叉训练',
      '轻松跑 30-40分钟',
      '休息',
      '轻松跑 45分钟',
      '休息',
      '中长跑 60分钟',
      '休息或步行恢复'
    ];
  } else if (vdot < 35) {
    weeklyStructure = [
      '轻松跑 30分钟',
      '休息或交叉训练',
      '轻松跑 40分钟',
      '休息',
      '节奏跑 20分钟',
      '长跑 60-90分钟',
      '休息'
    ];
  } else {
    weeklyStructure = [
      '轻松跑 45分钟',
      '间歇训练 40分钟',
      '轻松跑 50分钟',
      '节奏跑 35分钟',
      '轻松跑 40分钟',
      '长跑 90-120分钟',
      '恢复跑或休息'
    ];
  }
  
  // 恢复建议
  let recoveryAdvice = '';
  if (riskLevel === 'high') {
    recoveryAdvice = '立即减少训练强度，确保每晚8小时睡眠，增加拉伸和按摩。监测晨脉，如持续升高需完全休息。';
  } else if (riskLevel === 'moderate') {
    recoveryAdvice = '注意充足睡眠，增加恢复跑比例，每周至少2天完全休息或轻度交叉训练。';
  } else {
    recoveryAdvice = '保持规律作息，训练后及时补充营养，每周至少1天完全休息，定期进行深度拉伸。';
  }
  
  // 营养建议
  const nutritionTips = '跑步前2-3小时避免高纤维食物，长跑时每60分钟补充30-60g碳水化合物。训练后30分钟内补充蛋白质和碳水化合物，比例3:1或4:1。';
  
  return {
    trainingFocus,
    weeklyStructure,
    recoveryAdvice,
    nutritionTips
  };
};

// 分析近期活动
const analyzeRecentActivities = (activities: any[]) => {
  const now = new Date();
  const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
  
  // 排序活动数据，最新的在前
  const sortedActivities = activities.sort((a: any, b: any) => {
    const dateA = new Date(a.start_date).getTime();
    const dateB = new Date(b.start_date).getTime();
    return dateB - dateA; // 降序排列，最新的在前
  });
  
  const recentActivities = sortedActivities.filter((activity: any) => {
    const activityDate = new Date(activity.start_date);
    return activityDate >= thirtyDaysAgo && activityDate <= now;
  });
  
  console.log('Recent activities found:', recentActivities.length);
  console.log('Sample recent activity:', recentActivities[0]);
  
  const totalRuns = recentActivities.length;
  const totalDistance = recentActivities.reduce((sum: number, activity: any) => sum + (activity.distance || 0), 0);
  const avgDistance = totalRuns > 0 ? totalDistance / totalRuns : 0;
  const longestRun = recentActivities.reduce((max: number, activity: any) => Math.max(max, activity.distance || 0), 0);
  
  return {
    totalRuns,
    totalDistance,
    avgDistance,
    longestRun,
    recentActivities: recentActivities.slice(0, 10) // 返回最近10次活动用于详细分析
  };
};

// 辅助函数
const parseMovingTimeHelper = (movingTime: string): number => {
  const parts = movingTime.split(':').map(Number);
  if (parts.length === 2) {
    return parts[0] * 60 + parts[1]; // MM:SS
  } else if (parts.length === 3) {
    return parts[0] * 3600 + parts[1] * 60 + parts[2]; // HH:MM:SS
  }
  return 0;
};

const formatPaceHelper = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const secs = Math.round(seconds % 60);
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
};

const estimateVDOTFromPaceHelper = (paceSeconds: number): number => {
  // 基于5公里配速的简化VDOT估算
  if (paceSeconds < 240) return 60; // < 4:00/km
  if (paceSeconds < 270) return 55; // < 4:30/km
  if (paceSeconds < 300) return 50; // < 5:00/km
  if (paceSeconds < 330) return 45; // < 5:30/km
  if (paceSeconds < 360) return 40; // < 6:00/km
  if (paceSeconds < 420) return 35; // < 7:00/km
  return 30; // >= 7:00/km
};

const getFitnessLevelHelper = (vdot: number): string => {
  if (vdot >= 55) return '精英级';
  if (vdot >= 50) return '高级';
  if (vdot >= 45) return '中高级';
  if (vdot >= 40) return '中级';
  if (vdot >= 35) return '中初级';
  return '业余初级';
}; 