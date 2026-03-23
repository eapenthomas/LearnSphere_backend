import os
import joblib
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Model file path
MODEL_PATH = os.path.join(os.path.dirname(__file__), "cluster_model.pkl")

# Global variables for the loaded model and scaler
_cluster_model = None
_cluster_scaler = None

def load_cluster_model():
    """Load the K-Means model and scaler once at startup."""
    global _cluster_model, _cluster_scaler
    try:
        if os.path.exists(MODEL_PATH):
            data = joblib.load(MODEL_PATH)
            _cluster_model = data.get("model")
            _cluster_scaler = data.get("scaler")
        else:
            _cluster_model = None
            _cluster_scaler = None
    except Exception as e:
        print(f"Error loading cluster model: {e}")
        _cluster_model = None
        _cluster_scaler = None

# Initial load
load_cluster_model()

def is_clustering_available() -> bool:
    """Check if the clustering model has been trained and loaded."""
    return _cluster_model is not None and _cluster_scaler is not None

def predict_cluster(feature_vector: np.ndarray) -> int:
    """
    Predict the cluster label for a given feature vector.
    Assumes load_cluster_model() was called and successful.
    """
    if not is_clustering_available():
        return -1
    
    # Reshape for single prediction: (1, n_features)
    reshaped = feature_vector.reshape(1, -1)
    
    # Scale and predict
    scaled = _cluster_scaler.transform(reshaped)
    label = _cluster_model.predict(scaled)[0]
    return int(label)

def cluster_name(label: int, n_clusters: int) -> str:
    """
    Map cluster label back to a human-readable name.
    If K=3, an example mapping might be:
    Label 0 -> "Balanced Learner"
    Label 1 -> "High Achiever" 
    Label 2 -> "Developing Learner"
    
    NOTE: The exact meaning of the clusters depends on the centroids after training.
    For this generic implementation without analyzing actual real-world centroids,
    we'll map 3 common profiles.
    """
    if not is_clustering_available() or label == -1:
        return ""
    
    # Simplified mapping (in a real app, this would inspect centroid values)
    # E.g., highest overall score -> High Achiever, etc.
    if n_clusters == 3:
        names = {
            0: "Balanced Learner",
            1: "High Achiever",
            2: "Developing Learner"
        }
        return names.get(label, f"Cluster {label}")
        
    return f"Profile Type {label}"

def build_extended_features(
    skill_vector: np.ndarray, 
    avg_quiz: float, 
    completion_rate: float, 
    avg_assign: float
) -> np.ndarray:
    """
    Constructs the feature array matching the training schema.
    Schema: [skill_vec_1, ..., skill_vec_n, avg_quiz, comp_rate, avg_assign]
    """
    # Append the aggregated metrics to the existing skill vector
    extended = np.append(skill_vector, [avg_quiz, completion_rate, avg_assign])
    return extended
