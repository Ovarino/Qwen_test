"""
Backend сервер для управления биореактором через REST API.
Использует Flask для создания API endpoints.
"""

from flask import Flask, jsonify, request
from datetime import datetime
import threading
import random

app = Flask(__name__)

# Состояние биореактора (в реальном приложении это было бы подключено к оборудованию)
reactor_state = {
    "temperature": 37.0,        # °C
    "ph": 7.0,                  # pH уровень
    "dissolved_oxygen": 100.0,  # % насыщения кислородом
    "stirrer_speed": 200,       # об/мин
    "pump_a_rate": 0.0,         # мл/мин
    "pump_b_rate": 0.0,         # мл/мин
    "culture_volume": 1000.0,   # мл
    "optical_density": 0.1,     # OD600
    "status": "stopped",        # stopped, running, paused
    "start_time": None,
    "elapsed_time": 0           # секунд
}

# История параметров для графиков
history = {
    "temperature": [],
    "ph": [],
    "dissolved_oxygen": [],
    "optical_density": []
}

timer = None

def simulate_reactor():
    """Симуляция изменений параметров биореактора"""
    global reactor_state
    
    if reactor_state["status"] == "running":
        # Симуляция роста культуры
        reactor_state["elapsed_time"] += 1
        
        # Небольшие случайные колебания параметров
        reactor_state["temperature"] += random.uniform(-0.1, 0.1)
        reactor_state["temperature"] = max(30.0, min(45.0, reactor_state["temperature"]))
        
        reactor_state["ph"] += random.uniform(-0.05, 0.05)
        reactor_state["ph"] = max(6.0, min(8.0, reactor_state["ph"]))
        
        reactor_state["dissolved_oxygen"] += random.uniform(-1.0, 1.0)
        reactor_state["dissolved_oxygen"] = max(0.0, min(100.0, reactor_state["dissolved_oxygen"]))
        
        # Рост оптической плотности (имитация роста микроорганизмов)
        if reactor_state["elapsed_time"] > 10:
            reactor_state["optical_density"] *= 1.001
            reactor_state["optical_density"] = min(10.0, reactor_state["optical_density"])
        
        # Добавление в историю (каждые 5 секунд)
        if reactor_state["elapsed_time"] % 5 == 0:
            timestamp = datetime.now().isoformat()
            for key in history.keys():
                history[key].append({"time": timestamp, "value": reactor_state[key]})
                # Храним последние 100 значений
                if len(history[key]) > 100:
                    history[key].pop(0)
    
    # Планируем следующий вызов через 1 секунду
    global timer
    timer = threading.Timer(1.0, simulate_reactor)
    timer.daemon = True
    timer.start()

@app.route('/api/status', methods=['GET'])
def get_status():
    """Получить текущее состояние биореактора"""
    return jsonify({
        "success": True,
        "data": reactor_state
    })

@app.route('/api/history/<parameter>', methods=['GET'])
def get_history(parameter):
    """Получить историю параметра"""
    if parameter in history:
        return jsonify({
            "success": True,
            "data": history[parameter]
        })
    return jsonify({
        "success": False,
        "error": "Parameter not found"
    }), 404

@app.route('/api/control/start', methods=['POST'])
def start_cultivation():
    """Запустить культивирование"""
    if reactor_state["status"] == "stopped":
        reactor_state["status"] = "running"
        reactor_state["start_time"] = datetime.now().isoformat()
        reactor_state["elapsed_time"] = 0
        # Очистка истории
        for key in history.keys():
            history[key] = []
        return jsonify({
            "success": True,
            "message": "Культивирование запущено"
        })
    return jsonify({
        "success": False,
        "error": "Биореактор уже работает"
    }), 400

@app.route('/api/control/stop', methods=['POST'])
def stop_cultivation():
    """Остановить культивирование"""
    if reactor_state["status"] == "running":
        reactor_state["status"] = "stopped"
        return jsonify({
            "success": True,
            "message": "Культивирование остановлено"
        })
    return jsonify({
        "success": False,
        "error": "Биореактор не работает"
    }), 400

