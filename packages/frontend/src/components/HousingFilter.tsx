// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck

import React, { useState } from 'react';
import Textbox from './priceDropDown';
import RatingSlider from './Slider';
import { useTranslations } from 'next-intl';
import { useFilterStore } from '../store/useFilterStore';
import { ChevronDown } from 'lucide-react';

export const FULL_SUBURB_OPTIONS = {
  unsw: [
    'alexandria',
    'arncliffe',
    'banksia',
    'beaconsfield',
    'botany',
    'brighton-le-sands',
    'bronte',
    'camperdown',
    'chifley',
    'chippendale',
    'clovelly',
    'coogee',
    'darlington',
    'eastgardens',
    'eastlakes',
    'enmore',
    'erskineville',
    'hillsdale',
    'kensington',
    'kingsford',
    'kyeemagh',
    'malabar',
    'maroubra',
    'marrickville',
    'mascot',
    'matraville',
    'newtown',
    'paddington',
    'pagewood',
    'randwick',
    'redfern',
    'rockdale',
    'rosebery',
    'stanmore',
    'sydenham',
    'tempe',
    'turrella',
    'waterloo',
    'waverley',
    'zetland',
    'bondi-junction',
    'centennial-park',
    'la-perouse',
    'little-bay',
    'moore-park',
    'phillip-bay',
    'queens-park',
    'south-coogee',
    'st-peters',
    'wolli-creek',
  ],
  usyd: [
    'abbotsford',
    'alexandria',
    'allawah',
    'annandale',
    'arncliffe',
    'banksia',
    'barangaroo',
    'beaconsfield',
    'bexley',
    'blakehurst',
    'botany',
    'brighton-le-sands',
    'burwood',
    'camperdown',
    'carlton',
    'chippendale',
    'chiswick',
    'concord',
    'croydon',
    'darlinghurst',
    'darlington',
    'earlwood',
    'eastlakes',
    'enfield',
    'enmore',
    'erskineville',
    'glebe',
    'haymarket',
    'hurstville',
    'kensington',
    'kingsgrove',
    'kyeemagh',
    'maroubra',
    'marrickville',
    'mascot',
    'mortlake',
    'narwee',
    'newtown',
    'paddington',
    'pagewood',
    'penshurst',
    'pyrmont',
    'redfern',
    'rockdale',
    'rosebery',
    'stanmore',
    'strathfield',
    'sydenham',
    'sydney',
    'tempe',
    'turrella',
    'ultimo',
    'wareemba',
    'waterloo',
    'woolloomooloo',
    'zetland',
    'bardwell-valley',
    'beverly-hills',
    'breakfast-point',
    'canada-bay',
    'carss-park',
    'centennial-park',
    'clemton-park',
    'connells-point',
    'dawes-point',
    'five-dock',
    'forest-lodge',
    'kyle-bay',
    'millers-point',
    'moore-park',
    'north-strathfield',
    'russell-lea',
    'south-coogee',
    'st-peters',
    'surry-hills',
    'the-rocks',
    'walsh-bay',
    'wolli-creek',
  ],
};

export const SUBURB_OPTIONS = {
  unsw: [
    'alexandria',
    'bondi',
    'botany',
    'coogee',
    'eastgardens',
    'eastlakes',
    'hillsdale',
    'kensington',
    'kingsford',
    'maroubra',
    'mascot',
    'matraville',
    'paddington',
    'randwick',
    'redfern',
    'rosebery',
    'waterloo',
    'wollicreek',
    'zetland',
  ],
  usyd: [
    'burwood',
    'chippendale',
    'city',
    'glebe',
    'haymarket',
    'hurstville',
    'mascot',
    'newtown',
    'ultimo',
    'waterloo',
    'wollicreek',
    'zetland',
  ],
};

