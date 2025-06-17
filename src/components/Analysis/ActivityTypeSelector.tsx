import React from 'react';

interface ActivityTypeStats {
  name: string;
  icon: string;
  count: number;
  total_distance: number;
  percentage: number;
}

interface ActivityTypeSelectorProps {
  availableTypes: string[];
  selectedTypes: string[];
  onTypeChange: (_types: string[]) => void;
  typeStats?: { [key: string]: ActivityTypeStats };
}

const ACTIVITY_TYPE_NAMES: { [key: string]: string } = {
  all: '全部活动',
  running: '跑步',
  trail_running: '越野跑',
  cycling: '骑行',
  walking: '步行',
};

const ACTIVITY_TYPE_ICONS: { [key: string]: string } = {
  all: '🏃‍♂️🚴‍♂️',
  running: '🏃‍♂️',
  trail_running: '🥾',
  cycling: '🚴‍♂️',
  walking: '🚶‍♂️',
};

const ActivityTypeSelector: React.FC<ActivityTypeSelectorProps> = ({
  availableTypes,
  selectedTypes,
  onTypeChange,
  typeStats,
}) => {
  const allTypes = ['all', ...availableTypes];

  const handleTypeClick = (type: string) => {
    if (type === 'all') {
      onTypeChange(['all']);
    } else {
      if (selectedTypes.includes('all')) {
        onTypeChange([type]);
      } else {
        if (selectedTypes.includes(type)) {
          const newTypes = selectedTypes.filter((t) => t !== type);
          onTypeChange(newTypes.length > 0 ? newTypes : ['all']);
        } else {
          onTypeChange([...selectedTypes, type]);
        }
      }
    }
  };

  const isSelected = (type: string) => {
    return (
      selectedTypes.includes(type) ||
      (selectedTypes.includes('all') && type === 'all')
    );
  };

  return (
    <div className="activity-type-selector rounded-lg bg-white p-6 shadow-md">
      <h3 className="mb-4 text-lg font-semibold">🏃‍♂️ 活动类型</h3>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {allTypes.map((type) => {
          const stats = typeStats?.[type];
          const name = ACTIVITY_TYPE_NAMES[type] || type;
          const icon = ACTIVITY_TYPE_ICONS[type] || '🏃‍♂️';
          const selected = isSelected(type);

          return (
            <div
              key={type}
              onClick={() => handleTypeClick(type)}
              className={`
                relative cursor-pointer rounded-lg border-2 p-4 transition-all duration-200 hover:shadow-md
                ${
                  selected
                    ? 'border-blue-500 bg-blue-50 shadow-md'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }
              `}
            >
              <div className="text-center">
                <div className="mb-2 text-2xl">{icon}</div>
                <div className="font-medium text-gray-800">{name}</div>

                {stats && (
                  <div className="mt-2 text-sm text-gray-600">
                    <div>{stats.count} 次活动</div>
                    <div>{stats.total_distance.toFixed(1)} 公里</div>
                    <div className="text-xs text-gray-500">
                      {stats.percentage}%
                    </div>
                  </div>
                )}
              </div>

              {selected && (
                <div className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-blue-500">
                  <div className="text-xs text-white">✓</div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* 选择说明 */}
      <div className="mt-4 text-sm text-gray-500">
        💡 提示：点击单个类型进行筛选，可选择多个类型进行对比分析
      </div>

      {/* 已选择类型显示 */}
      {selectedTypes.length > 0 && !selectedTypes.includes('all') && (
        <div className="mt-3 flex flex-wrap gap-2">
          <span className="text-sm text-gray-600">已选择：</span>
          {selectedTypes.map((type) => (
            <span
              key={type}
              className="inline-flex items-center rounded-full bg-blue-100 px-2 py-1 text-xs text-blue-800"
            >
              {ACTIVITY_TYPE_ICONS[type]} {ACTIVITY_TYPE_NAMES[type]}
              <button
                onClick={() => handleTypeClick(type)}
                className="ml-1 text-blue-600 hover:text-blue-800"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

export default ActivityTypeSelector;
 