import React, { useState, useEffect } from 'react';
import {
  calculateVDOT,
  calculateMAF,
  calculateTSS,
  parseTimeToSeconds,
  formatTime,
  generateTrainingAdvice,
  getTheoryInfo,
  VDOTResult,
  MAFResult,
  TSSResult
} from '@/utils/professionalAnalysis';
import ComprehensiveAnalysis from '@/components/ComprehensiveAnalysis';
import { UserProfileProvider, useUserProfile } from '@/contexts/UserProfileContext';

const ProfessionalAnalysisInner: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'vdot' | 'maf' | 'tss' | 'comprehensive'>('vdot');
  const { userProfile } = useUserProfile();
  
  // VDOT计算器状态
  const [vdotInputs, setVdotInputs] = useState({
    distance: '5',
    hours: '0',
    minutes: '25',
    seconds: '0'
  });
  const [vdotResult, setVdotResult] = useState<VDOTResult | null>(null);

  // 使用用户配速数据自动填充
  useEffect(() => {
    if (userProfile?.km5_pace && vdotInputs.distance === '5') {
      const [minutes, seconds] = userProfile.km5_pace.split(':').map(Number);
      const totalSeconds = minutes * 60 + seconds;
      const raceTime = totalSeconds * 5; // 5km总时间
      const hours = Math.floor(raceTime / 3600);
      const mins = Math.floor((raceTime % 3600) / 60);
      const secs = raceTime % 60;
      
      setVdotInputs({
        distance: '5',
        hours: hours.toString(),
        minutes: mins.toString(),
        seconds: secs.toString()
      });
    }
  }, [userProfile, vdotInputs.distance]);

  // MAF计算器状态
  const [mafInputs, setMafInputs] = useState({
    age: '35',
    healthCategory: 'healthy'
  });
  const [mafResult, setMafResult] = useState<MAFResult | null>(null);

  // 使用用户年龄和健康状况自动填充MAF
  useEffect(() => {
    if (userProfile) {
      setMafInputs({
        age: userProfile.age.toString(),
        healthCategory: userProfile.healthStatus || 'healthy'
      });
    }
  }, [userProfile]);

  // TSS计算器状态
  const [tssInputs, setTssInputs] = useState({
    duration: '60',
    avgPace: '5:00',
    thresholdPace: '4:30'
  });
  const [tssResult, setTssResult] = useState<TSSResult | null>(null);

  // 使用用户乳酸阈值配速自动填充TSS
  useEffect(() => {
    if (userProfile?.lactate_threshold_pace) {
      setTssInputs(prev => ({
        ...prev,
        thresholdPace: userProfile.lactate_threshold_pace || '4:30'
      }));
    }
  }, [userProfile]);

  // 综合分析状态
  const [comprehensiveInputs, setComprehensiveInputs] = useState({
    age: '35',
    raceDistance: '10',
    raceTime: '45:00',
    healthStatus: 'healthy'
  });

  // VDOT计算函数
  const calculateVDOTClick = () => {
    const distance = parseFloat(vdotInputs.distance);
    const totalSeconds = parseInt(vdotInputs.hours) * 3600 + 
                        parseInt(vdotInputs.minutes) * 60 + 
                        parseInt(vdotInputs.seconds);
    
    if (distance <= 0 || totalSeconds <= 0) return;

    try {
      const result = calculateVDOT(distance, totalSeconds);
      setVdotResult(result);
    } catch (error) {
      console.error('VDOT计算错误:', error);
    }
  };

  // MAF计算函数
  const calculateMAFClick = () => {
    const age = parseInt(mafInputs.age);
    
    if (age <= 0 || age > 100) return;

    try {
      const result = calculateMAF(age, mafInputs.healthCategory);
      setMafResult(result);
    } catch (error) {
      console.error('MAF计算错误:', error);
    }
  };

  // TSS计算函数
  const calculateTSSClick = () => {
    const duration = parseFloat(tssInputs.duration);
    const avgPaceSeconds = parseTimeToSeconds(tssInputs.avgPace);
    const thresholdPaceSeconds = parseTimeToSeconds(tssInputs.thresholdPace);
    
    if (duration <= 0 || avgPaceSeconds <= 0 || thresholdPaceSeconds <= 0) return;
    
    try {
      const result = calculateTSS(duration, avgPaceSeconds, thresholdPaceSeconds);
      setTssResult(result);
    } catch (error) {
      console.error('TSS计算错误:', error);
    }
  };



  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 页面标题 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🏃‍♂️ 专业跑步数据分析平台
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            基于权威理论的科学训练指导
          </p>
          <p className="text-sm text-gray-500">
            采用 Jack Daniels VDOT、Phil Maffetone MAF 180、TrainingPeaks TSS 等专业理论
          </p>
        </div>

        {/* 导航标签 */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-1">
            <div className="flex space-x-1">
              {[
                { key: 'vdot', label: 'VDOT计算器', icon: '🎯' },
                { key: 'maf', label: 'MAF心率', icon: '❤️' },
                { key: 'tss', label: 'TSS评分', icon: '⚡' },
                { key: 'comprehensive', label: '综合分析', icon: '📊' }
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`px-6 py-3 rounded-md font-medium transition-colors ${
                    activeTab === tab.key
                      ? 'bg-blue-500 text-white shadow-sm'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* VDOT计算器 */}
        {activeTab === 'vdot' && (
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                🎯 VDOT训练系统
              </h2>
              <p className="text-gray-600">
                基于Jack Daniels理论，通过比赛成绩计算训练配速和能力预测
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-semibold mb-4">输入比赛成绩</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      比赛距离（公里）
                    </label>
                    <select
                      value={vdotInputs.distance}
                      onChange={(e) => setVdotInputs({...vdotInputs, distance: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="5">5公里</option>
                      <option value="10">10公里</option>
                      <option value="21.1">半程马拉松</option>
                      <option value="42.2">全程马拉松</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      完赛时间
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      <div>
                        <input
                          type="number"
                          value={vdotInputs.hours}
                          onChange={(e) => setVdotInputs({...vdotInputs, hours: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="时"
                          min="0"
                        />
                        <p className="text-xs text-gray-500 mt-1">小时</p>
                      </div>
                      <div>
                        <input
                          type="number"
                          value={vdotInputs.minutes}
                          onChange={(e) => setVdotInputs({...vdotInputs, minutes: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="分"
                          min="0"
                          max="59"
                        />
                        <p className="text-xs text-gray-500 mt-1">分钟</p>
                      </div>
                      <div>
                        <input
                          type="number"
                          value={vdotInputs.seconds}
                          onChange={(e) => setVdotInputs({...vdotInputs, seconds: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="秒"
                          min="0"
                          max="59"
                        />
                        <p className="text-xs text-gray-500 mt-1">秒钟</p>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={calculateVDOTClick}
                    className="w-full bg-blue-500 text-white py-3 px-6 rounded-md hover:bg-blue-600 transition-colors font-medium"
                  >
                    计算 VDOT 值
                  </button>
                </div>
              </div>

              {vdotResult && (
                <div>
                  <h3 className="text-lg font-semibold mb-4">分析结果</h3>
                  
                  <div className="bg-blue-50 rounded-lg p-6 mb-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-blue-600 mb-2">
                        {vdotResult.vdot}
                      </div>
                      <div className="text-sm text-gray-600">VDOT值</div>
                      <div className="text-lg font-medium text-gray-900 mt-2">
                        {vdotResult.fitnessLevel}
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">训练配速指导</h4>
                      <div className="grid grid-cols-2 gap-3">
                        <div className="bg-green-50 p-3 rounded-lg">
                          <div className="text-sm text-gray-600">轻松跑</div>
                          <div className="font-semibold text-green-700">{vdotResult.trainingPaces.easy}/公里</div>
                        </div>
                        <div className="bg-orange-50 p-3 rounded-lg">
                          <div className="text-sm text-gray-600">节奏跑</div>
                          <div className="font-semibold text-orange-700">{vdotResult.trainingPaces.tempo}/公里</div>
                        </div>
                        <div className="bg-red-50 p-3 rounded-lg">
                          <div className="text-sm text-gray-600">间歇跑</div>
                          <div className="font-semibold text-red-700">{vdotResult.trainingPaces.interval}/400米</div>
                        </div>
                        <div className="bg-purple-50 p-3 rounded-lg">
                          <div className="text-sm text-gray-600">重复跑</div>
                          <div className="font-semibold text-purple-700">{vdotResult.trainingPaces.repetition}/400米</div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">比赛时间预测</h4>
                      <div className="space-y-2">
                        {Object.entries(vdotResult.racePredictions).map(([distance, time]) => (
                          <div key={distance} className="flex justify-between items-center bg-gray-50 p-3 rounded-lg">
                            <span className="text-gray-700">{distance}</span>
                            <span className="font-semibold text-gray-900">{time}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* MAF心率计算器 */}
        {activeTab === 'maf' && (
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                ❤️ MAF 180心率训练系统
              </h2>
              <p className="text-gray-600">
                基于Phil Maffetone的180公式，计算最大有氧心率和训练区间
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-semibold mb-4">基本信息</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      年龄
                    </label>
                    <input
                      type="number"
                      value={mafInputs.age}
                      onChange={(e) => setMafInputs({...mafInputs, age: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="请输入年龄"
                      min="16"
                      max="80"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      健康状况
                    </label>
                    <select
                      value={mafInputs.healthCategory}
                      onChange={(e) => setMafInputs({...mafInputs, healthCategory: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="major_illness">重大疾病/服药/康复期 (-10)</option>
                      <option value="minor_issues">轻微问题/新手/感冒频繁 (-5)</option>
                      <option value="healthy">健康训练者 (0)</option>
                      <option value="elite">精英运动员/2年以上无伤 (+5)</option>
                      <option value="senior">65岁以上 (+10)</option>
                    </select>
                  </div>

                  <button
                    onClick={calculateMAFClick}
                    className="w-full bg-red-500 text-white py-3 px-6 rounded-md hover:bg-red-600 transition-colors font-medium"
                  >
                    计算 MAF 心率
                  </button>
                </div>
              </div>

              {mafResult && (
                <div>
                  <h3 className="text-lg font-semibold mb-4">心率区间</h3>
                  
                  <div className="bg-red-50 rounded-lg p-6 mb-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-red-600 mb-2">
                        {mafResult.mafHeartRate}
                      </div>
                      <div className="text-sm text-gray-600">MAF最大有氧心率</div>
                      <div className="text-lg font-medium text-gray-900 mt-2">
                        建议大部分训练保持在此心率以下
                      </div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    {Object.entries(mafResult.zones).map(([zoneKey, zone]) => (
                      <div key={zoneKey} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-center mb-2">
                          <div className="font-medium text-gray-900">
                            {zoneKey} - {zone.name}
                          </div>
                          <div className="text-lg font-bold text-blue-600">
                            {zone.min_hr}-{zone.max_hr} bpm
                          </div>
                        </div>
                        <div className="text-sm text-gray-600 mb-1">
                          {zone.description}
                        </div>
                        <div className="text-xs text-gray-500">
                          体感强度：{zone.rpe}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TSS计算器 */}
        {activeTab === 'tss' && (
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                ⚡ 训练压力评分 (TSS)
              </h2>
              <p className="text-gray-600">
                量化训练负荷，科学安排训练强度和恢复时间
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-semibold mb-4">训练数据</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      训练时长（分钟）
                    </label>
                    <input
                      type="number"
                      value={tssInputs.duration}
                      onChange={(e) => setTssInputs({...tssInputs, duration: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="60"
                      min="1"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      平均配速（分:秒/公里）
                    </label>
                    <input
                      type="text"
                      value={tssInputs.avgPace}
                      onChange={(e) => setTssInputs({...tssInputs, avgPace: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="5:00"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      阈值配速（分:秒/公里）
                    </label>
                    <input
                      type="text"
                      value={tssInputs.thresholdPace}
                      onChange={(e) => setTssInputs({...tssInputs, thresholdPace: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="4:30"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      通常为10公里或半程马拉松配速
                    </p>
                  </div>

                  <button
                    onClick={calculateTSSClick}
                    className="w-full bg-yellow-500 text-white py-3 px-6 rounded-md hover:bg-yellow-600 transition-colors font-medium"
                  >
                    计算 TSS 分数
                  </button>
                </div>
              </div>

              {tssResult && (
                <div>
                  <h3 className="text-lg font-semibold mb-4">训练负荷分析</h3>
                  
                  <div className="bg-yellow-50 rounded-lg p-6 mb-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-yellow-600 mb-2">
                        {tssResult.tss}
                      </div>
                      <div className="text-sm text-gray-600">TSS分数</div>
                      <div className="text-lg font-medium text-gray-900 mt-2">
                        {tssResult.interpretation}
                      </div>
                    </div>
                  </div>

                  <div className="bg-blue-50 rounded-lg p-6">
                    <h4 className="font-medium text-gray-900 mb-3">训练建议</h4>
                    <p className="text-gray-700">{tssResult.trainingAdvice}</p>
                    
                    <div className="mt-4 space-y-2">
                      <div className="text-sm">
                        <span className="font-medium">TSS参考标准：</span>
                      </div>
                      <div className="text-xs text-gray-600 space-y-1">
                        <div>• 150分以下：轻松训练，可每日进行</div>
                        <div>• 150-300分：中等强度，需1天恢复</div>
                        <div>• 300-450分：高强度训练，需2天恢复</div>
                        <div>• 450分以上：极高强度，需3天以上恢复</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 综合分析 */}
        {activeTab === 'comprehensive' && (
          <ComprehensiveAnalysis />
        )}

        {/* 理论说明 */}
        <div className="mt-12 bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">📚 理论基础说明</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="border border-gray-200 rounded-lg p-6">
              <h3 className="font-semibold text-gray-900 mb-3">🎯 VDOT系统</h3>
              <p className="text-sm text-gray-600 mb-3">
                由Jack Daniels博士开发，基于VO2max的跑步训练配速计算系统
              </p>
              <ul className="text-xs text-gray-500 space-y-1">
                <li>• 精确的训练配速指导</li>
                <li>• 科学的能力评估</li>
                <li>• 比赛成绩预测</li>
              </ul>
            </div>
            
            <div className="border border-gray-200 rounded-lg p-6">
              <h3 className="font-semibold text-gray-900 mb-3">❤️ MAF 180</h3>
              <p className="text-sm text-gray-600 mb-3">
                Phil Maffetone博士的最大有氧心率训练法，强调有氧基础建设
              </p>
              <ul className="text-xs text-gray-500 space-y-1">
                <li>• 提高脂肪燃烧效率</li>
                <li>• 减少受伤风险</li>
                <li>• 建立强大有氧基础</li>
              </ul>
            </div>
            
            <div className="border border-gray-200 rounded-lg p-6">
              <h3 className="font-semibold text-gray-900 mb-3">⚡ TSS评分</h3>
              <p className="text-sm text-gray-600 mb-3">
                训练压力评分系统，量化训练负荷和恢复需求
              </p>
              <ul className="text-xs text-gray-500 space-y-1">
                <li>• 客观量化训练强度</li>
                <li>• 科学安排恢复时间</li>
                <li>• 预防过度训练</li>
              </ul>
            </div>
          </div>
          
          <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <span className="text-yellow-600">⚠️</span>
              </div>
              <div className="ml-3">
                <h4 className="text-sm font-medium text-yellow-800">重要提醒</h4>
                <p className="text-sm text-yellow-700 mt-1">
                  本工具基于权威理论提供参考建议，实际训练应结合个人情况调整。
                  如有健康问题，请咨询专业医生或教练。
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const ProfessionalAnalysis: React.FC = () => {
  return (
    <UserProfileProvider>
      <ProfessionalAnalysisInner />
    </UserProfileProvider>
  );
};

export default ProfessionalAnalysis; 