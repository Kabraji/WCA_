import re
import pandas as pd

def preprocess(data):
    # Updated pattern to include optional AM/PM for 12-hour format
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2})\s?(AM|PM|am|pm)? - ([^:]+): (.*)'

    # Find all matches
    matches = re.findall(pattern, data)

    # Debugging: Print number of matches and a sample
    print(f"Number of matches: {len(matches)}")
    print(f"Sample matches: {matches[:2]}")

    # Create DataFrame directly from matches
    if not matches:
        raise ValueError("No matches found. Please check your data and regex pattern.")

    df = pd.DataFrame(matches, columns=['date', 'time', 'period', 'user', 'message'])

    # Combine date and time with period to create full datetime string
    df['datetime'] = df['date'] + ' ' + df['time'] + ' ' + df['period']

    # Convert to datetime
    df['date'] = pd.to_datetime(df['datetime'], format='%m/%d/%y %I:%M %p', errors='coerce')

    # Drop the 'datetime' column
    df.drop(columns=['datetime'], inplace=True)

    # Extract date components
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Create time periods (12-hour format)
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(f"{hour % 12 or 12}-00 PM")
        elif hour == 0:
            period.append('12-1 AM')
        else:
            next_hour = (hour + 1) % 12 or 12
            period.append(f"{hour % 12 or 12}-{next_hour} " + ("PM" if hour >= 12 else "AM"))

    df['period'] = period

    return df
