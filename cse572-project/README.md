# Loan Approval Prediction — CSE 572 Final Project

This repo contains the code for our CSE 572 (Data Mining) final project.
We built a supervised ML pipeline to predict loan approvals using the **Kaggle Playground S4E10** dataset.
The notebooks follow the same steps described in the final report: preprocessing, feature engineering, model comparison, imbalance handling, and threshold tuning.

---

## Project Summary

The task is a binary classification problem with **strong class imbalance** (only ~14% approved loans).
We dealt with skewed numeric values, outliers, and mixed feature types.

Main pipeline stages:

* exploratory analysis
* cleaning unrealistic values
* clipping outliers
* log transforms
* one-hot encoding
* RobustScaler / StandardScaler
* engineered features (loan stress ratio, log income, log loan)
* training Logistic Regression, RF, XGBoost, CatBoost
* stratified 5-fold CV
* threshold tuning for recall/F1

CatBoost was the strongest and most stable model (AUC ≈ 0.939, F1 ≈ 0.74).

---

## Repository Structure

```
data/
    train.csv
Loan.ipynb
loan_predict.ipynb
requirements.txt
README.md
```

**Loan.ipynb** – includes a full exploratory workflow with data inspection, visualizations, preprocessing steps, and model training for Logistic Regression, Random Forest, XGBoost, and CatBoost. It also provides ROC curves, confusion matrices, feature-importance plots, and ensemble testing to compare how different approaches behave on the dataset.

**loan_predict.ipynb** – contains the complete end-to-end modeling pipeline, including data cleaning, outlier handling, log transformations, engineered features (loan stress and ratios), encoding, scaling, stratified cross-validation, and threshold tuning. It also generates ROC/PR curves, evaluation metrics, prediction outputs, and represents the final methodology used in the report.

---

## Dataset Notes

* Training rows: **58,645**
* Test rows: **39,098** (no labels and not used)
* Target: `loan_status` (1 = approved)

Since Kaggle’s test set does not contain labels and is optional for the final project, we removed it from the repo.

---

## How to Run

Install deps:

```
pip install -r requirements.txt
```

Open the main notebook:

```
jupyter notebook loan_predict.ipynb
```

Running it will clean the data, engineer features, train/evaluate models, and create prediction files.

---

## Methods Used

### Cleaning & Preprocessing

* fixed unrealistic ages
* corrected employment-length errors
* clipped income outliers
* log transforms for financial fields
* RobustScaler + StandardScaler
* one-hot encoding

### Feature Engineering

* **loan_stress** = log(loan_amount) / log(person_income)
* log income, log loan
* clipped versions of financial variables

### Models

* Logistic Regression, Random Forest, XGBoost, CatBoost
* CatBoost selected as final model
* Best threshold found: **0.39**

### Imbalance Handling

* class weights
* stratified folds
* PR-curve-based threshold tuning
* recall + F1 prioritized

---

## Contributors

* **Zhandaulet Yespossynov**
* **Ashmit Pai**