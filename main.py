mport pandas as pd
from sodapy import Socrata
import matplotlib.pyplot as plt

# Initialize Socrata client
client = Socrata("data.cityofchicago.org",
                 "x81IzKZ9maYcXGFOGKWuCAZEA",
                 username="nickziebell28@gmail.com",
                 password="Riskey001?")

# Retrieve data from API
results = client.get("6iiy-9s97", limit=8097)

# Convert to pandas DataFrame
results_df = pd.DataFrame.from_records(results)

# Filter the data by year and month for rail boardings
before_covid = results_df[(results_df['service_date'] >= '2018-01-01') & (results_df['service_date'] <= '2020-02-28')]
after_covid = results_df[(results_df['service_date'] >= '2020-03-01') & (results_df['service_date'] <= '2023-3-30')]

# Select relevant columns and convert 'rail_boardings' to numeric
before_covid = before_covid[['service_date', 'rail_boardings']]
before_covid['rail_boardings'] = pd.to_numeric(before_covid['rail_boardings'])

after_covid = after_covid[['service_date', 'rail_boardings']]
after_covid['rail_boardings'] = pd.to_numeric(after_covid['rail_boardings'])

# Convert 'service_date' column to datetime, handling errors
before_covid['service_date'] = pd.to_datetime(before_covid['service_date'], errors='coerce')
after_covid['service_date'] = pd.to_datetime(after_covid['service_date'], errors='coerce')

# Drop rows with invalid dates (NaT)
before_covid = before_covid.dropna(subset=['service_date'])
after_covid = after_covid.dropna(subset=['service_date'])

# Convert 'service_date' to year and month
before_covid['service_date'] = before_covid['service_date'].dt.to_period('M').dt.to_timestamp()
after_covid['service_date'] = after_covid['service_date'].dt.to_period('M').dt.to_timestamp()

# Group by month and sum rail boardings
before_covid = before_covid.groupby(['service_date'])['rail_boardings'].sum().reset_index()
after_covid = after_covid.groupby(['service_date'])['rail_boardings'].sum().reset_index()

# Convert rail_boardings to millions and format for readability
before_covid['rail_boardings'] = before_covid['rail_boardings'] / 1000000
before_covid['rail_boardings'] = before_covid['rail_boardings'].apply(lambda x: f"{x:.1f}M")

after_covid['rail_boardings'] = after_covid['rail_boardings'] / 1000000
after_covid['rail_boardings'] = after_covid['rail_boardings'].apply(lambda x: f"{x:.1f}M")

print("Before COVID-19")
print(before_covid)
print("After COVID-19")
print(after_covid)

# Concatenate before and after COVID data
all_covid = pd.concat([before_covid, after_covid], axis=0)

# Remove 'M' suffix from 'rail_boardings' for numeric conversion
all_covid['rail_boardings'] = all_covid['rail_boardings'].str.replace('M', '')

# Convert 'rail_boardings' to numeric
all_covid['rail_boardings'] = pd.to_numeric(all_covid['rail_boardings'])

# Plotting
plt.plot(all_covid['service_date'], all_covid['rail_boardings'], color='red')

# Add a vertical line at February 2020
plt.axvline(pd.to_datetime('2020-02-01'), color='gray', linestyle='--')
plt.text(pd.to_datetime('2020-02-01'), all_covid['rail_boardings'].max() * 0.95, 'Covid Start', rotation=0)

# Labels and display
plt.xlabel('Month')
plt.ylabel('Rail Boardings (in millions)')
plt.ylim(0, all_covid['rail_boardings'].max())

plt.show()
