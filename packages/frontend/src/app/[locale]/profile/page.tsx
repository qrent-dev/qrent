'use client';

import { useUserStore } from '@/src/store/userInfoStore';
import { useRouter } from 'next/navigation';
import React from 'react';
import { useTranslations } from 'use-intl';

export default function ProfilePage() {
  const { userInfo } = useUserStore();
  const t = useTranslations('Profile');
  const router = useRouter();

  const user = {
    name: userInfo.name,
    email: userInfo.email,
    avatarUrl: userInfo.avatarUrl || 'https://www.gravatar.com/avatar/?d=mp',
  };

  return (
    <div className="max-w-2xl mx-auto p-6 font-sans">
      <h1 className="text-3xl font-bold text-blue-primary mb-6">{t('profile')}</h1>

      <div className="bg-white shadow rounded-lg p-6 flex items-center space-x-6">
        <img
          src={user.avatarUrl}
          alt="User Avatar"
          className="w-24 h-24 rounded-full object-cover border border-gray-300"
        />
        <div>
          <p className="text-xl font-semibold">{user.name}</p>
          <p className="text-gray-600">{user.email}</p>
        </div>
      </div>

      <div className="mt-8 space-y-4">
        <button
          className="w-full bg-blue-primary hover:bg-blue-900 text-white py-2 rounded-lg transition"
          onClick={() => router.push('/findAHome')}
        >
          {t('save')}
        </button>
      </div>
    </div>
  );
}
