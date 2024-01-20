import sys
import requests
from weatherKey import key
from datetime import datetime
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox, QMessageBox


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()

        self.api_key = key

        font = QFont("Garamond", 13)
        self.setFont(font)

        self.setWindowIcon(QIcon('icon.png'))

        self.setStyleSheet("""
    WeatherApp {
        background-color: white;
        border-radius: 10px;
    }

    QLabel, QLineEdit, QPushButton, QComboBox QAbstractItemView {
        color: black;
        border-radius: 10px;
    }

    QLineEdit, QComboBox {
        background-color: #ecf0f1;
        border: 1px solid #bdc3c7;
        padding: 8px;
        border-radius: 10px;
        color: black;
    }

    QAbstractItemView{
    background-color: #ecf0f1;
    color: black;
    }

    QPushButton {
        background-color: #3498db;
        border: 1px solid #2980b9;
        padding: 8px 16px;
        border-radius: 10px;
        color: white;
    }

    QPushButton:hover {
        background-color: #2c3e50;
    }

    QComboBox:checked {
        background-color: #3498db;
        color: white;
    }
""")



        self.init_ui()

    def set_color_scheme(self, primary, secondary, background, text_color):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, background)
        palette.setColor(QPalette.ColorRole.WindowText, secondary)
        palette.setColor(QPalette.ColorRole.Button, primary)
        palette.setColor(QPalette.ColorRole.ButtonText, background)
        palette.setColor(QPalette.ColorRole.Base, background)
        palette.setColor(QPalette.ColorRole.AlternateBase, primary)
        palette.setColor(QPalette.ColorRole.Text, text_color)
        palette.setColor(QPalette.ColorRole.WindowText, text_color)

        self.setPalette(palette)

    def init_ui(self):
        self.search_by_label = QLabel('Search by:')
        self.search_by_combobox = QComboBox()
        self.search_by_combobox.addItem('City Name')
        self.search_by_combobox.addItem('Coordinates')
        self.search_by_combobox.currentIndexChanged.connect(self.handle_search_type_change)

        self.city_label = QLabel('Enter city:')
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText('Enter city')

        self.coord_label = QLabel('Enter coordinates (lat, lon):')
        self.coord_input = QLineEdit()
        self.coord_input.setPlaceholderText('Example: 55.5, 33.3')

        self.units_label = QLabel('Select units:')
        self.units_combobox = QComboBox()
        self.units_combobox.addItem('Metric (°C, m/s)')
        self.units_combobox.addItem('Imperial (°F, mph)')

        self.current_weather_label = QLabel('Current Weather:')
        self.current_weather_info = QLabel()

        self.forecast_label = QLabel('Weather Forecast:')
        self.forecast_info = QLabel()

        self.search_button = QPushButton('Search')
        self.search_button.clicked.connect(self.search_weather)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.search_by_label)
        self.layout.addWidget(self.search_by_combobox)
        self.layout.addWidget(self.city_label)
        self.layout.addWidget(self.city_input)
        self.layout.addWidget(self.coord_label)
        self.layout.addWidget(self.coord_input)
        self.layout.addWidget(self.units_label)
        self.layout.addWidget(self.units_combobox)
        self.layout.addWidget(self.search_button)
        self.layout.addWidget(self.current_weather_label)
        self.layout.addWidget(self.current_weather_info)
        self.layout.addWidget(self.forecast_label)
        self.layout.addWidget(self.forecast_info)

        self.setLayout(self.layout)

        self.setWindowTitle('Weather in the Hell')
        self.show()

        self.handle_search_type_change(0)

    def handle_search_type_change(self, index):
        is_city_search = index == 0
        self.city_label.setVisible(is_city_search)
        self.city_input.setVisible(is_city_search)
        self.coord_label.setVisible(not is_city_search)
        self.coord_input.setVisible(not is_city_search)

    def search_weather(self):
        search_type = self.search_by_combobox.currentIndex()
        if search_type == 0:
            city = self.city_input.text().strip()
            if not city:
                self.show_error_message("Please enter a city name.")
                return

            if city.lower() == "weather in hell":
                self.display_easter_egg("It's hot. You have found the Easter egg.")
                return

            weather_data, forecast_data = self.get_weather_by_city(city)
        else:
            coords = self.coord_input.text().strip()
            if not coords:
                self.show_error_message("Please enter coordinates.")
                return

            try:
                lat, lon = map(float, coords.split(','))
            except ValueError:
                self.show_error_message("Invalid coordinates format. Please use 'lat, lon'.")
                return

            weather_data, forecast_data = self.get_weather_by_coords(lat, lon)

        if not weather_data:
            self.show_error_message("Unable to fetch weather data. Please check your input.")
            return

        self.display_weather(weather_data)
        if forecast_data:
            self.display_forecast(forecast_data)

    def get_weather_by_city(self, city):
        units_index = self.units_combobox.currentIndex()
        units = 'metric' if units_index == 0 else 'imperial'
        api_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units={units}&appid={self.api_key}'
        response = requests.get(api_url)
        if response.status_code == 200:
            weather_data = response.json()
            coordinates = (weather_data['coord']['lat'], weather_data['coord']['lon'])
            forecast_data = self.get_forecast(*coordinates)
            return weather_data, forecast_data
        else:
            return None, None

    def get_weather_by_coords(self, lat, lon):
        units_index = self.units_combobox.currentIndex()
        units = 'metric' if units_index == 0 else 'imperial'
        api_url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units={units}&appid={self.api_key}'
        response = requests.get(api_url)
        if response.status_code == 200:
            weather_data = response.json()
            forecast_data = self.get_forecast(lat, lon)
            return weather_data, forecast_data
        else:
            return None, None

    def display_weather(self, weather_data):
        if 'main' in weather_data:
            current_weather = weather_data['main']
            weather_description = weather_data['weather'][0]['description']
            wind_info = weather_data['wind']
            visibility = weather_data.get('visibility', '')
            dt_timestamp = weather_data.get('dt', '')
            dt_readable = datetime.utcfromtimestamp(dt_timestamp).strftime('%Y-%m-%d %H:%M:%S')

            temperature_unit = "°C" if self.units_combobox.currentIndex() == 0 else "°F"
            speed_unit = "m/s" if self.units_combobox.currentIndex() == 0 else "mph"

            city_name = weather_data.get('name', '')
            current_info = f'City: {city_name}\n' \
                           f'Temperature: {current_weather.get("temp", "")}{temperature_unit}\n' \
                           f'Feels Like: {current_weather.get("feels_like", "")}{temperature_unit}\n' \
                           f'Humidity: {current_weather.get("humidity", "")}%\n' \
                           f'Wind Speed: {wind_info.get("speed", "")}{speed_unit}\n' \
                           f'Conditions: {weather_description}\n' \
                           f'Visibility: {visibility} meters\n' \
                           f'Date and Time: {dt_readable}'

            self.current_weather_info.setText(current_info)
        else:
            self.show_error_message("Unexpected response structure. Unable to extract weather information.")

    def get_forecast(self, lat, lon):
        units_index = self.units_combobox.currentIndex()
        units = 'metric' if units_index == 0 else 'imperial'
        api_url = f'http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units={units}&cnt=&appid={self.api_key}'
        response = requests.get(api_url)
        return response.json() if response.status_code == 200 else None

    def display_forecast(self, forecast_data):
        forecast_info = ""
        max_temp_by_date = {}

        temperature_unit = "°C" if self.units_combobox.currentIndex() == 0 else "°F"

        for forecast_entry in forecast_data.get('list', []):
            date_timestamp = forecast_entry.get('dt', '')
            date_readable = datetime.utcfromtimestamp(date_timestamp).strftime('%Y-%m-%d')
            temp_max = forecast_entry['main']['temp_max'] if 'main' in forecast_entry else ''

            if date_readable not in max_temp_by_date or temp_max > max_temp_by_date[date_readable]:
                max_temp_by_date[date_readable] = temp_max

        for date, max_temp in max_temp_by_date.items():
            forecast_info += f'{date}: Max Temperature: {max_temp}{temperature_unit}\n'

        self.forecast_info.setText(forecast_info)

    def display_easter_egg(self, message):
        easter_egg_box = QMessageBox()
        easter_egg_box.setStyleSheet("""
            background-color: #ecf0f1;
            color: black;
        """)
        easter_egg_box.setWindowTitle("Easter Egg")
        easter_egg_box.setIcon(QMessageBox.Icon.Information)
        easter_egg_box.setText(message)
        easter_egg_box.exec()


    def show_error_message(self, message):
        msg_box = QMessageBox()
        msg_box.setStyleSheet("""
            background-color: #ecf0f1;
            color: black;
        """)
        msg_box.setWindowTitle('Error')
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setText(message)
        msg_box.exec()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    sys.exit(app.exec())
