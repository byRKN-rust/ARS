#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для отладки конфигурации
"""

import os
from config import Config

def debug_config():
    """Отладка конфигурации"""
    print("🔍 Отладка конфигурации...")
    print("=" * 50)
    
    # Проверяем переменные окружения напрямую
    print("📋 Переменные окружения:")
    print(f"TELEGRAM_TOKEN (env): {os.getenv('TELEGRAM_TOKEN', 'НЕ НАЙДЕН')}")
    print(f"TELEGRAM_ADMIN_ID (env): {os.getenv('TELEGRAM_ADMIN_ID', 'НЕ НАЙДЕН')}")
    print(f"FUNPAY_LOGIN (env): {os.getenv('FUNPAY_LOGIN', 'НЕ НАЙДЕН')}")
    print(f"FUNPAY_PASSWORD (env): {os.getenv('FUNPAY_PASSWORD', 'НЕ НАЙДЕН')}")
    
    print("\n📋 Значения из Config:")
    print(f"TELEGRAM_TOKEN (config): {Config.TELEGRAM_TOKEN}")
    print(f"TELEGRAM_ADMIN_ID (config): {Config.TELEGRAM_ADMIN_ID}")
    print(f"FUNPAY_LOGIN (config): {Config.FUNPAY_LOGIN}")
    print(f"FUNPAY_PASSWORD (config): {Config.FUNPAY_PASSWORD}")
    
    print("\n🔧 Проверка работоспособности:")
    
    # Проверяем токен
    if Config.TELEGRAM_TOKEN and Config.TELEGRAM_TOKEN != '':
        print("✅ TELEGRAM_TOKEN настроен")
        print(f"   Токен: {Config.TELEGRAM_TOKEN[:20]}...")
    else:
        print("❌ TELEGRAM_TOKEN не настроен")
    
    # Проверяем admin ID
    if Config.TELEGRAM_ADMIN_ID and Config.TELEGRAM_ADMIN_ID != '':
        print("✅ TELEGRAM_ADMIN_ID настроен")
        print(f"   Admin ID: {Config.TELEGRAM_ADMIN_ID}")
    else:
        print("❌ TELEGRAM_ADMIN_ID не настроен")
    
    # Проверяем FunPay
    if Config.FUNPAY_LOGIN and Config.FUNPAY_LOGIN != '':
        print("✅ FUNPAY_LOGIN настроен")
    else:
        print("❌ FUNPAY_LOGIN не настроен")
    
    if Config.FUNPAY_PASSWORD and Config.FUNPAY_PASSWORD != '':
        print("✅ FUNPAY_PASSWORD настроен")
    else:
        print("❌ FUNPAY_PASSWORD не настроен")
    
    print("\n📊 Рекомендации:")
    
    if not Config.TELEGRAM_TOKEN or Config.TELEGRAM_TOKEN == '':
        print("⚠️ TELEGRAM_TOKEN не найден в переменных окружения")
        print("   Используется значение по умолчанию из config.py")
    
    if not Config.TELEGRAM_ADMIN_ID or Config.TELEGRAM_ADMIN_ID == '':
        print("⚠️ TELEGRAM_ADMIN_ID не найден в переменных окружения")
        print("   Используется значение по умолчанию из config.py")

if __name__ == '__main__':
    debug_config()
