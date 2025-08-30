#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Упрощенный Telegram бот для системы аренды Steam аккаунтов
Без signal handling для решения проблем в Railway
"""

import logging
import asyncio
import os
import sys
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import Config
from database import Database

class SimpleSteamRentalBot:
    def __init__(self):
        self.token = Config.TELEGRAM_TOKEN
        self.admin_id = Config.TELEGRAM_ADMIN_ID
        self.db = Database()
        self.application = None
        
        # Настройка логирования
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(__name__)
        
    def setup(self):
        """Настройка бота"""
        self.logger.info(f"🔧 Настройка Telegram бота...")
        self.logger.info(f"🔑 Token: {self.token[:20] if self.token else 'НЕ НАЙДЕН'}...")
        self.logger.info(f"👤 Admin ID: {self.admin_id}")
        
        if not self.token:
            self.logger.error("❌ TELEGRAM_TOKEN не настроен!")
            return False
            
        try:
            self.application = Application.builder().token(self.token).build()
            
            # Добавляем обработчики команд
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("accounts", self.accounts_command))
            self.application.add_handler(CommandHandler("rentals", self.rentals_command))
            self.application.add_handler(CommandHandler("support", self.support_command))
            self.application.add_handler(CommandHandler("admin", self.admin_command))
            
            # Обработчик для inline кнопок
            self.application.add_handler(CallbackQueryHandler(self.button_callback))
            
            self.logger.info("✅ Telegram бот настроен успешно")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка настройки бота: {e}")
            return False
    
    def run(self):
        """Запуск бота без signal handling"""
        if not self.application:
            self.logger.error("❌ Бот не настроен!")
            return
            
        try:
            self.logger.info("🚀 Запуск Telegram бота...")
            
            # Полностью отключаем signal handling
            import signal
            
            # Отключаем все signal handling
            if hasattr(signal, 'set_wakeup_fd'):
                try:
                    signal.set_wakeup_fd(-1)
                except (ValueError, OSError):
                    pass
            
            # Отключаем обработчики сигналов
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            
            # Создаем новый event loop для этого потока
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Запускаем бота с минимальными настройками
            self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,
                close_loop=False
            )
        except Exception as e:
            self.logger.error(f"❌ Ошибка запуска бота: {e}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        
        # Добавляем пользователя в базу данных
        self.db.add_user(
            telegram_id=str(user.id),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        welcome_text = f"""
🎮 Добро пожаловать в Steam Rental System!

Привет, {user.first_name}! 👋

Я помогу вам арендовать аккаунты Steam для игр.

📋 Доступные команды:
/accounts - Показать доступные аккаунты
/rentals - Ваши активные аренды
/status - Статус системы
/support - Поддержка
/help - Справка

💡 Для начала работы выберите команду или используйте кнопки ниже.
        """
        
        keyboard = [
            [InlineKeyboardButton("📋 Аккаунты", callback_data="show_accounts")],
            [InlineKeyboardButton("📋 Мои аренды", callback_data="show_rentals")],
            [InlineKeyboardButton("📊 Статус", callback_data="show_status")],
            [InlineKeyboardButton("❓ Помощь", callback_data="show_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
❓ Справка по использованию бота

📋 Основные команды:
/start - Главное меню
/accounts - Показать доступные аккаунты
/rentals - Ваши активные аренды
/status - Статус системы
/support - Связаться с поддержкой

🔧 Как арендовать аккаунт:
1. Используйте команду /accounts
2. Выберите подходящий аккаунт
3. Укажите время аренды
4. Оплатите услугу
5. Получите данные аккаунта

⚠️ Важно:
• Время аренды отсчитывается с момента получения данных
• После окончания аренды пароль автоматически изменяется
• Используйте аккаунт только для игр
• Не изменяйте настройки аккаунта

📞 Поддержка: /support
        """
        await update.message.reply_text(help_text)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status"""
        try:
            # Получаем статистику из базы данных
            total_accounts = self.db.get_total_accounts()
            available_accounts = self.db.get_available_accounts()
            active_rentals = self.db.get_active_rentals()
            
            status_text = f"""
📊 Статус системы

✅ Система работает
🕐 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 Статистика:
• Всего аккаунтов: {total_accounts}
• Доступно для аренды: {available_accounts}
• Активных аренд: {active_rentals}

🔧 Система мониторинга активна
            """
                
        except Exception as e:
            status_text = f"""
❌ Ошибка получения статуса: {e}

