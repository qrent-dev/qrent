// eslint-disable-next-line @typescript-eslint/ban-ts-comment
//@ts-nocheck

'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHome, faArrowRight } from '@fortawesome/free-solid-svg-icons';
import { useTranslations } from 'next-intl';
import JustLandedHouseCard from './JustLandedHouseCard';
import { useFilterStore } from '../store/useFilterStore';

const JustLanded = () => {
  const [school, setSchool] = useState('unsw');
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(false);
  const { filter, updateFilter } = useFilterStore();
  const t = useTranslations('JustLanded');

  const handleViewAllClick = () => {
    updateFilter({ newToday: true });
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const requestBody = {};
      if (filter.university === 'UNSW') {
        requestBody.targetSchool = 'University of New South Wales';
      } else if (filter.university === 'USYD') {
        requestBody.targetSchool = 'University of Sydney';
      } else {
        requestBody.targetSchool = 'University of Technology Sydney';
      }
      requestBody.page = 1;
      requestBody.pageSize = 9;
      requestBody.orderBy = [{ averageScore: 'desc' }];

      console.log('Sending request:', requestBody);

      const response = await fetch('/api/properties/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      let results = await response.json();
      results = results.properties;
      setListings(results);

      console.log(results);
    } catch (error) {
      console.error('Error fetching properties:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [school]);

  return (
    <div className="max-w-screen-lg mx-auto mt-10 px-6">
      {/* Section Header */}
      <div className="flex justify-between items-center border-b pb-2 mb-4">
        {/* Title + Controls */}
        <div className="flex items-center gap-3">
          <h2 className="text-2xl font-bold flex items-center gap-3">
            <FontAwesomeIcon icon={faHome} className="text-blue-primary" />
            {t('just-landed')}
          </h2>
          {/* School Toggle Buttons */}
          <div className="flex border rounded-lg overflow-hidden">
            <button
              className={`px-3 py-2 ${
                school === 'unsw' ? 'bg-blue-primary text-white' : 'bg-gray-200'
              }`}
              onClick={() => setSchool('unsw')}
            >
              UNSW
            </button>
            <button
              className={`px-3 py-2 ${
                school === 'usyd' ? 'bg-blue-primary text-white' : 'bg-gray-200'
              }`}
              onClick={() => setSchool('usyd')}
            >
              USYD
            </button>
            <button
              className={`px-3 py-2 ${
                school === 'uts' ? 'bg-blue-primary text-white' : 'bg-gray-200'
              }`}
              onClick={() => setSchool('uts')}
            >
              UTS
            </button>
          </div>
        </div>

        <Link href="findAHome" legacyBehavior>
          <a
            className="text-blue-primary hover:underline flex items-center ml-2"
            onClick={handleViewAllClick}
          >
            {t('view-all')} <FontAwesomeIcon icon={faArrowRight} className="ml-2" />
          </a>
        </Link>
      </div>

      <div className="max-w-screen-lg mx-auto mt-10 mb-20 px-6 overflow-y-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {listings.map((house, index) => (
            <JustLandedHouseCard key={index} house={house} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default JustLanded;
