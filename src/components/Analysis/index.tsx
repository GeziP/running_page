import React, { useState, useEffect } from 'react';
import ActivityTypeSelector from './ActivityTypeSelector';
import StatsOverview from './StatsOverview';
import Charts from './Charts';

interface AnalysisData {
  activityTypes?: any;
  basicStats?: any;
  overview?: any;
  recentSummary?: any;
}

const Analysis: React.FC = () => {
  const [selectedTypes, setSelectedTypes] = useState<string[]>(['all']);
  const [analysisData, setAnalysisData] = useState<AnalysisData>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalysisData();
  }, []);

  const loadAnalysisData = async () => {
    try {
      setLoading(true);
      
      // 并行加载所有分析数据
      const [typesRes, overviewRes, summaryRes] = await Promise.allSettled([
        fetch('/src/static/analysis/activity_types.json'),
        fetch('/src/static/analysis/analysis_overview.json'),
        fetch('/src/static/analysis/recent_summary.json')
      ]);

      const data: AnalysisData = {};

      if (typesRes.status === 'fulfilled' && typesRes.value.ok) {
        data.activityTypes = await typesRes.value.json();
      }

      if (overviewRes.status === 'fulfilled' && overviewRes.value.ok) {
        data.overview = await overviewRes.value.json();
      }

      if (summaryRes.status === 'fulfilled' && summaryRes.value.ok) {
        data.recentSummary = await summaryRes.value.json();
      }

      setAnalysisData(data);
    } catch (err) {
      setError('加载分析数据失败');
      console.error('Error loading analysis data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-lg">🔄 正在加载分析数据...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-red-500">❌ {error}</div>
      </div>
    );
  }

  const availableTypes = analysisData.activityTypes?.available_types || [];

  return (
    <div className="analysis-container space-y-6">
      {/* 页面标题 */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">
          📊 数据分析
        </h2>
        <p className="text-gray-600">
          深入了解您的运动表现和趋势
        </p>
      </div>

      {/* 活动类型选择器 */}
      <ActivityTypeSelector
        availableTypes={availableTypes}
        selectedTypes={selectedTypes}
        onTypeChange={setSelectedTypes}
        typeStats={analysisData.activityTypes?.type_statistics}
      />

      {/* 统计概览 */}
      <StatsOverview
        selectedTypes={selectedTypes}
        overviewData={analysisData.overview}
        recentSummary={analysisData.recentSummary}
      />

      {/* 图表展示 */}
      <Charts
        selectedTypes={selectedTypes}
        analysisData={analysisData}
      />
    </div>
  );
};

export default Analysis; 