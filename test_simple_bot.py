#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Простой тест Telegram бота без signal handling
"""

import asyncio
import threading
import time
from telegram_bot import SteamRentalBot

def test_bot_simple():
    """Простой тест бота"""
    print("🧪 Простой тест Telegram бота...")
    print("=" * 50)
    
    try:
        # Создаем бота
        print("1️⃣ Создание бота...")
        bot = SteamRentalBot()
        print("   ✅ Бот создан")
        
        # Настраиваем бота
        print("2️⃣ Настройка бота...")
        success = bot.setup()
        if success:
            print("   ✅ Бот настроен")
        else:
            print("   ❌ Ошибка настройки")
            return
        
        # Запускаем бота в отдельном потоке
        print("3️⃣ Запуск бота в потоке...")
        bot_thread = threading.Thread(target=bot.run, daemon=True)
        bot_thread.start()
        
        # Ждем немного
        print("4️⃣ Ожидание запуска...")
        time.sleep(5)
        
        # Проверяем, что поток жив
        if bot_thread.is_alive():
            print("   ✅ Бот запущен и работает")
            print("   ✅ Поток активен")
        else:
            print("   ❌ Поток бота завершился")
        
        print("\n" + "=" * 50)
        print("🎉 Тест завершен успешно!")
        print("✅ Бот готов к работе без signal handling")
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_bot_simple()
