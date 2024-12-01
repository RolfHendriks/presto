# BookMate
A product recommendation system based on user reviews.

## Overview
BookMate is a product recommendation algorithm built for a large-scale product database comprising millions of reviews and hundreds of thousands of products.

Though BookMate began as an exploration in recommender algorithms, it quickly turned into an exploration of designing and developing a performant SQL data architecture for large volumes of product data from disparate sources. This was partly because I found the idea of creating a backend architecture for e-commerce data inherently interesting and partly because I learned that creating a high-quality music recommendation system generally requires very large volumes of data:

## Information Overload: How Much Data Does A Recommender System Need?

I would estimate that **it takes on the order of tens of millions of user reviews to make a high-quality music recommendation system** that handles niche tastes, which is more than is publicly available in any dataset. The exact number of ratings/reviews depends on many factors, most notably on how obscure your desired genres/artists are. This estimation is based on a variety of data points:

- A dataset of 5M album reviews covers about 120,000 artists 
- **There are over 2.2 million unique music artists with published works**, according to the [MusicBrainz](https://musicbrainz.org/) database
- Of the 120,000 covered artists, only

## Data Sets
To do

## Project Structure

### data
The data folder contains all logic related to database management and administration. This includes:
- Logic for defining the initial database schema and setting up an SQL database. The SQL database is designed as a unified product database that can handle a variety of products from a variety of sources.
- Ingest logic for batch-inserting large volumes of review and product data into SQL
- Parsing logic to convert data from various sources into a format suitable for ingest
- Database administration tasks such as sanitizing data

The data folder also contains all raw data including the product SQL database and external datasets used. Because of the large volumes of data involved, these data files are not included in this shared repository.

### utils
This folder contains any general-purpose tools used to explore data or to provide recommendations.