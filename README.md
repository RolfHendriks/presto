# Presto
A high-performance book and music recommendation system handling millions of reviews within milliseconds.

## Overview
Presto is a product recommendation algorithm centered around user reviews - like a ‘users who liked this also liked’ section on an e-commerce site.

Presto is built for speed, running on a high-performance SQL database of over 7 million reviews of almost a million books and albums originating from different sources. Though nominally a recommendation algorithm project, Presto is actually a project centered around SQL database architecture and performance.

## Key Features
- Search through millions of reviews in milliseconds
- Search by book title, album title, author, or artist
- Find product recommendations based on **[cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity)** of user reviews
- Search capabilities including:
  - **Diacritic insensitivity** (e.g. 'Celine Dion' matches 'Céline Dion'. Important in all non-English countries)
  - Insensitivity to filler words (e.g. 'The Hunger Games' matches 'Hunger Games')
  - Insensitivity to name ordering (e.g. 'george orwell' matches 'Orwell, George')
- Flexible high-performance **SQL backend** that can handle products of various types from various sources
- Disambiguation for multiple editions of the same product

## The Algorithm

The simplest way to understand Presto! is to see it from a user's perspective. This project includes a user-facing [demo notebook](./demo.ipynb) that can input a book, album, author, or artist to search and output a matching result and recommendation:

![Presto Demo](/images/demo.png)

The recommendation portion of the algorithm is based on [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity) of user reviews. Cosine similarities work by first creating a table of user reviews by product, then evaluating the pairwise similarities of every two possible products based on user ratings. The final recommendations are the products whose user ratings are closest to the searched product:

![Recommendations Explained](/images/recommendations.png)

Recommendation algorithms are a remarkable and simple example of emergent intelligence. Although Presto! only looks at product ids, user ids, and ratings (it does not even know the name of the product being compared, nor anything else about it), its recommendations pick up on works:
- by the same artist/author
- by aliases of the same artist
- of the same genre
- created at a similar time
- having a similar soundscape
- being a direct influence on the artist
- etc

For more details about how Presto!s recommendations work, see the [Recommendations Notebook](/presto/04-recommendations.ipynb)


## The Data

Presto! stands on the shoulders of giants, and on over 7 gigabytes of product and review data pulled from different sources:

![Dataset](/images/products.png)

The size of Presto!s dataset was borne of the humbling realization that creating a recommendation system that can compete with mainstream algorithms like Amazon or Spotify takes enormous amounts of data - more than is publicly available in any dataset. Although Presto!s data set is large enough to handle well-known artists and authors with excellence, only a small percentage of products have enough user reviews to make high-quality recommendations. This is despite the majority of the project being spent on the dataset:

![Reviews Per Product](/images/review_coverage.png)

### Data Sources

The fully developed product makes use of three excellent sources of data:

### McAuley Labs Amazon Review Dataset

https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023

Used for Presto! music recommendations. McAuley Labs features by far the most extensive user review dataset seen during Presto!s research phase. The full dataset comprises over half a billion reviews from 34 categories, including but nowhere near limited to music.

### Amazon Books Reviews Kaggle Dataset

https://www.kaggle.com/datasets/mohamedbakhet/amazon-books-reviews

Used for Presto! book recommendations. Though not quite as extensive as the McAuley Labs dataset, this dataset featured richer and more easily parsable data per book. Pulling from two different datasets also validated the idea of a flexible product backend and ingest pipeline.

### MusicBrainz Database

https://musicbrainz.org/doc/Development/JSON_Data_Dumps

MusicBrainz is the Wikipedia of music data, featuring comprehensive up-to-date coverage of the genres, artists, albums, and songs of the world. Though Presto! product recommendations do not directly use MusicBrainz, MusicBrainz was used to help clean data ingested into the database and to research the landscape of music data.

## Project Structure

### demo notebook
The demo notebook is a good starting point for exploring Presto from a user’s perspective. It is a Jupyter Lab notebook that simulates how Presto would operate in a production environment. Namely: given a search term and category, output a page full of product data including recommendations.

### numbered notebooks
Going through the numbered notebooks in order is a good way to explore Presto’s features and inner workings in more detail. These notebooks are designed to be user-facing and visual.

### data folder
The data folder contains all logic related to database management and administration. This includes:
- The final sql database containing product and review data
- Raw data from various data sources
- Setting up the initial SQL database and defining its schema 
- Ingest logic for batch-inserting large volumes of review and product data into SQL
- Parsing logic to convert data from various sources into a format suitable for ingest
- Database administration tasks such as sanitizing data

This project enforces a clean separation between database administration and data analysis. The data folder does not contain any logic for exploring data, and the rest of the project does not conduct any database administration.

### shared folder
This folder contains a variety of utilities to encapsulate shared logic between workflows. This includes but is not limited to:
- Abstraction layer for product recommendations and product/review queries
- Shared styling for data visualization (e.g. user review chart)
- User-facing string formattting

## Getting Started

Running Presto! requires a Python environment with:
- numpy
- matplotlib
- Jupyter Labs / Python Notebooks
- Scikit Learn
- Spacy

This setup is most easily achieved by running an Anaconda Python installation and installing Spacy.

Because Presto!s product database exceeds github storage limits by a wide margin, successfuly running Presto! requires extensive one-time setup to create the Presto! product database. The data/ingest folder contains notebooks with instructions on how to configure and populate a Presto! product and review database.
