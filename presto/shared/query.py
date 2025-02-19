import os
import re
import time
import unidecode

import pandas as pd
import sqlite3 as sql

import shared.reviews as rev

##################
# Utilities
#################
def connect(db = 'data/products.sql') -> sql.Connection:
    if not os.path.exists(db):
        curdir = os.path.abspath(os.curdir)
        print(f"Path {db} does not exist in {curdir}")
    return sql.connect(db)

query_verbosity = 1
def query(q: str, conn: sql.Connection, params = None, verbosity = query_verbosity, query_description = None) -> pd.DataFrame:
    """
    Utility to execute an SQL query with optional automatic logging and performance profiling
    """
    if verbosity > 1:
        print(f'QUERY: {q}')
    query_description = query_description or q
    t = time.perf_counter()
    results = pd.read_sql_query(q, conn, params = params)
    if verbosity > 0:
        elapsed = time.perf_counter() - t
        print(f'{query_description}: {len(results)} results in {elapsed:.3f} seconds')
    return results

def get_records_by_ids(
    ids: pd.Series, 
    table: str, 
    connection: sql.Connection, 
    id_column = 'id', 
    select = "*",
    verbosity = query_verbosity, query_description = None
) -> pd.DataFrame:
    """
    General-purpose utility to fetch details for multiple records by ID. Testing has shown this form of query to be quite scalable and performant.
    """
    query_description = query_description or f'{table}.{id_column} lookup ({len(ids)} values)'
    values = ','.join('?' * len(ids))
    params = ids
    q = f"SELECT {select} FROM {table} WHERE {id_column} IN ({values})"
    return query(q, conn = connection, params = params, verbosity = verbosity, query_description = query_description)

def search_text(text: str) -> str:
    """
    Transforms a string into one that is suitable for searching.

    Normalize both the search term and the data to be searched to achieve robust search matching including:
    - Ignoring prefixed 'The' in a band name (The Offspring vs Offspring, etc)
    - Handling inverted first/last name ('Taylor Swift' vs 'Swift, Taylor')
    - Diacritic insensitivity ('Céline Dion' vs 'Celine Dion')
    - Ignoring all whitespace and punctuation, focusing only on alphanumeric characters
    - + more
    """
    # Transform 'Lastname, Firstname' to 'Firstname Lastname'
    if type(text) != str:
        return search_text(str(text))
    components = text.split(', ')
    if len(components) == 2:
        text = components[1] + ' ' + components[0]
    result = text.casefold().replace('the', '')
    result = re.sub(r'[^\w]', '', result) # remove all non-alphanumeric characters
    result = unidecode.unidecode(result) # remove all accents/diacritics
    return result

###########
# Products
###########
def remove_duplicate_products(products: pd.DataFrame) -> pd.DataFrame:
    """
    Given a set of products, returns a set of products with duplicate editions removed.
    Duplicate editions are products that are search-equivalent in both title and artist/author.

    In case of duplicates, the record appearing earliest in the list is retained. For example, in a list sorted by 
    popularity, this method will retain the most popular edition of each product.
    """
    return products.drop_duplicates(subset = ['title_search', 'creator_search'])

def find_products(
    category: str,
    search_term: str,
    conn: sql.Connection,
    search_field: str = 'title',
    exact_match = False,
    verbosity = query_verbosity,
    remove_duplicates = True
) -> pd.DataFrame:
    """
    Implements a sophisticated product search based on a search term and desired category. Cases handled include:
    - Sorting by popularity to help disambiguate multi-result searches
    - All of the search special cases described in the search_text documentation
    """
    columns = 'id, COUNT(*) AS reviews, p.title, title_search, creator, creator_search, publisher, description, release_date, category, subcategory'
    search_term = search_text(search_term)
    params = [category, search_term] if exact_match else [category, f'%{search_term}%']
    operator = "=" if exact_match else 'LIKE'
    q = f"""
    SELECT {columns} 
    FROM review r JOIN product p ON r.product_id = p.id
    WHERE category = ? AND {search_field}_search {operator} ?
    GROUP BY product_id ORDER BY reviews DESC
    """
    results = query(q, conn, params = params, query_description = 'find_products', verbosity = verbosity)
    if remove_duplicates:
        results = remove_duplicate_products(results)
    return results.drop(columns = ['title_search', 'creator_search'])

def get_product_details(product_ids, conn: sql.Connection, select = '*', verbosity = query_verbosity) -> pd.DataFrame:
    """
    Given a list of up to 250,000 product IDs, return product details for each product.
    """
    result = get_records_by_ids(
        product_ids, 
        'product', 
        conn, 
        select = select, 
        verbosity= verbosity, query_description = f'product details {len(product_ids)}'
    )
    if 'id' in result.columns:
        result.set_index('id', inplace = True)
    return result

############
# Reviews
############
def get_reviews(
    product_id_or_products, # use product id for single product reviews, collection of ids for multiple products
    conn: sql.Connection,
    drop_null_reviewers = False,
    fields = '*',
    verbosity = query_verbosity
) -> pd.DataFrame:
    """
    Retrieves all reviews associated with one or more products
    """
    product_ids = [product_id_or_products] if isinstance(product_id_or_products, str) else product_id_or_products
    values = ','.join('?' * len(product_ids))
    q = f"SELECT {fields} FROM review WHERE product_id IN ({values})"
    if drop_null_reviewers:
        q += " AND user_id IS NOT NULL;"
    return query(q, conn, params = product_ids, query_description = 'get_reviews', verbosity = verbosity)

def _filter_unhlepful_reviews(reviews: pd.DataFrame) -> pd.DataFrame:
    return reviews[reviews.upvotes >= reviews.downvotes]

def get_related_reviews(
    reviews: pd.DataFrame,
    conn: sql.Connection,
    filter_unhelpful_reviews = True,
    max_reviewer_count = 100,
    max_product_count = 1_000,
    verbosity = query_verbosity, t = None
) -> pd.DataFrame:
    """
    Given reviews of a product, get all reviews of related products.
    Related products are defined as products who share reviewers in common with the passed in dataset.
    """
    t = t or time.perf_counter()
    def profile(message: str):
        if verbosity > 0:
            elapsed = time.perf_counter() - t
            print(f"{elapsed:.3}: {message}")

    reviews = reviews.copy()
    if filter_unhelpful_reviews:
        reviews = _filter_unhlepful_reviews(reviews)
    user_ids = reviews.user_id.dropna().unique()
    related_reviews = get_records_by_ids(
        user_ids, 
        table = 'review', id_column = 'user_id', select = 'user_id, product_id, rating, upvotes, downvotes', 
        connection = conn, 
        verbosity = 0
    )
    count = len(related_reviews)
    if verbosity > 0:
        user_count = len(related_reviews.user_id.unique())
        product_count = len(related_reviews.product_id.unique())
        profile(f'Got {count} related reviews of {product_count} products by {user_count} users')
    if filter_unhelpful_reviews:
        related_reviews = _filter_unhlepful_reviews(related_reviews)
        if len(related_reviews) < count:
            profile(f'Filtered {len(related_reviews)} helpful related reviews')
            count = len(related_reviews)
    related_reviews = rev.filter_reviews(related_reviews, max_user_count = max_reviewer_count, max_product_count = max_product_count)
    if len(related_reviews) < count:
        profile(f'Filtered {len(related_reviews)} related reviews by user and/or product')
    return related_reviews


###################
# Recommendations
###################

from scipy import sparse
from sklearn.metrics import pairwise_distances

def get_ratings_by_user(data: pd.DataFrame, product_column = 'product_id', user_column = 'user_id', rating_column = 'rating') -> pd.DataFrame:
    """
    Given a dataset that contains ratings per user, return a matrix of user reviews with products as rows and users as columns. This format can be useful for visualization and for computing pairwise similarities.
    """
    return pd.pivot(data, values = 'rating', index = 'product_id', columns = 'user_id')

def get_pairwise_similarities(product_ratings_by_user: pd.DataFrame, fill_value = 0) -> pd.DataFrame:
    """
    Given a matrix of product reviews by users, return a matrix of pairwise product similarities.
    
    This method is central to providing recommendations. To find products most related to a searched product, 
    check the row or column of the searched product in the resulting matrix.
    """
    user_ratings_per_product_sparse = sparse.csr_matrix(product_ratings_by_user.fillna(fill_value))
    # compute pairwise cosine similarities
    # The resulting entries represent the cosine of the angles between the user review vectors of two products.
    # A cosine similarity of 1 represents identical products while a cosine similarity of 0 represents orthogonal / unrelated products
    cosine_similarities = pairwise_distances(user_ratings_per_product_sparse, metric = 'cosine')
    # cosine similarities return 0 for identical products and 1 for produts with no similarity. Let's invert the 
    # scale for an intuitive user-facing metric.
    product_similarities = 1 - cosine_similarities
    product_ids = product_ratings_by_user.index.values
    return pd.DataFrame(product_similarities, index = product_ids, columns = product_ids)
                        
