# Presto
A high-performance product recommendation system handling millions of reviews within milliseconds.

## Overview
Presto is a product recommendation algorithm centered around user reviews, behaving similarly to a ‘users who liked this also liked’ section on an e-commerce site.

Presto is built for speed, running on a high-performance SQL database of over 7 million reviews of almost a million books and albums originating from different sources. Though nominally a recommendation algorithm project, Presto is actually a project centered around SQL database architecture and performance.

This project uses:
- Jupyter Lab Python notebooks
- Python’s [Anaconda](https://www.anaconda.com/download) ecosystem. Specifically:
  - Pandas
  - Matplotlib
  - Scipy
  - Scikit-Learn
- sqlite

## The Algorithm

Presto uses [Cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity)  to find recommendations for similar products.

To do: fill in details

## Datasets

To do: 

## Project Structure

### demo notebook
The demo notebook is a good starting point for exploring Presto from a user’s perspective. It is a Jupyter Lab notebook that simulates how Presto would operate in a production environment. Namely: given a search term and category, output a page full of product data including recommendations.

### numbered notebooks
Going through the numbered notebooks in order is a good way to explore Presto’s features and inner workings in more detail. These notebooks are designed to be user-facing and visual.

### presto/data
The data folder contains all logic related to database management and administration. This includes:
* The final sql database containing product and review data
* Raw data from various data sources
- Setting up the initial SQL database and defining its schema 
- Ingest logic for batch-inserting large volumes of review and product data into SQL
- Parsing logic to convert data from various sources into a format suitable for ingest
- Database administration tasks such as sanitizing data

This project enforces a clean separation between database administration and data analysis. The data folder does not contain any logic for exploring data, and the rest of the project does not conduct any database administration.

### presto/shared
This folder contains a variety of utilities to encapsulate shared logic between workflows. This includes but is not limited to:
- Abstraction layer for product recommendations and product/review queries
- Shared styling for data visualization (e.g. user review chart)
- User-facing string formattting

## Appendix: How Much Data Does A Production-Grade Music Recommender Need?

One lesson I learned thoroughly in this project is that high-quality recommendations require vast amounts of data. How much data exactly do we need for a product-grade recommender though?

On the upper end, I would estimate that **it takes on the order of tens of millions of user reviews to make a high-quality music recommendation system** that handles niche tastes and can compete with mainstream recommenders like those on Amazon or Spotify. This is more than is publicly available in any dataset. The exact number of ratings/reviews depends on many factors, most notably on how obscure your desired genres/artists are. 

This high-end estimation is based on a variety of data points:
- When I stress-tested the Presto database against the most niche artists I could think of, only 30% had 10 or more reviews and 40% had no reviews at all. Meanwhile the [MusicBrainz](https://musicbrainz.org/) database boasted comprehensive coverage of every niche artist I entered.
- **There are over 2.2 million unique music artists with published works**, according to the [MusicBrainz](https://musicbrainz.org/) database
- The Presto dataset of 5M album reviews covers about 120,000 artists. To do: how many exactly have 10 or more reviews
- I takes about 10 reviews make decent recommendations
- User reviews are very unevenly distributed, so achieving 10 reviews for each product will take far more than 10 x as many reviews as products

To do: low-end estimate


## 


