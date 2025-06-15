// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
'use client';
import React, { useEffect, useState } from 'react';
import { useTranslations } from 'use-intl';
import { filterReportStore } from '../store/filterReportStore';

const FilterReport = () => {
  const t = useTranslations('FilterReport');
  const { report } = filterReportStore();

  const [data, setData] = useState(null);

  useEffect(() => {
    fetch('/api/properties/region-summary?regions=')
      .then(res => res.json())
      .then(result => setData(result))
      .catch(console.error);
  }, []);

  if (data == null) {
    return;
  }

  const top5Details = data.top5Regions.map(regionItem => {
    const matchedSummary = data.summaries.find(s => s.region === regionItem.region);

    return {
      regionName: regionItem.region.split('-nsw')[0],
      propertyCount: regionItem.propertyCount,
      averageWeeklyPrice: matchedSummary?.averageWeeklyPrice ?? null,
      averageCommuteTime: matchedSummary?.averageCommuteTime ?? null,
    };
  });

  console.log(top5Details);

  return (
    <div>
      <div className="w-full bg-white rounded-lg shadow p-6 flex flex-col gap-6">
        {/* Top Section: Row layout */}
        <div className="flex flex-wrap text-gray-800">
          <div className="block border-b-2 border-gray-200 w-max pb-2 text-md font-medium">
            {t('current-num-filtered-listings')}
            <span className="text-blue-primary text-2xl">
              {report.currentListings} / {report.totalListings}
            </span>
          </div>
          <div className="text-xs mt-4">
            • {t('avg-rent')}
            <span className="text-xs">${Math.round(report.avgRent)}/w</span>
          </div>
          <div className="text-xs">
            • {t('avg-time')}
            <span className="text-xs">{Math.round(report.avgTravelTime)}min</span>
          </div>
        </div>
      </div>

      {/* Bottom Section: Area Ranking */}
      <div className="w-full bg-white rounded-lg shadow p-6 flex flex-col mt-4">
        <h3 className="text-lg font-semibold text-gray-800">{t('pop-areas')}</h3>

        <div className="flex flex-col divide-y divide-gray-200">
          {top5Details.map((item, index) => (
            <div key={index} className="py-4">
              <div className="text-md font-semibold text-gray-800">
                {item.regionName.toUpperCase()}
              </div>
              <div className="text-sm text-gray-700 mt-1">
                {t('num-of-properties')}
                {item.propertyCount} (
                {((item.propertyCount / report.totalListings) * 100).toFixed(1)}%)
              </div>
              <div className="text-sm text-gray-700">
                {t('avg-rent')}${item.averageWeeklyPrice?.toFixed(0)}/w
              </div>
              <div className="text-sm text-gray-700">
                {t('avg-time')}
                {item.averageCommuteTime?.toFixed(0)}min
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FilterReport;
