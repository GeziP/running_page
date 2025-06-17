import React from 'react';

// 图表组件
interface ChartsProps {
  selectedTypes: string[];
  analysisData: any;
}

const Charts: React.FC<ChartsProps> = ({
  selectedTypes: _selectedTypes,
  analysisData: _analysisData,
}) => {
  return (
    <div className="charts-container space-y-6">
      <div className="rounded-lg bg-white p-6 shadow-md">
        <h3 className="mb-4 text-lg font-semibold">📊 图表分析</h3>
        <div className="py-8 text-center text-gray-500">
          📈 图表功能正在开发中，敬请期待！
        </div>
      </div>
    </div>
  );
};

export default Charts;
