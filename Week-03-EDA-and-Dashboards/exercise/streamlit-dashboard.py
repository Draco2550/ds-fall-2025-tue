import streamlit as st
import pandas as pd
import altair as alt
# import plotly.express as px

alt.themes.enable("dark")

def genre_count_bar(df, top_n=20, height=None):
    counts = df.groupby('genres').size().reset_index(name='count')
    counts = counts.sort_values('count', ascending=False).head(top_n)
    row_height = 28
    height = height or max(300, counts.shape[0] * row_height)
    chart = alt.Chart(counts).mark_bar().encode(
        x=alt.X('count:Q', title='Number of Ratings'),
        y=alt.Y('genres:N', sort='-x', title='Genre'),
        tooltip=['genres', 'count']
    ).properties(height=height, title=f'Top {len(counts)} Genres by Rating Count')
    return chart

def genre_mean_rating_bar(df, top_n=20, height=None):
    means = df.groupby('genres')['rating'].mean().reset_index(name='mean_rating')
    means = means.sort_values('mean_rating', ascending=False).head(top_n)
    row_height = 28
    height = height or max(300, means.shape[0] * row_height)
    chart = alt.Chart(means).mark_bar().encode(
        x=alt.X('mean_rating:Q', title='Mean Rating'),
        y=alt.Y('genres:N', sort='-x', title='Genre'),
        tooltip=[alt.Tooltip('genres:N'), alt.Tooltip('mean_rating:Q', format='.2f')]
    ).properties(height=height, title=f'Top {len(means)} Genres by Mean Rating')
    return chart


def ratings_by_year_line(df, agg='mean'):
    
    agg_map = {'mean': 'mean', 'median': 'median'}
    if agg not in agg_map:
        agg = 'mean'
    series = df.groupby('year')['rating'].agg(agg).reset_index().dropna()
    chart = alt.Chart(series).mark_line(point=True).encode(
        x=alt.X('year:O', title='Release Year'),
        y=alt.Y(f'rating:Q', title=f'Rating ({agg})'),
        tooltip=[alt.Tooltip('year:O'), alt.Tooltip('rating:Q', format='.2f')]
    ).properties(title=f'Rating {agg.title()} by Year')
    return chart

def top_n_movies_bar(df, min_ratings=50, top_n=5):

    filtered = df.groupby('title').filter(lambda x: x['rating'].size >= min_ratings)
    summary = filtered.groupby('title').agg(
        mean_rating=('rating', 'mean'),
        rating_count=('rating', 'size'),
        year=('year', 'first')
    ).reset_index()
    top = summary.nlargest(top_n, 'mean_rating')
    chart = alt.Chart(top).mark_bar().encode(
        x=alt.X('mean_rating:Q', title='Mean Rating'),
        y=alt.Y('title:N', sort='-x', title='Title'),
        color=alt.Color('rating_count:Q', scale=alt.Scale(scheme='blues'), title='Rating Count'),
        tooltip=[alt.Tooltip('title:N'), alt.Tooltip('mean_rating:Q', format='.2f'), alt.Tooltip('rating_count:Q'), alt.Tooltip('year:O')]
    ).properties(title=f'Top {top_n} Movies (≥{min_ratings} Ratings)')
    return chart


@st.cache_data
def load_data():
    return pd.read_csv("./Week-03-EDA-and-Dashboards/data/movie_ratings.csv")

df = load_data()

print(df.head())
# print(df.describe())
# print(df.info())
# print(df.isnull().sum())

df_genres = df[['genres', 'rating']]
# print(df_genres.head())
# print(df_genres.value_counts())
# print(df_genres.groupby('genres').aggregate(['count']))
df_genre_sorted = df_genres.groupby('genres').aggregate(['count'])
df_genre_sorted = df_genre_sorted.sort_values(('rating','count'),ascending=False) # Q1 DONE! Use Bar chart
print(df_genre_sorted.head())
df_high_ratings = df_genres.groupby('genres')['rating'].mean()

