# Pleasant Weather Prediction for European Cities

**Machine Learning Project | June 2025**  
*Author: Denis Kleptsov*

---

## Project Overview

ClimateWins aims to deliver robust, accurate, and interpretable machine learning models to predict "pleasant weather" days in European cities. These models support smarter planning for tourism, city management, and public services.

## Tools & Technologies

- Python (Jupyter Notebooks, pandas, scikit-learn)
- ML libraries: XGBoost, LightGBM, Optuna
- Data Viz: matplotlib, seaborn, Plotly
- Data Source: [ECA&D](https://www.ecad.eu/) (European Climate Assessment & Dataset)
- Version control: Git & GitHub

## Repository Structure

```text
├── notebooks/          <- Jupyter notebooks for each step of the analysis
├── data/               <- Data files (raw and processed)
├── results/            <- Outputs: maps, dashboard, etc.
├── scripts/            <- Reusable Python scripts (if any)
├── README.md           <- Project documentation (this file)
└── .gitignore          <- Git ignore rules
```

## Project Goals & Methodology

- **Data Processing**: Clean, standardize, and engineer features from raw ECA&D weather datasets (1960–2022).
- **Modeling**: Train and evaluate several models:
    - Baselines: Logistic Regression, Decision Trees
    - Advanced: Random Forest, Gradient Boosting, XGBoost, Neural Networks (MLP)
    - Feature selection (Mutual Information, RFE, Boruta)
- **Evaluation**: Multilabel metrics (Accuracy, F1, Hamming Loss, Jaccard Index)
- **Communication**: Share interpretable results and recommendations with stakeholders.
- **Reproducibility**: All analysis and modeling steps documented in Jupyter Notebooks.

## How to Reproduce

1. **Clone this repository**
    ```bash
    git clone https://github.com/YOUR_USERNAME/pleasant-weather-prediction.git
    cd pleasant-weather-prediction
    ```

2. **Set up your environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate (Windows)
    pip install -r requirements.txt
    ```

3. **Download the sample data**
    - Full datasets are not included due to size—use a sample for demo.

4. **Run the notebooks**
    - Open `notebooks/ml_model_training_v08_scalled.ipynb` in JupyterLab or VSCode.

5. **Explore results**
    - Output figures and summary tables are saved in `/results/`.

## Key Results

- **Gradient Boosting**: Highest multilabel accuracy (0.9899) and F1 (0.9889)
- Model performance summarized for each city (see notebook for details)
- All steps are transparent and reproducible

## Next Steps

- Implement advanced feature selection
- Build web dashboard/API for public predictions
- Expand interpretability and stakeholder communication

## Documentation

- [Project plan PDF](d05_results/07_06_ML_project_plan.pdf)
- [Project slides](05_results/ML_project_presentation.pdf)