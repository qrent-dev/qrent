// eslint-disable-next-line @typescript-eslint/ban-ts-comment
//@ts-nocheck
'use client';

import { ChevronDown } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { useState } from 'react';
import 'react-datepicker/dist/react-datepicker.css';

const LetterForm = () => {
  const [openAccordion, setOpenAccordion] = useState(1);
  const [isCoverLetter, setIsCoverLetter] = useState(true);
  const [requiredDocs, setRequiredDocs] = useState([]);
  const [showFlatmate, setShowFlatmate] = useState(false);
  const [optionalDocs, setOptionalDocs] = useState([]);
  const t = useTranslations('PrepareDocuments');
  const [CLInfo, setCLInfo] = useState({
    name: '',
    university: '',
    major: '',
    moveInDate: '',
    leaseTerm: '',
    budget: '',
    financialStatement: [],
    rentalHistory: '',
    previousExperiences: [],
    personality: [],
    bgInfo: '',
  });
  const [PLInfo, setPLInfo] = useState({
    fatherName: '',
    motherName: '',
    fatherContactNum: '',
    motherContactNum: '',
    contactEmail: '',
    studentName: '',
    homeAddress: '',
    weeklyRent: '',
    livingExpenses: '',
    sourceOfFunds: '',
    accountBalance: '',
    annualIncome: '',
    proofDocs: '',
    prepayRent: '',
    liabilityStatement: '',
    otherCommitments: '',
  });

  const financialStatementOpts = [
    'Parent Letter',
    t('account-balance'),
    t('proof-of-income'),
    t('scholarship'),
  ];
  const personalityOpts = [
    t('no-smoke'),
    t('no-pets'),
    t('quiet-lifestyle'),
    t('tidy'),
    t('no-party'),
    t('regular-schedule'),
  ];
  const sourceOfFundsOpts = [
    t('salary-income'),
    t('savings'),
    t('property-income'),
    t('investment-income'),
  ];
  const proofDocsOpts = [t('bank-statement'), t('income-proof'), t('property-proof'), t('tax')];

  const handleCheckboxChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { value, checked } = event.target;

    setCLInfo(prevState => {
      // If checked, add the value to the proofOfFunds array, otherwise remove it
      const newProofOfFunds = checked
        ? [...prevState.financialStatement, value]
        : prevState.financialStatement.filter(item => item !== value);

      return { ...prevState, financialStatement: newProofOfFunds };
    });
  };

  const handlePersonalityCheckboxChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { value, checked } = event.target;

    setCLInfo(prevState => {
      // If checked, add the value to the proofOfFunds array, otherwise remove it
      const personalities = checked
        ? [...prevState.personality, value]
        : prevState.personality.filter(item => item !== value);

      return { ...prevState, personality: personalities };
    });
  };

  const handleRentalHistoryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setCLInfo(prevState => ({
      ...prevState,
      rentalHistory: value,
      previousExperience: value === 'first-time' ? '' : prevState.previousExperiences, // Clear if first-time
    }));
  };

  const handleSourceFundsCheckboxChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { value, checked } = event.target;

    setPLInfo(prevState => {
      // If checked, add the value to the proofOfFunds array, otherwise remove it
      const source = checked
        ? [...prevState.sourceOfFunds, value]
        : prevState.sourceOfFunds.filter(item => item !== value);

      return { ...prevState, sourceOfFunds: source };
    });
  };

  const handleProofDocsCheckboxChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { value, checked } = event.target;

    setPLInfo(prevState => {
      // If checked, add the value to the proofOfFunds array, otherwise remove it
      const source = checked
        ? [...prevState.proofDocs, value]
        : prevState.proofDocs.filter(item => item !== value);

      return { ...prevState, proofDocs: source };
    });
  };

  const toggleAccordion = index => {
    setOpenAccordion(openAccordion === index ? null : index);
  };

  const handleToggleForm = isCoverLetter => {
    setIsCoverLetter(isCoverLetter);
  };

  const addExperience = () => {
    setCLInfo({
      ...CLInfo,
      previousExperiences: [...CLInfo.previousExperiences, ''],
    });
  };

  const removeExperience = index => {
    const updatedExperiences = CLInfo.previousExperiences.filter((_, i) => i !== index);
    setCLInfo({ ...CLInfo, previousExperiences: updatedExperiences });
  };

  return (
    <div className="space-y-6">
      <div className="flex space-x-4 mb-6">
        <button
          onClick={() => handleToggleForm(true)}
          className={`px-6 py-3 rounded-md text-lg font-semibold ${
            isCoverLetter ? 'bg-blue-primary text-white shadow-md' : 'bg-gray-300 text-gray-800'
          }`}
        >
          Cover Letter
        </button>
        <button
          onClick={() => handleToggleForm(false)}
          className={`px-6 py-3 rounded-md text-lg font-semibold ${
            !isCoverLetter ? 'bg-blue-primary text-white shadow-md' : 'bg-gray-300 text-gray-800'
          }`}
        >
          Parent Letter
        </button>
      </div>

      {isCoverLetter ? (
        <div className="space-y-6">
          {/* Student Information */}
          <div className="pb-1">
            <h2 className="text-xl font-semibold">
              <button
                className="w-full text-left py-3 px-4 bg-gray-100 rounded-md flex items-center justify-between"
                onClick={() => toggleAccordion(1)}
              >
                <span>1. {t('student-info')}</span>
                <ChevronDown
                  className={`w-5 h-5 transform transition-transform duration-300 ${
                    openAccordion === 1 ? 'rotate-180' : 'rotate-0'
                  }`}
                />
              </button>
            </h2>
            <div
              className={`transition-all duration-500 ease-in-out max-h-0 overflow-hidden ${
                openAccordion === 1 ? 'max-h-screen opacity-100' : 'opacity-0'
              }`}
            >
              {openAccordion === 1 && (
                <div className="space-y-6 px-6 py-4">
                  <div>
                    <label className="block text-sm font-medium">{t('full-name')}</label>
                    <input
                      type="text"
                      className="form-input mt-2 block w-full rounded-md border-gray-300"
                      value={CLInfo.name ?? ''}
                      placeholder="e.g. Zhang Ming"
                      onChange={e => setCLInfo({ ...CLInfo, name: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium">{t('uni')}</label>
                    <select
                      className="form-select mt-2 block w-full rounded-md border-gray-300"
                      value={CLInfo.university ?? ''}
                      onChange={e => setCLInfo({ ...CLInfo, university: e.target.value })}
                    >
                      <option value="unsw">UNSW</option>
                      <option value="usyd">USYD</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium">{t('major')}</label>
                    <input
                      type="text"
                      className="form-input mt-2 block w-full rounded-md border-gray-300"
                      placeholder="e.g. Computer Science"
                      value={CLInfo.major}
                      onChange={e => setCLInfo({ ...CLInfo, major: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium">{t('dob')}</label>
                    <input
                      type="date"
                      className="form-input mt-2 block w-full rounded-md border-gray-300"
                      value={CLInfo.dob ?? ''}
                      onChange={e => setCLInfo({ ...CLInfo, dob: e.target.value })}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium">{t('contact-info')}</label>
                    <input
                      type="text"
                      className="form-input mt-2 block w-full rounded-md border-gray-300"
                      value={CLInfo.contact ?? ''}
                      onChange={e => setCLInfo({ ...CLInfo, contact: e.target.value })}
                    />
                  </div>

                  {/* flatmate information (if have) */}
                  <div>
                    <div className="flex items-center mt-4">
                      <span className="mr-3 text-sm font-medium">{t('add-flatmate')}</span>
                      <button
                        type="button"
                        onClick={() => setShowFlatmate(!showFlatmate)}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-300 ${
                          showFlatmate ? 'bg-blue-primary' : 'bg-gray-300'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-300 ${
                            showFlatmate ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                      </button>
                    </div>

                    {showFlatmate && (
                      <div className="mt-4 space-y-4 pl-4 ">
                        <div>
                          <label className="block text-sm font-medium">
                            {t('name-of-flatmate')}
                          </label>
                          <input
                            type="text"
                            className="form-input mt-1 block w-full rounded-md border-gray-300"
                            placeholder="e.g. Li Hua"
                            value={CLInfo.flatmateName ?? ''}
                            onChange={e => setCLInfo({ ...CLInfo, flatmateName: e.target.value })}
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium">{t('relationship')}</label>
                          <select
                            className="form-select mt-1 block w-full rounded-md border-gray-300"
                            value={CLInfo.relationship ?? ''}
                            onChange={e => setCLInfo({ ...CLInfo, relationship: e.target.value })}
                          >
                            <option value="">{t('please-select')}</option>
                            <option value="friend">{t('friend')}</option>
                            <option value="classmate">{t('classmate')}</option>
                            <option value="partner">{t('partner')}</option>
                            <option value="other">{t('relatives')}</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium">
                            {t('other-information')}
                          </label>
                          <input
                            type="text"
                            className="form-input mt-1 block w-full rounded-md border-gray-300"
                            placeholder={t('other-info-ph')}
                            value={CLInfo.otherInfo ?? ''}
                            onChange={e => setCLInfo({ ...CLInfo, otherInfo: e.target.value })}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Living Plan */}
          <div className="pb-1">
            <h2 className="text-xl font-semibold">
              <button
                className="w-full text-left py-3 px-4 bg-gray-100 rounded-md flex items-center justify-between"
                onClick={() => toggleAccordion(2)}
              >
                <span>2. {t('living-plan')}</span>
                <ChevronDown
                  className={`w-5 h-5 transform transition-transform duration-300 ${
                    openAccordion === 1 ? 'rotate-180' : 'rotate-0'
                  }`}
                />
              </button>
            </h2>
            <div
              className={`transition-all duration-500 ease-in-out max-h-0 overflow-hidden ${
                openAccordion === 2 ? 'max-h-screen opacity-100' : 'opacity-0'
              }`}
            >
              {openAccordion === 2 && (
                <div className="space-y-6 px-6 py-4">
                  <div>
                    <label className="block text-sm font-medium">{t('move-in-date')}</label>
                    <input
                      type="date"
                      value={CLInfo.moveInDate}
                      onChange={e => setCLInfo({ ...CLInfo, moveInDate: e.target.value })}
                      className="form-input mt-2 block w-full rounded-md border-gray-300"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium">{t('lease-term')}</label>
                    <input
                      type="number"
                      className="form-input mt-2 block w-full rounded-md border-gray-300"
                      min="1"
                      max="24"
                      required
                      value={CLInfo.leaseTerm}
                      onChange={e => setCLInfo({ ...CLInfo, leaseTerm: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium">{t('rent-budget')}</label>
                    <input
                      type="number"
                      className="form-input block w-full rounded-md border-gray-300"
                      min="100"
                      required
                      value={CLInfo.budget}
                      onChange={e => setCLInfo({ ...CLInfo, budget: e.target.value })}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Financial Statement */}
          <div className="pb-1">
            <h2 className="text-xl font-semibold">
              <button
                className="w-full text-left py-3 px-4 bg-gray-100 rounded-md flex items-center justify-between"
                onClick={() => toggleAccordion(3)}
              >
                <span>3. {t('financial-statement')}</span>
                <ChevronDown
                  className={`w-5 h-5 transform transition-transform duration-300 ${
                    openAccordion === 1 ? 'rotate-180' : 'rotate-0'
                  }`}
                />
              </button>
            </h2>
            <div
              className={`transition-all duration-500 ease-in-out max-h-0 overflow-hidden ${
                openAccordion === 3 ? 'max-h-screen opacity-100' : 'opacity-0'
              }`}
            >
              {openAccordion === 3 && (
                <div className="space-y-6 px-6 py-4">
                  <div>
                    <label className="block text-sm font-medium">{t('proof-of-funds')}</label>
                    <div className="space-y-2 mt-4">
                      {/* Render checkboxes dynamically */}
                      {financialStatementOpts.map(option => (
                        <div key={option} className="flex items-center">
                          <input
                            type="checkbox"
                            id={option}
                            name="proofOfFunds"
                            value={option}
                            checked={CLInfo.financialStatement.includes(option)}
                            onChange={handleCheckboxChange}
                            className="mr-2"
                          />
                          <label htmlFor={option} className="text-sm">
                            {option}
                          </label>
                        </div>
                      ))}
                      {/* extra msg */}
                      {CLInfo.financialStatement.includes(t('account-balance')) && (
                        <div className="mt-2">
                          <label className="block text-sm font-medium">{t('acc-balance')}</label>
                          <input
                            type="text"
                            className="form-input mt-1 block w-full rounded-md border-gray-300"
                            placeholder={t('acc-bal-ph')}
                            value={CLInfo.accountBalance ?? ''}
                            onChange={e => setCLInfo({ ...CLInfo, accountBalance: e.target.value })}
                          />
                        </div>
                      )}

                      {CLInfo.financialStatement.includes(t('proof-of-income')) && (
                        <div className="mt-2">
                          <label className="block text-sm font-medium">{t('income')}</label>
                          <input
                            type="text"
                            className="form-input mt-1 block w-full rounded-md border-gray-300"
                            placeholder={t('income-ph')}
                            value={CLInfo.incomeProof ?? ''}
                            onChange={e => setCLInfo({ ...CLInfo, incomeProof: e.target.value })}
                          />
                        </div>
                      )}

                      {CLInfo.financialStatement.includes(t('scholarship')) && (
                        <div className="mt-2">
                          <label className="block text-sm font-medium">{t('scholar-info')}</label>
                          <input
                            type="text"
                            className="form-input mt-1 block w-full rounded-md border-gray-300"
                            placeholder={t('scholar-ph')}
                            value={CLInfo.scholarship ?? ''}
                            onChange={e => setCLInfo({ ...CLInfo, scholarship: e.target.value })}
                          />
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Rental History */}
          <div className="pb-1">
            <h2 className="text-xl font-semibold">
              <button
                className="w-full text-left py-3 px-4 bg-gray-100 rounded-md flex items-center justify-between"
                onClick={() => toggleAccordion(4)}
              >
                <span>4. {t('rental-history')}</span>
                <ChevronDown
                  className={`w-5 h-5 transform transition-transform duration-300 ${
                    openAccordion === 1 ? 'rotate-180' : 'rotate-0'
                  }`}
                />
              </button>
            </h2>

            <div
              className={`transition-all duration-500 ease-in-out max-h-0 overflow-hidden ${
                openAccordion === 4 ? 'max-h-screen opacity-100' : 'opacity-0'
              }`}
            >
              {openAccordion === 4 && (
                <div className="space-y-6 px-6 py-4">
                  {/* Radio Buttons */}
                  <div className="space-y-2">
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name="rentalHistory"
                        value="first-time"
                        checked={CLInfo.rentalHistory === 'first-time'}
                        onChange={handleRentalHistoryChange}
                        className="mr-2"
                      />
                      {t('first-time')}
                    </label>

                    <label className="flex items-center">
                      <input
                        type="radio"
                        name="rentalHistory"
                        value="not-first-time"
                        checked={CLInfo.rentalHistory === 'not-first-time'}
                        onChange={handleRentalHistoryChange}
                        className="mr-2"
                      />
                      {t('not-first-time')}
                    </label>
                  </div>

                  {/* Additional Section for Previous Rental Experience */}
                  {CLInfo.rentalHistory === 'not-first-time' && (
                    <div className="mt-4 space-y-4 transition-all duration-500">
                      <label className="block text-sm font-medium">{t('rental-experience')}</label>

                      <div className="max-h-96 overflow-y-auto space-y-4">
                        {CLInfo.previousExperiences.map((experience, index) => (
                          <div key={index} className="relative p-4 border rounded-md space-y-4">
                            <div>
                              <label className="block text-sm font-medium">{t('house-add')}</label>
                              <input
                                type="text"
                                className="form-input mt-1 block w-full rounded-md border-gray-300"
                                placeholder={t('house-add-ph')}
                                value={experience.address}
                                onChange={e =>
                                  handleExperienceFieldChange(index, 'address', e.target.value)
                                }
                              />
                            </div>

                            <div>
                              <label className="block text-sm font-medium">{t('rental-dur')}</label>
                              <input
                                type="text"
                                className="form-input mt-1 block w-full rounded-md border-gray-300"
                                placeholder={t('rental-ph')}
                                value={experience.duration}
                                onChange={e =>
                                  handleExperienceFieldChange(index, 'duration', e.target.value)
                                }
                              />
                            </div>

                            <div>
                              <label className="block text-sm font-medium">{t('rent')}</label>
                              <input
                                type="text"
                                className="form-input mt-1 block w-full rounded-md border-gray-300"
                                placeholder={t('rent')}
                                value={experience.weeklyRent}
                                onChange={e =>
                                  handleExperienceFieldChange(index, 'weeklyRent', e.target.value)
                                }
                              />
                            </div>

                            <div className="flex items-center space-x-2">
                              <input
                                type="checkbox"
                                id={`ref-${index}`}
                                checked={experience.hasReference}
                                onChange={e =>
                                  handleExperienceFieldChange(
                                    index,
                                    'hasReference',
                                    e.target.checked
                                  )
                                }
                                className="mr-2"
                              />
                              <label htmlFor={`ref-${index}`} className="text-sm">
                                {t('landlords-ref')}
                              </label>
                            </div>

                            <div>
                              <label className="block text-sm font-medium">{t('extra-msg')}</label>
                              <textarea
                                rows={3}
                                className="form-input mt-1 block w-full rounded-md border-gray-300"
                                placeholder={t('extra-ph')}
                                value={experience.notes}
                                onChange={e =>
                                  handleExperienceFieldChange(index, 'notes', e.target.value)
                                }
                              />
                            </div>

                            <button
                              className="absolute top-1 right-1 text-red-500"
                              onClick={() => removeExperience(index)}
                            >
                              {t('delete')}
                            </button>
                          </div>
                        ))}
                      </div>

                      {/* Add More Experience Button */}
                      <button
                        className="mt-2 px-4 py-2 bg-blue-primary text-white rounded-md"
                        onClick={addExperience}
                      >
                        {t('add-more-experience')}
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Background Information */}
          <div className="pb-1">
            <h2 className="text-xl font-semibold">
              <button
                className="w-full text-left py-3 px-4 bg-gray-100 rounded-md flex items-center justify-between"
                onClick={() => toggleAccordion(5)}
              >
                <span>5. {t('background')}</span>
                <ChevronDown
                  className={`w-5 h-5 transform transition-transform duration-300 ${
                    openAccordion === 1 ? 'rotate-180' : 'rotate-0'
                  }`}
                />
              </button>
            </h2>
            <div
              className={`transition-all duration-500 ease-in-out max-h-0 overflow-hidden ${
                openAccordion === 5 ? 'max-h-screen opacity-100' : 'opacity-0'
              }`}
            >
              {openAccordion === 5 && (
                <div className="space-y-6 px-6 py-4">
                  <div>
                    <label className="block text-sm font-medium">{t('personality')}</label>
                    <div className="space-y-2 mt-4">
                      {/* Render checkboxes dynamically */}
                      {personalityOpts.map(option => (
                        <div key={option} className="flex items-center">
                          <input
                            type="checkbox"
                            id={option}
                            name="personalities"
                            value={option}
                            checked={CLInfo.personality.includes(option)}
                            onChange={handlePersonalityCheckboxChange}
                            className="mr-2"
                          />
                          <label htmlFor={option} className="text-sm">
                            {option}
                          </label>
                        </div>
                      ))}
                    </div>

                    <label className="block text-sm font-medium mt-3">{t('additional-info')}</label>
                    <div className="relative p-4 border rounded-md mt-3">
                      <textarea
                        className="form-input block w-full rounded-md border-gray-300 focus:outline-none focus:ring-0 focus:border-gray-300"
                        rows={3}
                        placeholder={t('additional-info-ph')}
                        value={CLInfo.bgInfo}
                        onChange={e => setCLInfo({ ...CLInfo, bgInfo: e.target.value })}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Required Documents */}
          <div className="pb-1">
            <h2 className="text-xl font-semibold">
              <button
                className="w-full text-left py-3 px-4 bg-gray-100 rounded-md flex items-center justify-between"
                onClick={() => toggleAccordion(11)}
              >
                <span>{t('docs')}</span>
                <ChevronDown
                  className={`w-5 h-5 transform transition-transform duration-300 ${
                    openAccordion === 11 ? 'rotate-180' : 'rotate-0'
                  }`}
                />
              </button>
            </h2>

            <div
              className={`transition-all duration-500 ease-in-out max-h-0 overflow-hidden ${
                openAccordion === 11 ? 'max-h-screen opacity-100' : 'opacity-0'
              }`}
            >
              {openAccordion === 11 && (
                <div className="space-y-6 px-6 py-4">
                  {/* Essential Documents */}
                  <div>
                    <div className="text-sm font-semibold text-gray-700 mb-2">{t('ess-docs')}</div>
                    <div className="space-y-2">
                      {[t('passport'), t('visa'), t('financial-statement')].map(doc => (
                        <label key={doc} className="flex items-center">
                          <input
                            type="checkbox"
                            value={doc}
                            checked={requiredDocs.includes(doc)}
                            onChange={() => {
                              if (requiredDocs.includes(doc)) {
                                setRequiredDocs(requiredDocs.filter(d => d !== doc));
                              } else {
                                setRequiredDocs([...requiredDocs, doc]);
                              }
                            }}
                            className="mr-2"
                          />
                          {doc}
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Optional Documents */}
                  <div>
                    <div className="text-sm font-semibold text-gray-700 mb-2">{t('opt-docs')}</div>
                    <div className="space-y-2">
                      {[t('proof-enr'), t('ref-letter'), t('emp-proof'), t('oth-docs')].map(doc => (
                        <label key={doc} className="flex items-center">
                          <input
                            type="checkbox"
                            value={doc}
                            checked={optionalDocs.includes(doc)}
                            onChange={() => {
                              if (optionalDocs.includes(doc)) {
                                setOptionalDocs(optionalDocs.filter(d => d !== doc));
                              } else {
                                setOptionalDocs([...optionalDocs, doc]);
                              }
                            }}
                            className="mr-2"
                          />
                          {doc}
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Guarantor Information */}
          <div className="pb-1">
            <h2 className="text-xl font-semibold">
              <button
                className="w-full text-left py-3 px-4 bg-gray-100 rounded-md flex items-center justify-between"
                onClick={() => toggleAccordion(7)}
              >
                <span>1. {t('guarantor-info')}</span>
                <ChevronDown
                  className={`w-5 h-5 transform transition-transform duration-300 ${
                    openAccordion === 1 ? 'rotate-180' : 'rotate-0'
                  }`}
                />
              </button>
            </h2>
            <div
              className={`transition-all duration-500 ease-in-out max-h-0 overflow-hidden ${
                openAccordion === 7 ? 'max-h-screen opacity-100' : 'opacity-0'
              }`}
            >
              {openAccordion === 7 && (
                <div className="space-y-6 px-6 py-4">
                  <div className="font-semibold">
                    {/* Parent names */}
                    <div className="pb-4">
                      <div className="flex jusrify-between items-center mt-3 gap-3">
                        {/* Father */}
                        <div className="space-y-2 flex-1">
                          <div className="text-sm text-gray-600">{t('dad-name')}</div>
                          <textarea
                            className="flex border rounded px-2 py-1 max-h-40 overflow-y-auto w-full"
                            placeholder="e.g. Zhang Wei"
                            value={PLInfo.fatherName}
                            onChange={e =>
                              setPLInfo({
                                ...PLInfo,
                                fatherName: e.target.value,
                              })
                            }
                          />
                        </div>

                        {/* Mother */}
                        <div className="space-y-2 flex-1">
                          <div className="text-sm text-gray-600">{t('mom-name')}</div>
                          <textarea
                            className="flex border rounded px-2 py-1 max-h-40 overflow-y-auto w-full"
                            placeholder="e.g. Li Mei"
                            value={PLInfo.motherName}
                            onChange={e =>
                              setPLInfo({
                                ...PLInfo,
                                motherName: e.target.value,
                              })
                            }
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="font-semibold">
                    {/* Parent tel */}
                    <div className="pb-4">
                      <div className="flex jusrify-between items-center mt-3 gap-3">
                        {/* Father tel */}
                        <div className="space-y-2 flex-1">
                          <div className="text-sm text-gray-600">{t('dad-tel')}</div>
                          <textarea
                            className="flex border rounded px-2 py-1 max-h-40 overflow-y-auto w-full"
                            placeholder="e.g. +86 138 xxxx xxxx"
                            value={PLInfo.fatherContactNum}
                            onChange={e =>
                              setPLInfo({
                                ...PLInfo,
                                fatherContactNum: e.target.value,
                              })
                            }
                          />
                        </div>

                        {/* Mother tel */}
                        <div className="space-y-2 flex-1">
                          <div className="text-sm text-gray-600">{t('mom-tel')}</div>
                          <textarea
                            className="flex border rounded px-2 py-1 max-h-40 overflow-y-auto w-full"
                            placeholder="e.g. +86 138 xxxx xxxx"
                            value={PLInfo.motherContactNum}
                            onChange={e =>
                              setPLInfo({
                                ...PLInfo,
                                motherContactNum: e.target.value,
                              })
                            }
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="font-semibold">
                    <div className="pb-4">
                      <div className="flex jusrify-between items-center mt-3 gap-3">
                        {/* Contact email */}
                        <div className="space-y-2 flex-1">
                          <div className="text-sm text-gray-600">{t('email')}</div>
                          <textarea
                            className="flex border rounded px-2 py-1 max-h-40 overflow-y-auto w-full"
                            placeholder="e.g. parent@gmail.com"
                            value={PLInfo.contactEmail}
                            onChange={e =>
                              setPLInfo({
                                ...PLInfo,
                                contactEmail: e.target.value,
                              })
                            }
                          />
                        </div>

                        {/* name */}
                        <div className="space-y-2 flex-1">
                          <div className="text-sm text-gray-600">{t('student-name')}</div>
                          <textarea
                            className="flex border rounded px-2 py-1 max-h-40 overflow-y-auto w-full"
                            placeholder="e.g. Zhang Ming"
                            value={PLInfo.studentName}
                            onChange={e =>
                              setPLInfo({
                                ...PLInfo,
                                studentName: e.target.value,
                              })
                            }
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="font-semibold">
                    <div className="pb-4">
                      <div className="flex jusrify-between items-center mt-3 gap-3">
                        {/* Father */}
                        <div className="space-y-2 flex-1">
                          <div className="text-sm text-gray-600">{t('home-address')}</div>
                          <textarea
                            className="flex border rounded px-2 py-1 max-h-40 overflow-y-auto w-full"
                            placeholder="e.g. No.123, XiDan Street, Beijing, China"
                            value={PLInfo.homeAddress}
                            onChange={e =>
                              setPLInfo({
                                ...PLInfo,
                                homeAddress: e.target.value,
                              })
                            }
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Financial Support */}
          <div className="pb-1">
            <h2 className="text-xl font-semibold">
              <button
                className="w-full text-left py-3 px-4 bg-gray-100 rounded-md flex items-center justify-between"
                onClick={() => toggleAccordion(8)}
              >
                <span>2. {t('financial-support')}</span>
                <ChevronDown
                  className={`w-5 h-5 transform transition-transform duration-300 ${
                    openAccordion === 1 ? 'rotate-180' : 'rotate-0'
                  }`}
                />
              </button>
            </h2>
            <div
              className={`transition-all duration-500 ease-in-out max-h-0 overflow-hidden ${
                openAccordion === 8 ? 'max-h-screen opacity-100' : 'opacity-0'
              }`}
            >
              {openAccordion === 8 && (
                <div className="space-y-6 px-6 py-4">
                  <div>
                    <div className="font-semibold">
                      <div className="pb-4">
                        <div className="flex jusrify-between items-center mt-3 gap-3">
                          {/* Weekly Rent */}
                          <div className="space-y-2 flex-1">
                            <div className="text-sm text-gray-600">{t('weekly-rent')}</div>
                            <textarea
                              className="flex border rounded px-2 py-1 max-h-40 overflow-y-auto w-full"
                              placeholder="e.g. 300$"
                              value={PLInfo.weeklyRent}
                              onChange={e =>
                                setPLInfo({
                                  ...PLInfo,
                                  weeklyRent: e.target.value,
                                })
                              }
                            />
                          </div>

                          {/* livingExpenses */}
                          <div className="space-y-2 flex-1">
                            <div className="text-sm text-gray-600">{t('living-expen')}</div>
                            <textarea
                              className="flex border rounded px-2 py-1 max-h-40 overflow-y-auto w-full"
                              placeholder="e.g. 800$"
                              value={PLInfo.livingExpenses}
                              onChange={e =>
                                setPLInfo({
                                  ...PLInfo,
                                  livingExpenses: e.target.value,
                                })
                              }
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2 mt-4 font-semibold">
                    <div className="text-sm text-gray-600">{t('source-funds')}</div>
                    {sourceOfFundsOpts.map(option => (
                      <div key={option} className="flex items-center">
                        <input
                          type="checkbox"
                          id={option}
                          name="sourceOfFunds"
                          value={option}
                          checked={PLInfo.sourceOfFunds.includes(option)}
                          onChange={handleSourceFundsCheckboxChange}
                          className="mr-2"
                        />
                        <label htmlFor={option} className="text-sm">
                          {option}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Proof of Guarantor's Ability */}
          <div className="pb-1">
            <h2 className="text-xl font-semibold">
              <button
                className="w-full text-left py-3 px-4 bg-gray-100 rounded-md flex items-center justify-between"
                onClick={() => toggleAccordion(9)}
              >
                <span>3. {t('proof-guarantor-ability')}</span>
                <ChevronDown
                  className={`w-5 h-5 transform transition-transform duration-300 ${
                    openAccordion === 1 ? 'rotate-180' : 'rotate-0'
                  }`}
                />
              </button>
            </h2>
            <div
              className={`transition-all duration-500 ease-in-out max-h-0 overflow-hidden ${
                openAccordion === 9 ? 'max-h-screen opacity-100' : 'opacity-0'
              }`}
            >
              {openAccordion === 9 && (
                <div className="space-y-6 px-6 py-4">
                  <div>
                    <div className="font-semibold">
                      <div className="pb-4">
                        <div className="flex jusrify-between items-center mt-3 gap-3">
                          {/* account balance */}
                          <div className="space-y-2 flex-1">
                            <div className="text-sm text-gray-600">{t('account-balance')}</div>
                            <textarea
                              className="flex border rounded px-2 py-1 max-h-40 overflow-y-auto w-full"
                              placeholder="e.g. 500000"
                              value={PLInfo.accountBalance}
                              onChange={e =>
                                setPLInfo({
                                  ...PLInfo,
                                  accountBalance: e.target.value,
                                })
                              }
                            />
                          </div>

                          {/* annualIncome */}
                          <div className="space-y-2 flex-1">
                            <div className="text-sm text-gray-600">{t('annual-income')}</div>
                            <textarea
                              className="flex border rounded px-2 py-1 max-h-40 overflow-y-auto w-full"
                              placeholder="e.g. 300000"
                              value={PLInfo.annualIncome}
                              onChange={e =>
                                setPLInfo({
                                  ...PLInfo,
                                  annualIncome: e.target.value,
                                })
                              }
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2 mt-4 font-semibold">
                    <div className="text-sm text-gray-600">{t('proof-docs')}</div>
                    {proofDocsOpts.map(option => (
                      <div key={option} className="flex items-center">
                        <input
                          type="checkbox"
                          id={option}
                          name="proofDocs"
                          value={option}
                          checked={PLInfo.proofDocs.includes(option)}
                          onChange={handleProofDocsCheckboxChange}
                          className="mr-2"
                        />
                        <label htmlFor={option} className="text-sm">
                          {option}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Additional Commitment */}
          <div className="pb-1">
            <h2 className="text-xl font-semibold">
              <button
                className="w-full text-left py-3 px-4 bg-gray-100 rounded-md flex items-center justify-between"
                onClick={() => toggleAccordion(10)}
              >
                <span>4. {t('additional-commitment')}</span>
                <ChevronDown
                  className={`w-5 h-5 transform transition-transform duration-300 ${
                    openAccordion === 1 ? 'rotate-180' : 'rotate-0'
                  }`}
                />
              </button>
            </h2>
            <div
              className={`transition-all duration-500 ease-in-out max-h-0 overflow-hidden ${
                openAccordion === 10 ? 'max-h-screen opacity-100' : 'opacity-0'
              }`}
            >
              {openAccordion === 10 && (
                <div className="space-y-6 px-6 py-4">
                  <div className="font-semibold">
                    <div className="pb-4">
                      <div className="flex jusrify-between items-center mt-3 gap-3">
                        {/* Prepay Rent */}
                        <div className="space-y-2 flex-1">
                          <div className="text-sm text-gray-600">{t('willingness')}</div>
                          <select
                            className="flex border rounded px-2 py-1 max-h-40 overflow-y-auto w-full"
                            value={PLInfo.prepayRent}
                            onChange={e =>
                              setPLInfo({
                                ...PLInfo,
                                prepayRent: e.target.value,
                              })
                            }
                          >
                            <option>{t('no-prepayment')}</option>
                            <option>{t('pay-1-month')}</option>
                            <option>{t('pay-3-month')}</option>
                            <option>{t('pay-6-month')}</option>
                            <option>{t('pay-9-month')}</option>
                            <option>{t('pay-12-month')}</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2 mt-4">
                    <div className="text-sm text-gray-600 font-semibold">
                      {t('joint-liability')}
                    </div>
                    <input
                      type="checkbox"
                      value={PLInfo.liabilityStatement}
                      onChange={e =>
                        setPLInfo({
                          ...PLInfo,
                          liabilityStatement: e.target.value,
                        })
                      }
                      className="mr-2"
                    />
                    <label className="text-sm font-semibold">{t('will-joint-liability')}</label>
                    <div className="text-xs">{t('will-joint-msg')}</div>
                  </div>
                  <div className="space-y-2 mt-4">
                    {' '}
                    <label className="block text-sm font-medium mt-3">
                      {t('additional-commitment')}
                    </label>
                    <div className="relative p-4 border rounded-md mt-3">
                      <textarea
                        className="form-input block w-full rounded-md border-gray-300 focus:outline-none focus:ring-0 focus:border-gray-300"
                        rows={3}
                        placeholder={t('additional-commitment-ph')}
                        value={PLInfo.otherCommitments}
                        onChange={e =>
                          setPLInfo({
                            ...PLInfo,
                            otherCommitments: e.target.value,
                          })
                        }
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LetterForm;
