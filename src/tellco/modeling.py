"""
Lightweight numpy-only implementations of the modeling primitives this
project needs (StandardScaler, PCA, K-Means, Linear Regression).

Why not scikit-learn? This sandbox has no outbound package-index access and
scikit-learn/scipy are not preinstalled. The APIs below intentionally mirror
scikit-learn's fit/transform/predict conventions so this module is a drop-in
stand-in -- in a normal dev environment you would simply
`from sklearn.cluster import KMeans` etc. instead. Swap-in instructions are
in the README.
"""
from __future__ import annotations

import numpy as np


class StandardScaler:
    """Zero-mean, unit-variance scaling, fit on training data."""

    def fit(self, X: np.ndarray) -> "StandardScaler":
        X = np.asarray(X, dtype=float)
        self.mean_ = X.mean(axis=0)
        self.scale_ = X.std(axis=0, ddof=0)
        self.scale_[self.scale_ == 0] = 1.0
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        return (X - self.mean_) / self.scale_

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        return self.fit(X).transform(X)


class PCA:
    """Principal Component Analysis via eigendecomposition of the covariance matrix."""

    def __init__(self, n_components: int = 2):
        self.n_components = n_components

    def fit(self, X: np.ndarray) -> "PCA":
        X = np.asarray(X, dtype=float)
        self.mean_ = X.mean(axis=0)
        Xc = X - self.mean_
        cov = np.cov(Xc, rowvar=False)
        eigvals, eigvecs = np.linalg.eigh(cov)
        order = np.argsort(eigvals)[::-1]
        eigvals, eigvecs = eigvals[order], eigvecs[:, order]
        self.explained_variance_ = eigvals[: self.n_components]
        self.explained_variance_ratio_ = eigvals[: self.n_components] / eigvals.sum()
        self.components_ = eigvecs[:, : self.n_components].T
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        return (X - self.mean_) @ self.components_.T

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        return self.fit(X).transform(X)


class KMeans:
    """Lloyd's-algorithm K-Means with k-means++ initialization and multiple restarts."""

    def __init__(self, n_clusters: int = 3, n_init: int = 10, max_iter: int = 300, random_state: int = 42):
        self.n_clusters = n_clusters
        self.n_init = n_init
        self.max_iter = max_iter
        self.random_state = random_state

    def _kmeans_plus_plus_init(self, X: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        n_samples = X.shape[0]
        centers = [X[rng.integers(n_samples)]]
        for _ in range(1, self.n_clusters):
            dist_sq = np.min(
                [np.sum((X - c) ** 2, axis=1) for c in centers], axis=0
            )
            probs = dist_sq / dist_sq.sum()
            next_idx = rng.choice(n_samples, p=probs)
            centers.append(X[next_idx])
        return np.array(centers)

    def _single_run(self, X: np.ndarray, rng: np.random.Generator):
        centers = self._kmeans_plus_plus_init(X, rng)
        labels = np.zeros(X.shape[0], dtype=int)
        for _ in range(self.max_iter):
            dists = np.linalg.norm(X[:, None, :] - centers[None, :, :], axis=2)
            new_labels = dists.argmin(axis=1)
            if np.array_equal(new_labels, labels) and _ > 0:
                labels = new_labels
                break
            labels = new_labels
            for k in range(self.n_clusters):
                if np.any(labels == k):
                    centers[k] = X[labels == k].mean(axis=0)
        dists = np.linalg.norm(X[:, None, :] - centers[None, :, :], axis=2)
        inertia = np.sum(dists[np.arange(len(X)), labels] ** 2)
        return centers, labels, inertia

    def fit(self, X: np.ndarray) -> "KMeans":
        X = np.asarray(X, dtype=float)
        rng = np.random.default_rng(self.random_state)
        best = None
        for i in range(self.n_init):
            centers, labels, inertia = self._single_run(X, rng)
            if best is None or inertia < best[2]:
                best = (centers, labels, inertia)
        self.cluster_centers_, self.labels_, self.inertia_ = best
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        dists = np.linalg.norm(X[:, None, :] - self.cluster_centers_[None, :, :], axis=2)
        return dists.argmin(axis=1)

    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        return self.fit(X).labels_


def elbow_method(X: np.ndarray, k_range=range(1, 9), random_state: int = 42):
    """Return list of (k, inertia) for the elbow-method plot."""
    results = []
    for k in k_range:
        km = KMeans(n_clusters=k, n_init=5, random_state=random_state).fit(X)
        results.append((k, km.inertia_))
    return results


class LinearRegression:
    """Ordinary least squares via the normal equation (numpy.linalg.lstsq)."""

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LinearRegression":
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        X_design = np.hstack([np.ones((X.shape[0], 1)), X])
        coef, residuals, rank, sv = np.linalg.lstsq(X_design, y, rcond=None)
        self.intercept_ = coef[0]
        self.coef_ = coef[1:]
        self._fitted_X, self._fitted_y = X, y
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        return self.intercept_ + X @ self.coef_

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        y = np.asarray(y, dtype=float)
        y_pred = self.predict(X)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)
        return 1 - ss_res / ss_tot if ss_tot > 0 else 0.0


def euclidean_distance(X: np.ndarray, point: np.ndarray) -> np.ndarray:
    """Row-wise Euclidean distance from each row of X to a single reference point."""
    X = np.asarray(X, dtype=float)
    point = np.asarray(point, dtype=float)
    return np.linalg.norm(X - point, axis=1)
