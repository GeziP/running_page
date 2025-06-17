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
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">📊 图表分析</h3>
        <div className="text-center text-gray-500 py-8">
          📈 图表功能正在开发中，敬请期待！
        </div>
      </div>
    </div>
  );
};

export default Charts;
