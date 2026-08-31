import numpy as np, pandas as pd, matplotlib.pyplot as plt
import math,random,warnings
from scipy.stats import pearsonr
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.feature_selection import (SelectKBest, chi2, f_classif, RFE, mutual_info_classif, SelectFromModel, SelectPercentile, GenericUnivariateSelect, RFECV)

warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', None)
np.random.seed(42)

# Data loading and preprocessing
df = pd.read_csv('airline.csv')
df.drop(["Unnamed: 0", "id"], axis=1, inplace=True)
df["Arrival Delay in Minutes"] = df["Arrival Delay in Minutes"].fillna(df["Arrival Delay in Minutes"].mean())
df = df.sample(n=1000, random_state=42)
le = LabelEncoder()
cat_cols = ["Gender", "Customer Type", "Type of Travel", "Class", "satisfaction"]
for label in cat_cols:
    df[label] = le.fit_transform(df[label])
# Drop outliers
outliers_distance = df[df['Flight Distance'] > 3736.5]
df.drop(outliers_distance.index, inplace=True)
outliers_departure = df[df['Departure Delay in Minutes'] > 800]
df.drop(outliers_departure.index, inplace = True)
outlier_arrival = df[df['Arrival Delay in Minutes'] > 650]
df.drop(outlier_arrival.index, inplace = True)

scaler = StandardScaler()
for column in df.columns:
    if df[column].dtype == type(float) or df[column].dtype == type(int):
        df[column] = scaler.fit_transform(df[column].values.reshape(-1, 1))

X = df.drop(columns=['satisfaction'])
y = df['satisfaction']
# Assuming X, y are defined and preprocessed
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

def train_on_selected_features(X_train, y_train, X_test, y_test, feature_indices):
    #return True performance on test dataset
    feature_indices = [feature_indices] if isinstance(feature_indices, int) else feature_indices
    model = GradientBoostingClassifier(random_state=42)
    model.fit(X_train.iloc[:, feature_indices], y_train)
    accuracy = accuracy_score(y_test, model.predict(X_test.iloc[:, feature_indices]))
    return accuracy

def generate_error(eta_u,eta_o):
  rnd=random.uniform(-math.log(eta_u), math.log(eta_o))
  error=math.e**rnd
  return error

def result_with_new_feature(X_train, y_train, X_test, y_test, current_features, new_feature):
    extended_feature_set = current_features + [new_feature] if current_features else [new_feature]
    extended_accuracy = train_on_selected_features(X_train, y_train, X_test, y_test, extended_feature_set)
    return extended_accuracy

def oracle_simulation(X_train, y_train, X_test, y_test, K, eta_u, eta_o):
  selected_features = []
  available_features = set(range(X_train.shape[1]))  # Start with all features as available
  Accuracy_Results=[]
  while len(selected_features) < K:
    # Recalculate gains for all remaining available features using list comprehension
    base_accuracy = train_on_selected_features(X_train, y_train, X_test, y_test, selected_features) if selected_features else 0
    feature_performance=[] #[feature,etd_acc,actual_acc,predict_acc]
    for feature in available_features:
      extend_accuracy=result_with_new_feature(X_train, y_train, X_test, y_test, selected_features, feature)
      actual_gain=extend_accuracy-base_accuracy
      predict_gain=actual_gain*generate_error(eta_u, eta_o)
      feature_performance.append((feature,extend_accuracy,actual_gain,predict_gain))
    #sort features based on predict_gain
    feature_performance.sort(reverse=True, key=lambda x: x[3])
    selected_feature=feature_performance[0][0]
    selected_features.append(selected_feature)
    available_features.remove(selected_feature)  # Remove the selected feature to avoid reselection
    print("new feature selected (idx,exp_result,actual_gain,predict_gain):", feature_performance[0])
    new_accuracy=train_on_selected_features(X_train, y_train, X_test, y_test, selected_features) if selected_features else 0
    print("performance with ",len(selected_features)," features: ", new_accuracy)
    Accuracy_Results.append(new_accuracy)
  return Accuracy_Results

