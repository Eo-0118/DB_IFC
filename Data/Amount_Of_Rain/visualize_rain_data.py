
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load the data
df = pd.read_csv('cumulative_rain_data.csv', encoding='utf-8')

# --- Plot 1: Total Cumulative Rainfall by Station ---
plt.figure(figsize=(12, 8))
# Set font to one that supports Korean characters
plt.rcParams['font.family'] = 'AppleGothic'
total_rain_by_station = df.groupby('지역명')['기간 누적 강수량'].sum().sort_values(ascending=False)
sns.barplot(x=total_rain_by_station.index, y=total_rain_by_station.values)
plt.title('지역별 총 누적 강수량')
plt.xlabel('지역명')
plt.ylabel('총 누적 강수량 (mm)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('rainfall_by_station.png')
print("Generated rainfall_by_station.png")

# --- Plot 2: Histogram of Rainfall Duration ---
plt.figure(figsize=(10, 6))
sns.histplot(df['강수 기간'], bins=20, kde=True)
plt.title('강수 기간 분포')
plt.xlabel('강수 기간 (일)')
plt.ylabel('빈도')
plt.tight_layout()
plt.savefig('rainfall_duration_histogram.png')
print("Generated rainfall_duration_histogram.png")

# --- Plot 3: Scatter plot of Duration vs. Cumulative Rainfall ---
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='강수 기간', y='기간 누적 강수량', alpha=0.5)
plt.title('강수 기간과 누적 강수량의 관계')
plt.xlabel('강수 기간 (일)')
plt.ylabel('기간 누적 강수량 (mm)')
plt.tight_layout()
plt.savefig('duration_vs_rainfall_scatter.png')
print("Generated duration_vs_rainfall_scatter.png")
