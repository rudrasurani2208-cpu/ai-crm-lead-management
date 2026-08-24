import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    roc_auc_score
)

# --------------------------------------------------
# CREATE DEMO HISTORICAL LEAD DATA
# --------------------------------------------------

np.random.seed(42)

num_leads = 1000

sources = [
    "Website",
    "Instagram",
    "LinkedIn",
    "Referral",
    "Cold Call",
    "Other"
]

data = []

for _ in range(num_leads):

    budget = np.random.randint(5000, 200000)
    interest = np.random.randint(1, 11)
    source = np.random.choice(sources)

    # Create realistic conversion probability
    probability = 0.10

    probability += interest * 0.05

    if budget >= 100000:
        probability += 0.15
    elif budget >= 50000:
        probability += 0.08

    if source == "Referral":
        probability += 0.15
    elif source in ["LinkedIn", "Website"]:
        probability += 0.08
    elif source == "Cold Call":
        probability -= 0.05

    probability = min(max(probability, 0.05), 0.95)

    converted = np.random.binomial(
        1,
        probability
    )

    data.append(
        {
            "budget": budget,
            "interest": interest,
            "source": source,
            "converted": converted
        }
    )


df = pd.DataFrame(data)

print("Dataset created successfully.")
print(df.head())

# --------------------------------------------------
# FEATURES AND TARGET
# --------------------------------------------------

X = df[
    [
        "budget",
        "interest",
        "source"
    ]
]

y = df["converted"]

# --------------------------------------------------
# TRAIN TEST SPLIT
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# --------------------------------------------------
# PREPROCESSING
# --------------------------------------------------

numeric_features = [
    "budget",
    "interest"
]

categorical_features = [
    "source"
]

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            StandardScaler(),
            numeric_features
        ),
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        )
    ]
)

# --------------------------------------------------
# MACHINE LEARNING PIPELINE
# --------------------------------------------------

model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000
            )
        )
    ]
)

# --------------------------------------------------
# TRAIN MODEL
# --------------------------------------------------

model.fit(
    X_train,
    y_train
)

# --------------------------------------------------
# MODEL EVALUATION
# --------------------------------------------------

predictions = model.predict(
    X_test
)

probabilities = model.predict_proba(
    X_test
)[:, 1]

accuracy = accuracy_score(
    y_test,
    predictions
)

roc_auc = roc_auc_score(
    y_test,
    probabilities
)

print("\n---------------------------")
print("MODEL PERFORMANCE")
print("---------------------------")

print(
    f"Accuracy: {accuracy:.2%}"
)

print(
    f"ROC-AUC: {roc_auc:.3f}"
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions
    )
)

# --------------------------------------------------
# SAVE TRAINED MODEL
# --------------------------------------------------

joblib.dump(
    model,
    "lead_conversion_model.pkl"
)

print(
    "\nModel saved successfully as "
    "'lead_conversion_model.pkl'"
)
