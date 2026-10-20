"""
Cyber Doppelgänger - Legitimate User Reference Profile
Safe Adaptive Behavioural Identity & Continuous User Verification

Represents the statistical baseline distribution of a legitimate user.
Serves as an immutable reference during Phase 4 inference.
Safe adaptation and baseline updates are strictly deferred to Phase 5.
"""

from typing import Dict, Any, List, Optional
import datetime
import numpy as np
import json
from pathlib import Path

from ml.preprocessing.feature_preprocessor import ALL_FEATURE_KEYS, FeaturePreprocessor


class ReferenceProfile:
    """
    Encapsulates distribution statistics for legitimate behavioral patterns.
    Features:
    - Robust statistics: Mean, Standard Deviation, Median, IQR (75th - 25th percentile).
    - Zero-variance detection to avoid degenerate scaling.
    - Deterministic JSON and dictionary export for transparency and auditability.
    """

    def __init__(
        self,
        user_id: str = "DEFAULT_USER",
        model_version: str = "1.0.0",
        schema_version: str = "2.0",
        training_data_version: str = "dataset-v1"
    ):
        self.user_id = user_id
        self.model_version = model_version
        self.schema_version = schema_version
        self.training_data_version = training_data_version
        self.created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        self.sample_count: int = 0
        self.feature_names: List[str] = list(ALL_FEATURE_KEYS)
        self.feature_means: Dict[str, float] = {}
        self.feature_stds: Dict[str, float] = {}
        self.feature_medians: Dict[str, float] = {}
        self.feature_iqrs: Dict[str, float] = {}
        self.zero_variance_features: List[str] = []
        self.session_identifiers: List[str] = []

    def fit_from_matrix(
        self,
        feature_matrix: np.ndarray,
        feature_names: List[str],
        session_ids: Optional[List[str]] = None
    ) -> "ReferenceProfile":
        """
        Computes robust distribution statistics from an unscaled feature matrix.
        """
        if feature_matrix.shape[0] == 0:
            raise ValueError("Cannot construct ReferenceProfile from empty feature matrix.")

        self.sample_count = int(feature_matrix.shape[0])
        self.feature_names = list(feature_names)
        self.session_identifiers = list(set(session_ids)) if session_ids else []

        for idx, feat_name in enumerate(self.feature_names):
            col = feature_matrix[:, idx]
            mean_val = float(np.mean(col))
            std_val = float(np.std(col))
            median_val = float(np.median(col))
            q75, q25 = np.percentile(col, [75, 25])
            iqr_val = float(q75 - q25)

            self.feature_means[feat_name] = round(mean_val, 4)
            self.feature_stds[feat_name] = round(std_val, 4)
            self.feature_medians[feat_name] = round(median_val, 4)
            self.feature_iqrs[feat_name] = round(iqr_val, 4)

            # Detect zero variance
            if std_val < 1e-6:
                self.zero_variance_features.append(feat_name)

        return self

    def fit_from_snapshots(
        self,
        snapshots: List[Dict[str, Any]],
        preprocessor: Optional[FeaturePreprocessor] = None
    ) -> "ReferenceProfile":
        """
        Extracts raw unscaled vectors and builds reference statistics.
        """
        if not snapshots:
            raise ValueError("Snapshot list cannot be empty.")

        prep = preprocessor or FeaturePreprocessor(schema_version=self.schema_version)
        vectors = [prep.extract_feature_vector(s) for s in snapshots]
        matrix = np.vstack(vectors)

        sessions = []
        for s in snapshots:
            sess_id = s.get("session_id") or s.get("sessionId")
            if sess_id:
                sessions.append(str(sess_id))

        return self.fit_from_matrix(matrix, prep.feature_names, sessions)

    def to_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable dictionary representation."""
        return {
            "user_id": self.user_id,
            "model_version": self.model_version,
            "schema_version": self.schema_version,
            "training_data_version": self.training_data_version,
            "created_at": self.created_at,
            "sample_count": self.sample_count,
            "feature_names": self.feature_names,
            "feature_means": self.feature_means,
            "feature_stds": self.feature_stds,
            "feature_medians": self.feature_medians,
            "feature_iqrs": self.feature_iqrs,
            "zero_variance_features": self.zero_variance_features,
            "session_identifiers": self.session_identifiers
        }

    def save_json(self, filepath: str) -> None:
        """Saves profile summary as JSON."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_json(cls, filepath: str) -> "ReferenceProfile":
        """Loads profile from JSON."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        profile = cls(
            user_id=data.get("user_id", "DEFAULT_USER"),
            model_version=data.get("model_version", "1.0.0"),
            schema_version=data.get("schema_version", "2.0"),
            training_data_version=data.get("training_data_version", "dataset-v1")
        )
        profile.created_at = data.get("created_at", profile.created_at)
        profile.sample_count = data.get("sample_count", 0)
        profile.feature_names = data.get("feature_names", list(ALL_FEATURE_KEYS))
        profile.feature_means = data.get("feature_means", {})
        profile.feature_stds = data.get("feature_stds", {})
        profile.feature_medians = data.get("feature_medians", {})
        profile.feature_iqrs = data.get("feature_iqrs", {})
        profile.zero_variance_features = data.get("zero_variance_features", [])
        profile.session_identifiers = data.get("session_identifiers", [])
        return profile
