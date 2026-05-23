"""
GUI для оператора биореактора.
Использует CustomTkinter для современного интерфейса.
Связь с бэкендом через REST API.
"""

import customtkinter as ctk
import requests
import threading
import time
from datetime import timedelta

# Настройки внешнего вида
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class BioreactorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Биореактор - Панель Оператора")
        self.geometry("1200x800")
        
        # URL бэкенда
        self.backend_url = "http://localhost:5000/api"
        
        # Флаг для остановки обновления
        self.running = True
        
        # Создание основного интерфейса
        self.create_widgets()
        
        # Запуск потока для периодического обновления данных
        self.update_thread = threading.Thread(target=self.periodic_update, daemon=True)
        self.update_thread.start()
        
        # Обработка закрытия окна
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Создание всех виджетов интерфейса"""
        
        # === Верхняя панель с заголовком и статусом ===
        self.top_frame = ctk.CTkFrame(self, height=80)
        self.top_frame.pack(fill="x", padx=10, pady=10)
        
        self.title_label = ctk.CTkLabel(
            self.top_frame, 
            text="🧪 БИОРЕАКТОР - ПАНЕЛЬ ОПЕРАТОРА",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(side="left", padx=20, pady=20)
        
        self.status_frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        self.status_frame.pack(side="right", padx=20, pady=20)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Статус: НЕ АКТИВЕН",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="gray"
        )
        self.status_label.pack(side="left", padx=10)
        
        self.time_label = ctk.CTkLabel(
            self.status_frame,
            text="Время: 00:00:00",
            font=ctk.CTkFont(size=14)
        )
        self.time_label.pack(side="left", padx=10)
        
        # === Основная область с параметрами ===
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Левая колонка - параметры в реальном времени
        self.left_frame = ctk.CTkFrame(self.main_frame, width=400)
        self.left_frame.pack(side="left", fill="y", padx=(0, 10))
        self.left_frame.pack_propagate(False)
        
        self.create_monitoring_panel()
        
        # Правая колонка - управление
        self.right_frame = ctk.CTkFrame(self.main_frame)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self.create_control_panel()
        
        # === Нижняя панель с кнопками управления ===
        self.bottom_frame = ctk.CTkFrame(self, height=100)
        self.bottom_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.create_action_buttons()
    
    def create_monitoring_panel(self):
        """Панель мониторинга параметров"""
        title = ctk.CTkLabel(
            self.left_frame,
            text="📊 МОНИТОРИНГ ПАРАМЕТРОВ",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=10)
        
        # Контейнер для параметров
        self.params_frame = ctk.CTkScrollableFrame(self.left_frame)
        self.params_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Температура
        self.temp_frame = self.create_param_card(
            self.params_frame,
            "🌡️ Температура",
            "37.0 °C",
            "temperature_value"
        )
        
        # pH
        self.ph_frame = self.create_param_card(
            self.params_frame,
            "🧪 pH",
            "7.0",
            "ph_value"
        )
        
        # Кислород
        self.oxygen_frame = self.create_param_card(
            self.params_frame,
            "💨 Растворенный кислород",
            "100.0 %",
            "oxygen_value"
        )
        
        # Скорость мешалки
        self.stirrer_frame = self.create_param_card(
            self.params_frame,
            "⚙️ Мешалка",
            "200 об/мин",
            "stirrer_value"
        )
        
        # Оптическая плотность
        self.od_frame = self.create_param_card(
            self.params_frame,
            "📈 Оптическая плотность (OD600)",
            "0.1",
            "od_value"
        )
        
        # Объем культуры
        self.volume_frame = self.create_param_card(
            self.params_frame,
            "🧫 Объем культуры",
            "1000.0 мл",
            "volume_value"
        )
        
        # Насос A
        self.pump_a_frame = self.create_param_card(
            self.params_frame,
            "💉 Насос A (кислота/щелочь)",
            "0.0 мл/мин",
            "pump_a_value"
        )
        
        # Насос B
        self.pump_b_frame = self.create_param_card(
            self.params_frame,
            "💉 Насос B (питательная среда)",
            "0.0 мл/мин",
            "pump_b_value"
        )
    
    def create_param_card(self, parent, title, value, value_attr):
        """Создание карточки параметра"""
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.pack(fill="x", pady=5, padx=5)
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=13),
            anchor="w"
        )
        title_label.pack(fill="x", padx=10, pady=(10, 5))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#3498db",
            anchor="w"
        )
        value_label.pack(fill="x", padx=10, pady=(0, 10))
        
        setattr(self, value_attr, value_label)
        return card
    
    def create_control_panel(self):
        """Панель управления параметрами"""
        title = ctk.CTkLabel(
            self.right_frame,
            text="⚙️ УПРАВЛЕНИЕ ПАРАМЕТРАМИ",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=10)
        
        # Контейнер с прокруткой для элементов управления
        self.controls_scroll = ctk.CTkScrollableFrame(self.right_frame)
        self.controls_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Управление температурой
        temp_frame = ctk.CTkFrame(self.controls_scroll)
        temp_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            temp_frame,
            text="Температура (°C):",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=10)
        
        self.temp_slider = ctk.CTkSlider(
            temp_frame,
            from_=20,
            to=50,
            number_of_steps=30,
            command=lambda v: self.temp_value_label.configure(text=f"{v:.1f}")
        )
        self.temp_slider.pack(side="left", padx=10, expand=True, fill="x")
        self.temp_slider.set(37.0)
        
        self.temp_value_label = ctk.CTkLabel(
            temp_frame,
            text="37.0",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=50
        )
        self.temp_value_label.pack(side="left", padx=10)
        
        ctk.CTkButton(
            temp_frame,
            text="Установить",
            width=100,
            command=self.set_temperature
        ).pack(side="left", padx=10)
        
        # Управление pH
        ph_frame = ctk.CTkFrame(self.controls_scroll)
        ph_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            ph_frame,
            text="Целевой pH:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=10)
        
        self.ph_slider = ctk.CTkSlider(
            ph_frame,
            from_=5.0,
            to=9.0,
            number_of_steps=40,
            command=lambda v: self.ph_value_label.configure(text=f"{v:.2f}")
        )
        self.ph_slider.pack(side="left", padx=10, expand=True, fill="x")
        self.ph_slider.set(7.0)
        
        self.ph_value_label = ctk.CTkLabel(
            ph_frame,
            text="7.00",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=50
        )
        self.ph_value_label.pack(side="left", padx=10)
        
        ctk.CTkButton(
            ph_frame,
            text="Установить",
            width=100,
            command=self.set_ph
        ).pack(side="left", padx=10)
        
        # Управление мешалкой
        stirrer_frame = ctk.CTkFrame(self.controls_scroll)
        stirrer_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            stirrer_frame,
            text="Мешалка (об/мин):",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=10)
        
        self.stirrer_slider = ctk.CTkSlider(
            stirrer_frame,
            from_=0,
            to=1000,
            number_of_steps=100,
            command=lambda v: self.stirrer_value_label.configure(text=f"{int(v)}")
        )
        self.stirrer_slider.pack(side="left", padx=10, expand=True, fill="x")
        self.stirrer_slider.set(200)
        
        self.stirrer_value_label = ctk.CTkLabel(
            stirrer_frame,
            text="200",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=50
        )
        self.stirrer_value_label.pack(side="left", padx=10)
        
        ctk.CTkButton(
            stirrer_frame,
            text="Установить",
            width=100,
            command=self.set_stirrer
        ).pack(side="left", padx=10)
        
        # Управление насосом A
        pump_a_frame = ctk.CTkFrame(self.controls_scroll)
        pump_a_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            pump_a_frame,
            text="Насос A (мл/мин):",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=10)
        
        self.pump_a_slider = ctk.CTkSlider(
            pump_a_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            command=lambda v: self.pump_a_value_label.configure(text=f"{v:.1f}")
        )
        self.pump_a_slider.pack(side="left", padx=10, expand=True, fill="x")
        self.pump_a_slider.set(0.0)
        
        self.pump_a_value_label = ctk.CTkLabel(
            pump_a_frame,
            text="0.0",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=50
        )
        self.pump_a_value_label.pack(side="left", padx=10)
        
        ctk.CTkButton(
            pump_a_frame,
            text="Установить",
            width=100,
            command=self.set_pump_a
        ).pack(side="left", padx=10)
        
        # Управление насосом B
        pump_b_frame = ctk.CTkFrame(self.controls_scroll)
        pump_b_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            pump_b_frame,
            text="Насос B (мл/мин):",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=10)
        
        self.pump_b_slider = ctk.CTkSlider(
            pump_b_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            command=lambda v: self.pump_b_value_label.configure(text=f"{v:.1f}")
        )
        self.pump_b_slider.pack(side="left", padx=10, expand=True, fill="x")
        self.pump_b_slider.set(0.0)
        
        self.pump_b_value_label = ctk.CTkLabel(
            pump_b_frame,
            text="0.0",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=50
        )
        self.pump_b_value_label.pack(side="left", padx=10)
        
        ctk.CTkButton(
            pump_b_frame,
            text="Установить",
            width=100,
            command=self.set_pump_b
        ).pack(side="left", padx=10)
    
    def create_action_buttons(self):
        """Кнопки управления процессом"""
        # Кнопка запуска
        self.start_button = ctk.CTkButton(
            self.bottom_frame,
            text="▶️ ЗАПУСК",
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#27ae60",
            hover_color="#2ecc71",
            width=200,
            height=50,
            command=self.start_cultivation
        )
        self.start_button.pack(side="left", padx=20, pady=25)
        
        # Кнопка паузы
        self.pause_button = ctk.CTkButton(
            self.bottom_frame,
            text="⏸️ ПАУЗА",
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#f39c12",
            hover_color="#f1c40f",
            width=200,
            height=50,
            command=self.pause_cultivation,
            state="disabled"
        )
        self.pause_button.pack(side="left", padx=20, pady=25)
        
        # Кнопка остановки
        self.stop_button = ctk.CTkButton(
            self.bottom_frame,
            text="⏹️ ОСТАНОВКА",
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            width=200,
            height=50,
            command=self.stop_cultivation,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=20, pady=25)
        
        # Кнопка сброса
        self.reset_button = ctk.CTkButton(
            self.bottom_frame,
            text="🔄 СБРОС",
            font=ctk.CTkFont(size=16),
            fg_color="#7f8c8d",
            hover_color="#95a5a6",
            width=150,
            height=50,
            command=self.reset_reactor
        )
        self.reset_button.pack(side="right", padx=20, pady=25)
    
    def start_cultivation(self):
        """Запуск культивирования"""
        try:
            response = requests.post(f"{self.backend_url}/control/start", timeout=5)
            data = response.json()
            if data.get("success"):
                self.show_message("Успех", data.get("message", "Культивирование запущено"))
                self.update_buttons_state("running")
            else:
                self.show_message("Ошибка", data.get("error", "Не удалось запустить"))
        except requests.exceptions.RequestException as e:
            self.show_message("Ошибка подключения", f"Не удалось соединиться с сервером: {str(e)}")
    
    def pause_cultivation(self):
        """Пауза/возобновление культивирования"""
        try:
            response = requests.post(f"{self.backend_url}/control/pause", timeout=5)
            data = response.json()
            if data.get("success"):
                self.show_message("Успех", data.get("message", "Статус изменен"))
                # Обновление кнопок будет выполнено при следующем обновлении статуса
        except requests.exceptions.RequestException as e:
            self.show_message("Ошибка подключения", f"Не удалось соединиться с сервером: {str(e)}")
    
    def stop_cultivation(self):
        """Остановка культивирования"""
        try:
            response = requests.post(f"{self.backend_url}/control/stop", timeout=5)
            data = response.json()
            if data.get("success"):
                self.show_message("Успех", data.get("message", "Культивирование остановлено"))
                self.update_buttons_state("stopped")
            else:
                self.show_message("Ошибка", data.get("error", "Не удалось остановить"))
        except requests.exceptions.RequestException as e:
            self.show_message("Ошибка подключения", f"Не удалось соединиться с сервером: {str(e)}")
    
    def reset_reactor(self):
        """Сброс параметров"""
        try:
            response = requests.post(f"{self.backend_url}/reset", timeout=5)
            data = response.json()
            if data.get("success"):
                self.show_message("Успех", data.get("message", "Параметры сброшены"))
                self.update_buttons_state("stopped")
        except requests.exceptions.RequestException as e:
            self.show_message("Ошибка подключения", f"Не удалось соединиться с сервером: {str(e)}")
    
    def set_temperature(self):
        """Установка температуры"""
        try:
            temp = self.temp_slider.get()
            response = requests.post(
                f"{self.backend_url}/settings/temperature",
                json={"temperature": temp},
                timeout=5
            )
            data = response.json()
            if data.get("success"):
                self.show_message("Успех", data.get("message", "Температура установлена"))
        except requests.exceptions.RequestException as e:
            self.show_message("Ошибка подключения", f"Не удалось соединиться с сервером: {str(e)}")
    
    def set_ph(self):
        """Установка pH"""
        try:
            ph = self.ph_slider.get()
            response = requests.post(
                f"{self.backend_url}/settings/ph",
                json={"ph": ph},
                timeout=5
            )
            data = response.json()
            if data.get("success"):
                self.show_message("Успех", data.get("message", "pH установлен"))
        except requests.exceptions.RequestException as e:
            self.show_message("Ошибка подключения", f"Не удалось соединиться с сервером: {str(e)}")
    
    def set_stirrer(self):
        """Установка скорости мешалки"""
        try:
            speed = self.stirrer_slider.get()
            response = requests.post(
                f"{self.backend_url}/settings/stirrer",
                json={"speed": int(speed)},
                timeout=5
            )
            data = response.json()
            if data.get("success"):
                self.show_message("Успех", data.get("message", "Скорость мешалки установлена"))
        except requests.exceptions.RequestException as e:
            self.show_message("Ошибка подключения", f"Не удалось соединиться с сервером: {str(e)}")
    
    def set_pump_a(self):
        """Установка насоса A"""
        try:
            rate = self.pump_a_slider.get()
            response = requests.post(
                f"{self.backend_url}/pumps/a",
                json={"rate": rate},
                timeout=5
            )
            data = response.json()
            if data.get("success"):
                self.show_message("Успех", data.get("message", "Насос A настроен"))
        except requests.exceptions.RequestException as e:
            self.show_message("Ошибка подключения", f"Не удалось соединиться с сервером: {str(e)}")
    
    def set_pump_b(self):
        """Установка насоса B"""
        try:
            rate = self.pump_b_slider.get()
            response = requests.post(
                f"{self.backend_url}/pumps/b",
                json={"rate": rate},
                timeout=5
            )
            data = response.json()
            if data.get("success"):
                self.show_message("Успех", data.get("message", "Насос B настроен"))
        except requests.exceptions.RequestException as e:
            self.show_message("Ошибка подключения", f"Не удалось соединиться с сервером: {str(e)}")
    
    def update_buttons_state(self, status):
        """Обновление состояния кнопок"""
        if status == "running":
            self.start_button.configure(state="disabled")
            self.pause_button.configure(state="normal")
            self.stop_button.configure(state="normal")
        elif status == "paused":
            self.start_button.configure(state="disabled")
            self.pause_button.configure(state="normal", text="▶️ ВОЗОБНОВИТЬ")
            self.stop_button.configure(state="normal")
        else:  # stopped
            self.start_button.configure(state="normal")
            self.pause_button.configure(state="disabled", text="⏸️ ПАУЗА")
            self.stop_button.configure(state="disabled")
    
    def update_status_display(self, status):
        """Обновление отображения статуса"""
        if status == "running":
            self.status_label.configure(text="Статус: РАБОТАЕТ", text_color="#2ecc71")
        elif status == "paused":
            self.status_label.configure(text="Статус: НА ПАУЗЕ", text_color="#f39c12")
        else:
            self.status_label.configure(text="Статус: НЕ АКТИВЕН", text_color="#e74c3c")
    
    def periodic_update(self):
        """Периодическое обновление данных"""
        while self.running:
            try:
                response = requests.get(f"{self.backend_url}/status", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        reactor_data = data.get("data", {})
                        
                        # Обновление значений в GUI (в главном потоке)
                        self.after(0, lambda: self.update_monitoring_values(reactor_data))
                        
            except requests.exceptions.RequestException:
                pass  # Игнорируем ошибки подключения
            
            time.sleep(2)  # Обновление каждые 2 секунды
    
    def update_monitoring_values(self, data):
        """Обновление значений на панели мониторинга"""
        try:
            # Температура
            if hasattr(self, 'temperature_value'):
                self.temperature_value.configure(text=f"{data.get('temperature', 0):.1f} °C")
            
            # pH
            if hasattr(self, 'ph_value'):
                self.ph_value.configure(text=f"{data.get('ph', 0):.2f}")
            
            # Кислород
            if hasattr(self, 'oxygen_value'):
                self.oxygen_value.configure(text=f"{data.get('dissolved_oxygen', 0):.1f} %")
            
            # Мешалка
            if hasattr(self, 'stirrer_value'):
                self.stirrer_value.configure(text=f"{data.get('stirrer_speed', 0)} об/мин")
            
            # Оптическая плотность
            if hasattr(self, 'od_value'):
                self.od_value.configure(text=f"{data.get('optical_density', 0):.3f}")
            
            # Объем
            if hasattr(self, 'volume_value'):
                self.volume_value.configure(text=f"{data.get('culture_volume', 0):.1f} мл")
            
            # Насос A
            if hasattr(self, 'pump_a_value'):
                self.pump_a_value.configure(text=f"{data.get('pump_a_rate', 0):.1f} мл/мин")
            
            # Насос B
            if hasattr(self, 'pump_b_value'):
                self.pump_b_value.configure(text=f"{data.get('pump_b_rate', 0):.1f} мл/мин")
            
            # Статус
            status = data.get('status', 'stopped')
            self.update_status_display(status)
            self.update_buttons_state(status)
            
            # Время
            elapsed = data.get('elapsed_time', 0)
            hours, remainder = divmod(int(elapsed), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.time_label.configure(text=f"Время: {hours:02d}:{minutes:02d}:{seconds:02d}")
            
        except Exception as e:
            print(f"Ошибка обновления значений: {e}")
    
    def show_message(self, title, message):
        """Показ сообщения пользователю"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        
        label = ctk.CTkLabel(
            dialog,
            text=message,
            font=ctk.CTkFont(size=14),
            wraplength=350
        )
        label.pack(expand=True, padx=20, pady=20)
        
        button = ctk.CTkButton(
            dialog,
            text="OK",
            width=100,
            command=dialog.destroy
        )
        button.pack(pady=(0, 20))
        
        # Центрирование диалога
        dialog.transient(self)
        dialog.grab_set()
    
    def on_closing(self):
        """Обработка закрытия окна"""
        self.running = False
        self.destroy()


if __name__ == "__main__":
    app = BioreactorGUI()
    app.mainloop()
