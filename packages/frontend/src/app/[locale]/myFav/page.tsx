// @ts-nocheck
'use client';
import HouseCard from '@/src/components/HouseCard';
import { useFilterStore } from '@/src/store/useFilterStore';
import { useUserStore } from '@/src/store/userInfoStore';
import { useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';
import React, { useEffect, useRef, useState } from 'react';
import { getUserSubscriptions } from '../../api/properties/client/getUserSubscriptions';

const Page = () => {
  const [listings, setListings] = useState([]);
  const { filter, updateFilter } = useFilterStore();
  const topRef = useRef();
  const router = useRouter();
  const t = useTranslations('MyFav');

  const token = useUserStore(state => state.userInfo.token).token;

  useEffect(() => {
    const getSubscriptions = async () => {
      if (!token) {
        return;
      }

      try {
        const res = await fetch('/api/users/subscriptions', {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!res.ok) {
          throw new Error(`API Error: ${res.status}`);
        }

        const subscriptions = await res.json();

        updateFilter({ subscriptions });
      } catch (err) {
        console.error('Failed to fetch subscriptions', err);
      }
    };

    getSubscriptions();
  }, [token, updateFilter]);

  useEffect(() => {
    setListings(filter.subscriptions || []);
  }, [filter.subscriptions]);

  return (
    <div className="flex flex-col items-center px-4 min-h-screen">
      {/* Centered heading + summary + button */}
      <div ref={topRef} className="w-full max-w-xl text-center mt-8">
        <h1 className="text-2xl font-semibold mb-2">{t('title')}</h1>
        <p className="text-sm text-gray-600 mb-4">
          {t('subtitle1')} {listings.length} {t('subtitle2')}.
        </p>
        {listings.length === 0 && <p className="text-gray-500">{t('no-listings')}</p>}
      </div>

      {/* Listings grid: full width with max */}
      {listings.length > 0 && (
        <div className="flex flex-col gap-8 w-full max-w-6xl mt-6">
          {listings.map((house, index) => (
            <HouseCard key={index} house={house} />
          ))}
        </div>
      )}

      {/* Back button centered */}
      <button
        onClick={() => router.push('/findAHome')}
        className="mt-6 mb-6 px-4 py-2 rounded bg-blue-primary text-white hover:bg-blue-900"
      >
        {t('explore')}
      </button>
    </div>
  );
};

export default Page;
