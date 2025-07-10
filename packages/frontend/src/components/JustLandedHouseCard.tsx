// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import { useTranslations } from 'next-intl';
import React, { useState } from 'react';
import { FaBath, FaBed, FaHeart, FaMapMarkerAlt } from 'react-icons/fa';
import { unsubscribeFromProperty } from '../app/api/properties/client/ubsubscribe';
import { subscribeToProperty } from '../app/api/properties/client/subscribe';
import { useUserStore } from '../store/userInfoStore';
import {
  getDescription,
  getPropertyTypeLabel,
  getScoreClassAndText,
  initializeHouseData,
} from '../utils/house';

const HouseCard = ({ house }) => {
  const t = useTranslations('HouseCard');
  const token = useUserStore(state => state.userInfo.token).token;
  const [isFavorited, setIsFavorited] = useState(false);
  const toggleFavorite = async e => {
    e.preventDefault();
    if (!token) return alert('Login required');

    try {
      if (isFavorited) {
        await unsubscribeFromProperty(house.id, token);
      } else {
        await subscribeToProperty(house.id, token);
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
      className="block border border-gray-300 rounded-lg shadow-lg hover:shadow-2xl transition duration-300 p-6 bg-white hover:bg-gray-50"
    >
      <div className="mb-4">
        <h3 className="text-xl font-semibold text-gray-800">
          {house.address || 'Unknown Address'}
        </h3>
        <div className="flex items-center space-x-1 mt-2 mb-4">
          <FaMapMarkerAlt className="text-gray-700 text-sm" />
          <span className="text-sm text-gray-500">{house.region || 'Unknown Location'}</span>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <span className="text-xl font-semibold text-blue-primary">
          {`$${house.price}`}{' '}
          <span className="text-xs font-normal text-gray-600 whitespace-nowrap">pw</span>
        </span>
        <span className={`text-xs ${scoreClass} rounded-full px-2 py-1`}>{scoreText}</span>
        <button onClick={toggleFavorite} className="focus:outline-none">
          <FaHeart
            className={`text-2xl transition-colors duration-200 ${
              isFavorited ? 'text-pink-500' : 'text-gray-300'
            }`}
          />
        </button>
      </div>

      <div className="flex space-x-4 mt-4">
        <div className="flex items-center space-x-1 bg-gray-100 text-blue-primary px-3 py-1 rounded-sm">
          <FaBed className="text-blue-primary" />
          <span className="text-sm ">{house.bedroomCount}</span>
        </div>
        <div className="flex items-center space-x-1 bg-gray-100 text-blue-primary px-3 py-1 rounded-sm">
          <FaBath className="text-blue-primary" />
          <span className="text-sm ">{house.bathroomCount}</span>
        </div>
        <div className="flex items-center space-x-1 bg-gray-100 text-blue-primary px-3 py-1 rounded-sm max-w-full overflow-hidden">
          <span className="inline-block bg-gray-100 text-gray-800 rounded-full text-xs truncate">
            {propertyType}
          </span>
        </div>
      </div>

      <div className="mt-4">
        <div className="mt-2">
          {description
            .map((kw, index) => (
              <span
                key={index} // always use a unique key if you map through an array
                className="inline-block bg-gray-200 text-gray-700 px-2 py-1 rounded-full text-xs mr-2"
              >
                {kw}
              </span>
            ))
            .concat(
              // If more than 3 keywords, show +X
              description.length > 3 && (
                <span key="more" className="text-gray-500 text-xs">
                  +{description.length - 3}
                </span>
              )
            )}
        </div>
      </div>
    </a>
  );
};

export default HouseCard;