def get_recommendations_from_reviews(
    product_id: str,
    reviews: pd.DataFrame,
    conn: sql.Connection,
    limit = 100,
    fill_value = 0,
    verbosity = query_verbosity, t = None,
    remove_duplicates = True
) -> pd.DataFrame:
    """
    Given a dataset of users, products, and ratings, return a list of products 
    similar to the one with the passed in product ID. For each product, include a 
    normalized similarity score with 1 = identical product, 0 = not at all similar.

    Tip: use get_related_reviews to obtain a good dataset for a product.

    Parameters
    ---------
    - fill_value: the rating to fill in if a user has not rated a product
    """
    # recommendation tables can get enormous. Apply some sanity checks first:
    t = t or time.perf_counter()
    def profile(message: str):
        if verbosity > 0:
            elapsed = time.perf_counter() - t
            print(f"{elapsed:.3}: {message}")
    user_count = len(reviews.user_id.unique())
    product_count = len(reviews.product_id.unique())
    
    # crunch the numbers to find similar products using cosine similarity
    user_ratings_per_product = get_ratings_by_user(reviews)
    pairwise_product_similarities = get_pairwise_similarities(user_ratings_per_product)
    profile('Calculated similarities')

    # recommended products sorted by most similar
    recommendations = pairwise_product_similarities.loc[product_id].sort_values(ascending = False)
    recommendations.drop(index = product_id, inplace = True) # Don't recommend the same product as the input.
    recommendations.name = 'similarity'
    
    # add product data for user-facing results. We only have product Ids.
    details = get_product_details(recommendations.index, conn, verbosity = 0)
    recommendations = pd.concat([recommendations, details], axis = 1).rename(columns = {product_id: 'score'})
    if remove_duplicates:
        count = len(recommendations)
        recommendations = remove_duplicate_products(recommendations)
        if len(recommendations) < count:
            profile(f'Removed {count - len(recommendations)} duplicate editions of the same product')

    if limit != None:
        recommendations = recommendations[:limit]
    recommendations = recommendations.drop(columns = ['title_search', 'creator_search'])
    profile('Added product details')
    return recommendations

def get_recommendations(
    category: str,

    # search settings
    search_term: str,
    conn: sql.Connection,
    search_field = 'title',
    exact_match = True,

    # recommendation settings
    filter_unhelpful_reviews = True,
    reviewer_max_pool_size = 100, # maximum number of reviewers to use for recommendations. Reducing this size improves performance and relevance by focusing on users with many reviews.

    product_max_pool_size = 1_000, # maximum number of products to consider for recommendations
    missing_rating_value = 0,   # the value to fill in for rating when a user has not rated a product
    limit = 100,    # maximum number of recommendations

    # misc settings
    verbosity = query_verbosity, t = None,
    remove_duplicates = True
) -> dict:
    """
    All-in-one user-facing recommendation algorithm inputting search criteria and outputting various product details and recommendations.

    This method is intended to be the first method listed because it is the most central. Due to Python limitations though, it needs to be listed 
    last because Python requires us to define our utility methods before defining the methods using the utility methods.
    """
    t = t or time.perf_counter()
    def profile(message: str):
        if verbosity > 0:
            elapsed = time.perf_counter() - t
            print(f"{elapsed:.3}: {message}")
    
    # fetch matching products (no reviews yet)
    products = find_products(
        category = category, 
        search_term = search_term, search_field = search_field, exact_match = exact_match,
        remove_duplicates = remove_duplicates,
        conn = conn, 
        verbosity = verbosity
    )
    profile(f'Found {len(products)} products')

    # handle product results (none, exact match, multiple matches)
    count = products.shape[0]
    product = None if count == 0 else products.iloc[0]   

    # check out user reviews for the returned product
    reviews = None
    recommendations = None
    if product is not None:
        #product_ids = product.id if search_field == 'title' else products.id
        product_ids = product.id
        reviews = get_reviews(product_ids, conn, verbosity = 0)
        profile(f'Got {len(reviews)} reviews')
        if filter_unhelpful_reviews:
            count = len(reviews)
            reviews = _filter_unhlepful_reviews(reviews)
            if len(reviews) < count:
                profile(f'Filtered {len(reviews)} helpful reviews')

        # get related reviews for recommendations
        related_reviews = get_related_reviews(
            reviews, 
            conn, 
            filter_unhelpful_reviews = False,
            max_reviewer_count = reviewer_max_pool_size,
            verbosity = verbosity, t = t
        )
        if filter_unhelpful_reviews:
            count = len(related_reviews)
            related_reviews = rev.filter_reviews(related_reviews, reviewer_max_pool_size, product_max_pool_size)
            if len(related_reviews) < count:
                profile(f'Filtered {len(related_reviews)} of {count} helpful reviews')
        recommendations = get_recommendations_from_reviews(
            product.id, 
            related_reviews, 
            conn, 
            limit = limit, fill_value = missing_rating_value,
            verbosity = verbosity, t = t, 
            remove_duplicates = remove_duplicates
        )
    
    return {
        "result": product,
        "results": products,
        "reviews": reviews,
        "recommendations": recommendations
    }

