import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { Plus, TrendingUp, TrendingDown, Trash2, Briefcase } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { api } from '../services/api';
import { toast } from '../hooks/use-toast';

const PortfolioPage = () => {
  const { t, language } = useLanguage();
  const [portfolio, setPortfolio] = useState([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [allItems, setAllItems] = useState([]);
  const [prices, setPrices] = useState({ gold: [], currency: [] });
  const [newItem, setNewItem] = useState({
    type: 'gold',
    name: '',
    quantity: '',
    buyPrice: ''
  });

  useEffect(() => {
    fetchPortfolio();
    fetchPrices();
  }, []);

  const fetchPortfolio = async () => {
    setLoading(true);
    try {
      const data = await api.getPortfolio();
      setPortfolio(data);
    } catch (error) {
      console.error('Failed to fetch portfolio:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPrices = async () => {
    try {
      const data = await api.getPrices();
      setPrices(data);
      
      const items = [];
      if (data.gold) {
        data.gold.forEach(item => {
          items.push({
            value: language === 'tr' ? item.name : item.nameEn,
            label: language === 'tr' ? item.name : item.nameEn,
            price: item.sell,
            type: 'gold',
            nameEn: item.nameEn,
            nameTr: item.name
          });
        });
      }
      
      if (data.currency) {
        data.currency.forEach(item => {
          items.push({
            value: language === 'tr' ? item.name : item.nameEn,
            label: language === 'tr' ? item.name : item.nameEn,
            price: item.sell,
            type: 'currency',
            nameEn: item.nameEn,
            nameTr: item.name
          });
        });
      }
      
      setAllItems(items);
    } catch (error) {
      console.error('Failed to fetch prices:', error);
    }
  };

  const handleAddItem = async () => {
    if (newItem.name && newItem.quantity && newItem.buyPrice) {
      try {
        const selectedItem = allItems.find(item => item.value === newItem.name);
        const itemData = {
          type: newItem.type,
          name: selectedItem?.nameTr || newItem.name,
          nameEn: selectedItem?.nameEn || newItem.name,
          quantity: parseFloat(newItem.quantity),
          buyPrice: parseFloat(newItem.buyPrice)
        };
        
        await api.createPortfolioItem(itemData);
        await fetchPortfolio();
        setNewItem({ type: 'gold', name: '', quantity: '', buyPrice: '' });
        setIsDialogOpen(false);
        toast({ title: 'Başarılı', description: 'Portföye eklendi' });
      } catch (error) {
        console.error('Failed to add item:', error);
        toast({ title: 'Hata', description: 'Ürün eklenemedi', variant: 'destructive' });
      }
    }
  };

  const handleDeleteItem = async (id) => {
    try {
      await api.deletePortfolioItem(id);
      await fetchPortfolio();
      toast({ title: 'Başarılı', description: 'Portföyden silindi' });
    } catch (error) {
      console.error('Failed to delete item:', error);
      toast({ title: 'Hata', description: 'Ürün silinemedi', variant: 'destructive' });
    }
  };

  const getCurrentPrice = (item) => {
    const priceItem = allItems.find(p => 
      (language === 'tr' ? p.nameTr === item.name : p.nameEn === item.nameEn)
    );
    return priceItem?.price || item.buyPrice;
  };

  const calculateProfit = (item) => {
    const currentPrice = getCurrentPrice(item);
    const profit = (currentPrice - item.buyPrice) * item.quantity;
    const percentage = ((currentPrice - item.buyPrice) / item.buyPrice) * 100;
    return { profit, percentage, currentPrice };
  };

  const totalValue = portfolio.reduce((sum, item) => {
    const currentPrice = getCurrentPrice(item);
    return sum + (currentPrice * item.quantity);
  }, 0);
  const totalCost = portfolio.reduce((sum, item) => sum + (item.buyPrice * item.quantity), 0);
  const totalProfit = totalValue - totalCost;
  const totalPercentage = totalCost > 0 ? (totalProfit / totalCost) * 100 : 0;

  if (loading) {
    return (
      <div className=\"pb-20 pt-6 px-4 text-center\">
        <p className=\"text-gray-500\">Yükleniyor...</p>
      </div>
    );
  }

  return (
    <div className="pb-20 pt-6 px-4">
      <div className="max-w-md mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-yellow-600 font-bold text-lg">{t('portfolio_title')}</h2>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-yellow-500 hover:bg-yellow-600 text-white">
                <Plus size={18} className="mr-1" />
                {t('add_item')}
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-sm">
              <DialogHeader>
                <DialogTitle>{t('add_item')}</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <Label>{t('selectType')}</Label>
                  <select
                    value={newItem.type}
                    onChange={(e) => setNewItem({ ...newItem, type: e.target.value, name: '' })}
                    className="w-full px-3 py-2 border rounded-lg mt-1"
                  >
                    <option value="gold">{t('gold')}</option>
                    <option value="currency">{t('currency')}</option>
                  </select>
                </div>
                <div>
                  <Label>{t('selectItem')}</Label>
                  <select
                    value={newItem.name}
                    onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg mt-1"
                  >
                    <option value="">{t('selectItem')}</option>
                    {allItems
                      .filter(item => item.type === newItem.type)
                      .map(item => (
                        <option key={item.value} value={item.value}>
                          {item.label}
                        </option>
                      ))}
                  </select>
                </div>
                <div>
                  <Label>{t('quantity')}</Label>
                  <Input
                    type="number"
                    value={newItem.quantity}
                    onChange={(e) => setNewItem({ ...newItem, quantity: e.target.value })}
                    placeholder="0"
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label>{t('buyPrice')}</Label>
                  <Input
                    type="number"
                    value={newItem.buyPrice}
                    onChange={(e) => setNewItem({ ...newItem, buyPrice: e.target.value })}
                    placeholder="0.00"
                    className="mt-1"
                  />
                </div>
                <div className="flex gap-2">
                  <Button onClick={() => setIsDialogOpen(false)} variant="outline" className="flex-1">
                    {t('cancel')}
                  </Button>
                  <Button onClick={handleAddItem} className="flex-1 bg-yellow-500 hover:bg-yellow-600">
                    {t('save')}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Summary Card */}
        {portfolio.length > 0 && (
          <div className="bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-2xl p-6 mb-6 text-white shadow-lg">
            <p className="text-sm opacity-90 mb-1">{t('total')} {t('portfolio')}</p>
            <p className="text-3xl font-bold mb-3">
              {totalValue.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ₺
            </p>
            <div className="flex items-center gap-2">
              {totalProfit >= 0 ? <TrendingUp size={18} /> : <TrendingDown size={18} />}
              <span className="font-semibold">
                {totalProfit >= 0 ? '+' : ''}{totalProfit.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ₺
              </span>
              <span className="opacity-90">({totalProfit >= 0 ? '+' : ''}{totalPercentage.toFixed(2)}%)</span>
            </div>
          </div>
        )}

        {/* Portfolio Items */}
        {portfolio.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Briefcase size={48} className="mx-auto mb-3 opacity-30" />
            <p>{t('portfolio_empty')}</p>
          </div>
        ) : (
          <div className="space-y-3">
            {portfolio.map((item) => {
              const { profit, percentage } = calculateProfit(item);
              const name = language === 'tr' ? item.name : item.nameEn;
              return (
                <div key={item.id} className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-bold text-gray-800">{name}</h3>
                      <p className="text-sm text-gray-500">{item.quantity} {t('quantity')}</p>
                    </div>
                    <button
                      onClick={() => handleDeleteItem(item.id)}
                      className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <p className="text-gray-500">{t('buyPrice')}</p>
                      <p className="font-semibold">{item.buyPrice.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</p>
                    </div>
                    <div>
                      <p className="text-gray-500">{t('currentPrice')}</p>
                      <p className="font-semibold">{item.currentPrice.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</p>
                    </div>
                  </div>
                  <div className={`mt-3 pt-3 border-t flex items-center justify-between ${
                    profit >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    <span className="text-sm font-semibold">{t('profit_loss')}</span>
                    <div className="flex items-center gap-2 font-bold">
                      {profit >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                      <span>
                        {profit >= 0 ? '+' : ''}{profit.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                      </span>
                      <span className="text-sm">({profit >= 0 ? '+' : ''}{percentage.toFixed(2)}%)</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default PortfolioPage;