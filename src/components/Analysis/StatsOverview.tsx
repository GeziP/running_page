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

const StatsOverview = ({
  selectedTypes: _selectedTypes,
  overviewData,
  recentSummary: _recentSummary,
}: StatsOverviewProps) => {
  if (!overviewData) return null;

  const overview = overviewData.overview || {};
  // const typeBreakdown = overviewData.type_breakdown || {};

  return {
    component: 'div',
    className: 'stats-overview bg-white rounded-lg shadow-md p-6',
    children: [
      {
        component: 'h3',
        className: 'text-lg font-semibold mb-4',
        children: '📈 统计概览',
      },
      {
        component: 'div',
        className: 'grid grid-cols-2 md:grid-cols-4 gap-4',
        children: [
          {
            component: 'div',
            className: 'text-center p-4 bg-blue-50 rounded-lg',
            children: [
              {
                component: 'div',
                className: 'text-2xl font-bold text-blue-600',
                children: overview.total_activities || 0,
              },
              {
                component: 'div',
                className: 'text-sm text-gray-600',
                children: '总活动数',
              },
            ],
          },
          {
            component: 'div',
            className: 'text-center p-4 bg-green-50 rounded-lg',
            children: [
              {
                component: 'div',
                className: 'text-2xl font-bold text-green-600',
                children: `${overview.total_distance_km || 0} km`,
              },
              {
                component: 'div',
                className: 'text-sm text-gray-600',
                children: '总距离',
              },
            ],
          },
          {
            component: 'div',
            className: 'text-center p-4 bg-purple-50 rounded-lg',
            children: [
              {
                component: 'div',
                className: 'text-2xl font-bold text-purple-600',
                children: overview.total_time_formatted || '0:00',
              },
              {
                component: 'div',
                className: 'text-sm text-gray-600',
                children: '总时间',
              },
            ],
          },
          {
            component: 'div',
            className: 'text-center p-4 bg-orange-50 rounded-lg',
            children: [
              {
                component: 'div',
                className: 'text-2xl font-bold text-orange-600',
                children: `${overview.avg_distance_per_activity || 0} km`,
              },
              {
                component: 'div',
                className: 'text-sm text-gray-600',
                children: '平均距离',
              },
            ],
          },
        ],
      },
    ],
  };
};

export default StatsOverview;
