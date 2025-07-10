import React from 'react';
import { SUBURB_OPTIONS } from '../config/suburbOptions';


const AREA_MAPPINGS = {
  Bondi: ['Bondi-Junction'],
  WolliCreek: ['Wolli-Creek'],
  City: ['Sydney', 'Millers-Point', 'Moore-Park', 'Surry-Hills', 'The-Rocks', 'Woolloomooloo'],
};

const AreaCheckbox = ({
  area,
  setArea,
  university,
  areaMappings = AREA_MAPPINGS,
}: {
  area: string[];
  setArea: (newArea: string[]) => void;
  university: 'UNSW' | 'USYD';
  areaMappings?: Record<string, string[]>;
}) => {
  const areaOptions = SUBURB_OPTIONS[university.toLowerCase() as 'unsw' | 'usyd'];

  const handleCheckboxChange = (option: string) => {
    if (option === 'Any') {
      setArea(area.includes('Any') && area.length === 1 ? [] : ['Any']);
      return;
    }

    if (area.includes('Any')) {
      const newAreas = [option, ...(areaMappings[option] || [])];
      setArea(newAreas);
      return;
    }

    let newArea;
    if (area.includes(option)) {
      newArea = area.filter(
        item => item !== option && !(areaMappings[option] || []).includes(item)
      );
    } else {
      newArea = [...area, option, ...(areaMappings[option] || [])];
    }

    setArea(newArea);
  };

  return (
    <div className="mt-2 max-h-52 overflow-y-auto grid grid-cols-2 gap-2">
      {['Any', ...areaOptions].map(option => (
        <div key={option} className="flex items-center">
          <input
            type="checkbox"
            id={`checkbox-${option}`}
            value={option}
            checked={area.includes(option)}
            onChange={() => handleCheckboxChange(option)}
            className="mr-2"
            disabled={area.includes('Any') && option !== 'Any' && !area.includes(option)}
          />
          <label
            htmlFor={`checkbox-${option}`}
            className={`text-gray-600 ${
              area.includes('Any') && option !== 'Any' && !area.includes(option)
                ? 'opacity-50'
                : ''
            }`}
          >
            {option}
          </label>
        </div>
      ))}
    </div>
  );
};

export default AreaCheckbox;
