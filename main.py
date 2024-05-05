import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Function to load data from CSV file
@st.cache_data
def load_data():
    df = pd.read_csv('test_data.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Serve Time'] = pd.to_datetime(df['Serve Time'])
    return df.copy()  

# Format sales price
def format_sales_price(price):
    if price < 1000:
        return f"${price:.0f}"
    elif price < 10000:
        return f"${price/1000:.1f}k"
    else:
        return f"${price/1000:.0f}k"

# Load data
data = load_data()

# Title of the dashboard
st.title('Restaurant Management Dashboard')

# Sidebar for date range selection
st.sidebar.title('Date Range Selection')
start_date = st.sidebar.date_input("Start date", data['Date'].min().date())
end_date = st.sidebar.date_input("End date", data['Date'].max().date())

# Convert 'Serve Time' column to datetime and format it
data['Serve Time'] = pd.to_datetime(data['Serve Time']) 
data['Serve Time'] = data['Serve Time'].dt.strftime('%Y-%m-%d %H:%M:%S')

filtered_data = data[(data['Date'] >= pd.Timestamp(start_date)) & (data['Date'] <= pd.Timestamp(end_date))]

# Dataset preview
st.subheader('Dataset Preview')
st.dataframe(filtered_data) 

# Checkbox to aggregate sales data by week or month
if st.sidebar.checkbox("Aggregate by Week", True):
    freq = 'W'
else:
    freq = 'M'



# Sales performance over time
st.subheader('Sales Performance Over Time')

# Group sales data by selected frequency and sum the sales prices
sales_data = filtered_data.groupby([pd.Grouper(key='Date', freq=freq)])['Price'].sum().reset_index()

# Plot the sales performance over time
fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(x='Date', y='Price', data=sales_data, ax=ax)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)  # Rotate x-axis labels

# Format y-axis labels
y_ticks = plt.yticks()[0]
y_labels = [format_sales_price(y) for y in y_ticks]
plt.yticks(y_ticks, y_labels)

plt.ylabel('Sales Price')
plt.xlabel('Date')
plt.grid(True)
st.pyplot(fig)



# Popular menu items
st.subheader('Popular Menu Items')

# Count orders for each menu item
menu_counts = filtered_data['Menu'].value_counts().reset_index()
menu_counts.columns = ['Menu', 'Orders']

# Plot popular menu items
plt.figure(figsize=(10, 6))
sns.barplot(x='Orders', y='Menu', data=menu_counts, palette='viridis')
plt.xlabel('Orders')
plt.ylabel('Menu Item')
plt.grid(True)
st.pyplot(plt.gcf()) 



# Popular categories
st.subheader('Popular Categories')

# Calculate percentage of orders for each category
total_orders = filtered_data.shape[0]
category_counts = filtered_data['Category'].value_counts()
category_percentages = (category_counts / total_orders) * 100

# Plot popular categories
plt.figure(figsize=(10, 6))
plt.pie(category_percentages, labels=category_percentages.index, autopct='%1.1f%%', startangle=140, colors=['skyblue', 'lightgreen'])
plt.title('Sales Percentage of Categories (Food vs. Drink)')
plt.axis('equal') 
st.pyplot(plt.gcf())




# Overall orders by category
st.subheader('Overall Orders by Category')

# Group orders by category and month, then plot
plt.figure(figsize=(10, 6))
orders_by_category = filtered_data.groupby([pd.Grouper(key='Date', freq='M'), 'Category']).size().unstack(fill_value=0)
orders_by_category.plot(kind='bar', figsize=(10, 6))
plt.xlabel('Month')
plt.ylabel('Number of Orders')
plt.grid(True)
plt.legend(title='Category')
month_names = orders_by_category.index.strftime('%b')
plt.xticks(range(len(month_names)), month_names, rotation=45)
st.pyplot(plt.gcf())




# Overall sales by category
st.subheader('Overall Sales by Category')

# Group sales by category and month, then plot
plt.figure(figsize=(10, 6))
sales_by_category = filtered_data.groupby([pd.Grouper(key='Date', freq='M'), 'Category'])['Price'].sum().unstack(fill_value=0)
sales_by_category.plot(kind='bar', figsize=(10, 6))
plt.xlabel('Month')
plt.ylabel('Sales')
plt.grid(True)
plt.legend(title='Category')
plt.yticks(plt.yticks()[0], [format_sales_price(x) for x in plt.yticks()[0]])
month_names = sales_by_category.index.strftime('%b')
plt.xticks(range(len(month_names)), month_names, rotation=45)
st.pyplot(plt.gcf())



# Mean duration between order time and serve time for each week
st.subheader('Mean Duration Between Order Time and Serve Time for Each Week')

# Calculate duration between order time and serve time in minutes
filtered_data['Order Time'] = pd.to_datetime(filtered_data['Order Time'])
filtered_data['Serve Time'] = pd.to_datetime(filtered_data['Serve Time'])
filtered_data['Duration'] = (filtered_data['Serve Time'] - filtered_data['Order Time']).dt.total_seconds() / 60

# Group by week and category, calculate mean duration, and plot
filtered_data['Week'] = filtered_data['Order Time'].dt.to_period('W').dt.start_time
mean_duration_per_week = filtered_data.groupby(['Week', 'Category'])['Duration'].mean().reset_index()
mean_duration_per_week.columns = ['Week', 'Category', 'Mean Duration (Minutes)']
plt.figure(figsize=(10, 6))
for category in mean_duration_per_week['Category'].unique():
    cat_data = mean_duration_per_week[mean_duration_per_week['Category'] == category]
    week_numbers = cat_data['Week'].dt.isocalendar().week
    plt.plot(week_numbers, cat_data['Mean Duration (Minutes)'], marker='o', linestyle='-', label=category)

plt.xlabel('Week')
plt.ylabel('Mean Duration (Minutes)')
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
st.pyplot(plt.gcf())




# Mean duration between order time and serve time for each day
st.subheader('Mean Duration Between Order Time and Serve Time for Each Day')

# Group by day and category, calculate mean duration, and plot
mean_duration_per_day = filtered_data.groupby([filtered_data['Order Time'].dt.date, 'Category'])['Duration'].mean().reset_index()
mean_duration_per_day.columns = ['Day', 'Category', 'Mean Duration (Minutes)']
plt.figure(figsize=(10, 6))
for category in mean_duration_per_day['Category'].unique():
    cat_data = mean_duration_per_day[mean_duration_per_day['Category'] == category]
    plt.plot(cat_data['Day'], cat_data['Mean Duration (Minutes)'], marker='o', linestyle='-', label=category)

plt.xlabel('Day')
plt.ylabel('Mean Duration (Minutes)')
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
st.pyplot(plt.gcf())



# Find the day with the maximum mean duration
max_duration_day = mean_duration_per_day.loc[mean_duration_per_day['Mean Duration (Minutes)'].idxmax()]['Day']

st.write(f" - The day with maximum mean duration is {max_duration_day}")

# Credits
st.sidebar.markdown('Created by Almas Toh-i')
