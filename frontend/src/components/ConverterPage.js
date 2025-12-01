import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { ArrowRightLeft } from 'lucide-react';
import { api } from '../services/api';

const ConverterPage = () => {
  const { t, language } = useLanguage();
  const [amount, setAmount] = useState('1');
  const [fromItem, setFromItem] = useState('GRAM ALTIN');
  const [toItem, setToItem] = useState('TRY');
  const [result, setResult] = useState(null);
  const [allItems, setAllItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPrices = async () => {
      setLoading(true);
      try {
        const data = await api.getPrices();
        const items = [];
        
        if (data.gold) {
          data.gold.forEach(item => {
            items.push({
              value: language === 'tr' ? item.name : item.nameEn,
              label: language === 'tr' ? item.name : item.nameEn,
              price: item.sell,
              type: 'gold'
            });
          });
        }
        
        if (data.currency) {
          data.currency.forEach(item => {
            items.push({
              value: language === 'tr' ? item.name : item.nameEn,
              label: language === 'tr' ? item.name : item.nameEn,
              price: item.sell,
              type: 'currency'
            });
          });
        }
        
        items.push({ value: 'TRY', label: 'Türk Lirası (TRY)', price: 1, type: 'currency' });
        setAllItems(items);
      } catch (error) {
        console.error('Failed to fetch prices:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchPrices();
  }, [language]);

  const handleCalculate = () => {
    const fromPrice = allItems.find(item => item.value === fromItem)?.price || 1;
    const toPrice = allItems.find(item => item.value === toItem)?.price || 1;
    const numAmount = parseFloat(amount) || 0;
    
    const calculatedResult = (numAmount * fromPrice) / toPrice;
    setResult(calculatedResult);
  };

  const handleSwap = () => {
    const temp = fromItem;
    setFromItem(toItem);
    setToItem(temp);
    setResult(null);
  };

  if (loading) {
    return (
      <div className="pb-20 pt-6 px-4 text-center">
        <p className="text-gray-500">Yükleniyor...</p>
      </div>
    );
  }

  return (
    <div className="pb-20 pt-6 px-4">
      <div className="max-w-md mx-auto">
        {/* Header */}
        <div className="text-center mb-6">
          <h2 className="text-yellow-600 font-bold text-lg">{t('converter_title')}</h2>
          <p className="text-gray-500 text-sm mt-1">{t('converter_subtitle')}</p>
        </div>

        {/* Calculator Card */}
        <div className="bg-white rounded-2xl shadow-lg p-6 space-y-5">
          {/* Amount Input */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              {t('amount')}
            </label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0.00"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent text-lg font-semibold"
            />
          </div>

          {/* From Select */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              {t('from')}
            </label>
            <select
              value={fromItem}
              onChange={(e) => setFromItem(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent bg-white font-medium"
            >
              {allItems.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </div>

          {/* Swap Button */}
          <div className="flex justify-center">
            <button
              onClick={handleSwap}
              className="p-3 rounded-full bg-yellow-100 hover:bg-yellow-200 transition-colors"
            >
              <ArrowRightLeft className="text-yellow-600" size={20} />
            </button>
          </div>

          {/* To Select */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              {t('to')}
            </label>
            <select
              value={toItem}
              onChange={(e) => setToItem(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent bg-white font-medium"
            >
              {allItems.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </div>

          {/* Calculate Button */}
          <button
            onClick={handleCalculate}
            className="w-full py-3.5 bg-gradient-to-r from-yellow-500 to-yellow-600 text-white font-bold rounded-lg hover:from-yellow-600 hover:to-yellow-700 transition-all shadow-md hover:shadow-lg"
          >
            {t('calculate')}
          </button>

          {/* Result */}
          {result !== null && (
            <div className="mt-6 p-4 bg-yellow-50 rounded-lg border-2 border-yellow-200">
              <p className="text-sm font-semibold text-gray-700 mb-1">{t('result')}:</p>
              <p className="text-2xl font-bold text-yellow-600">
                {result.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                {amount} {fromItem} = {result.toFixed(2)} {toItem}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConverterPage;