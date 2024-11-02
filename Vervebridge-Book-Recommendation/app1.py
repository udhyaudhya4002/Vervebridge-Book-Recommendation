import streamlit as st
import numpy as np
import pickle

# Load models and data
st.header("Book Recommendation")
model = pickle.load(open('artifacts/model.pkl', 'rb'))
book_name = pickle.load(open('F:\\Vervebridge-Book-Recommendation\\artifacts\\book_names.pkl', 'rb'))
final_rating = pickle.load(open('artifacts/final_rating.pkl', 'rb'))
book_pivot = pickle.load(open('artifacts/book_pivot.pkl', 'rb'))

# Initialize session state for last searched book and page selection
if 'last_searched' not in st.session_state:
    st.session_state.last_searched = None
if 'page' not in st.session_state:
    st.session_state.page = "home"

# Display top-rated books function
def display_top_rated():
    top_books = final_rating.sort_values(by='rating', ascending=False).head(10)
    book_list = []
    for _, row in top_books.iterrows():
        book_list.append((row['title'], row['image_url']))
    return book_list

# Function to interleave top-rated and last-searched recommendations
def display_mixed_books():
    top_books = display_top_rated()
    if st.session_state.last_searched:
        last_searched_books, last_searched_images = recommend_book(st.session_state.last_searched)
        
        # Interleave top-rated and last-searched recommendations
        mixed_books = []
        max_len = max(len(top_books), len(last_searched_books))
        for i in range(max_len):
            if i < len(top_books):
                mixed_books.append(top_books[i])
            if i < len(last_searched_books):
                mixed_books.append((last_searched_books[i], last_searched_images[i]))
        return mixed_books
    else:
        return top_books

# Fetch poster URLs function
def fetch_poster(suggestion):
    book_names = []
    ids_index = []
    poster_urls = []
    
    for book_id in suggestion[0]:
        book_names.append(book_pivot.index[book_id])
        
    for name in book_names:
        try:
            ids = np.where(final_rating['title'] == name)[0][0]
            ids_index.append(ids)
        except IndexError:
            st.warning(f"Image not found for {name}")
            continue
    
    for idx in ids_index:
        url = final_rating.iloc[idx]['image_url']
        poster_urls.append(url)
    
    return poster_urls

# Recommend books function
def recommend_book(book_name):
    book_list = []
    try:
        book_id = np.where(book_pivot.index == book_name)[0][0]
        distance, suggestion = model.kneighbors(book_pivot.iloc[book_id, :].values.reshape(1, -1), n_neighbors=11)
        poster_url = fetch_poster(suggestion)
        
        for i in range(1, len(suggestion[0])):
            book_list.append(book_pivot.index[suggestion[0][i]])
        
        return book_list, poster_url
    except IndexError:
        st.error("Book not found in the recommendations database.")
        return [], []

# Book search input
select_box = st.selectbox("Type the name of a book", book_name)

# Button to suggest books on a separate search page
if st.button('Suggest Book'):
    st.session_state.page = "search_results"
    st.session_state.last_searched = select_box

# Display different content based on page selection
if st.session_state.page == "home":
    st.subheader("Top Books")
    books_to_display = display_mixed_books() if st.session_state.last_searched else display_top_rated()
    
    num_cols = 5
    num_books = len(books_to_display)
    for i in range(0, num_books, num_cols):
        cols = st.columns(num_cols)
        for j in range(num_cols):
            if i + j < num_books:
                with cols[j]:
                    title, image_url = books_to_display[i + j]
                    st.text(title)
                    st.image(image_url, use_column_width=True)

elif st.session_state.page == "search_results":
    st.subheader(f"Suggestions based on '{st.session_state.last_searched}'")
    recommendation_books, poster_url = recommend_book(st.session_state.last_searched)
    
    num_cols = 5
    num_books = len(recommendation_books)
    for i in range(0, num_books, num_cols):
        cols = st.columns(num_cols)
        for j in range(num_cols):
            if i + j < num_books:
                with cols[j]:
                    st.text(recommendation_books[i + j])
                    st.image(poster_url[i + j], use_column_width=True)

# Button to go back to the home page
if st.session_state.page == "search_results" and st.button('Back to Home'):
    st.session_state.page = "home"
