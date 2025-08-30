#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отдельный модуль для запуска Telegram бота
"""

import asyncio
import signal
import sys
import os
from telegram_bot import SteamRentalBot

def run_bot():
    """Запуск бота с правильной обработкой сигналов"""
    try:
        # Создаем бота
        bot = SteamRentalBot()
        
        # Настраиваем бота
        if not bot.setup():
            print("❌ Не удалось настроить бота")
            return
        
        print("✅ Бот настроен успешно")
        
        # Отключаем signal handling для этого процесса
        if hasattr(signal, 'set_wakeup_fd'):
            try:
                signal.set_wakeup_fd(-1)
            except (ValueError, OSError):
                pass
        
        # Запускаем бота
        print("🚀 Запуск бота...")
        bot.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")

if __name__ == '__main__':
    run_bot()