def evaluate_with_oracle_and_feature_importance_baseline(X, y, X_train, y_train, X_test, y_test, max_K, eta_u, eta_o):
    # Store accuracies for each method
    multi_oracle_accuracies = [[] for _ in range(max_K)]

    def collect_oracle(single_experiment, multi_experiment):
        for i in range(len(multi_experiment)):
            multi_experiment[i].append(single_experiment[i])

    repeating = 5 # Number of simulations per eta value

    for _ in range(repeating):
        oracle_accuracies = oracle_simulation(X_train, y_train, X_test, y_test, max_K, eta_u, eta_o)  # Oracle method
        collect_oracle(oracle_accuracies, multi_oracle_accuracies)

    baseline_accuracies = []
    rfe_accuracies = []
    mutual_info_accuracies = []
    extra_trees_accuracies = []
    K_values = list(range(1, max_K + 1))

    for K in K_values:
        # Baseline method (SelectKBest)
        selector = SelectKBest(f_classif, k=K)
        X_train_baseline = selector.fit_transform(X_train, y_train)
        X_test_baseline = selector.transform(X_test)
        classifier_baseline = GradientBoostingClassifier(random_state=42)
        classifier_baseline.fit(X_train_baseline, y_train)
        y_pred_baseline = classifier_baseline.predict(X_test_baseline)
        baseline_accuracies.append(accuracy_score(y_test, y_pred_baseline))

        # RFE method
        estimator = DecisionTreeClassifier(random_state=42)
        selector_rfe = RFE(estimator, n_features_to_select=K, step=1)
        X_train_rfe = selector_rfe.fit_transform(X_train, y_train)
        X_test_rfe = selector_rfe.transform(X_test)
        classifier_rfe = GradientBoostingClassifier(random_state=42)
        classifier_rfe.fit(X_train_rfe, y_train)
        y_pred_rfe = classifier_rfe.predict(X_test_rfe)
        rfe_accuracies.append(accuracy_score(y_test, y_pred_rfe))

        # Mutual Information method
        mutual_info = mutual_info_classif(X_train, y_train)
        top_features_indices = np.argsort(mutual_info)[-K:]
        X_train_mi = X_train.iloc[:, top_features_indices]
        X_test_mi = X_test.iloc[:, top_features_indices]

        # Training GradientBoostingClassifier with the selected features
        classifier_mi = GradientBoostingClassifier(random_state=42)
        classifier_mi.fit(X_train_mi, y_train)
        y_pred_mi = classifier_mi.predict(X_test_mi)

        # Evaluating the performance
        mutual_info_accuracies.append(accuracy_score(y_test, y_pred_mi))

        # Extra Trees method
        model = ExtraTreesClassifier()
        model.fit(X_train, y_train)
        feat_importances = pd.Series(model.feature_importances_, index=X_train.columns)
        selected_features_extra_trees = feat_importances.nlargest(K).index
        classifier_extra_trees = GradientBoostingClassifier(random_state=42)
        classifier_extra_trees.fit(X_train[selected_features_extra_trees], y_train)
        y_pred_extra_trees = classifier_extra_trees.predict(X_test[selected_features_extra_trees])
        extra_trees_accuracies.append(accuracy_score(y_test, y_pred_extra_trees))

    # Plotting results
    plt.figure(figsize=(10, 8))

    oracle_medians = [np.median(data) for data in multi_oracle_accuracies]
    oracle_lower = [np.percentile(data, 25) for data in multi_oracle_accuracies]
    oracle_upper = [np.percentile(data, 75) for data in multi_oracle_accuracies]

    # Ensure non-negative error bars
    lower_errors = [max(0, median - low) for median, low in zip(oracle_medians, oracle_lower)]
    upper_errors = [max(0, high - median) for median, high in zip(oracle_medians, oracle_upper)]
    errors = [lower_errors, upper_errors]

    plt.errorbar(K_values, oracle_medians, yerr=errors, fmt='o-', color='#3B5387', label='SOP-Greedy', linestyle='-', capsize=5, capthick=2, linewidth=4, markersize=8)
    plt.plot(K_values, baseline_accuracies, '^-', color='#00C1C2', label='SelectKBest', linewidth=4, markersize=8)
    plt.plot(K_values, rfe_accuracies, 'd-', color='#6A5DC4', label='RFE', linewidth=4, markersize=8)
    plt.plot(K_values, extra_trees_accuracies, 's-', color='#D2AA3A', label='Extra Trees', linewidth=4, markersize=8)
    plt.plot(K_values, mutual_info_accuracies, '*-', color='#47AF79', label='Mutual Information', linewidth=4, markersize=8)

    plt.xlabel('Number of Features (K)', fontsize=26)
    plt.ylabel('Accuracy', fontsize=26)
    plt.ylim([0.5, 1.0])
    plt.xticks(range(1, max_K + 1), fontsize=26)
    plt.yticks(np.linspace(0.5, 1.0, 6), fontsize=26)
    plt.legend(fontsize=20, loc='lower right')

    plt.grid(True)

    # Save the figure as a PDF
    plt.savefig(r'C:\Users\1\Desktop\predictive_performance_airline3.pdf', format='pdf', bbox_inches='tight')
    plt.show()


evaluate_with_oracle_and_feature_importance_baseline(X, y, X_train, y_train, X_test, y_test, 7, 1.5, 1.5)