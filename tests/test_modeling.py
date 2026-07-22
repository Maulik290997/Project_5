import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
import pytest

from tellco.modeling import StandardScaler, PCA, KMeans, LinearRegression, euclidean_distance


def test_standard_scaler_zero_mean_unit_var():
    X = np.array([[1.0, 10.0], [2.0, 20.0], [3.0, 30.0]])
    Xs = StandardScaler().fit_transform(X)
    assert np.allclose(Xs.mean(axis=0), 0, atol=1e-8)
    assert np.allclose(Xs.std(axis=0), 1, atol=1e-8)


def test_pca_reduces_dimensions_and_orders_variance():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(200, 5))
    X[:, 1] = X[:, 0] * 3 + 0.01 * rng.normal(size=200)  # correlated column
    pca = PCA(n_components=2).fit(X)
    Xp = pca.transform(X)
    assert Xp.shape == (200, 2)
    assert pca.explained_variance_ratio_[0] >= pca.explained_variance_ratio_[1]


def test_kmeans_recovers_well_separated_clusters():
    rng = np.random.default_rng(1)
    cluster_a = rng.normal(loc=0, scale=0.1, size=(30, 2))
    cluster_b = rng.normal(loc=20, scale=0.1, size=(30, 2))
    X = np.vstack([cluster_a, cluster_b])
    km = KMeans(n_clusters=2, n_init=5, random_state=1).fit(X)
    labels_a = km.labels_[:30]
    labels_b = km.labels_[30:]
    assert len(set(labels_a)) == 1
    assert len(set(labels_b)) == 1
    assert labels_a[0] != labels_b[0]


def test_linear_regression_recovers_known_coefficients():
    rng = np.random.default_rng(2)
    X = rng.normal(size=(500, 2))
    y = 2 * X[:, 0] - 3 * X[:, 1] + 5
    lr = LinearRegression().fit(X, y)
    assert lr.coef_ == pytest.approx([2, -3], abs=1e-6)
    assert lr.intercept_ == pytest.approx(5, abs=1e-6)
    assert lr.score(X, y) == pytest.approx(1.0, abs=1e-6)


def test_euclidean_distance_matches_manual_computation():
    X = np.array([[0.0, 0.0], [3.0, 4.0]])
    point = np.array([0.0, 0.0])
    d = euclidean_distance(X, point)
    assert d[0] == pytest.approx(0.0)
    assert d[1] == pytest.approx(5.0)
