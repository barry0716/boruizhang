import pandas as pd
from datetime import datetime
import calendar

# read the CSV from the same directory, skipping lines with parsing errors
input_path = 'AusStage_S22025PE1.csv'
df = pd.read_csv(
    input_path,
    dtype=str,
    engine='python',
    on_bad_lines='skip'  # Automatically skip lines with incorrect field counts or quotation errors
)

# Define the function to clean and validate dates
def clean_date_with_validation(s):
    # NULL → NaT
    if pd.isna(s) or str(s).strip() == '':
        return pd.NaT
    t = str(s).strip()

    # Validate that the year, month, and day values are within their legal ranges
    def is_valid_ymd(year, month, day):
        y, m, d = int(year), int(month), int(day)
        if not (1 <= m <= 12):
            return False
        max_day = calendar.monthrange(y, m)[1]
        return 1 <= d <= max_day

    # Full date format (YYYY-MM-DD)
    if '-' in t and len(t) == 10:
        parts = t.split('-')
        if len(parts) == 3:
            y, m, d = parts
            if y.isdigit() and m.isdigit() and d.isdigit() and is_valid_ymd(y, m, d):
                return datetime.strptime(t, '%Y-%m-%d').date()

    # Year-month format (YYYY-MM) → pad with the first day of the month
    if '-' in t and len(t) == 7:
        parts = t.split('-')
        if len(parts) == 2:
            y, m = parts
            if y.isdigit() and m.isdigit() and 1 <= int(m) <= 12:
                return datetime(int(y), int(m), 1).date()

    # Year only (YYYY) → pad to January 1 of that year.
    if t.isdigit() and len(t) == 4:
        return datetime(int(t), 1, 1).date()

    # treat other format as illegal
    return pd.NaT

# apply clean function
df['First Date Cleaned'] = df['First Date'].apply(clean_date_with_validation)
df['Last Date Cleaned'] = df.apply(
    lambda row: clean_date_with_validation(row['Last Date'])
    if pd.notna(row['Last Date']) and str(row['Last Date']).strip() != ''
    else row['First Date Cleaned'],
    axis=1
)

# save CSV after cleaning
output_path = 'AusStage_S22025PE1_cleaned_dates_validated.csv'
df.to_csv(output_path, index=False, date_format='%Y-%m-%d')

print(f"Done: The file with cleaned and validated dates has been saved. → {output_path}")
