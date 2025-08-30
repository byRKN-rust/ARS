import time
import random
import requests
from bs4 import BeautifulSoup
from config import Config
import logging

class FunPayManager:
    def __init__(self):
        self.base_url = Config.FUNPAY_BASE_URL
        self.login = Config.FUNPAY_LOGIN
        self.password = Config.FUNPAY_PASSWORD
        self.session = requests.Session()
        self.is_logged_in = False
        
        # Настройка логирования
        self.logger = logging.getLogger(__name__)
        
        # Настройка сессии
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def login_to_funpay(self):
        """Вход в аккаунт FunPay через API"""
        try:
            self.logger.info("🔐 Попытка входа в FunPay...")
            
            # Получаем страницу входа для получения CSRF токена
            login_page = self.session.get(f"{self.base_url}/account/login")
            soup = BeautifulSoup(login_page.content, 'html.parser')
            
            # Ищем CSRF токен
            csrf_token = None
            csrf_input = soup.find('input', {'name': '_token'})
            if csrf_input:
                csrf_token = csrf_input.get('value')
            
            if not csrf_token:
                self.logger.warning("⚠️ CSRF токен не найден, продолжаем без него")
            
            # Данные для входа
            login_data = {
                'login': self.login,
                'password': self.password,
            }
            
            if csrf_token:
                login_data['_token'] = csrf_token
            
            # Выполняем вход
            response = self.session.post(
                f"{self.base_url}/account/login",
                data=login_data,
                allow_redirects=True
            )
            
            # Проверяем успешность входа
            if response.status_code == 200:
                # Проверяем, что мы на странице аккаунта
                if 'account' in response.url or 'profile' in response.url:
                    self.is_logged_in = True
                    self.logger.info("✅ Успешный вход в FunPay")
                    return True
                else:
                    # Проверяем наличие элементов, указывающих на успешный вход
                    soup = BeautifulSoup(response.content, 'html.parser')
                    if soup.find('a', {'href': '/account/logout'}) or soup.find('div', {'class': 'user-menu'}):
                        self.is_logged_in = True
                        self.logger.info("✅ Успешный вход в FunPay (по элементам страницы)")
                        return True
            
            self.logger.error("❌ Не удалось войти в FunPay")
            return False
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка при входе в FunPay: {e}")
            return False
    
    def get_orders(self):
        """Получение списка заказов"""
        try:
            if not self.is_logged_in:
                if not self.login_to_funpay():
                    return []
            
            self.logger.info("📋 Получение списка заказов...")
            
            response = self.session.get(f"{self.base_url}/account/orders")
            if response.status_code != 200:
                self.logger.error(f"❌ Ошибка получения заказов: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            orders = []
            
            # Ищем заказы на странице (адаптируйте селекторы под реальную структуру)
            order_elements = soup.find_all('div', {'class': 'order-item'})
            
            for order_elem in order_elements:
                try:
                    order = {
                        'id': order_elem.get('data-order-id', ''),
                        'title': order_elem.find('h3').text.strip() if order_elem.find('h3') else '',
                        'status': order_elem.find('span', {'class': 'status'}).text.strip() if order_elem.find('span', {'class': 'status'}) else '',
                        'price': order_elem.find('span', {'class': 'price'}).text.strip() if order_elem.find('span', {'class': 'price'}) else '',
                        'created_at': order_elem.find('span', {'class': 'date'}).text.strip() if order_elem.find('span', {'class': 'date'}) else ''
                    }
                    orders.append(order)
                except Exception as e:
                    self.logger.warning(f"⚠️ Ошибка парсинга заказа: {e}")
                    continue
            
            self.logger.info(f"✅ Получено {len(orders)} заказов")
            return orders
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения заказов: {e}")
            return []
    
    def get_reviews(self):
        """Получение списка отзывов"""
        try:
            if not self.is_logged_in:
                if not self.login_to_funpay():
                    return []
            
            self.logger.info("⭐ Получение списка отзывов...")
            
            response = self.session.get(f"{self.base_url}/account/reviews")
            if response.status_code != 200:
                self.logger.error(f"❌ Ошибка получения отзывов: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            reviews = []
            
            # Ищем отзывы на странице (адаптируйте селекторы под реальную структуру)
            review_elements = soup.find_all('div', {'class': 'review-item'})
            
            for review_elem in review_elements:
                try:
                    review = {
                        'id': review_elem.get('data-review-id', ''),
                        'author': review_elem.find('span', {'class': 'author'}).text.strip() if review_elem.find('span', {'class': 'author'}) else '',
                        'rating': review_elem.find('span', {'class': 'rating'}).text.strip() if review_elem.find('span', {'class': 'rating'}) else '',
                        'text': review_elem.find('div', {'class': 'text'}).text.strip() if review_elem.find('div', {'class': 'text'}) else '',
                        'created_at': review_elem.find('span', {'class': 'date'}).text.strip() if review_elem.find('span', {'class': 'date'}) else ''
                    }
                    reviews.append(review)
                except Exception as e:
                    self.logger.warning(f"⚠️ Ошибка парсинга отзыва: {e}")
                    continue
            
            self.logger.info(f"✅ Получено {len(reviews)} отзывов")
            return reviews
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения отзывов: {e}")
            return []
    
    def create_rental_listing(self, game_name: str, price_per_hour: float, account_id: str = None):
        """
        Создание объявления на FunPay для аренды аккаунта
        """
        try:
            if not self.is_logged_in:
                if not self.login_to_funpay():
                    return None
            
            self.logger.info(f"📝 Создание объявления для игры: {game_name}")
            
            # Получаем страницу создания объявления
            response = self.session.get(f"{self.base_url}/account/sells/add")
            if response.status_code != 200:
                self.logger.error(f"❌ Ошибка получения страницы создания объявления: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ищем CSRF токен
            csrf_token = None
            csrf_input = soup.find('input', {'name': '_token'})
            if csrf_input:
                csrf_token = csrf_input.get('value')
            
            # Данные для создания объявления
            listing_data = {
                'title': f'Аренда аккаунта {game_name}',
                'description': f'Аренда аккаунта Steam для игры {game_name}. Цена: {price_per_hour} руб/час.',
                'price': price_per_hour,
                'category': 'steam-accounts',
                'game': game_name,
            }
            
            if csrf_token:
                listing_data['_token'] = csrf_token
            
            # Создаем объявление
            response = self.session.post(
                f"{self.base_url}/account/sells/add",
                data=listing_data,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                self.logger.info("✅ Объявление успешно создано")
                return {
                    'success': True,
                    'message': 'Объявление создано успешно',
                    'listing_id': 'auto_generated'  # В реальной системе нужно получить ID
                }
            else:
                self.logger.error(f"❌ Ошибка создания объявления: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка создания объявления: {e}")
            return None
    
    def update_listing(self, listing_id: str, new_data: dict):
        """Обновление объявления"""
        try:
            if not self.is_logged_in:
                if not self.login_to_funpay():
                    return False
            
            self.logger.info(f"🔄 Обновление объявления {listing_id}")
            
            # Получаем страницу редактирования
            response = self.session.get(f"{self.base_url}/account/sells/edit/{listing_id}")
            if response.status_code != 200:
                self.logger.error(f"❌ Ошибка получения страницы редактирования: {response.status_code}")
                return False
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ищем CSRF токен
            csrf_token = None
            csrf_input = soup.find('input', {'name': '_token'})
            if csrf_input:
                csrf_token = csrf_input.get('value')
            
            # Добавляем CSRF токен к данным
            if csrf_token:
                new_data['_token'] = csrf_token
            
            # Обновляем объявление
            response = self.session.post(
                f"{self.base_url}/account/sells/edit/{listing_id}",
                data=new_data,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                self.logger.info("✅ Объявление успешно обновлено")
                return True
            else:
                self.logger.error(f"❌ Ошибка обновления объявления: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка обновления объявления: {e}")
            return False
    
    def delete_listing(self, listing_id: str):
        """Удаление объявления"""
        try:
            if not self.is_logged_in:
                if not self.login_to_funpay():
                    return False
            
            self.logger.info(f"🗑️ Удаление объявления {listing_id}")
            
            # Получаем страницу удаления
            response = self.session.get(f"{self.base_url}/account/sells/delete/{listing_id}")
            if response.status_code != 200:
                self.logger.error(f"❌ Ошибка получения страницы удаления: {response.status_code}")
                return False
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ищем CSRF токен
            csrf_token = None
            csrf_input = soup.find('input', {'name': '_token'})
            if csrf_input:
                csrf_token = csrf_input.get('value')
            
            # Данные для удаления
            delete_data = {}
            if csrf_token:
                delete_data['_token'] = csrf_token
            
            # Удаляем объявление
            response = self.session.post(
                f"{self.base_url}/account/sells/delete/{listing_id}",
                data=delete_data,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                self.logger.info("✅ Объявление успешно удалено")
                return True
            else:
                self.logger.error(f"❌ Ошибка удаления объявления: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка удаления объявления: {e}")
            return False
    
    def sync_with_funpay(self):
        """Синхронизация с FunPay"""
        try:
            self.logger.info("🔄 Синхронизация с FunPay...")
            
            # Получаем заказы
            orders = self.get_orders()
            
            # Получаем отзывы
            reviews = self.get_reviews()
            
            self.logger.info(f"✅ Синхронизация завершена. Заказов: {len(orders)}, отзывов: {len(reviews)}")
            
            return {
                'orders': orders,
                'reviews': reviews,
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка синхронизации с FunPay: {e}")
            return {
                'orders': [],
                'reviews': [],
                'success': False,
                'error': str(e)
            }
    
    def close(self):
        """Закрытие сессии"""
        try:
            self.session.close()
            self.logger.info("🔒 Сессия FunPay закрыта")
        except Exception as e:
            self.logger.error(f"❌ Ошибка закрытия сессии: {e}")
