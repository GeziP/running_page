import React, { useState, useEffect } from 'react';
import { useUserProfile } from '../contexts/UserProfileContext';
import { calculateVDOT, calculateTSS } from '../utils/professionalAnalysis';

interface Activity {
  start_date: string;
  distance: number;
  moving_time: string | number;
  average_speed?: number;
  average_heartrate?: number;
  type?: string;
  id?: number;
}

interface WeeklyData {
  weekStart: string;
  totalDistance: number;
  totalRuns: number;
  avgPace: string;
  avgHeartRate: number;
  weeklyTSS: number;
  longestRun: number;
  activities: Activity[];
}

interface MonthlyData {
  month: string;
  totalDistance: number;
  totalRuns: number;
  avgPace: string;
  avgHeartRate: number;
  monthlyTSS: number;
  longestRun: number;
  weeklyAverage: number;
}

const MultiTimeframeAnalysis: React.FC = () => {
  const { userProfile } = useUserProfile();
  const [activities, setActivities] = useState<Activity[]>([]);
  const [selectedActivity, setSelectedActivity] = useState<Activity | null>(null);
  const [weeklyData, setWeeklyData] = useState<WeeklyData[]>([]);
  const [monthlyData, setMonthlyData] = useState<MonthlyData[]>([]);
  const [activeTab, setActiveTab] = useState<'single' | 'weekly' | 'monthly'>('single');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadActivitiesData();
  }, []);

  const loadActivitiesData = async () => {
    try {
      const response = await fetch('/static/activities.json');
      const data = await response.json();
      
      // 排序活动，最新的在前
      const sortedActivities = data.sort((a: Activity, b: Activity) => {
        return new Date(b.start_date).getTime() - new Date(a.start_date).getTime();
      });
      
      setActivities(sortedActivities);
      setSelectedActivity(sortedActivities[0]); // 默认选择最新的活动
      
      // 处理周数据
      const weeklyAnalysis = processWeeklyData(sortedActivities);
      setWeeklyData(weeklyAnalysis);
      
      // 处理月数据
      const monthlyAnalysis = processMonthlyData(sortedActivities);
      setMonthlyData(monthlyAnalysis);
      
    } catch (error) {
      console.error('Failed to load activities data:', error);
    } finally {
      setLoading(false);
    }
  };

  const processWeeklyData = (activities: Activity[]): WeeklyData[] => {
    const weeks: { [key: string]: Activity[] } = {};
    
    activities.forEach(activity => {
      const date = new Date(activity.start_date);
      const weekStart = getWeekStart(date);
      const weekKey = weekStart.toISOString().split('T')[0];
      
      if (!weeks[weekKey]) {
        weeks[weekKey] = [];
      }
      weeks[weekKey].push(activity);
    });
    
    return Object.entries(weeks)
      .slice(0, 12) // 最近12周
      .map(([weekKey, weekActivities]) => {
        const totalDistance = weekActivities.reduce((sum, act) => sum + (act.distance || 0), 0);
        const totalRuns = weekActivities.length;
        const avgSpeed = weekActivities.reduce((sum, act) => sum + (act.average_speed || 0), 0) / totalRuns;
        const avgHeartRate = weekActivities.reduce((sum, act) => sum + (act.average_heartrate || 0), 0) / totalRuns;
        const longestRun = Math.max(...weekActivities.map(act => act.distance || 0));
        
        // 计算周TSS
        const weeklyTSS = weekActivities.reduce((sum, act) => {
          if (act.average_speed && userProfile?.lactate_threshold_pace) {
            try {
              const duration = typeof act.moving_time === 'string' 
                ? parseTimeToMinutes(act.moving_time) 
                : act.moving_time || 0;
              const avgPaceSeconds = avgSpeed > 0 ? 1000 / avgSpeed : 0;
              const ltPaceSeconds = parseTimeToSeconds(userProfile.lactate_threshold_pace);
              const tss = calculateTSS(duration, avgPaceSeconds, ltPaceSeconds);
              return sum + tss.tss;
            } catch {
              return sum;
            }
          }
          return sum;
        }, 0);
        
        const avgPaceSeconds = avgSpeed > 0 ? 1000 / avgSpeed : 0;
        const avgPaceMinutes = Math.floor(avgPaceSeconds / 60);
        const avgPaceSecs = Math.round(avgPaceSeconds % 60);
        const avgPace = `${avgPaceMinutes}:${avgPaceSecs.toString().padStart(2, '0')}`;
        
        return {
          weekStart: weekKey,
          totalDistance: totalDistance / 1000, // 转换为公里
          totalRuns,
          avgPace,
          avgHeartRate: Math.round(avgHeartRate),
          weeklyTSS: Math.round(weeklyTSS),
          longestRun: longestRun / 1000,
          activities: weekActivities
        };
      })
      .sort((a, b) => new Date(b.weekStart).getTime() - new Date(a.weekStart).getTime());
  };

  const processMonthlyData = (activities: Activity[]): MonthlyData[] => {
    const months: { [key: string]: Activity[] } = {};
    
    activities.forEach(activity => {
      const date = new Date(activity.start_date);
      const monthKey = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;
      
      if (!months[monthKey]) {
        months[monthKey] = [];
      }
      months[monthKey].push(activity);
    });
    
    return Object.entries(months)
      .slice(0, 6) // 最近6个月
      .map(([monthKey, monthActivities]) => {
        const totalDistance = monthActivities.reduce((sum, act) => sum + (act.distance || 0), 0);
        const totalRuns = monthActivities.length;
        const avgSpeed = monthActivities.reduce((sum, act) => sum + (act.average_speed || 0), 0) / totalRuns;
        const avgHeartRate = monthActivities.reduce((sum, act) => sum + (act.average_heartrate || 0), 0) / totalRuns;
        const longestRun = Math.max(...monthActivities.map(act => act.distance || 0));
        
        // 计算月TSS
        const monthlyTSS = monthActivities.reduce((sum, act) => {
          if (act.average_speed && userProfile?.lactate_threshold_pace) {
            try {
              const duration = typeof act.moving_time === 'string' 
                ? parseTimeToMinutes(act.moving_time) 
                : act.moving_time || 0;
              const avgPaceSeconds = act.average_speed > 0 ? 1000 / act.average_speed : 0;
              const ltPaceSeconds = parseTimeToSeconds(userProfile.lactate_threshold_pace);
              const tss = calculateTSS(duration, avgPaceSeconds, ltPaceSeconds);
              return sum + tss.tss;
            } catch {
              return sum;
            }
          }
          return sum;
        }, 0);
        
        const avgPaceSeconds = avgSpeed > 0 ? 1000 / avgSpeed : 0;
        const avgPaceMinutes = Math.floor(avgPaceSeconds / 60);
        const avgPaceSecs = Math.round(avgPaceSeconds % 60);
        const avgPace = `${avgPaceMinutes}:${avgPaceSecs.toString().padStart(2, '0')}`;
        
        // 计算周平均距离
        const weeks = Math.ceil(monthActivities.length / 7); // 估算周数
        const weeklyAverage = totalDistance / 1000 / (weeks || 1);
        
        return {
          month: monthKey,
          totalDistance: totalDistance / 1000,
          totalRuns,
          avgPace,
          avgHeartRate: Math.round(avgHeartRate),
          monthlyTSS: Math.round(monthlyTSS),
          longestRun: longestRun / 1000,
          weeklyAverage
        };
      })
      .sort((a, b) => b.month.localeCompare(a.month));
  };

  const getWeekStart = (date: Date): Date => {
    const day = date.getDay();
    const diff = date.getDate() - day + (day === 0 ? -6 : 1); // 获取周一
    return new Date(date.setDate(diff));
  };

  const parseTimeToMinutes = (timeStr: string): number => {
    const parts = timeStr.split(':').map(Number);
    if (parts.length === 3) {
      return parts[0] * 60 + parts[1] + parts[2] / 60; // hours:minutes:seconds
    } else if (parts.length === 2) {
      return parts[0] + parts[1] / 60; // minutes:seconds
    }
    return parseFloat(timeStr) || 0;
  };

  const parseTimeToSeconds = (timeStr: string): number => {
    const parts = timeStr.split(':').map(Number);
    return parts[0] * 60 + parts[1];
  };

  const analyzeActivity = (activity: Activity) => {
    if (!activity) return null;
    
    const distance = activity.distance / 1000; // 转换为公里
    const avgSpeed = activity.average_speed || 0;
    const pace = avgSpeed > 0 ? 1000 / avgSpeed : 0;
    const paceMinutes = Math.floor(pace / 60);
    const paceSeconds = Math.round(pace % 60);
    const paceStr = `${paceMinutes}:${paceSeconds.toString().padStart(2, '0')}`;
    
    let vdotEstimate = 0;
    let recommendations = '';
    
    // 如果距离和时间合适，计算VDOT
    if (distance >= 3 && pace > 0) {
      try {
        const duration = typeof activity.moving_time === 'string' 
          ? parseTimeToMinutes(activity.moving_time) * 60 
          : activity.moving_time || 0;
        const vdotResult = calculateVDOT(distance, duration);
        vdotEstimate = vdotResult.vdot;
        
        // 生成建议
        if (userProfile?.km5_pace) {
          const userPaceSeconds = parseTimeToSeconds(userProfile.km5_pace);
          if (pace < userPaceSeconds * 0.9) {
            recommendations = '配速偏快，注意控制强度，避免过度训练';
          } else if (pace > userPaceSeconds * 1.3) {
            recommendations = '轻松跑配速，适合恢复和有氧基础建设';
          } else {
            recommendations = '配速适中，符合中等强度训练';
          }
        }
      } catch (error) {
        console.error('VDOT calculation failed:', error);
      }
    }
    
    return {
      distance,
      pace: paceStr,
      vdotEstimate,
      recommendations,
      heartRate: activity.average_heartrate,
      duration: activity.moving_time
    };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">加载分析数据中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 时间维度选择 */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">⏱️ 多时间维度分析</h2>
        
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          {[
            { key: 'single', label: '单次分析', icon: '🎯', desc: '分析单次跑步表现' },
            { key: 'weekly', label: '周度分析', icon: '📅', desc: '最近12周训练趋势' },
            { key: 'monthly', label: '月度分析', icon: '📊', desc: '最近6个月数据对比' }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex-1 px-4 py-3 rounded-md transition-colors ${
                activeTab === tab.key
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <div className="text-center">
                <div className="text-lg mb-1">{tab.icon}</div>
                <div className="font-medium text-sm">{tab.label}</div>
                <div className="text-xs text-gray-500">{tab.desc}</div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 单次跑步分析 */}
      {activeTab === 'single' && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🏃‍♂️ 单次跑步详细分析</h3>
          
          {/* 跑步选择 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">选择要分析的跑步</label>
            <select
              value={selectedActivity?.start_date || ''}
              onChange={(e) => {
                const activity = activities.find(act => act.start_date === e.target.value);
                setSelectedActivity(activity || null);
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {activities.slice(0, 20).map((activity, index) => (
                <option key={index} value={activity.start_date}>
                  {new Date(activity.start_date).toLocaleDateString('zh-CN')} - 
                  {(activity.distance / 1000).toFixed(2)}km
                </option>
              ))}
            </select>
          </div>

          {/* 分析结果 */}
          {selectedActivity && (
            <div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-blue-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {(selectedActivity.distance / 1000).toFixed(2)}
                  </div>
                  <div className="text-sm text-gray-600">距离 (km)</div>
                </div>
                
                <div className="bg-green-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {analyzeActivity(selectedActivity)?.pace || '-'}
                  </div>
                  <div className="text-sm text-gray-600">配速 (/km)</div>
                </div>
                
                <div className="bg-red-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-red-600">
                    {selectedActivity.average_heartrate ? Math.round(selectedActivity.average_heartrate) : '-'}
                  </div>
                  <div className="text-sm text-gray-600">平均心率 (bpm)</div>
                </div>
                
                <div className="bg-purple-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {analyzeActivity(selectedActivity)?.vdotEstimate?.toFixed(1) || '-'}
                  </div>
                  <div className="text-sm text-gray-600">VDOT估算</div>
                </div>
              </div>

              {/* 专业建议 */}
              {analyzeActivity(selectedActivity)?.recommendations && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h4 className="font-medium text-yellow-800 mb-2">💡 专业建议</h4>
                  <p className="text-yellow-700 text-sm">
                    {analyzeActivity(selectedActivity)?.recommendations}
                  </p>
                </div>
              )}

              {/* 心率区间分析 */}
              {selectedActivity.average_heartrate && userProfile?.maxHeartRate && (
                <div className="mt-4 bg-gray-50 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">❤️ 心率区间分析</h4>
                  <div className="text-sm text-gray-600">
                    <div>平均心率: {Math.round(selectedActivity.average_heartrate)} bpm</div>
                    <div>心率储备: {((selectedActivity.average_heartrate / userProfile.maxHeartRate) * 100).toFixed(1)}%</div>
                    {userProfile.lactateThresholdHR && (
                      <div>
                        {selectedActivity.average_heartrate > userProfile.lactateThresholdHR 
                          ? '高强度训练区间 - 注意恢复' 
                          : '有氧训练区间 - 适合基础建设'
                        }
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* 周度分析 */}
      {activeTab === 'weekly' && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📅 周度训练分析</h3>
          
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">周</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">距离</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">次数</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">平均配速</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">平均心率</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">周TSS</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">最长跑</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {weeklyData.map((week, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {new Date(week.weekStart).toLocaleDateString('zh-CN', { 
                        month: 'short', 
                        day: 'numeric' 
                      })}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">{week.totalDistance.toFixed(1)}km</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{week.totalRuns}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{week.avgPace}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {week.avgHeartRate > 0 ? `${week.avgHeartRate} bpm` : '-'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        week.weeklyTSS > 400 ? 'bg-red-100 text-red-800' :
                        week.weeklyTSS > 250 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {week.weeklyTSS}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">{week.longestRun.toFixed(1)}km</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 月度分析 */}
      {activeTab === 'monthly' && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 月度训练对比</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {monthlyData.map((month, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="text-center mb-4">
                  <h4 className="text-lg font-semibold text-gray-900">
                    {new Date(month.month + '-01').toLocaleDateString('zh-CN', { 
                      year: 'numeric', 
                      month: 'long' 
                    })}
                  </h4>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">总距离:</span>
                    <span className="font-medium">{month.totalDistance.toFixed(1)}km</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">跑步次数:</span>
                    <span className="font-medium">{month.totalRuns}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">平均配速:</span>
                    <span className="font-medium">{month.avgPace}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">周均距离:</span>
                    <span className="font-medium">{month.weeklyAverage.toFixed(1)}km</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">月度TSS:</span>
                    <span className={`font-medium ${
                      month.monthlyTSS > 1200 ? 'text-red-600' :
                      month.monthlyTSS > 800 ? 'text-yellow-600' :
                      'text-green-600'
                    }`}>
                      {month.monthlyTSS}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">最长跑:</span>
                    <span className="font-medium">{month.longestRun.toFixed(1)}km</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MultiTimeframeAnalysis; 