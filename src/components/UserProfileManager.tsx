import React, { useState, useEffect } from 'react';

export interface UserProfile {
  // 基本信息
  age: number;
  weight: number; // kg
  height: number; // cm
  gender: 'male' | 'female';
  
  // 心率相关
  maxHeartRate?: number;
  restingHeartRate?: number;
  lactateThresholdHR?: number;
  
  // 配速相关
  marathon_pace?: string; // 马拉松最佳配速 (min:sec/km)
  half_marathon_pace?: string; // 半马最佳配速
  km10_pace?: string; // 10公里最佳配速
  km5_pace?: string; // 5公里最佳配速
  lactate_threshold_pace?: string; // 乳酸阈值配速
  
  // 训练相关
  weeklyMileage?: number; // 周跑量 (km)
  trainingExperience?: number; // 训练年数
  fitnessLevel?: 'beginner' | 'intermediate' | 'advanced' | 'elite';
  
  // 健康状况
  healthStatus?: 'excellent' | 'good' | 'fair' | 'recovering';
  injuries?: string[];
  
  // 目标设定
  primaryGoal?: 'fitness' | 'weight_loss' | '5k' | '10k' | 'half_marathon' | 'marathon' | 'ultra';
  targetRaceDate?: string;
  targetTime?: string;
}

interface UserProfileManagerProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (profile: UserProfile) => void;
  initialProfile?: UserProfile;
}

