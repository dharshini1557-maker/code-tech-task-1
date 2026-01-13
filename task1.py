import requests
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)

class WeatherDashboard:
    def __init__(self, api_key, city="London", use_demo=False):
        """
        Initialize the Weather Dashboard
        
        Parameters:
        api_key (str): Your OpenWeatherMap API key
        city (str): City name for weather data
        use_demo (bool): Use demo data instead of API
        """
        self.api_key = api_key
        self.city = city
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.use_demo = use_demo
        
    def generate_demo_data(self):
        """Generate realistic demo weather data"""
        print("Using DEMO DATA - API key not required")
        
        # Current weather demo
        current = {
            'main': {
                'temp': 18.5,
                'feels_like': 17.2,
                'humidity': 65,
                'pressure': 1013
            },
            'wind': {'speed': 4.5},
            'weather': [{'description': 'partly cloudy', 'main': 'Clouds'}]
        }
        
        # Forecast demo data (40 data points = 5 days)
        base_time = datetime.now()
        forecast_list = []
        
        for i in range(40):
            time_point = base_time + timedelta(hours=i*3)
            # Generate realistic temperature variation
            temp = 18 + 5 * np.sin(i * np.pi / 8) + np.random.uniform(-2, 2)
            
            forecast_list.append({
                'dt': int(time_point.timestamp()),
                'main': {
                    'temp': round(temp, 1),
                    'feels_like': round(temp - 1.5, 1),
                    'humidity': int(60 + 20 * np.sin(i * np.pi / 12) + np.random.uniform(-5, 5)),
                    'pressure': int(1010 + 10 * np.sin(i * np.pi / 20))
                },
                'wind': {'speed': round(3 + 3 * np.random.random(), 1)},
                'weather': [{'main': np.random.choice(['Clear', 'Clouds', 'Rain'], p=[0.4, 0.5, 0.1]),
                           'description': 'demo weather'}]
            })
        
        forecast = {'list': forecast_list}
        
        return current, forecast
    
    def fetch_current_weather(self):
        """Fetch current weather data"""
        if self.use_demo:
            current, _ = self.generate_demo_data()
            return current
            
        url = f"{self.base_url}/weather"
        params = {
            'q': self.city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching current weather: {e}")
            print("\n⚠️  API KEY ISSUE DETECTED!")
            print("Your API key may not be activated yet (takes up to 2 hours)")
            print("Switching to DEMO MODE...\n")
            self.use_demo = True
            return self.fetch_current_weather()
    
    def fetch_forecast(self):
        """Fetch 5-day weather forecast"""
        if self.use_demo:
            _, forecast = self.generate_demo_data()
            return forecast
            
        url = f"{self.base_url}/forecast"
        params = {
            'q': self.city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching forecast: {e}")
            self.use_demo = True
            return self.fetch_forecast()
    
    def process_forecast_data(self, forecast_data):
        """Process forecast data into a pandas DataFrame"""
        if not forecast_data:
            return None
        
        data_list = []
        for item in forecast_data['list']:
            data_list.append({
                'datetime': datetime.fromtimestamp(item['dt']),
                'temperature': item['main']['temp'],
                'feels_like': item['main']['feels_like'],
                'humidity': item['main']['humidity'],
                'pressure': item['main']['pressure'],
                'wind_speed': item['wind']['speed'],
                'weather': item['weather'][0]['main'],
                'description': item['weather'][0]['description']
            })
        
        return pd.DataFrame(data_list)
    
    def create_dashboard(self):
        """Create comprehensive weather visualization dashboard"""
        # Fetch data
        current = self.fetch_current_weather()
        forecast = self.fetch_forecast()
        
        if not current or not forecast:
            print("Failed to fetch weather data. Please check your API key and internet connection.")
            return
        
        # Process forecast data
        df = self.process_forecast_data(forecast)
        
        # Create figure with subplots
        fig = plt.figure(figsize=(16, 12))
        title_suffix = " (DEMO DATA)" if self.use_demo else ""
        fig.suptitle(f'Weather Dashboard - {self.city}{title_suffix}', 
                    fontsize=20, fontweight='bold', y=0.995)
        
        # 1. Current Weather Info (Text Box)
        ax1 = plt.subplot(3, 3, 1)
        ax1.axis('off')
        current_info = f"""
        CURRENT CONDITIONS
        
        Temperature: {current['main']['temp']:.1f}°C
        Feels Like: {current['main']['feels_like']:.1f}°C
        Humidity: {current['main']['humidity']}%
        Pressure: {current['main']['pressure']} hPa
        Wind Speed: {current['wind']['speed']} m/s
        Conditions: {current['weather'][0]['description'].title()}
        """
        ax1.text(0.1, 0.5, current_info, fontsize=12, verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        
        # 2. Temperature Forecast Line Plot
        ax2 = plt.subplot(3, 3, 2)
        ax2.plot(df['datetime'], df['temperature'], marker='o', linewidth=2, 
                color='#FF6B6B', label='Temperature')
        ax2.plot(df['datetime'], df['feels_like'], marker='s', linewidth=2, 
                linestyle='--', color='#4ECDC4', label='Feels Like')
        ax2.set_title('Temperature Forecast (5 Days)', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Date/Time')
        ax2.set_ylabel('Temperature (°C)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 3. Temperature Distribution
        ax3 = plt.subplot(3, 3, 3)
        sns.histplot(data=df, x='temperature', kde=True, color='#FF6B6B', ax=ax3)
        ax3.set_title('Temperature Distribution', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Temperature (°C)')
        ax3.set_ylabel('Frequency')
        
        # 4. Humidity Over Time
        ax4 = plt.subplot(3, 3, 4)
        ax4.fill_between(df['datetime'], df['humidity'], alpha=0.3, color='#95E1D3')
        ax4.plot(df['datetime'], df['humidity'], marker='o', color='#38ada9', linewidth=2)
        ax4.set_title('Humidity Forecast', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Date/Time')
        ax4.set_ylabel('Humidity (%)')
        ax4.grid(True, alpha=0.3)
        plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 5. Wind Speed
        ax5 = plt.subplot(3, 3, 5)
        ax5.bar(df['datetime'], df['wind_speed'], color='#A8E6CF', edgecolor='#56ab91')
        ax5.set_title('Wind Speed Forecast', fontsize=14, fontweight='bold')
        ax5.set_xlabel('Date/Time')
        ax5.set_ylabel('Wind Speed (m/s)')
        ax5.grid(True, alpha=0.3, axis='y')
        plt.setp(ax5.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 6. Pressure Trend
        ax6 = plt.subplot(3, 3, 6)
        ax6.plot(df['datetime'], df['pressure'], marker='D', color='#FFD93D', 
                linewidth=2, markersize=4)
        ax6.set_title('Atmospheric Pressure', fontsize=14, fontweight='bold')
        ax6.set_xlabel('Date/Time')
        ax6.set_ylabel('Pressure (hPa)')
        ax6.grid(True, alpha=0.3)
        plt.setp(ax6.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 7. Weather Conditions Pie Chart
        ax7 = plt.subplot(3, 3, 7)
        weather_counts = df['weather'].value_counts()
        colors = sns.color_palette('pastel')[0:len(weather_counts)]
        ax7.pie(weather_counts.values, labels=weather_counts.index, autopct='%1.1f%%',
               colors=colors, startangle=90)
        ax7.set_title('Weather Conditions Distribution', fontsize=14, fontweight='bold')
        
        # 8. Temperature vs Humidity Scatter
        ax8 = plt.subplot(3, 3, 8)
        scatter = ax8.scatter(df['temperature'], df['humidity'], 
                             c=df['wind_speed'], cmap='viridis', 
                             s=100, alpha=0.6, edgecolors='black')
        ax8.set_title('Temperature vs Humidity', fontsize=14, fontweight='bold')
        ax8.set_xlabel('Temperature (°C)')
        ax8.set_ylabel('Humidity (%)')
        cbar = plt.colorbar(scatter, ax=ax8)
        cbar.set_label('Wind Speed (m/s)')
        ax8.grid(True, alpha=0.3)
        
        # 9. Daily Temperature Range
        ax9 = plt.subplot(3, 3, 9)
        df['date'] = df['datetime'].dt.date
        daily_stats = df.groupby('date').agg({
            'temperature': ['min', 'max', 'mean']
        }).reset_index()
        daily_stats.columns = ['date', 'min_temp', 'max_temp', 'mean_temp']
        
        x_pos = range(len(daily_stats))
        ax9.bar(x_pos, daily_stats['max_temp'] - daily_stats['min_temp'], 
               bottom=daily_stats['min_temp'], color='#FFEAA7', 
               edgecolor='#FDCB6E', alpha=0.7)
        ax9.plot(x_pos, daily_stats['mean_temp'], marker='o', color='#E17055', 
                linewidth=2, markersize=8, label='Mean')
        ax9.set_xticks(x_pos)
        ax9.set_xticklabels(daily_stats['date'], rotation=45, ha='right')
        ax9.set_title('Daily Temperature Range', fontsize=14, fontweight='bold')
        ax9.set_xlabel('Date')
        ax9.set_ylabel('Temperature (°C)')
        ax9.legend()
        ax9.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        filename = 'weather_dashboard_demo.png' if self.use_demo else 'weather_dashboard.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"\n✅ Dashboard saved as '{filename}'")
        plt.show()
        
        return df

# Example usage
if __name__ == "__main__":
    # Replace with your OpenWeatherMap API key
    # Get free API key at: https://openweathermap.org/api
    API_KEY = "2535b1cc9123d7f0b3660aac31ed80e4"
    
    # You can change the city
    CITY = "coimbatore"
    
    # Set use_demo=True to test without API key
    # Set use_demo=False to use real API data
    USE_DEMO = False  # Change to True to use demo data immediately
    
    print("="*60)
    print("WEATHER DASHBOARD GENERATOR")
    print("="*60)
    
    # Create dashboard
    dashboard = WeatherDashboard(API_KEY, CITY, use_demo=USE_DEMO)
    weather_df = dashboard.create_dashboard()
    
    # Print summary statistics
    if weather_df is not None:
        print("\n" + "="*60)
        print("WEATHER STATISTICS SUMMARY")
        print("="*60)
        print(weather_df[['temperature', 'humidity', 'wind_speed']].describe())
        print("\n✅ Dashboard generation complete!")