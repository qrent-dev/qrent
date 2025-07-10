import { usePathname } from 'next/navigation';

export const formatAddress = (address: string = '') =>
  address
    .replaceAll('-', ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');

export const getPropertyTypeLabel = (type: number) => {
  switch (type) {
    case 1:
      return 'House';
    case 2:
      return 'Apartment/Unit/Flat';
    case 3:
      return 'Studio';
    case 4:
      return 'Semi-detached';
    default:
      return 'Unknown';
  }
};

export const getScoreClassAndText = (score: number | undefined, t: any) => {
  if (score == null || isNaN(score)) {
    return {
      scoreClass: 'border border-gray-300 text-gray-400 bg-white',
      scoreText: `N/A ${t('points')}`,
    };
  }

  const scoreValue = score.toFixed(1);
  const point = t('points');
  const top = t('top');
  const good = t('good');

  let scoreClass = '';
  let scoreText = `${scoreValue} ${point}`;

  if (score >= 18.3) {
    scoreClass = 'bg-orange-500 text-white shadow-md shadow-orange-400';
    scoreText = `${top} ${scoreText}`;
  } else if (score >= 18.0) {
    scoreClass = 'bg-orange-400 text-white shadow-md shadow-orange-400';
    scoreText = `${good} ${scoreText}`;
  } else {
    scoreClass = 'border border-blue-primary text-blue-primary bg-white';
  }

  return { scoreClass, scoreText };
};

export const getLocale = (): string => {
  if (usePathname().startsWith('/en')) {
    return 'en';
  } else {
    return 'zh';
  }
};

export const getDescription = (
  keywords: string,
  description: string,
  descriptionCn: string
): string[] => {
  if (getLocale() == 'en') {
    if (keywords == null) {
      return description.split(',');
    } else {
      return keywords.split(',');
    }
  } else {
    return descriptionCn.split(',');
  }
};

export const initializeHouseData = (house: any) => {
  return {
    ...house,
    address: formatAddress(house.address ?? 'Unknown'),
    addressLine2: house.addressLine2 ?? 'Unknown',
    averageScore: house.averageScore ?? 0,
    descriptionCn: house.descriptionCn ?? '',
    descriptionEn: house.descriptionEn ?? '',
    keywords: house.keywords ?? '',
    url: house.url ?? '#',
    region: house.region ?? 'Unknown',
    publishedAt: house.publishedAt ? house.publishedAt.split('T')[0] : 'Unknown',
    availableDate: house.availableDate?.split('T')[0] ?? 'Unknown',
  };
};
