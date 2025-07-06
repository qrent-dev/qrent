'use client';
import { Dropdown, DropdownTrigger, DropdownMenu, DropdownItem, Button } from '@heroui/react';
import { User } from 'lucide-react';
import { useTranslations } from 'use-intl';
import { useUserStore } from '../store/userInfoStore';
import { useRouter } from 'next/navigation';

export default function DropDownList() {
  const t = useTranslations('DropDownList');
  const { userInfo } = useUserStore();
  const router = useRouter();

  return (
    <Dropdown>
      <DropdownTrigger>
        <Button className="font-serif text-xl ">
          {userInfo?.name ? (
            <span
              className="max-w-[100px] truncate overflow-hidden whitespace-nowrap"
              title={userInfo.name}
            >
              {userInfo.name.toUpperCase()}
            </span>
          ) : (
            <User className="w-6 h-6" /> // Default icon if not logged in
          )}
        </Button>
      </DropdownTrigger>
      <DropdownMenu aria-label="Static Actions" className="bg-white shadow-md rounded-lg">
        {userInfo?.name ? (
          <>
            <DropdownItem key="profile" href="/profile" className="font-sans">
              {t('profile')}
            </DropdownItem>
            <DropdownItem key="findAHome" href="/findAHome" className="font-sans">
              {t('efficiency-filter')}
            </DropdownItem>
            <DropdownItem key="rentalGuide" href="/rentalGuide" className="font-sans">
              {t('rental-guide')}
            </DropdownItem>
            <DropdownItem key="prepareDocuments" href="/prepareDocuments" className="font-sans">
              {t('prepare-documents')}
            </DropdownItem>
            <DropdownItem key="prepareDocuments" href="/myFav" className="font-sans">
              {t('myFav')}
            </DropdownItem>
            <DropdownItem
              key="logout"
              onClick={() => {
                localStorage.clear();
                router.push('/');
                window.location.reload();
              }}
              className="font-sans"
            >
              {t('logout')}
            </DropdownItem>
          </>
        ) : (
          <>
            <DropdownItem key="login" href="/login" className="font-sans">
              {t('login')}
            </DropdownItem>
            <DropdownItem key="signup" href="/signup" className="font-sans">
              {t('signup')}
            </DropdownItem>
          </>
        )}
      </DropdownMenu>
    </Dropdown>
  );
}