Попробуйте позже или обратитесь в поддержку: /support
            """
        
        await update.message.reply_text(status_text)
    
    async def accounts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /accounts"""
        try:
            accounts = self.db.get_available_accounts_list()
            
            if not accounts:
                await update.message.reply_text("❌ Нет доступных аккаунтов в данный момент.")
                return
            
            text = "📋 Доступные аккаунты:\n\n"
            keyboard = []
            
            for i, account in enumerate(accounts[:10]):  # Показываем максимум 10
                text += f"🎮 Аккаунт #{account['id']}\n"
                text += f"📝 Описание: {account.get('description', 'Нет описания')}\n"
                text += f"💰 Цена: {account.get('price', 'Не указана')} руб/час\n\n"
                
                keyboard.append([InlineKeyboardButton(
                    f"Арендовать #{account['id']}", 
                    callback_data=f"rent_account_{account['id']}"
                )])
            
            if len(accounts) > 10:
                text += f"... и еще {len(accounts) - 10} аккаунтов"
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(text, reply_markup=reply_markup)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка получения аккаунтов: {e}")
    
    async def rentals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /rentals"""
        user_id = update.effective_user.id
        
        try:
            rentals = self.db.get_user_rentals(user_id)
            
            if not rentals:
                await update.message.reply_text("📭 У вас нет активных аренд.")
                return
            
            text = "📋 Ваши активные аренды:\n\n"
            
            for rental in rentals:
                end_time = datetime.fromisoformat(rental['end_time'])
                remaining = end_time - datetime.now()
                
                if remaining.total_seconds() > 0:
                    hours = int(remaining.total_seconds() // 3600)
                    minutes = int((remaining.total_seconds() % 3600) // 60)
                    
                    text += f"🎮 Аккаунт #{rental['account_id']}\n"
                    text += f"⏰ Осталось: {hours}ч {minutes}м\n"
                    text += f"🕐 Завершение: {end_time.strftime('%Y-%m-%d %H:%M')}\n\n"
                else:
                    text += f"🎮 Аккаунт #{rental['account_id']} - Истек\n\n"
            
            await update.message.reply_text(text)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка получения аренд: {e}")
    
    async def support_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /support"""
        support_text = """
📞 Поддержка

Если у вас возникли вопросы или проблемы:

👨‍💼 Администратор: @admin
📧 Email: support@steamrental.com
💬 Чат: @steamrental_support

⏰ Время работы: 24/7

🔧 Часто задаваемые вопросы:
• Как работает аренда? - Время отсчитывается с момента получения данных
• Что после окончания? - Пароль автоматически изменяется
• Можно ли продлить? - Да, оплатив дополнительное время
• Безопасно ли? - Да, все аккаунты проверены
        """
        await update.message.reply_text(support_text)
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /admin"""
        user_id = update.effective_user.id
        
        if str(user_id) != self.admin_id:
            await update.message.reply_text("❌ У вас нет доступа к админ-панели.")
            return
        
        admin_text = """
🔧 Админ-панель

📊 Быстрая статистика:
        """
        
        try:
            total_accounts = self.db.get_total_accounts()
            available_accounts = self.db.get_available_accounts()
            active_rentals = self.db.get_active_rentals()
            total_users = self.db.get_total_users()
            
            admin_text += f"""
• Всего аккаунтов: {total_accounts}
• Доступно: {available_accounts}
• Активных аренд: {active_rentals}
• Пользователей: {total_users}
            """
        except Exception as e:
            admin_text += f"\n❌ Ошибка получения статистики: {e}"
        
        keyboard = [
            [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("👥 Пользователи", callback_data="admin_users")],
            [InlineKeyboardButton("🎮 Аккаунты", callback_data="admin_accounts")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(admin_text, reply_markup=reply_markup)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "show_accounts":
            await self.accounts_command(update, context)
        elif data == "show_status":
            await self.status_command(update, context)
        elif data == "show_help":
            await self.help_command(update, context)
        elif data == "show_rentals":
            await self.rentals_command(update, context)
        elif data.startswith("rent_account_"):
            account_id = data.split("_")[2]
            await self.handle_rent_request(update, context, account_id)
        elif data.startswith("rent_time_"):
            parts = data.split("_")
            account_id = parts[2]
            duration = int(parts[3])
            await self.handle_rent_confirmation(update, context, account_id, duration)
        elif data == "admin_stats":
            await self.admin_stats(update, context)
        elif data == "admin_users":
            await self.admin_users(update, context)
        elif data == "admin_accounts":
            await self.admin_accounts(update, context)
        elif data == "admin_back":
            await self.admin_command(update, context)
    
    async def handle_rent_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE, account_id: str):
        """Обработка запроса на аренду"""
        try:
            account = self.db.get_account(account_id)
            if not account:
                await update.callback_query.edit_message_text("❌ Аккаунт не найден.")
                return
            
            text = f"""
🎮 Аренда аккаунта #{account_id}

📝 Описание: {account.get('description', 'Нет описания')}
💰 Цена: {account.get('price', 'Не указана')} руб/час

