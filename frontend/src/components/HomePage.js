import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { TrendingUp, TrendingDown, Search, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

const PriceCard = ({ item, language }) => {
  const name = language === 'tr' ? item.name : item.nameEn;
  const isPositive = item.change >= 0;

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-3 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold text-gray-800 text-sm">{name}</h3>
        <div className={`flex items-center gap-1 text-xs font-semibold ${
          isPositive ? 'text-green-600' : 'text-red-600'
        }`}>
          {isPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
          {isPositive ? '+' : ''}{item.change.toFixed(2)}%
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div>
          <p className="text-gray-500 text-xs">Alış</p>
          <p className="font-bold text-gray-900">{item.buy.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
        </div>
        <div>
          <p className="text-gray-500 text-xs">Satış</p>
          <p className="font-bold text-gray-900">{item.sell.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
        </div>
      </div>
    </div>
  );
};

const HomePage = () => {
  const { t, language } = useLanguage();
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('gold');
  const [goldPrices, setGoldPrices] = useState([]);
  const [currencies, setCurrencies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchPrices = async () => {
    setLoading(true);
    try {
      const data = await api.getPrices();
      if (data.gold) setGoldPrices(data.gold);
      if (data.currency) setCurrencies(data.currency);
      setLastUpdate(new Date(data.lastUpdate));
    } catch (error) {
      console.error('Failed to fetch prices:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrices();
    // Auto-refresh every 60 seconds
    const interval = setInterval(fetchPrices, 60000);
    return () => clearInterval(interval);
  }, []);

  const filteredGold = goldPrices.filter(item => {
    const name = language === 'tr' ? item.name : item.nameEn;
    return name.toLowerCase().includes(searchQuery.toLowerCase());
  });

  const filteredCurrencies = currencies.filter(item => {
    const name = language === 'tr' ? item.name : item.nameEn;
    return name.toLowerCase().includes(searchQuery.toLowerCase());
  });

  return (
    <div className="pb-20 pt-4">
      {/* Search Bar */}
      <div className="px-4 mb-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            placeholder={t('search')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
          />
          <button
            onClick={fetchPrices}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 hover:bg-gray-100 rounded-lg transition-colors"
            disabled={loading}
          >
            <RefreshCw size={16} className={`text-gray-600 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex gap-2 px-4 mb-4">
        <button
          onClick={() => setActiveCategory('gold')}
          className={`flex-1 py-2.5 rounded-lg font-semibold text-sm transition-all ${
            activeCategory === 'gold'
              ? 'bg-yellow-500 text-white shadow-md'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          {t('gold')}
        </button>
        <button
          onClick={() => setActiveCategory('currency')}
          className={`flex-1 py-2.5 rounded-lg font-semibold text-sm transition-all ${
            activeCategory === 'currency'
              ? 'bg-yellow-500 text-white shadow-md'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          {t('currency')}
        </button>
      </div>

      {/* Price List */}
      <div className="px-4">
        {loading && goldPrices.length === 0 ? (
          <div className="text-center py-12">
            <RefreshCw size={32} className="mx-auto text-yellow-500 animate-spin mb-3" />
            <p className="text-gray-500">Yükleniyor...</p>
          </div>
        ) : (
          <>
            {activeCategory === 'gold' && (
              <div>
                <h2 className="text-yellow-600 font-bold text-center mb-4 text-sm tracking-wide">
                  {t('goldPrices')}
                </h2>
                <div className="space-y-3">
                  {filteredGold.map((item) => (
                    <PriceCard key={item.id} item={item} language={language} />
                  ))}
                </div>
              </div>
            )}

            {activeCategory === 'currency' && (
              <div>
                <h2 className="text-yellow-600 font-bold text-center mb-4 text-sm tracking-wide">
                  {t('currencyRates')}
                </h2>
                <div className="space-y-3">
                  {filteredCurrencies.map((item) => (
                    <PriceCard key={item.id} item={item} language={language} />
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Last Update Time */}
      {lastUpdate && (
        <div className="text-center mt-6 text-xs text-gray-500">
          Son Güncelleme: {lastUpdate.toLocaleString('tr-TR')}
        </div>
      )}
    </div>
  );
};

export default HomePage;