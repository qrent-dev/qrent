// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck

import React, { useState } from 'react';
import Textbox from './Textbox';
import RatingSlider from './Slider';
import { useTranslations } from 'next-intl';
import { useFilterStore } from '../store/useFilterStore';
import { ChevronDown } from 'lucide-react';
import { useUserStore } from '../store/userInfoStore';
import AreaCheckbox from './AreaCheckbox';

const HousingFilter = () => {
  const t = useTranslations('Search');
  const [accordionOpen, setAccordionOpen] = useState(false);
  const { filter, updateFilter } = useFilterStore();

  const handleNewTodayCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    updateFilter({ newToday: e.target.checked });
  };

  return (
    <>
      {/* University */}
      <div className="mt-4">
        <div className="text-lg text-gray-600 font-bold">{t('university')}</div>
        <select
          aria-label="university"
          className="border rounded px-2 py-1 max-h-40 overflow-y-auto w-full"
          value={filter.university}
          onChange={e => updateFilter({ ...filter, university: e.target.value })}
        >
          <option>UNSW</option>
          <option>USYD</option>
          <option>UTS</option>
        </select>
      </div>

      {/* Price Range */}
      <div className="mt-4">
        <div className="text-lg text-gray-600 font-bold">{t('price-range')}</div>
        <div className="flex justify-between gap-4">
          <div className="flex-1">
            <Textbox
              label=""
              name="priceMin"
              filter={filter}
              setFilter={updateFilter}
              ph={t('min')}
            />
          </div>
          <div className="flex-1">
            <Textbox
              label=""
              name="priceMax"
              filter={filter}
              setFilter={updateFilter}
              ph={t('max')}
            />
          </div>
        </div>
      </div>

      <div className="mt-4">
        <div className="text-lg text-gray-600 font-bold">{t('bedrooms')}</div>
        <div className="flex justify-between gap-4">
          <div className="flex-1">
            <Textbox
              label=""
              name="bedroomMin"
              filter={filter}
              setFilter={updateFilter}
              ph={t('min')}
            />
          </div>
          <div className="flex-1">
            <Textbox
              label=""
              name="bedroomMax"
              filter={filter}
              setFilter={updateFilter}
              ph={t('max')}
            />
          </div>
        </div>
      </div>

      <div className="mt-4">
        <div className="text-lg text-gray-600 font-bold">{t('bathrooms')}</div>
        <div className="flex justify-between gap-4">
          <div className="flex-1">
            <Textbox
              label=""
              name="bathroomMin"
              filter={filter}
              setFilter={updateFilter}
              ph={t('min')}
            />
          </div>
          <div className="flex-1">
            <Textbox
              label=""
              name="bathroomMax"
              filter={filter}
              setFilter={updateFilter}
              ph={t('max')}
            />
          </div>
        </div>
      </div>

      {/* Property Type */}
      <div className="mt-4">
        <div className="text-lg text-gray-600 font-bold">{t('property-type')}</div>
        <div className="flex justify-between items-center gap-3 mt-3">
          <select
            aria-label="propertyType"
            className="border rounded px-2 py-1 max-h-40 overflow-y-auto w-full"
            value={filter.propertyType}
            onChange={e => updateFilter({ ...filter, propertyType: e.target.value })}
          >
            <option>Any</option>
            <option>House</option>
            <option>Apartment/Unit/Flat</option>
            <option>Studio</option>
            <option>Semi-detached</option>
          </select>
        </div>
      </div>

      <div className="flex items-center gap-8 mt-4">
        {/* New today */}
        <div className="flex items-center gap-2">
          <label htmlFor="newTodayCheckbox" className="text-lg text-gray-600 font-bold">
            {t('new-today')}
          </label>
          <input
            type="checkbox"
            id="newTodayCheckbox"
            checked={filter.newToday}
            onChange={handleNewTodayCheckboxChange}
            className="mt-1"
          />
        </div>

        {/* My favorites */}
        {/* <div className="flex items-center gap-2">
          <label htmlFor="myFavCheckbox" className="text-lg text-gray-600 font-bold">
            {t('my-fav')}
          </label>
          <input
            type="checkbox"
            id="myFavCheckbox"
            checked={filter.myFav}
            onChange={handleMyFavCheckboxChange}
            className="mt-1"
          />
        </div> */}
      </div>

      {/* Area */}
      <div className="mt-4">
        <div
          className="text-lg text-gray-600 font-bold cursor-pointer flex items-center justify-between"
          onClick={() => setAccordionOpen(!accordionOpen)}
        >
          <span>{t('area')}</span>
          <ChevronDown
            className={`w-5 h-5 transform transition-transform duration-300 ${
              accordionOpen ? 'rotate-180' : 'rotate-0'
            }`}
          />
        </div>

        {accordionOpen && (
          <AreaCheckbox
            area={filter.area}
            setArea={newArea => updateFilter({ ...filter, area: newArea })}
            university={filter.university}
          />
        )}
      </div>

      {/* Rate */}
      <div className="mt-4">
        <div className="text-lg text-gray-600 font-bold">{t('rate')}</div>
        <RatingSlider filter={filter} updateFilter={updateFilter} />
      </div>

      {/* commute time */}
      <div className="mt-4">
        <div className="text-lg text-gray-600 font-bold">{t('travel-time')} (Minutes)</div>
        <div className="flex justify-between gap-4">
          <div className="flex-1">
            <Textbox
              label=""
              name="commuteTimeMin"
              filter={filter}
              setFilter={updateFilter}
              ph={t('min')}
            />
          </div>
          <div className="flex-1">
            <Textbox
              label=""
              name="commuteTimeMax"
              filter={filter}
              setFilter={updateFilter}
              ph={t('max')}
            />
          </div>
        </div>
      </div>

      {/* Avaliable Date */}
      <div className="pb-4 mt-4">
        <div className="text-lg text-gray-600 font-bold">{t('avaliable-date')}</div>
        <input
          aria-label="date"
          type="date"
          className="border rounded px-2 py-1 mt-2"
          value={filter.avaliableDate}
          onChange={e => updateFilter({ ...filter, avaliableDate: e.target.value })}
        />
      </div>
    </>
  );
};

export default HousingFilter;
