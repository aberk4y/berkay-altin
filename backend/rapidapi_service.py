import os
import requests
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY', '')
RAPIDAPI_HOST = "gold-and-foreign-exchange-information-from-turkish-companies.p.rapidapi.com"

class RapidAPIService:
    def __init__(self):
        self.headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": RAPIDAPI_HOST
        }
        self.base_url = f"https://{RAPIDAPI_HOST}"
    
    def get_gold_prices(self) -> List[Dict]:
        """Fetch gold prices from RapidAPI"""
        try:
            url = f"{self.base_url}/altin"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._format_gold_data(data)
            else:
                logger.error(f"RapidAPI gold prices error: {response.status_code}")
                return self._get_fallback_gold_data()
        except Exception as e:
            logger.error(f"Error fetching gold prices: {str(e)}")
            return self._get_fallback_gold_data()
    
    def get_currency_rates(self) -> List[Dict]:
        """Fetch currency rates from RapidAPI"""
        try:
            url = f"{self.base_url}/doviz"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._format_currency_data(data)
            else:
                logger.error(f"RapidAPI currency rates error: {response.status_code}")
                return self._get_fallback_currency_data()
        except Exception as e:
            logger.error(f"Error fetching currency rates: {str(e)}")
            return self._get_fallback_currency_data()
    
    def _format_gold_data(self, data: Dict) -> List[Dict]:
        """Format gold data from API response"""
        formatted = []
        counter = 1
        
        gold_mapping = {
            'has_altin': ('HAS ALTIN', 'PURE GOLD'),
            'ons': ('ONS', 'OUNCE'),
            'ceyrek_altin': ('ÇEYREK ALTIN', 'QUARTER GOLD'),
            'yarim_altin': ('YARIM ALTIN', 'HALF GOLD'),
            'tam_altin': ('TAM ALTIN', 'FULL GOLD'),
            'ayar22': ('22 AYAR', '22 CARAT'),
            'gram_altin': ('GRAM ALTIN', 'GRAM GOLD'),
            'gumus': ('ALTIN GÜMÜŞ', 'GOLD SILVER'),
            'resat': ('REŞAT ALTIN', 'RESAT GOLD'),
            'ata': ('ATA ALTIN', 'ATA GOLD')
        }
        
        for key, (name_tr, name_en) in gold_mapping.items():
            if key in data:
                item_data = data[key]
                buy = float(item_data.get('alis', 0))
                sell = float(item_data.get('satis', 0))
                change = float(item_data.get('degisim', 0))
                
                formatted.append({
                    'id': counter,
                    'name': name_tr,
                    'nameEn': name_en,
                    'buy': buy,
                    'sell': sell,
                    'change': change,
                    'unit': 'TRY'
                })
                counter += 1
        
        return formatted
    
    def _format_currency_data(self, data: Dict) -> List[Dict]:
        """Format currency data from API response"""
        formatted = []
        counter = 1
        
        currency_mapping = {
            'dolar': ('USD', 'USD', '$'),
            'euro': ('EUR', 'EUR', '€'),
            'sterlin': ('GBP', 'GBP', '£'),
            'frank': ('CHF', 'CHF', 'Fr'),
            'avustralya_dolari': ('AUD', 'AUD', '$'),
            'kanada_dolari': ('CAD', 'CAD', '$'),
            'suudi_arabistan_riyali': ('SAR', 'SAR', 'ر.س'),
            'japon_yeni': ('JPY', 'JPY', '¥'),
            'kuveyt_dinari': ('KWD', 'KWD', 'KD')
        }
        
        for key, (name_tr, name_en, symbol) in currency_mapping.items():
            if key in data:
                item_data = data[key]
                buy = float(item_data.get('alis', 0))
                sell = float(item_data.get('satis', 0))
                change = float(item_data.get('degisim', 0))
                
                formatted.append({
                    'id': counter,
                    'name': name_tr,
                    'nameEn': name_en,
                    'buy': buy,
                    'sell': sell,
                    'change': change,
                    'symbol': symbol,
                    'unit': 'TRY'
                })
                counter += 1
        
        # Add special gold/currency rates
        if 'usd_kg' in data:
            item_data = data['usd_kg']
            formatted.append({
                'id': counter,
                'name': 'USD/KG',
                'nameEn': 'USD/KG',
                'buy': float(item_data.get('alis', 0)),
                'sell': float(item_data.get('satis', 0)),
                'change': float(item_data.get('degisim', 0)),
                'symbol': '$',
                'unit': 'TRY'
            })
            counter += 1
        
        if 'eur_kg' in data:
            item_data = data['eur_kg']
            formatted.append({
                'id': counter,
                'name': 'EUR/KG',
                'nameEn': 'EUR/KG',
                'buy': float(item_data.get('alis', 0)),
                'sell': float(item_data.get('satis', 0)),
                'change': float(item_data.get('degisim', 0)),
                'symbol': '€',
                'unit': 'TRY'
            })
        
        return formatted
    
    def _get_fallback_gold_data(self) -> List[Dict]:
        """Fallback gold data if API fails"""
        return [
            {'id': 1, 'name': 'HAS ALTIN', 'nameEn': 'PURE GOLD', 'buy': 5807.50, 'sell': 5858.70, 'change': 0.74, 'unit': 'TRY'},
            {'id': 2, 'name': 'ONS', 'nameEn': 'OUNCE', 'buy': 4239.5, 'sell': 4239.9, 'change': 0.53, 'unit': 'TRY'},
            {'id': 3, 'name': 'ÇEYREK ALTIN', 'nameEn': 'QUARTER GOLD', 'buy': 2389.0, 'sell': 2398.0, 'change': 0.68, 'unit': 'TRY'},
            {'id': 4, 'name': 'YARIM ALTIN', 'nameEn': 'HALF GOLD', 'buy': 4779.0, 'sell': 4796.0, 'change': 0.72, 'unit': 'TRY'},
            {'id': 5, 'name': 'TAM ALTIN', 'nameEn': 'FULL GOLD', 'buy': 9558.0, 'sell': 9592.0, 'change': 0.75, 'unit': 'TRY'},
            {'id': 6, 'name': '22 AYAR', 'nameEn': '22 CARAT', 'buy': 5282.82, 'sell': 5545.77, 'change': 4.83, 'unit': 'TRY'},
            {'id': 7, 'name': 'GRAM ALTIN', 'nameEn': 'GRAM GOLD', 'buy': 5778.46, 'sell': 5876.28, 'change': 1.55, 'unit': 'TRY'},
            {'id': 8, 'name': 'ALTIN GÜMÜŞ', 'nameEn': 'GOLD SILVER', 'buy': 70.66, 'sell': 73.63, 'change': 0.59, 'unit': 'TRY'},
            {'id': 9, 'name': 'REŞAT ALTIN', 'nameEn': 'RESAT GOLD', 'buy': 9872.0, 'sell': 9912.0, 'change': 0.82, 'unit': 'TRY'},
            {'id': 10, 'name': 'ATA ALTIN', 'nameEn': 'ATA GOLD', 'buy': 9612.0, 'sell': 9652.0, 'change': 0.78, 'unit': 'TRY'}
        ]
    
    def _get_fallback_currency_data(self) -> List[Dict]:
        """Fallback currency data if API fails"""
        return [
            {'id': 1, 'name': 'USD', 'nameEn': 'USD', 'buy': 34.125, 'sell': 34.225, 'change': 0.55, 'symbol': '$', 'unit': 'TRY'},
            {'id': 2, 'name': 'EUR', 'nameEn': 'EUR', 'buy': 35.890, 'sell': 36.050, 'change': 0.68, 'symbol': '€', 'unit': 'TRY'},
            {'id': 3, 'name': 'GBP', 'nameEn': 'GBP', 'buy': 43.250, 'sell': 43.450, 'change': 0.42, 'symbol': '£', 'unit': 'TRY'},
            {'id': 4, 'name': 'CHF', 'nameEn': 'CHF', 'buy': 38.650, 'sell': 38.850, 'change': 0.38, 'symbol': 'Fr', 'unit': 'TRY'},
            {'id': 5, 'name': 'AUD', 'nameEn': 'AUD', 'buy': 22.150, 'sell': 22.350, 'change': 0.25, 'symbol': '$', 'unit': 'TRY'},
            {'id': 6, 'name': 'CAD', 'nameEn': 'CAD', 'buy': 24.050, 'sell': 24.250, 'change': 0.31, 'symbol': '$', 'unit': 'TRY'},
            {'id': 7, 'name': 'SAR', 'nameEn': 'SAR', 'buy': 9.100, 'sell': 9.200, 'change': 0.18, 'symbol': 'ر.س', 'unit': 'TRY'},
            {'id': 8, 'name': 'JPY', 'nameEn': 'JPY', 'buy': 0.226, 'sell': 0.230, 'change': 0.22, 'symbol': '¥', 'unit': 'TRY'},
            {'id': 9, 'name': 'KWD', 'nameEn': 'KWD', 'buy': 111.250, 'sell': 112.150, 'change': 0.45, 'symbol': 'KD', 'unit': 'TRY'},
            {'id': 10, 'name': 'USD/KG', 'nameEn': 'USD/KG', 'buy': 137.020, 'sell': 137.520, 'change': 0.55, 'symbol': '$', 'unit': 'TRY'},
            {'id': 11, 'name': 'EUR/KG', 'nameEn': 'EUR/KG', 'buy': 118.090, 'sell': 118.750, 'change': 0.68, 'symbol': '€', 'unit': 'TRY'}
        ]

rapidapi_service = RapidAPIService()