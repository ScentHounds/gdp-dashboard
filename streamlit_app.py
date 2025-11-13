import streamlit as st
import pandas as pd
import math
from pathlib import Path

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='ASP dashboard',
    #page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_gdp_data():
    """Grab ASP data from a XLSX file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'C:\Users\Bloodhound\Documents\Tájegységi dolgok\ASP_data'
    raw_ASP_df = pd.read_excel(DATA_FILENAME)

    MIN_YEAR = 2017
    MAX_YEAR = 2025

    # The data above has columns like:
    # - Country Name
    # - Country Code
    # - [Stuff I don't care about]
    # - GDP for 1960
    # - GDP for 1961
    # - GDP for 1962
    # - ...
    # - GDP for 2022
    #
    # ...but I want this instead:
    # - Country Name
    # - Country Code
    # - Year
    # - GDP
    #
    # So let's pivot all those year-columns into two: Year and GDP
    ASP_df = raw_ASP_df.melt(
        ['Település'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Megerősítés dátuma',
        'VT kód',
    )

    # Convert years from string to integers
    ASP_df['Megerősítés dátuma'] = pd.to_numeric(ASP_df['Megerősítés dátuma'])

    return ASP_df

ASP_df = get_ASP_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :earth_americas: ASP dashboard

Browse GDP data from the [World Bank Open Data](https://data.worldbank.org/) website. As you'll
notice, the data only goes to 2022 right now, and datapoints for certain years are often missing.
But it's otherwise a great (and did I mention _free_?) source of data.
'''

# Add some spacing
''
''

min_value = ASP_df['Megerősítés dátuma'].min()
max_value = ASP_df['Megerősítés dátuma'].max()

from_year, to_year = st.slider(
    'Which years are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

City = ASP_df['Település'].unique()

if not len(City):
    st.warning("Select at least one country")

selected_City = st.multiselect(
    'Which countries would you like to view?',
    Cities,
    ['Gyermely', 'Budakeszi', 'Szentendre', 'Zsámbék', 'Süttő', 'Tarján'])

''
''
''

# Filter the data
filtered_ASP_df = ASP_df[
    (ASP_df['Település'].isin(selected_City))
    & (ASP_df['Megerősítés dátuma'] <= to_year)
    & (from_year <= ASP_df['Megerősítés dátuma'])
]

st.header('ASP over time', divider='gray')

''

st.line_chart(
    filtered_ASP_df,
    x='Megerősítés dátuma',
    y='VT kód',
    color='Település',
)

''
''


first_year = ASP_df[ASP_df['Megerősítés dátuma'] == from_year]
last_year = ASP_df[ASP_df['Megerősítés dátuma'] == to_year]

st.header(f'ASP in {to_year}', divider='gray')

''

cols = st.columns(4)

for i, City in enumerate(selected_City):
    col = cols[i % len(cols)]

    with col:
        first_ASP = first_year[first_year['Település'] == country]['ASP'].iat[0] / 1000000000
        last_ASP = last_year[last_year['Település'] == country]['ASP'].iat[0] / 1000000000

        if math.isnan(first_ASP):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_ASP / first_ASP:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{country} ASP',
            value=f'{last_ASP:,.0f}B',
            delta=growth,
            delta_color=delta_color
        )