const HousingFilter = () => {
  const t = useTranslations('Search');

  const [accordionOpen, setAccordionOpen] = useState(false);

  const { filter, updateFilter } = useFilterStore();

  const unswAreaOptions = [...SUBURB_OPTIONS.unsw];
  const usydAreaOptions = [...SUBURB_OPTIONS.usyd];

  const handleNewTodayCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    updateFilter({ newToday: e.target.checked });
  };

  const handleMyFavCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    updateFilter({ myFav: e.target.checked });
  };

  const handleCheckboxChange = (option: string) => {
    // Define area mappings - when key is selected, also include the value(s)
    const areaMappings: Record<string, string[]> = {
      Bondi: ['Bondi-Junction'],
      WolliCreek: ['Wolli-Creek'],
      City: ['Sydney', 'Millers-Point', 'Moore-Park', 'Surry-Hills', 'The-Rocks', 'Woolloomooloo'],
    };

    // If "Any" is selected
    if (option === 'Any') {
      if (filter.area.includes('Any') && filter.area.length == 1) {
        updateFilter({
          ...filter,
          area: [],
        });
      } else {
        updateFilter({
          ...filter,
          area: ['Any'],
        });
      }
      return;
    }

    // If another option is selected while "Any" was previously selected
    if (filter.area.includes('Any')) {
      const newAreas = [option];
      // Add mapped areas if they exist for this option
      if (areaMappings[option]) {
        newAreas.push(...areaMappings[option]);
      }

      updateFilter({
        ...filter,
        area: newAreas,
      });
      return;
    }

    // Normal toggle behavior for other cases
    let newArea;
    if (filter.area.includes(option)) {
      // When unselecting, remove both the option and any mapped areas
      newArea = filter.area.filter(
        item => item !== option && !areaMappings[option]?.includes(item)
      );
    } else {
      // When selecting, add both the option and any mapped areas
      newArea = [...filter.area, option];
      if (areaMappings[option]) {
        newArea.push(...areaMappings[option]);
      }
    }

    updateFilter({
      ...filter,
      area: newArea,
    });
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

      {/* new today */}
      <div className="mt-4">
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
      </div>

      {/* My favorites */}
      <div className="mt-4">
        <div className="flex items-center gap-2">
          <label htmlFor="newTodayCheckbox" className="text-lg text-gray-600 font-bold">
            {t('my-fav')}
          </label>

          <input
            type="checkbox"
            id="myFavCheckbox"
            checked={filter.myFav}
            onChange={handleMyFavCheckboxChange}
            className="mt-1"
          />
        </div>
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
          <div className="mt-2 max-h-52 overflow-y-auto grid grid-cols-2 gap-2">
            {/* "Any" option - always shown */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="checkbox-any"
                value="Any"
                checked={filter.area.includes('Any')}
                onChange={() => handleCheckboxChange('Any')}
                className="mr-2"
              />
              <label htmlFor="checkbox-any" className="text-gray-600">
                Any
              </label>
            </div>

            {/* University-specific options */}
            {filter.university === 'UNSW' &&
              unswAreaOptions.map((option, index) => (
                <div key={index} className="flex items-center">
                  <input
                    type="checkbox"
                    id={`checkbox-${index}`}
                    value={option}
                    checked={filter.area.includes(option)}
                    onChange={() => handleCheckboxChange(option)}
                    className="mr-2"
                    disabled={filter.area.includes('Any') && !filter.area.includes(option)}
                  />
                  <label
                    htmlFor={`checkbox-${index}`}
                    className={`text-gray-600 ${filter.area.includes('Any') ? 'opacity-50' : ''}`}
                  >
                    {option}
                  </label>
                </div>
              ))}

            {filter.university === 'USYD' &&
              usydAreaOptions.map((option, index) => (
                <div key={index} className="flex items-center">
                  <input
                    type="checkbox"
                    id={`checkbox-${index}`}
                    value={option}
                    checked={filter.area.includes(option)}
                    onChange={() => handleCheckboxChange(option)}
                    className="mr-2"
                    disabled={filter.area.includes('Any') && !filter.area.includes(option)}
                  />
                  <label
                    htmlFor={`checkbox-${index}`}
                    className={`text-gray-600 ${filter.area.includes('Any') ? 'opacity-50' : ''}`}
                  >
                    {option}
                  </label>
                </div>
              ))}
          </div>
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
