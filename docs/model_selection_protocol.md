## Model selection criteria

The final model for each crop is selected according to a common set of predefined criteria.

The primary objective is the prediction of the conditional median yield. Therefore, **Q2 pinball loss on the 2016–2018 outer-validation period is the primary selection metric**.

For each crop, the eligible candidate with the lowest Q2 outer-validation loss is identified. A relative improvement of at least **5%** over the strongest alternative is considered practically meaningful.

If the difference between the best-performing candidates is below this threshold, the models are treated as practically equivalent and the following tie-breaking criteria are applied, in order:

1. **Temporal robustness**  
   Preference is given to the model showing more consistent performance across the chronological development folds.

2. **Quantile behaviour**  
   Where Q1 and Q3 predictions are available, preference is given to models with more coherent performance across quantiles, satisfactory empirical coverage, and no relevant quantile-crossing issues.

3. **Parsimony**  
   If predictive performance remains effectively equivalent, preference is given to the simpler specification, considering the number of predictors, preprocessing complexity, model complexity, and dependence on tuning.

4. **Reproducibility**  
   Preference is given to models that can be reproduced more easily and reliably, with lower dependence on external services, authenticated APIs, or additional computational infrastructure.

If no meaningful distinction emerges after applying these criteria, the simpler reference specification is retained.

The same selection rule is applied independently to **Durum wheat, Soft wheat, and Grain maize**.

Once the winning specification for each crop has been selected, its model family, feature set, preprocessing steps, and relevant hyperparameters are frozen. The selected model is then refitted using all admissible observations prior to the test period and evaluated once on the untouched **2019–2022 final test set**.

The final test set is used exclusively for performance assessment and does not influence model selection.