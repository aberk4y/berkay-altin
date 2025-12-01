import os
import requests
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY', '')
RAPIDAPI_HOST = "harem-altin-live-gold-price-data.p.rapidapi.com"

class HaremAPIService:
    def __init__(self):
        self.headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": RAPIDAPI_HOST
        }
        self.base_url = f"https://{RAPIDAPI_HOST}"
    
    def get_all_prices(self) -> Dict:
        """Fetch all gold and currency prices from Harem Altın API"""
        try:
            url = f"{self.base_url}/harem_altin/prices"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return self._format_prices(data.get('data', []))
                else:
                    logger.error(f"Harem API error: {data.get('message')}")
                    return self._get_fallback_data()
            else:
                logger.error(f"Harem API HTTP error: {response.status_code}")
                return self._get_fallback_data()
        except Exception as e:
            logger.error(f"Error fetching Harem prices: {str(e)}")
            return self._get_fallback_data()
    
    def _parse_turkish_number(self, value: str, is_percent: bool = False) -> float:
        """Parse Turkish formatted numbers (5.777,76 -> 5777.76)"""
        try:
            if not value or value == '':
                return 0.0
            
            # For percentages, API uses dot as decimal separator
            if is_percent:
                # Percent values like "34.72" or "0.50" - already in correct format
                return float(value)
            
            # For prices: Turkish format with dot as thousands separator and comma as decimal
            # Example: "5.777,76" -> 5777.76
            cleaned = value.replace('.', '').replace(',', '.')
            return float(cleaned)
        except:
            return 0.0
    
    def _format_prices(self, raw_data: List[Dict]) -> Dict:
        """Format Harem API data into gold and currency categories"""
        gold_items = []
        currency_items = []
        
        # Gold price mappings
        gold_mapping = {
            'Has Altın': ('HAS ALTIN', 'PURE GOLD'),
            'ONS': ('ONS', 'OUNCE'),
            'GRAM ALTIN': ('GRAM ALTIN', 'GRAM GOLD'),
            '22 AYAR': ('22 AYAR', '22 CARAT'),
            '14 AYAR': ('14 AYAR', '14 CARAT'),
            'ALTIN GÜMÜŞ': ('ALTIN GÜMÜŞ', 'GOLD SILVER'),
            'YENİ ÇEYREK': ('ÇEYREK ALTIN', 'QUARTER GOLD'),
            'YENİ YARIM': ('YARIM ALTIN', 'HALF GOLD'),
            'YENİ TAM': ('TAM ALTIN', 'FULL GOLD'),
            'YENİ ATA': ('ATA ALTIN', 'ATA GOLD'),
            'ESKİ ÇEYREK': ('ESKİ ÇEYREK', 'OLD QUARTER'),
            'ESKİ YARIM': ('ESKİ YARIM', 'OLD HALF'),
            'ESKİ TAM': ('ESKİ TAM', 'OLD FULL'),
            'ESKİ ATA': ('ESKİ ATA', 'OLD ATA')
        }
        
        # Currency mappings
        currency_mapping = {
            'USD/KG': ('USD/KG', 'USD/KG', '$'),
            'EUR/KG': ('EUR/KG', 'EUR/KG', '€')
        }
        
        gold_counter = 1
        currency_counter = 1
        
        for item in raw_data:
            key = item.get('key', '')
            buy = self._parse_turkish_number(item.get('buy', '0'))
            sell = self._parse_turkish_number(item.get('sell', '0'))
            percent = self._parse_turkish_number(item.get('percent', '0'))
            
            # Check if it's a gold item
            if key in gold_mapping:
                name_tr, name_en = gold_mapping[key]
                gold_items.append({
                    'id': gold_counter,
                    'name': name_tr,
                    'nameEn': name_en,
                    'buy': buy,
                    'sell': sell,
                    'change': percent,
                    'unit': 'TRY'
                })
                gold_counter += 1
            
            # Check if it's a currency item
            elif key in currency_mapping:
                name_tr, name_en, symbol = currency_mapping[key]
                currency_items.append({
                    'id': currency_counter,
                    'name': name_tr,
                    'nameEn': name_en,
                    'buy': buy,
                    'sell': sell,
                    'change': percent,
                    'symbol': symbol,
                    'unit': 'TRY'
                })
                currency_counter += 1
        
        # Add major currencies from free API
        try:
            currency_response = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
            if currency_response.status_code == 200:
                rates = currency_response.json().get('rates', {})
                try_rate = rates.get('TRY', 42.0)
                
                currencies = [
                    ('USD', 'USD', '$', 1.0),
                    ('EUR', 'EUR', '€', rates.get('EUR', 0.92)),
                    ('GBP', 'GBP', '£', rates.get('GBP', 0.79)),
                    ('CHF', 'CHF', 'Fr', rates.get('CHF', 0.88)),
                    ('AUD', 'AUD', '$', rates.get('AUD', 1.54)),
                    ('CAD', 'CAD', '$', rates.get('CAD', 1.41)),
                    ('SAR', 'SAR', 'ر.س', rates.get('SAR', 3.75)),
                    ('JPY', 'JPY', '¥', rates.get('JPY', 151.0)),
                    ('KWD', 'KWD', 'KD', rates.get('KWD', 0.31))
                ]
                
                for code, name, symbol, usd_rate in currencies:
                    if code == 'USD':
                        try_buy = try_rate * 0.995
                        try_sell = try_rate * 1.005
                    else:
                        usd_per_currency = 1 / usd_rate if usd_rate > 0 else 1
                        try_buy = (usd_per_currency * try_rate) * 0.995
                        try_sell = (usd_per_currency * try_rate) * 1.005
                    
                    change = round((try_rate - 42.0) / 42.0 * 100, 2)
                    
                    currency_items.append({
                        'id': currency_counter,
                        'name': code,
                        'nameEn': code,
                        'buy': round(try_buy, 2),
                        'sell': round(try_sell, 2),
                        'change': change,
                        'symbol': symbol,
                        'unit': 'TRY'
                    })
                    currency_counter += 1
        except:
            pass
        
        return {
            'gold': gold_items[:10],  # Return top 10
            'currency': currency_items[:11]  # Return top 11
        }
    
    def _get_fallback_data(self) -> Dict:
        """Fallback data if API fails"""
        return {
            'gold': [
                {'id': 1, 'name': 'HAS ALTIN', 'nameEn': 'PURE GOLD', 'buy': 5807.50, 'sell': 5858.70, 'change': 0.74, 'unit': 'TRY'},
                {'id': 2, 'name': 'ONS', 'nameEn': 'OUNCE', 'buy': 4239.5, 'sell': 4239.9, 'change': 0.53, 'unit': 'TRY'},
                {'id': 3, 'name': 'ÇEYREK ALTIN', 'nameEn': 'QUARTER GOLD', 'buy': 2389.0, 'sell': 2398.0, 'change': 0.68, 'unit': 'TRY'},
                {'id': 4, 'name': 'YARIM ALTIN', 'nameEn': 'HALF GOLD', 'buy': 4779.0, 'sell': 4796.0, 'change': 0.72, 'unit': 'TRY'},
                {'id': 5, 'name': 'TAM ALTIN', 'nameEn': 'FULL GOLD', 'buy': 9558.0, 'sell': 9592.0, 'change': 0.75, 'unit': 'TRY'},
                {'id': 6, 'name': '22 AYAR', 'nameEn': '22 CARAT', 'buy': 5282.82, 'sell': 5545.77, 'change': 4.83, 'unit': 'TRY'},
                {'id': 7, 'name': 'GRAM ALTIN', 'nameEn': 'GRAM GOLD', 'buy': 5778.46, 'sell': 5876.28, 'change': 1.55, 'unit': 'TRY'},
                {'id': 8, 'name': 'ALTIN GÜMÜŞ', 'nameEn': 'GOLD SILVER', 'buy': 70.66, 'sell': 73.63, 'change': 0.59, 'unit': 'TRY'},
                {'id': 9, 'name': 'ESKİ ÇEYREK', 'nameEn': 'OLD QUARTER', 'buy': 9320.0, 'sell': 9493.0, 'change': 0.82, 'unit': 'TRY'},
                {'id': 10, 'name': 'ATA ALTIN', 'nameEn': 'ATA GOLD', 'buy': 9612.0, 'sell': 9652.0, 'change': 0.78, 'unit': 'TRY'}
            ],
            'currency': [
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
        }

harem_api_service = HaremAPIService()
