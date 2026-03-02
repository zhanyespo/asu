CSE 572 – Homework 3: Data Mining

Author: Zhandaulet Yespossynov
Course: CSE 572 – Data Mining
Semester: Fall 2025

This repository contains my full implementation and analysis for Homework 3, which is divided into two major components: a custom K-Means clustering system and a movie recommendation system based on the MovieLens dataset. Both parts follow the requirements from the assignment and include experiments, evaluations, and summarized findings.

1. K-Means Clustering

The first part of the project focuses on implementing the K-Means clustering algorithm completely from scratch. The implementation is modular and allows switching between several distance functions, which lets us study how different similarity measures influence clustering behavior on high-dimensional image data.

Distance Metrics

The algorithm supports three metrics:

Euclidean distance, the classic metric used in standard K-Means.

1 – Cosine similarity, which focuses on the angle between vectors rather than their magnitude.

1 – Generalized Jaccard similarity, which measures overlap between normalized vectors.

The dataset for this section comes from the provided kmeans_data.zip.

Stopping Criteria

K-Means was evaluated under three stopping rules:

The centroids no longer move.

The SSE value increases compared to the previous iteration.

A maximum iteration limit with 500 is reached.

These criteria let us compare how quickly each distance metric converges.

Outputs and Evaluation

The script produces the final centroids, the number of iterations needed for convergence, SSE values across iterations, and cluster assignments. Using majority voting, each cluster is given a label, allowing us to compute the predictive accuracy of each metric. In addition, several visualizations are generated, including SSE curves and accuracy comparisons.

Key Observations

Across all experiments, Euclidean distance consistently produced the highest SSE and the lowest accuracy, meaning it struggled to form meaningful clusters on this dataset. Cosine and Jaccard distances behaved more stably, with Jaccard achieving the highest accuracy overall. Euclidean converged the fastest but delivered the weakest results, while cosine required the most iterations to stabilize. These findings suggest that non-Euclidean similarity measures are better suited for high-dimensional, image-based data.

2. Recommendation System

The second part of the project implements a small recommendation system based on the MovieLens “ratings_small.csv” dataset. This component uses the surprise library to test several collaborative filtering models and analyze their performance under different similarity measures and neighborhood sizes.

Models Implemented

Three models were evaluated under 5-fold cross-validation:

User-Based Collaborative Filtering (UserCF)

Item-Based Collaborative Filtering (ItemCF)

Probabilistic Matrix Factorization (PMF) implemented via surprise.SVD(biased=False)

Evaluation Metrics

The accuracy of each model was measured using:

MAE (Mean Absolute Error)

RMSE (Root Mean Squared Error)

These metrics help compare how closely the predicted ratings match real user ratings.

Similarity Metric Experiments

UserCF and ItemCF were further tested using three similarity functions: cosine similarity, MSD (Mean Squared Difference), and Pearson correlation. The results were consistent across both models:

MSD gave the best performance,

Cosine came second,

Pearson had the highest error, especially for UserCF.

This shows that similarity choice plays an important role in collaborative filtering.

Tuning the Number of Neighbors (K)

To analyze the effect of neighborhood size, I tested K values of 5, 10, 20, 30, 40, 60, and 80.
UserCF performed best at K = 40, while ItemCF continued improving with larger neighborhoods and reached its lowest RMSE at K = 80. The two models therefore have different optimal K values, which reflects the fact that item-based patterns are often more stable than user behavior.

Summary of Results

Overall, PMF achieved the best accuracy, producing the lowest MAE and RMSE among all models. UserCF ranked second, and ItemCF third. MSD was the most effective similarity metric in both CF methods. Larger neighborhoods improved performance across the board, although the optimal K differs between UserCF and ItemCF. These results match typical behavior observed on sparse rating datasets like MovieLens.

3. Project Structure

.
├── README.md
├── data
│   ├── data.csv
│   ├── data_description.txt
│   ├── label.csv
│   └── ratings_small.csv
├── requirements.txt
├── results
│   ├── kmean
│   │   ├── cosine_results.txt
│   │   ├── dimennsional_data_converted.png
│   │   ├── euclidean_results.txt
│   │   ├── jaccard_results.txt
│   │   ├── pca_before_clustering.png
│   │   ├── pca_cosine.png
│   │   ├── pca_euclidean.png
│   │   ├── pca_explained_variance.png
│   │   ├── pca_jaccard.png
│   │   ├── silhouete_score.png
│   │   ├── summary_all.txt
│   │   └── tnse_visual.png
│   └── recsys
│       ├── baseline_models.csv
│       ├── k_tuning_itemcf.csv
│       ├── k_tuning_usercf.csv
│       └── similarity_metrics.csv
└── scripts
    ├── k-mean.ipynb
    ├── kmean_helper.py
    └── rec_sys.ipynb