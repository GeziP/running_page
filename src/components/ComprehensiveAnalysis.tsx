import React, { useState, useEffect } from 'react';
import { getComprehensiveAnalysis } from '../utils/professionalAnalysis';
import UserProfileManager, { UserProfile } from './UserProfileManager';
import { useUserProfile } from '../contexts/UserProfileContext';
import MultiTimeframeAnalysis from './MultiTimeframeAnalysis';

interface AnalysisData {
  trainingLoad: {
    weeklyTSS: number;
    monthlyTSS: number;
    yearlyTSS: number;
    trendDirection: 'increasing' | 'decreasing' | 'stable';
    riskLevel: 'low' | 'moderate' | 'high';
  };
  performance: {
    avgPace: string;
    paceImprovement: number;
    avgHeartRate: number;
    vdotEstimate: number;
    fitnessLevel: string;
  };
  recommendations: {
    trainingFocus: string;
    weeklyStructure: string[];
    recoveryAdvice: string;
    nutritionTips: string;
  };
  recentActivities: {
    totalRuns: number;
    totalDistance: number;
    avgDistance: number;
    longestRun: number;
    recentActivities?: any[]; // 最近的跑步记录
  };
}

const ComprehensiveAnalysis: React.FC = () => {
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showProfileManager, setShowProfileManager] = useState(false);
  const [activeSubTab, setActiveSubTab] = useState<'overview' | 'timeframe'>('overview');
  const { userProfile, setUserProfile } = useUserProfile();

  useEffect(() => {
    const loadAnalysis = async () => {
      try {
        setLoading(true);
        const data = await getComprehensiveAnalysis();
        setAnalysisData(data);
      } catch (err) {
        setError('无法加载分析数据，请稍后重试');
        console.error('Analysis loading error:', err);
      } finally {
        setLoading(false);
      }
    };

    loadAnalysis();
  }, []);

  const handleProfileSave = (profile: UserProfile) => {
    setUserProfile(profile);
    // 重新分析数据
    const loadAnalysis = async () => {
      try {
        const data = await getComprehensiveAnalysis();
        setAnalysisData(data);
      } catch (err) {
        console.error('Failed to reload analysis:', err);
      }
    };
    loadAnalysis();
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="text-center py-16">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">正在分析您的训练数据...</p>
        </div>
      </div>
    );
  }

  if (error || !analysisData) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="text-center py-16">
          <div className="text-6xl mb-4">⚠️</div>
          <h3 className="text-xl font-medium text-gray-900 mb-2">数据加载失败</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 transition-colors"
          >
            重新加载
          </button>
        </div>
      </div>
    );
  }

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'low': return 'text-green-600 bg-green-50';
      case 'moderate': return 'text-yellow-600 bg-yellow-50';
      case 'high': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing': return '📈';
      case 'decreasing': return '📉';
      default: return '➡️';
    }
  };

  return (
    <div className="space-y-8">
      {/* 标题和设置 */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              📊 综合专业分析
            </h2>
            <p className="text-gray-600">
              基于您的历史训练数据，提供全面的能力评估和训练指导方案
            </p>
          </div>
          <div className="flex items-center space-x-4">
            {userProfile && (
              <div className="text-right text-sm text-gray-600">
                <div>👤 {userProfile.age}岁 {userProfile.gender === 'male' ? '男' : '女'}</div>
                {userProfile.km5_pace && (
                  <div>🏃‍♂️ 5K配速: {userProfile.km5_pace}</div>
                )}
              </div>
            )}
            <button
              onClick={() => setShowProfileManager(true)}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors flex items-center"
            >
              ⚙️ {userProfile ? '编辑个人信息' : '设置个人信息'}
            </button>
          </div>
        </div>
        
        {!userProfile && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start">
              <span className="text-yellow-600 mr-2">💡</span>
              <div>
                <h4 className="text-sm font-medium text-yellow-800">建议设置个人信息</h4>
                <p className="text-sm text-yellow-700 mt-1">
                  设置您的年龄、心率、配速等信息，可以获得更精准的训练建议和风险评估。
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 训练负荷分析 */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
          ⚡ 训练负荷分析
          <span className="ml-2 text-sm font-normal text-gray-500">
            {getTrendIcon(analysisData.trainingLoad.trendDirection)} 
            {analysisData.trainingLoad.trendDirection === 'increasing' ? '负荷递增' : 
             analysisData.trainingLoad.trendDirection === 'decreasing' ? '负荷递减' : '负荷稳定'}
          </span>
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-blue-50 rounded-lg p-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600 mb-1">
                {analysisData.trainingLoad.weeklyTSS}
              </div>
              <div className="text-sm text-gray-600">周TSS</div>
              <div className="text-xs text-gray-500 mt-1">训练压力评分</div>
            </div>
          </div>
          
          <div className="bg-green-50 rounded-lg p-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600 mb-1">
                {analysisData.trainingLoad.monthlyTSS}
              </div>
              <div className="text-sm text-gray-600">月TSS</div>
              <div className="text-xs text-gray-500 mt-1">月度累积</div>
            </div>
          </div>
          
          <div className="bg-purple-50 rounded-lg p-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600 mb-1">
                {analysisData.trainingLoad.yearlyTSS}
              </div>
              <div className="text-sm text-gray-600">年TSS</div>
              <div className="text-xs text-gray-500 mt-1">年度累积</div>
            </div>
          </div>
        </div>

        <div className={`rounded-lg p-4 ${getRiskLevelColor(analysisData.trainingLoad.riskLevel)}`}>
          <div className="flex items-center">
            <span className="text-lg mr-2">
              {analysisData.trainingLoad.riskLevel === 'low' ? '✅' :
               analysisData.trainingLoad.riskLevel === 'moderate' ? '⚠️' : '🚨'}
            </span>
            <div>
              <div className="font-medium">
                过度训练风险：
                {analysisData.trainingLoad.riskLevel === 'low' ? '低风险' :
                 analysisData.trainingLoad.riskLevel === 'moderate' ? '中等风险' : '高风险'}
              </div>
              <div className="text-sm opacity-80 mt-1">
                {analysisData.trainingLoad.riskLevel === 'low' ? 
                  '当前训练负荷合理，可以继续保持' :
                  analysisData.trainingLoad.riskLevel === 'moderate' ?
                  '建议增加恢复训练，注意身体信号' :
                  '需要立即减少训练强度，增加休息时间'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 运动表现分析 */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h3 className="text-xl font-bold text-gray-900 mb-6">🏃‍♂️ 运动表现分析</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900 mb-1">
              {analysisData.performance.avgPace}
            </div>
            <div className="text-sm text-gray-600">平均配速</div>
            <div className="text-xs text-gray-500">分:秒/公里</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900 mb-1 flex items-center justify-center">
              {analysisData.performance.paceImprovement > 0 ? '📈' : 
               analysisData.performance.paceImprovement < 0 ? '📉' : '➡️'}
              <span className="ml-1">
                {Math.abs(analysisData.performance.paceImprovement)}s
              </span>
            </div>
            <div className="text-sm text-gray-600">配速改善</div>
            <div className="text-xs text-gray-500">相比上月</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900 mb-1">
              {analysisData.performance.avgHeartRate}
            </div>
            <div className="text-sm text-gray-600">平均心率</div>
            <div className="text-xs text-gray-500">次/分钟</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900 mb-1">
              {analysisData.performance.vdotEstimate}
            </div>
            <div className="text-sm text-gray-600">VDOT值</div>
            <div className="text-xs text-gray-500">{analysisData.performance.fitnessLevel}</div>
          </div>
        </div>

        <div className="bg-blue-50 rounded-lg p-6">
          <h4 className="font-medium text-gray-900 mb-3">🎯 能力水平评估</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium">当前等级：</span>
              <span className="text-blue-600 ml-1">{analysisData.performance.fitnessLevel}</span>
            </div>
            <div>
              <span className="font-medium">VDOT值：</span>
              <span className="text-blue-600 ml-1">{analysisData.performance.vdotEstimate}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 近期活动统计 */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h3 className="text-xl font-bold text-gray-900 mb-6">📈 近期活动统计（最近30天）</h3>
        
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900 mb-1">
              {analysisData.recentActivities.totalRuns}
            </div>
            <div className="text-sm text-gray-600">总跑步次数</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900 mb-1">
              {(analysisData.recentActivities.totalDistance / 1000).toFixed(1)}km
            </div>
            <div className="text-sm text-gray-600">总距离</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900 mb-1">
              {(analysisData.recentActivities.avgDistance / 1000).toFixed(1)}km
            </div>
            <div className="text-sm text-gray-600">平均距离</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900 mb-1">
              {(analysisData.recentActivities.longestRun / 1000).toFixed(1)}km
            </div>
            <div className="text-sm text-gray-600">最长距离</div>
          </div>
        </div>

        {/* 最近跑步记录详情 */}
        {analysisData.recentActivities.recentActivities && analysisData.recentActivities.recentActivities.length > 0 && (
          <div>
            <h4 className="text-lg font-semibold text-gray-900 mb-4">🏃‍♂️ 最近跑步记录</h4>
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">日期</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">距离</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">配速</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">心率</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">时长</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">类型</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {analysisData.recentActivities.recentActivities.slice(0, 5).map((activity: any, index: number) => {
                    const distance = (activity.distance / 1000).toFixed(2);
                    const avgSpeed = activity.average_speed || 0;
                    const paceSeconds = avgSpeed > 0 ? 1000 / avgSpeed : 0;
                    const paceMinutes = Math.floor(paceSeconds / 60);
                    const paceSecs = Math.round(paceSeconds % 60);
                    const pace = `${paceMinutes}:${paceSecs.toString().padStart(2, '0')}`;
                    const date = new Date(activity.start_date).toLocaleDateString('zh-CN');
                    const movingTime = activity.moving_time || '0:00';
                    
                    return (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm text-gray-900">{date}</td>
                        <td className="px-4 py-3 text-sm text-gray-900">{distance}km</td>
                        <td className="px-4 py-3 text-sm text-gray-900">{pace}/km</td>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {activity.average_heartrate ? `${Math.round(activity.average_heartrate)} bpm` : '-'}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">{movingTime}</td>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {activity.type || '跑步'}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            
            {analysisData.recentActivities.recentActivities.length > 5 && (
              <div className="mt-4 text-center">
                <p className="text-sm text-gray-500">
                  显示最近5次跑步，共{analysisData.recentActivities.recentActivities.length}次活动
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 个性化训练建议 */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h3 className="text-xl font-bold text-gray-900 mb-6">💡 个性化训练建议</h3>
        
        <div className="space-y-6">
          <div className="bg-green-50 rounded-lg p-6">
            <h4 className="font-medium text-gray-900 mb-3 flex items-center">
              🎯 训练重点
            </h4>
            <p className="text-gray-700">{analysisData.recommendations.trainingFocus}</p>
          </div>
          
          <div className="bg-blue-50 rounded-lg p-6">
            <h4 className="font-medium text-gray-900 mb-3 flex items-center">
              📅 建议周训练结构
            </h4>
            <div className="space-y-2">
              {analysisData.recommendations.weeklyStructure.map((day, index) => (
                <div key={index} className="flex items-center text-sm text-gray-700">
                  <span className="w-16 text-gray-500 font-medium">
                    {['周一', '周二', '周三', '周四', '周五', '周六', '周日'][index]}:
                  </span>
                  <span className="ml-2">{day}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-purple-50 rounded-lg p-6">
              <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                🛌 恢复建议
              </h4>
              <p className="text-sm text-gray-700">{analysisData.recommendations.recoveryAdvice}</p>
            </div>
            
            <div className="bg-orange-50 rounded-lg p-6">
              <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                🥗 营养建议
              </h4>
              <p className="text-sm text-gray-700">{analysisData.recommendations.nutritionTips}</p>
            </div>
          </div>
        </div>
      </div>

      {/* 数据说明 */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h3 className="text-lg font-bold text-gray-900 mb-4">📋 数据说明</h3>
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm text-gray-600 space-y-2">
            <p>• TSS (Training Stress Score)：基于训练时间和强度计算的训练压力评分</p>
            <p>• VDOT值：反映跑者有氧能力的综合指标，数值越高代表能力越强</p>
            <p>• 建议基于Jack Daniels跑步训练理论、MAF 180心率法和TSS训练负荷理论</p>
            <p>• 所有建议仅供参考，请结合个人实际情况调整训练计划</p>
          </div>
        </div>
      </div>

      {/* 用户个人信息管理器 */}
      <UserProfileManager
        isOpen={showProfileManager}
        onClose={() => setShowProfileManager(false)}
        onSave={handleProfileSave}
        initialProfile={userProfile || undefined}
      />
    </div>
  );
};

export default ComprehensiveAnalysis; 