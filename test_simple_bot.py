#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест упрощенного Telegram бота
"""

from telegram_bot_simple import SimpleSteamRentalBot
from config import Config

def test_simple_bot():
    """Тест упрощенного бота"""
    print("🧪 Тест упрощенного Telegram бота...")
    print("=" * 50)
    
    # Тест 1: Конфигурация
    print("\n1️⃣ Тест конфигурации:")
    print(f"   TELEGRAM_TOKEN: {Config.TELEGRAM_TOKEN[:20] if Config.TELEGRAM_TOKEN else 'НЕ НАЙДЕН'}...")
    print(f"   TELEGRAM_ADMIN_ID: {Config.TELEGRAM_ADMIN_ID}")
    
    # Тест 2: Создание бота
    print("\n2️⃣ Тест создания бота:")
    try:
        bot = SimpleSteamRentalBot()
        print("   ✅ Бот создан успешно")
        print(f"   🔑 Token: {bot.token[:20] if bot.token else 'НЕ НАЙДЕН'}...")
        print(f"   👤 Admin ID: {bot.admin_id}")
    except Exception as e:
        print(f"   ❌ Ошибка создания бота: {e}")
        return
    
    # Тест 3: Настройка бота
    print("\n3️⃣ Тест настройки бота:")
    try:
        success = bot.setup()
        if success:
            print("   ✅ Бот настроен успешно")
            print("   ✅ Обработчики команд добавлены")
        else:
            print("   ❌ Не удалось настроить бота")
            return
    except Exception as e:
        print(f"   ❌ Ошибка настройки бота: {e}")
        return
    
    # Тест 4: Проверка базы данных
    print("\n4️⃣ Тест базы данных:")
    try:
        total_accounts = bot.db.get_total_accounts()
        available_accounts = bot.db.get_available_accounts()
        active_rentals = bot.db.get_active_rentals()
        
        print(f"   📊 Всего аккаунтов: {total_accounts}")
        print(f"   🟢 Доступно: {available_accounts}")
        print(f"   🔴 В аренде: {active_rentals}")
        print("   ✅ База данных работает")
    except Exception as e:
        print(f"   ❌ Ошибка базы данных: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Тест упрощенного бота завершен!")
    print("\n📋 Рекомендации:")
    print("   • Перезапустите приложение в Railway")
    print("   • Проверьте Telegram бота командой /start")
    print("   • Используйте /admin для доступа к админ-панели")
    print("   • Бот должен работать без ошибок set_wakeup_fd")

if __name__ == '__main__':
    test_simple_bot()
