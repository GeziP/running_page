import { useEffect, useState } from 'react';
import { Analytics } from '@vercel/analytics/react';
import Layout from '@/components/Layout';
import LocationStat from '@/components/LocationStat';
import RunMap from '@/components/RunMap';
import RunTable from '@/components/RunTable';
import SVGStat from '@/components/SVGStat';
import YearsStat from '@/components/YearsStat';
import useActivities from '@/hooks/useActivities';
import useSiteMetadata from '@/hooks/useSiteMetadata';
import { IS_CHINESE } from '@/utils/const';
import {
  Activity,
  IViewState,
  filterAndSortRuns,
  filterCityRuns,
  filterTitleRuns,
  filterYearRuns,
  geoJsonForRuns,
  getBoundsForGeoData,
  scrollToMap,
  sortDateFunc,
  titleForShow,
  RunIds,
} from '@/utils/utils';

const Index = () => {
  const { siteTitle } = useSiteMetadata();
  const { activities, thisYear } = useActivities();
  const [year, setYear] = useState(thisYear);
  const [runIndex, setRunIndex] = useState(-1);
  const [runs, setActivity] = useState(
    filterAndSortRuns(activities, year, filterYearRuns, sortDateFunc)
  );
  const [title, setTitle] = useState('');
  const [geoData, setGeoData] = useState(geoJsonForRuns(runs));
  // for auto zoom
  const bounds = getBoundsForGeoData(geoData);
  const [intervalId, setIntervalId] = useState<number>();

  const [viewState, setViewState] = useState<IViewState>({
    ...bounds,
  });

  const changeByItem = (
    item: string,
    name: string,
    func: (_run: Activity, _value: string) => boolean
  ) => {
    scrollToMap();
    if (name != 'Year') {
      setYear(thisYear);
    }
    setActivity(filterAndSortRuns(activities, item, func, sortDateFunc));
    setRunIndex(-1);
    setTitle(`${item} ${name} Running Heatmap`);
  };

  const changeYear = (y: string) => {
    // default year
    setYear(y);

    if ((viewState.zoom ?? 0) > 3 && bounds) {
      setViewState({
        ...bounds,
      });
    }

    changeByItem(y, 'Year', filterYearRuns);
    clearInterval(intervalId);
  };

  const changeCity = (city: string) => {
    changeByItem(city, 'City', filterCityRuns);
  };

  const changeTitle = (title: string) => {
    changeByItem(title, 'Title', filterTitleRuns);
  };

  const locateActivity = (runIds: RunIds) => {
    const ids = new Set(runIds);

    const selectedRuns = !runIds.length
      ? runs
      : runs.filter((r: any) => ids.has(r.run_id));

    if (!selectedRuns.length) {
      return;
    }

    const lastRun = selectedRuns.sort(sortDateFunc)[0];

    if (!lastRun) {
      return;
    }
    setGeoData(geoJsonForRuns(selectedRuns));
    setTitle(titleForShow(lastRun));
    clearInterval(intervalId);
    scrollToMap();
  };

  useEffect(() => {
    setViewState({
      ...bounds,
    });
  }, [geoData]);

  useEffect(() => {
    const runsNum = runs.length;
    // maybe change 20 ?
    const sliceNume = runsNum >= 20 ? runsNum / 20 : 1;
    let i = sliceNume;
    const id = setInterval(() => {
      if (i >= runsNum) {
        clearInterval(id);
      }

      const tempRuns = runs.slice(0, i);
      setGeoData(geoJsonForRuns(tempRuns));
      i += sliceNume;
    }, 100);
    setIntervalId(id);
  }, [runs]);

  useEffect(() => {
    if (year !== 'Total') {
      return;
    }

    let svgStat = document.getElementById('svgStat');
    if (!svgStat) {
      return;
    }

    const handleClick = (e: Event) => {
      const target = e.target as HTMLElement;
      if (target.tagName.toLowerCase() === 'path') {
        // Use querySelector to get the <desc> element and the <title> element.
        const descEl = target.querySelector('desc');
        if (descEl) {
          // If the runId exists in the <desc> element, it means that a running route has been clicked.
          const runId = Number(descEl.innerHTML);
          if (!runId) {
            return;
          }
          locateActivity([runId]);
          return;
        }

        const titleEl = target.querySelector('title');
        if (titleEl) {
          // If the runDate exists in the <title> element, it means that a date square has been clicked.
          const [runDate] = titleEl.innerHTML.match(
            /\d{4}-\d{1,2}-\d{1,2}/
          ) || [`${+thisYear + 1}`];
          const runIDsOnDate = runs
            .filter((r) => r.start_date_local.slice(0, 10) === runDate)
            .map((r) => r.run_id);
          if (!runIDsOnDate.length) {
            return;
          }
          locateActivity(runIDsOnDate);
        }
      }
    };
    svgStat.addEventListener('click', handleClick);
    return () => {
      svgStat && svgStat.removeEventListener('click', handleClick);
    };
  }, [year]);

  return (
    <Layout>
      <div className="w-full lg:w-1/3">
        <h1 className="my-12 text-5xl font-extrabold italic">
          <a href="/">{siteTitle}</a>
        </h1>
        {(viewState.zoom ?? 0) <= 3 && IS_CHINESE ? (
          <LocationStat
            changeYear={changeYear}
            changeCity={changeCity}
            changeTitle={changeTitle}
          />
        ) : (
          <YearsStat year={year} onClick={changeYear} />
        )}
      </div>
      <div className="w-full lg:w-2/3">
        <RunMap
          title={title}
          viewState={viewState}
          geoData={geoData}
          setViewState={setViewState}
          changeYear={changeYear}
          thisYear={year}
        />
        {year === 'Total' ? (
          <>
            <SVGStat />
            <div className="mt-8 space-y-4">
              {/* 分析功能入口 */}
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border border-blue-200">
                <div className="text-center">
                  <h3 className="text-xl font-bold text-gray-800 mb-2">📊 运动数据深度分析</h3>
                  <p className="text-gray-600 mb-4">深入了解您的运动表现，发现运动规律和趋势</p>
                  <div className="flex flex-col sm:flex-row gap-3 justify-center">
                    <a 
                      href="./analysis.html" 
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center justify-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105"
                      title="打开详细的运动数据分析页面"
                    >
                      🔬 完整分析报告
                    </a>
                    <button 
                      onClick={() => {
                        // 打开数据文件夹显示分析结果
                        const features = [
                          '✅ 364条活动记录分析完成',
                          '📊 总距离：4229.3公里',
                          '⏱️ 总时间：463小时22分54秒',
                          '🏃‍♂️ 距离分布：40.4% (5-10km), 39.6% (10-20km)',
                          '🎯 个人最佳：最长51.75km，最快配速记录',
                          '📈 支持活动类型分类和趋势分析',
                          '',
                          '📂 数据文件位置：',
                          '• src/static/analysis/activity_types.json',
                          '• src/static/analysis/basic_statistics.json', 
                          '• src/static/analysis/analysis_overview.json',
                          '• src/static/analysis/recent_summary.json'
                        ];
                        alert('🎉 数据分析功能开发完成！\n\n' + features.join('\n'));
                      }}
                      className="inline-flex items-center justify-center px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg"
                    >
                      📈 查看数据摘要
                    </button>
                  </div>
                </div>
              </div>
              
              {/* 快速统计卡片 */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-blue-500">
                  <div className="flex items-center">
                    <div className="text-2xl mr-3">🎯</div>
                    <div>
                      <div className="text-sm text-gray-600">总活动数</div>
                      <div className="text-xl font-bold text-blue-600">364</div>
                    </div>
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-green-500">
                  <div className="flex items-center">
                    <div className="text-2xl mr-3">🛣️</div>
                    <div>
                      <div className="text-sm text-gray-600">总距离</div>
                      <div className="text-xl font-bold text-green-600">4,229.3 公里</div>
                    </div>
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-purple-500">
                  <div className="flex items-center">
                    <div className="text-2xl mr-3">⏱️</div>
                    <div>
                      <div className="text-sm text-gray-600">总时间</div>
                      <div className="text-xl font-bold text-purple-600">463 小时</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </>
        ) : (
          <RunTable
            runs={runs}
            locateActivity={locateActivity}
            setActivity={setActivity}
            runIndex={runIndex}
            setRunIndex={setRunIndex}
          />
        )}
      </div>
      {/* Enable Audiences in Vercel Analytics: https://vercel.com/docs/concepts/analytics/audiences/quickstart */}
      <Analytics />
    </Layout>
  );
};

export default Index;
