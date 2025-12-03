from __future__ import annotations

from typing import Optional

import numpy as np
import hdbscan
from sklearn.cluster import MiniBatchKMeans


class Clusterer:
    """Unified clustering interface supporting both KMeans and HDBSCAN"""
    
    def __init__(
        self,
        method: str = "hdbscan",  # "hdbscan" or "kmeans"
        n_clusters: int = 8,
        batch_size: int = 64,
        random_state: int = 42,
        min_cluster_size: int = 2,  # HDBSCAN parameter
        min_samples: Optional[int] = None,  # HDBSCAN parameter
    ) -> None:
        self.method = method
        self.n_clusters = n_clusters
        self.batch_size = batch_size
        self.random_state = random_state
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples

    def cluster_embeddings(
        self, embeddings: np.ndarray, n_clusters: Optional[int] = None
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Cluster embeddings using the specified method.
        Returns: (labels, centroids)
        - labels: cluster assignments (-1 for noise in HDBSCAN)
        - centroids: cluster centers (mean of points in each cluster)
        """
        if embeddings.size == 0:
            return np.array([]), np.empty((0,))

        if self.method == "hdbscan":
            return self._cluster_hdbscan(embeddings)
        else:
            return self._cluster_kmeans(embeddings, n_clusters)

    def _cluster_hdbscan(self, embeddings: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Cluster using HDBSCAN - automatically determines number of clusters"""
        min_samples = self.min_samples or self.min_cluster_size
        
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            min_samples=min_samples,
            metric="euclidean",
            cluster_selection_method="eom",  # "eom" or "leaf"
        )
        labels = clusterer.fit_predict(embeddings)
        
        # Calculate centroids for each cluster (excluding noise points with label -1)
        unique_labels = np.unique(labels)
        unique_labels = unique_labels[unique_labels != -1]  # Remove noise label
        
        if len(unique_labels) == 0:
            # All points are noise, return empty centroids
            return labels, np.empty((0, embeddings.shape[1]))
        
        centroids = []
        for label in unique_labels:
            cluster_points = embeddings[labels == label]
            centroid = cluster_points.mean(axis=0)
            centroids.append(centroid)
        
        centroids_array = np.array(centroids)
        return labels, centroids_array

    def _cluster_kmeans(
        self, embeddings: np.ndarray, n_clusters: Optional[int] = None
    ) -> tuple[np.ndarray, np.ndarray]:
        """Cluster using MiniBatchKMeans - requires number of clusters"""
        n_clusters = n_clusters or self.n_clusters
        n_clusters = min(n_clusters, embeddings.shape[0])
        
        model = MiniBatchKMeans(
            n_clusters=n_clusters,
            batch_size=self.batch_size,
            random_state=self.random_state,
            n_init="auto",
        )
        labels = model.fit_predict(embeddings)
        return labels, model.cluster_centers_


# Backward compatibility alias
KMeansClusterer = Clusterer