⏰ Выберите время аренды:
            """
            
            keyboard = [
                [InlineKeyboardButton("1 час", callback_data=f"rent_time_{account_id}_1")],
                [InlineKeyboardButton("3 часа", callback_data=f"rent_time_{account_id}_3")],
                [InlineKeyboardButton("6 часов", callback_data=f"rent_time_{account_id}_6")],
                [InlineKeyboardButton("12 часов", callback_data=f"rent_time_{account_id}_12")],
                [InlineKeyboardButton("24 часа", callback_data=f"rent_time_{account_id}_24")],
                [InlineKeyboardButton("« Назад", callback_data="show_accounts")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
            
        except Exception as e:
            await update.callback_query.edit_message_text(f"❌ Ошибка: {e}")
    
    async def handle_rent_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, account_id: str, duration: int):
        """Обработка подтверждения аренды"""
        user_id = update.effective_user.id
        
        try:
            account = self.db.get_account(account_id)
            if not account:
                await update.callback_query.edit_message_text("❌ Аккаунт не найден.")
                return
            
            # Создаем аренду
            success = self.db.create_rental(int(account_id), str(user_id), duration)
            
            if success:
                total_cost = duration * account.get('price', 50)
                
                text = f"""
✅ Аренда успешно создана!

🎮 Аккаунт: #{account_id}
📝 Игра: {account['game_name']}
⏰ Время: {duration} часов
💰 Стоимость: {total_cost} руб

📋 Данные аккаунта:
👤 Логин: {account['username']}
🔑 Пароль: (будет отправлен отдельно)

⚠️ Важно:
• Не меняйте пароль от аккаунта
• Не добавляйте друзей
• Используйте аккаунт только для игр

⏰ Время аренды истекает через {duration} часов
                """
                
                keyboard = [
                    [InlineKeyboardButton("📋 Мои аренды", callback_data="show_rentals")],
                    [InlineKeyboardButton("🎮 Еще аккаунты", callback_data="show_accounts")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
            else:
                await update.callback_query.edit_message_text("❌ Не удалось создать аренду. Аккаунт может быть уже занят.")
                
        except Exception as e:
            await update.callback_query.edit_message_text(f"❌ Ошибка создания аренды: {e}")
    
    async def admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать детальную статистику для админа"""
        user_id = update.effective_user.id
        
        if str(user_id) != self.admin_id:
            return
        
        try:
            stats = self.db.get_detailed_stats()
            
            text = """
📊 Детальная статистика

🎮 Аккаунты:
• Всего: {total_accounts}
• Доступно: {available_accounts}
• В аренде: {rented_accounts}
• Заблокированы: {blocked_accounts}

📈 Аренды:
• Активных: {active_rentals}
• Завершенных сегодня: {completed_today}
• Общий доход: {total_revenue} руб

👥 Пользователи:
• Всего: {total_users}
• Активных сегодня: {active_users_today}
• Новых сегодня: {new_users_today}
            """.format(**stats)
            
        except Exception as e:
            text = f"❌ Ошибка получения статистики: {e}"
        
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    
    async def admin_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать список пользователей для админа"""
        user_id = update.effective_user.id
        
        if str(user_id) != self.admin_id:
            return
        
        try:
            users = self.db.get_users_list()
            
            text = "👥 Список пользователей:\n\n"
            
            for user in users[:10]:  # Показываем первые 10
                text += f"👤 ID: {user['user_id']}\n"
                text += f"📅 Регистрация: {user['created_at']}\n"
                text += f"🎮 Аренд: {user['rentals_count']}\n\n"
            
            if len(users) > 10:
                text += f"... и еще {len(users) - 10} пользователей"
            
        except Exception as e:
            text = f"❌ Ошибка получения пользователей: {e}"
        
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    
    async def admin_accounts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать управление аккаунтами для админа"""
        user_id = update.effective_user.id
        
        if str(user_id) != self.admin_id:
            return
        
        try:
            accounts = self.db.get_all_accounts()
            
            if not accounts:
                text = "📭 Нет аккаунтов в системе."
            else:
                text = "📋 Список всех аккаунтов:\n\n"
                
                for account in accounts[:10]:  # Показываем первые 10
                    status = "🔴 В аренде" if account['is_rented'] else "🟢 Свободен"
                    text += f"🎮 #{account['id']} - {account['username']}\n"
                    text += f"📝 Игра: {account['game_name']}\n"
                    text += f"📊 Статус: {status}\n"
                    text += f"📅 Создан: {account['created_at']}\n\n"
                
                if len(accounts) > 10:
                    text += f"... и еще {len(accounts) - 10} аккаунтов"
            
        except Exception as e:
            text = f"❌ Ошибка получения аккаунтов: {e}"
        
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
