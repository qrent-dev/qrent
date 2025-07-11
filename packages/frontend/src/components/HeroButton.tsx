'use client';
import Link from 'next/link';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBookOpen, faFileAlt, faSearch, faDownload } from '@fortawesome/free-solid-svg-icons';
import { useTranslations } from 'next-intl';
import { useRentalGuideProgressStore } from '../store/rentalGuideProgressStore';
import { usePrepareDocProgressStore } from '../store/prepareDocProgressStore';

const HeroButton = () => {
  const t = useTranslations('HeroButton');

  const checkedItemsRentalGuide = useRentalGuideProgressStore(state => state.checkedItem);
  const checkedItemsPrepareDoc = usePrepareDocProgressStore(state => state.checkedItem);

  const mainNavItems = [
    {
      href: '/rentalGuide',
      icon: faBookOpen,
      title: t('rental-guide'),
      description: t('rental-guide-des'),
      progress: (checkedItemsRentalGuide / 21) * 100,
      progressText: `${checkedItemsRentalGuide}/21`,
    },
    {
      href: '/prepareDocuments',
      icon: faFileAlt,
      title: t('application-materials'),
      description: t('application-materials-des'),
      progress: (checkedItemsPrepareDoc / 7) * 100,
      progressText: `${checkedItemsPrepareDoc}/7`,
    },
  ];

  const secondaryNavItems = [
    {
      href: '/resourceCenter',
      icon: faDownload,
      title: t('resource-center'),
      description: t('resource-center-des'),
      highlight: true,
    },
    {
      href: '/findAHome',
      icon: faSearch,
      title: t('efficiency-filter'),
      description: t('efficiency-filter-des'),
    },
  ];

  return (
    <div className="max-w-screen-lg mx-auto mt-8 px-6">
      {/* main button */}
      <nav className="flex flex-wrap gap-6 mb-4">
        {mainNavItems.map((item, index) => (
          <Link
            key={index}
            href={item.href}
            className="flex-1 min-w-[250px] bg-white p-6 rounded-lg shadow-md flex items-center gap-4 hover:shadow-lg transition"
          >
            {/* Icon */}
            <div className="text-4xl text-blue-primary">
              <FontAwesomeIcon icon={item.icon} />
            </div>

            {/* Text Content */}
            <div className="flex-1">
              <h3 className="text-lg font-semibold">{item.title}</h3>
              <p className="text-sm text-gray-600">{item.description}</p>

              {/* Progress Indicator */}
              <div className="mt-2">
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-primary"
                    style={{ width: `${item.progress}%` }}
                  ></div>
                </div>
                <span className="text-xs text-gray-500">{item.progressText}</span>
              </div>
            </div>
          </Link>
        ))}
      </nav>

      <nav className="flex flex-wrap gap-4">
        {secondaryNavItems.map((item, index) => (
          <Link
            key={index}
            href={item.href}
            className="flex-1 min-w-[200px] bg-white p-4 rounded-lg shadow-md flex items-center gap-3 hover:shadow-lg transition relative"
          >
            {item.highlight && (
              <div className="absolute -top-3 -left-2 bg-blue-500 text-white text-xs px-2 py-1 rounded-full shadow-md animate-pulse">
                {t('guide')}
              </div>
            )}
            {/* Icon */}
            <div className="text-3xl text-blue-primary">
              <FontAwesomeIcon icon={item.icon} />
            </div>

            {/* Text Content */}
            <div className="flex-1">
              <h3 className="text-base font-semibold">{item.title}</h3>
              <p className="text-xs text-gray-600">{item.description}</p>
            </div>
          </Link>
        ))}
      </nav>
    </div>
  );
};

export default HeroButton;
