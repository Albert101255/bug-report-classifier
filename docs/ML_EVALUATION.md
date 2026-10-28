# Machine Learning Model Evaluation & Methodology

## 1. Executive Summary & Honest Appraisal

Triage utilizes a pragmatic, transparent, and reproducible machine learning pipeline designed specifically for single-issue text classification.

> [!NOTE]
> **Resolution of Legacy Misrepresentations**: Earlier experimental iterations of this codebase advertised "Monte Carlo Dropout variance" and deep learning uncertainty estimations despite running a standard scikit-learn Logistic Regression classifier. In Triage v2.0, all misleading terminology has been removed. Uncertainty is truthfully derived from calibrated multiclass probabilities and normalized Shannon entropy.

---

## 2. Dataset Migration

To enforce the non-negotiable architectural rule excluding CSV processing from the active application, training data handling was migrated to standard JSON Lines:
- **Active Dataset**: `data/training_dataset.jsonl` (60 curated software engineering bug reports).
- **Format**: JSON Lines containing `{"subject": "...", "description": "...", "team": "..."}`.
- **Historical Archive**: `data/archive/demo_bug_reports.csv` safely preserved as a static research reference.

---

## 3. Baseline Model Architecture

The active production pipeline consists of:
1. **Feature Extraction**: `TfidfVectorizer`
   - Tokenization: English word boundaries, lowercased.
   - N-Gram Range: $(1, 2)$ unigrams and bigrams.
   - Sublinear TF scaling enabled ($1 + \log(\text{tf})$).
   - English stopwords removed.
   - Resulting feature space: 656 distinct n-grams.
2. **Classification**: `LogisticRegression`
   - Multi-class: Multinomial loss with softmax output probabilities.
   - Regularization: L2 penalty ($C = 1.0$).
   - Solver: L-BFGS.

---

## 4. Evaluation Metrics

Evaluated on stratified holdout test split:

| Metric | Score | Interpretation |
|---|---|---|
| **Accuracy** | 0.6667 (66.7%) | Substantially outperforms random choice ($10\%$) across 10 classes on compact dataset. |
| **Macro-F1** | 0.6133 (61.3%) | Balanced harmonic mean of precision and recall across all teams. |
| **Vocabulary Size** | 656 features | Compact, fast-loading, low-memory footprint ($< 2 \text{MB}$). |
| **Inference Latency** | $< 5 \text{ ms}$ | Capable of providing real-time debounced previews as engineers type. |

---

## 5. Confidence, Uncertainty & Threshold Routing

For an input text $x$:
1. The vectorizer transforms text into TF-IDF vector $v$.
2. The logistic regression outputs class probability distribution $P = [p_1, p_2, \dots, p_K]$ where $\sum p_k = 1$.
3. **Confidence Score**:
   $$\text{Confidence} = \max_{k} p_k$$
4. **Uncertainty Score**:
   $$\text{Uncertainty} = 1 - \text{Confidence}$$
5. **Shannon Entropy (Telemetry)**:
   $$H(x) = -\frac{1}{\ln(K)} \sum_{k=1}^K p_k \ln(p_k)$$

### Routing Policy
- If $\text{Confidence} \ge \text{High Threshold}$ (default $0.25$ for 10 classes) and auto-assign is enabled: Issue is assigned immediately to the predicted team.
- If $\text{Uncertainty} > \text{Low Threshold}$ (default $0.50$): Issue is routed to the **Triage Review Inbox** with `PENDING` review status for engineer approval.

---

## 6. Deterministic Fallback Engine

If model artifacts are missing or unreadable, the system automatically falls back to a deterministic rule-based keyword matcher mapping core terms (`postgres`, `jwt`, `k8s`, `stripe`, `react`, etc.) to respective teams. Telemetry explicitly tags these predictions with `engine: "rule-fallback"`.
