import React from 'react';

// 统计概览组件
interface StatsOverviewProps {
  selectedTypes: string[];
  overviewData: any;
  recentSummary: any;
}

// const formatTime = (seconds: number): string => {
//   if (seconds <= 0) return '0:00';

//   const hours = Math.floor(seconds / 3600);
//   const minutes = Math.floor((seconds % 3600) / 60);
//   const secs = seconds % 60;

//   if (hours > 0) {
//     return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
//   } else {
//     return `${minutes}:${secs.toString().padStart(2, '0')}`;
//   }
// };

const StatsOverview: React.FC<StatsOverviewProps> = ({
  selectedTypes: _selectedTypes,
  overviewData,
  recentSummary: _recentSummary,
}) => {
  if (!overviewData) return null;

  const overview = overviewData.overview || {};
  // const typeBreakdown = overviewData.type_breakdown || {};

  return (
    <div className="stats-overview rounded-lg bg-white p-6 shadow-md">
      <h3 className="mb-4 text-lg font-semibold">📈 统计概览</h3>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <div className="rounded-lg bg-blue-50 p-4 text-center">
          <div className="text-2xl font-bold text-blue-600">
            {overview.total_activities || 0}
          </div>
          <div className="text-sm text-gray-600">总活动数</div>
        </div>
        <div className="rounded-lg bg-green-50 p-4 text-center">
          <div className="text-2xl font-bold text-green-600">
            {overview.total_distance_km || 0} km
          </div>
          <div className="text-sm text-gray-600">总距离</div>
        </div>
        <div className="rounded-lg bg-purple-50 p-4 text-center">
          <div className="text-2xl font-bold text-purple-600">
            {overview.total_time_formatted || '0:00'}
          </div>
          <div className="text-sm text-gray-600">总时间</div>
        </div>
        <div className="rounded-lg bg-orange-50 p-4 text-center">
          <div className="text-2xl font-bold text-orange-600">
            {overview.avg_distance_per_activity || 0} km
          </div>
          <div className="text-sm text-gray-600">平均距离</div>
        </div>
      </div>
    </div>
  );
};

export default StatsOverview;