const UserProfileManager: React.FC<UserProfileManagerProps> = ({
  isOpen,
  onClose,
  onSave,
  initialProfile
}) => {
  const [profile, setProfile] = useState<UserProfile>({
    age: 30,
    weight: 70,
    height: 170,
    gender: 'male',
    fitnessLevel: 'intermediate',
    healthStatus: 'good',
    primaryGoal: 'fitness',
    weeklyMileage: 30,
    trainingExperience: 2,
    ...initialProfile
  });

  const [activeTab, setActiveTab] = useState<'basic' | 'performance' | 'goals'>('basic');

  // 智能计算最大心率
  const calculateMaxHR = () => {
    const estimatedMaxHR = 220 - profile.age;
    setProfile(prev => ({ ...prev, maxHeartRate: estimatedMaxHR }));
  };

  // 智能推算乳酸阈值心率
  const calculateLactateThresholdHR = () => {
    if (profile.maxHeartRate && profile.restingHeartRate) {
      const hrReserve = profile.maxHeartRate - profile.restingHeartRate;
      const ltHR = Math.round(profile.restingHeartRate + hrReserve * 0.85);
      setProfile(prev => ({ ...prev, lactateThresholdHR: ltHR }));
    }
  };

  // 根据已知配速推算其他配速
  const estimatePaces = () => {
    if (profile.km5_pace) {
      const pace5kSeconds = parseTimeToSeconds(profile.km5_pace);
      
      // 基于Daniels公式的简化估算
      const pace10k = formatPaceFromSeconds(pace5kSeconds + 15); // 10K比5K慢15秒/km
      const paceHalf = formatPaceFromSeconds(pace5kSeconds + 45); // 半马比5K慢45秒/km
      const paceFull = formatPaceFromSeconds(pace5kSeconds + 90); // 全马比5K慢90秒/km
      const paceLT = formatPaceFromSeconds(pace5kSeconds + 25); // 乳酸阈值配速
      
      setProfile(prev => ({
        ...prev,
        km10_pace: pace10k,
        half_marathon_pace: paceHalf,
        marathon_pace: paceFull,
        lactate_threshold_pace: paceLT
      }));
    }
  };

  const parseTimeToSeconds = (timeStr: string): number => {
    const parts = timeStr.split(':').map(Number);
    return parts[0] * 60 + parts[1];
  };

  const formatPaceFromSeconds = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSave = () => {
    // 保存到localStorage
    localStorage.setItem('userProfile', JSON.stringify(profile));
    onSave(profile);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* 头部 */}
        <div className="bg-blue-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">👤 个人信息设置</h2>
              <p className="text-blue-100 mt-1">设置您的基础信息以获得更精准的训练建议</p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-300 text-2xl"
            >
              ✕
            </button>
          </div>
        </div>

        {/* 标签导航 */}
        <div className="border-b border-gray-200">
          <div className="flex">
            {[
              { key: 'basic', label: '基本信息', icon: '📋' },
              { key: 'performance', label: '运动数据', icon: '🏃‍♂️' },
              { key: 'goals', label: '目标设定', icon: '🎯' }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`px-6 py-4 font-medium transition-colors ${
                  activeTab === tab.key
                    ? 'border-b-2 border-blue-500 text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* 内容区域 */}
        <div className="p-6 max-h-[60vh] overflow-y-auto">
          {/* 基本信息 */}
          {activeTab === 'basic' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    年龄
                  </label>
                  <input
                    type="number"
                    value={profile.age}
                    onChange={(e) => setProfile(prev => ({ ...prev, age: parseInt(e.target.value) || 0 }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="10"
                    max="100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    性别
                  </label>
                  <select
                    value={profile.gender}
                    onChange={(e) => setProfile(prev => ({ ...prev, gender: e.target.value as 'male' | 'female' }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="male">男性</option>
                    <option value="female">女性</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    体重 (kg)
                  </label>
                  <input
                    type="number"
                    value={profile.weight}
                    onChange={(e) => setProfile(prev => ({ ...prev, weight: parseFloat(e.target.value) || 0 }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="30"
                    max="200"
                    step="0.1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    身高 (cm)
                  </label>
                  <input
                    type="number"
                    value={profile.height}
                    onChange={(e) => setProfile(prev => ({ ...prev, height: parseInt(e.target.value) || 0 }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="100"
                    max="250"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    训练经验 (年)
                  </label>
                  <input
                    type="number"
                    value={profile.trainingExperience}
                    onChange={(e) => setProfile(prev => ({ ...prev, trainingExperience: parseInt(e.target.value) || 0 }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="0"
                    max="50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    健康状况
                  </label>
                  <select
                    value={profile.healthStatus}
                    onChange={(e) => setProfile(prev => ({ ...prev, healthStatus: e.target.value as any }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="excellent">极佳</option>
                    <option value="good">良好</option>
                    <option value="fair">一般</option>
                    <option value="recovering">恢复中</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* 运动数据 */}
          {activeTab === 'performance' && (
            <div className="space-y-6">
              {/* 心率数据 */}
              <div className="bg-red-50 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  ❤️ 心率数据
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      最大心率 (bpm)
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type="number"
                        value={profile.maxHeartRate || ''}
                        onChange={(e) => setProfile(prev => ({ ...prev, maxHeartRate: parseInt(e.target.value) || undefined }))}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="计算或手动输入"
                      />
                      <button
                        onClick={calculateMaxHR}
                        className="px-3 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 text-sm"
                      >
                        计算
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      静息心率 (bpm)
                    </label>
                    <input
                      type="number"
                      value={profile.restingHeartRate || ''}
                      onChange={(e) => setProfile(prev => ({ ...prev, restingHeartRate: parseInt(e.target.value) || undefined }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="40-80"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      乳酸阈值心率 (bpm)
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type="number"
                        value={profile.lactateThresholdHR || ''}
                        onChange={(e) => setProfile(prev => ({ ...prev, lactateThresholdHR: parseInt(e.target.value) || undefined }))}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="估算值"
                      />
                      <button
                        onClick={calculateLactateThresholdHR}
                        className="px-3 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 text-sm"
                      >
                        估算
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* 配速数据 */}
              <div className="bg-green-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                    🏃‍♂️ 最佳配速记录
                  </h3>
                  <button
                    onClick={estimatePaces}
                    className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 text-sm"
                  >
                    根据5K配速估算其他配速
                  </button>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      5公里配速 (分:秒/km)
                    </label>
                    <input
                      type="text"
                      value={profile.km5_pace || ''}
                      onChange={(e) => setProfile(prev => ({ ...prev, km5_pace: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="4:30"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      10公里配速
                    </label>
                    <input
                      type="text"
                      value={profile.km10_pace || ''}
                      onChange={(e) => setProfile(prev => ({ ...prev, km10_pace: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="4:45"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      半程马拉松配速
                    </label>
                    <input
                      type="text"
                      value={profile.half_marathon_pace || ''}
                      onChange={(e) => setProfile(prev => ({ ...prev, half_marathon_pace: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="5:15"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      全程马拉松配速
                    </label>
                    <input
                      type="text"
                      value={profile.marathon_pace || ''}
                      onChange={(e) => setProfile(prev => ({ ...prev, marathon_pace: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="5:30"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      乳酸阈值配速
                    </label>
                    <input
                      type="text"
                      value={profile.lactate_threshold_pace || ''}
                      onChange={(e) => setProfile(prev => ({ ...prev, lactate_threshold_pace: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="4:55"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      周跑量 (km)
                    </label>
                    <input
                      type="number"
                      value={profile.weeklyMileage || ''}
                      onChange={(e) => setProfile(prev => ({ ...prev, weeklyMileage: parseInt(e.target.value) || undefined }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="30"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 目标设定 */}
          {activeTab === 'goals' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    主要目标
                  </label>
                  <select
                    value={profile.primaryGoal}
                    onChange={(e) => setProfile(prev => ({ ...prev, primaryGoal: e.target.value as any }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="fitness">保持健康</option>
                    <option value="weight_loss">减重</option>
                    <option value="5k">5公里比赛</option>
                    <option value="10k">10公里比赛</option>
                    <option value="half_marathon">半程马拉松</option>
                    <option value="marathon">全程马拉松</option>
                    <option value="ultra">超马</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    目标比赛日期
                  </label>
                  <input
                    type="date"
                    value={profile.targetRaceDate || ''}
                    onChange={(e) => setProfile(prev => ({ ...prev, targetRaceDate: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    目标时间
                  </label>
                  <input
                    type="text"
                    value={profile.targetTime || ''}
                    onChange={(e) => setProfile(prev => ({ ...prev, targetTime: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="例：1:30:00 (半马)"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    当前水平
                  </label>
                  <select
                    value={profile.fitnessLevel}
                    onChange={(e) => setProfile(prev => ({ ...prev, fitnessLevel: e.target.value as any }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="beginner">初学者</option>
                    <option value="intermediate">中级</option>
                    <option value="advanced">高级</option>
                    <option value="elite">精英</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 底部按钮 */}
        <div className="border-t border-gray-200 p-6">
          <div className="flex justify-end space-x-4">
            <button
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              取消
            </button>
            <button
              onClick={handleSave}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              保存设置
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfileManager;
export type { UserProfile }; 