df_high_ratings = df_high_ratings.sort_values(ascending=False) # Q2 DONE!
print(df_high_ratings.head())

df_movie_years = df[['genres', 'rating', 'year']]
# print(df_movie_years.head())
print(df_movie_years.groupby('year')['rating'].mean().sort_values()) # Q3 DONE! Use bar chart

df_5_best_rated = df[['title', 'rating', 'year']]
# print(df_5_best_rated.head())
# print(df_5_best_rated.groupby('title')['rating'].aggregate(['count']))
print(df_5_best_rated.groupby('title').filter(lambda x: x['rating'].size >= 50).groupby('title')['rating'].mean().nlargest(5)) # Q4 DONE >=50
print(df_5_best_rated.groupby('title').filter(lambda x: x['rating'].size >= 150).groupby('title')['rating'].mean().nlargest(5)) # Q4 DONE >= 150
# What's the breakdown of genres for the movies that were rated? Clean table up by removing not int's and nulls
# Which genres have the highest viewer satisfaction (highest ratings)?
# How does mean rating change across movie release years?
# What are the 5 best-rated movies that have at least 50 ratings? At least 150 ratings?

st.title("Movie Ratings Explorer")

# Q1
st.header("Genre counts")
st.altair_chart(genre_count_bar(df, top_n=20), use_container_width=True)

# Q2
st.header("Genre mean ratings")
st.altair_chart(genre_mean_rating_bar(df, top_n=20), use_container_width=True)

# Q3
st.header("Ratings by year")
st.altair_chart(ratings_by_year_line(df, agg='mean'), use_container_width=True)

# Q4
st.header("Top movies (filterable)")
min_ratings = st.slider("Min ratings", 10, 500, 50)
top_n = st.slider("Top N movies", 1, 20, 5)
st.altair_chart(top_n_movies_bar(df, min_ratings=min_ratings, top_n=top_n), use_container_width=True)

# # Sidebar
# with st.sidebar:
#     st.title('MovieLens')
    
   



#     color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
#     selected_color_theme = st.selectbox('Select a color theme', color_theme_list)


# Barchart -> Use for df_genres 

# #Choropleth map
# def make_choropleth(input_df, input_id, input_column, input_color_theme):
#     choropleth = px.choropleth(input_df, locations=input_id, color=input_column, locationmode="USA-states",
#                                color_continuous_scale=input_color_theme,
#                                range_color=(0, max(df_median_prices.price)), # might need to be adjusted, as the graph will probably consist of the whole price instead of the single highest.
#                                scope="usa",
#                                labels={'price':'Price'}
#                               )
#     choropleth.update_layout(
#         template='plotly_dark',
#         plot_bgcolor='rgba(0, 0, 0, 0)',
#         paper_bgcolor='rgba(0, 0, 0, 0)',
#         margin=dict(l=0, r=0, t=0, b=0),
#         height=350
#     )
#     return choropleth

# def format_number(num):
#     if num > 1000000:
#         if not num % 1000000:
#             return f'{num // 1000000} M'
#         return f'{round(num / 1000000, 1)} M'
#     return f'{num // 1000} K'

# def visualize_top_movies(df, min_ratings=50, top_n=5):
#     # Filter movies with at least 50 ratings
#     filtered = df.groupby('title').filter(lambda x: x['rating'].size >= min_ratings)

#     # Aggregate mean rating and count
#     summary = filtered.groupby('title').agg({
#         'rating': 'mean',
#         'year': 'first'  # optional, if you want to show release year
#     }).reset_index()

#     # Select top N movies
#     top_movies = summary.nlargest(top_n, 'rating')
    
#     chart = alt.Chart(top_movies).mark_bar().encode(
#         x='rating:Q',
#         y=alt.Y('title:N', sort='-x'),
#         tooltip=['title', 'rating', 'year']
#         ).properties(title=f'Top {top_n} Movies (≥{min_ratings} Ratings)')
    
#     return chart
