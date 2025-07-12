// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import { useTranslations } from 'next-intl';
import React, { useState } from 'react';
import {
  FaBath,
  FaBed,
  FaCalendarAlt,
  FaCar,
  FaMapMarkerAlt,
  FaRegClock,
  FaHeart,
} from 'react-icons/fa';
import { useUserStore } from '../store/userInfoStore';
import {
  getDescription,
  getPropertyTypeLabel,
  getScoreClassAndText,
  initializeHouseData,
} from '../utils/house';
import { useFilterStore } from '../store/useFilterStore';

const HouseCard = ({ house }) => {
  const t = useTranslations('HouseCard');
  const { filter, updateFilter } = useFilterStore();
  const [isFavorited, setIsFavorited] = useState(() => {
    return filter.subscriptions?.some(sub => sub.id === house.id);
  });
  const token = useUserStore(state => state.userInfo.token).token;

  const toggleFavorite = async e => {
    e.preventDefault();
    if (!token) return alert('Login required');

    try {
      if (isFavorited) {
        await fetch(`/api/properties/${house.id}/unsubscribe`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
        });
      } else {
        await fetch(`/api/properties/${house.id}/subscribe`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
        });
      }
      setIsFavorited(!isFavorited);
    } catch (err) {
      console.error(err);
      alert('Error subscribing');
    }
  };

  house = initializeHouseData(house);
  const { scoreClass, scoreText } = getScoreClassAndText(house.averageScore, t);
  const description = getDescription(house.keywords, house.description, house.descriptionCn);
  const propertyType = getPropertyTypeLabel(house.propertyType);

  return (
    <a
      href={house.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block border border-gray-300 rounded-lg shadow-lg hover:shadow-2xl transition duration-300 p-6 bg-white hover:bg-gray-50 relative"
    >
      <div className="mb-4">
        <div className="flex space-x-4">
          <h3 className="text-xl font-semibold text-gray-800">
            {house.address || 'Unknown Address'}
          </h3>
          {propertyType != '' && (
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1 bg-gray-100 text-blue-primary px-3 py-1 rounded-sm">
                <span className="inline-block rounded-full text-md">{propertyType}</span>
              </div>
              <button onClick={toggleFavorite} className="focus:outline-none">
                <FaHeart
                  className={`text-2xl transition-colors duration-200 ${
                    isFavorited ? 'text-pink-500' : 'text-gray-300'
                  }`}
                />
              </button>
            </div>
          )}
        </div>

        <div className="flex items-center space-x-1 mt-2 mb-4">
          <FaMapMarkerAlt className="text-gray-700 text-sm" />
          <span className="text-sm text-gray-500">{house.region || 'Unknown Location'}</span>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <span className="text-2xl font-semibold text-blue-primary">
          {`$${house.price}`}{' '}
          <span className="text-xs font-normal text-gray-600 whitespace-nowrap">pw</span>
        </span>
      </div>

      <span className={`text-md ${scoreClass} rounded-full px-2 py-1 absolute top-4 right-4`}>
        {scoreText}
      </span>

      <div className="flex space-x-4 mt-4">
        {house.bedroomCount != 0 && (
          <div className="flex items-center space-x-1 bg-gray-100 text-blue-primary px-3 py-1 rounded-sm">
            <FaBed className="text-blue-primary" />
            <span className="text-sm ">{house.bedroomCount}</span>
          </div>
        )}

        {house.bathroomCount != 0 && (
          <div className="flex items-center space-x-1 bg-gray-100 text-blue-primary px-3 py-1 rounded-sm">
            <FaBath className="text-blue-primary" />
            <span className="text-sm ">{house.bathroomCount}</span>
          </div>
        )}

        {house.commuteTime != 0 && (
          <div className="flex items-center space-x-1 bg-gray-100 text-blue-primary px-3 py-1 rounded-sm">
            <FaRegClock className="text-blue-primary" />
            <span className="text-sm">{house.commuteTime}</span>
          </div>
        )}

        <div className="flex items-center space-x-1 bg-gray-100 text-blue-primary px-3 py-1 rounded-sm">
          <FaCalendarAlt className="text-blue-primary" />
          <span className="text-sm">{house.availableDate || 'Unknown'}</span>
        </div>

        {house.parkingCount != null && (
          <div className="flex items-center space-x-1 bg-gray-100 text-blue-primary px-3 py-1 rounded-sm">
            <FaCar className="text-blue-primary" />
            <span className="text-sm">{house.parkingCount}</span>
          </div>
        )}
      </div>

      <div className="mt-4">
        <div className="mt-2">
          {description.map((kw, index) => (
            <span
              key={index}
              className="inline-block bg-gray-200 text-gray-700 px-2 py-1 rounded-full text-xs mr-2"
            >
              {kw}
            </span>
          ))}
        </div>
      </div>
    </a>
  );
};

export default HouseCard;
