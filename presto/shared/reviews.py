import pandas as pd

def sort_reviews(
    reviews: pd.DataFrame,
    include_quality = True  # inserts a 'quality' metric that measures the quality of the user review 
) -> pd.DataFrame:
    avg_upvotes = reviews.upvotes.mean()
    avg_downvotes = reviews.downvotes.mean()
    adj_upvotes, adj_downvotes = 1 + reviews.upvotes + avg_upvotes, 1 + reviews.downvotes + avg_downvotes
    #print(avg_upvotes, avg_downvotes) # the average review gets more downvotes than upvotes!
    ratios = (adj_upvotes / adj_downvotes).sort_values(ascending = False)
    result = reviews.loc[ratios.index]
    if include_quality:
        result['quality'] = ratios
    return result

def review_summary(reviews: pd.DataFrame, name = 'Review Summary') -> pd.DataFrame:
    """
    Given a dataset of reviews, output summary statistics
    """
    count = len(reviews)
    users = len(reviews.user_id.unique())
    products = len(reviews.product_id.unique())
    return pd.Series(
        [count, users, products],
        index = ['reviews', 'users', 'products'],
        name = name
    )

def filter_reviews(reviews: pd.DataFrame, max_user_count = None, max_product_count = None) -> pd.DataFrame:
    """
    Filter reviews to encompass a limited number of users and/or products. Users and products will be filtered out 
    by how infrequently they appear in the dataset.

    This is intended to improve both the performance and relevance of recommendations by filtering low-quality data.
    """
    result = reviews.copy()
    if max_user_count != None:
        ratings_by_user = result.groupby('user_id')['rating'].count().sort_values(ascending = False)
        users = ratings_by_user[:max_user_count]
        result = result[result.user_id.isin(users.index)]
    if max_product_count != None:
        ratings_by_product = result.groupby('product_id')['rating'].count().sort_values(ascending = False)
        products = ratings_by_product[:max_product_count]
        result = result[result.product_id.isin(products.index)]
    return result