@app.route('/api/control/pause', methods=['POST'])
def pause_cultivation():
    """Поставить на паузу"""
    if reactor_state["status"] == "running":
        reactor_state["status"] = "paused"
        return jsonify({
            "success": True,
            "message": "Культивирование на паузе"
        })
    elif reactor_state["status"] == "paused":
        reactor_state["status"] = "running"
        return jsonify({
            "success": True,
            "message": "Культивирование возобновлено"
        })
    return jsonify({
        "success": False,
        "error": "Невозможно изменить статус"
    }), 400

@app.route('/api/settings/temperature', methods=['POST'])
def set_temperature():
    """Установить температуру"""
    data = request.get_json()
    temp = data.get('temperature')
    if temp and 20 <= temp <= 50:
        reactor_state["temperature"] = float(temp)
        return jsonify({
            "success": True,
            "message": f"Температура установлена: {temp}°C"
        })
    return jsonify({
        "success": False,
        "error": "Температура должна быть в диапазоне 20-50°C"
    }), 400

@app.route('/api/settings/ph', methods=['POST'])
def set_ph():
    """Установить целевой pH"""
    data = request.get_json()
    ph_value = data.get('ph')
    if ph_value and 5.0 <= ph_value <= 9.0:
        # В реальной системе здесь была бы установка целевого значения
        return jsonify({
            "success": True,
            "message": f"Целевой pH установлен: {ph_value}"
        })
    return jsonify({
        "success": False,
        "error": "pH должен быть в диапазоне 5.0-9.0"
    }), 400

@app.route('/api/settings/stirrer', methods=['POST'])
def set_stirrer():
    """Установить скорость мешалки"""
    data = request.get_json()
    speed = data.get('speed')
    if speed and 0 <= speed <= 1000:
        reactor_state["stirrer_speed"] = int(speed)
        return jsonify({
            "success": True,
            "message": f"Скорость мешалки: {speed} об/мин"
        })
    return jsonify({
        "success": False,
        "error": "Скорость должна быть 0-1000 об/мин"
    }), 400

@app.route('/api/settings/oxygen', methods=['POST'])
def set_oxygen():
    """Установить целевое содержание кислорода"""
    data = request.get_json()
    oxygen = data.get('oxygen')
    if oxygen and 0 <= oxygen <= 100:
        # В реальной системе здесь была бы установка целевого значения
        return jsonify({
            "success": True,
            "message": f"Целевой кислород: {oxygen}%"
        })
    return jsonify({
        "success": False,
        "error": "Кислород должен быть 0-100%"
    }), 400

@app.route('/api/pumps/a', methods=['POST'])
def control_pump_a():
    """Управление насосом A (например, кислота/щелочь)"""
    data = request.get_json()
    rate = data.get('rate')
    if rate is not None and 0 <= rate <= 100:
        reactor_state["pump_a_rate"] = float(rate)
        return jsonify({
            "success": True,
            "message": f"Насос A: {rate} мл/мин"
        })
    return jsonify({
        "success": False,
        "error": "Скорость насоса должна быть 0-100 мл/мин"
    }), 400

@app.route('/api/pumps/b', methods=['POST'])
def control_pump_b():
    """Управление насосом B (например, питательная среда)"""
    data = request.get_json()
    rate = data.get('rate')
    if rate is not None and 0 <= rate <= 100:
        reactor_state["pump_b_rate"] = float(rate)
        return jsonify({
            "success": True,
            "message": f"Насос B: {rate} мл/мин"
        })
    return jsonify({
        "success": False,
        "error": "Скорость насоса должна быть 0-100 мл/мин"
    }), 400

@app.route('/api/reset', methods=['POST'])
def reset_reactor():
    """Сбросить все параметры к начальным значениям"""
    global reactor_state
    reactor_state = {
        "temperature": 37.0,
        "ph": 7.0,
        "dissolved_oxygen": 100.0,
        "stirrer_speed": 200,
        "pump_a_rate": 0.0,
        "pump_b_rate": 0.0,
        "culture_volume": 1000.0,
        "optical_density": 0.1,
        "status": "stopped",
        "start_time": None,
        "elapsed_time": 0
    }
    for key in history.keys():
        history[key] = []
    return jsonify({
        "success": True,
        "message": "Параметры сброшены"
    })

if __name__ == '__main__':
    print("Запуск сервера биореактора на порту 5000...")
    # Запуск симуляции
    simulate_reactor()
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
