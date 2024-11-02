import streamlit as st
import numpy as np
import pickle

# Load models and data
st.header("Book Recommendation")
model = pickle.load(open('artifacts/model.pkl', 'rb'))
book_name = pickle.load(open('F:\\Vervebridge-Book-Recommendation\\artifacts\\book_names.pkl', 'rb'))
final_rating = pickle.load(open('artifacts/final_rating.pkl', 'rb'))
book_pivot = pickle.load(open('artifacts/book_pivot.pkl', 'rb'))

# Select book input
select_box = st.selectbox(
    "Type the name of a book",
    book_name
)

# Function to fetch poster URLs
def fetch_poster(suggestion):
    book_names = []
    ids_index = []
    poster_urls = []

    # Get the book names from suggestions
    for book_id in suggestion:
        book_names.append(book_pivot.index[book_id])

    # Get the index of each book in the final_rating dataframe
    for name in book_names[0]:
        ids = np.where(final_rating['title'] == name)[0][0]
        ids_index.append(ids)

    # Fetch poster URLs using the indexes
    for idx in ids_index:
        url = final_rating.iloc[idx]['image_url']
        poster_urls.append(url)

    return poster_urls

# Function to recommend books
def recommend_book(book_name):
    book_list = []
    book_id = np.where(book_pivot.index == book_name)[0][0]
    distance, suggestion = model.kneighbors(book_pivot.iloc[book_id, :].values.reshape(1, -1), n_neighbors=11)
    poster_url = fetch_poster(suggestion)

    for i in range(len(suggestion)):
        books = book_pivot.index[suggestion[i]]
        for j in books:
            book_list.append(j)

    return book_list, poster_url

# Button to trigger book recommendations
if st.button('Suggest Book'):
    recommendation_books, poster_url = recommend_book(select_box)

    # Display recommended books in rows and columns for better layout
    num_cols = 5  # Number of columns per row
    num_books = len(recommendation_books)

    for i in range(1, min(11, num_books), num_cols):  # Loop to create multiple rows
        cols = st.columns(num_cols)  # Create columns for each row

        for j in range(num_cols):
            if i + j < num_books:  # To ensure we don't go out of bounds
                with cols[j]:  # Assign each book to a column
                    st.text(recommendation_books[i + j])
                    st.image(poster_url[i + j], use_column_width=True)  # Fit the image in the column
