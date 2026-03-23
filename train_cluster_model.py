import os
import joblib
import numpy as np
import logging
from supabase import create_client, Client
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Model file path
MODEL_PATH = os.path.join(os.path.dirname(__file__), "cluster_model.pkl")

def get_supabase_client() -> Client:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase configuration")
    return create_client(supabase_url, supabase_key)

def fetch_training_data():
    """Fetches all student quiz and assignment data across all courses to build training vectors."""
    logger.info("Fetching data from Supabase...")
    supabase = get_supabase_client()
    
    # 1. Get all enrollments
    enroll_res = supabase.table("enrollments").select("student_id, course_id").execute()
    enrollments = enroll_res.data or []
    if not enrollments:
        logger.warning("No enrollments found.")
        return [], []
        
    # Group by course to process course-by-course
    course_students = {}
    for e in enrollments:
        cid = e["course_id"]
        if cid not in course_students:
            course_students[cid] = []
        course_students[cid].append(e["student_id"])
        
    # 2. Get all quizzes and assignments
    quizzes_res = supabase.table("quizzes").select("id, course_id").execute()
    assignments_res = supabase.table("assignments").select("id, course_id, max_score").execute()
    
    quizzes = quizzes_res.data or []
    assignments = assignments_res.data or []
    
    # 3. Get all submissions
    qs_res = supabase.table("quiz_submissions").select("student_id, quiz_id, score, total_marks").execute()
    as_res = supabase.table("assignment_submissions").select("student_id, assignment_id, score").execute()
    
    quiz_subs = qs_res.data or []
    asgn_subs = as_res.data or []
    
    # Pre-index for fast lookup
    qs_map = {} # (student_id, quiz_id) -> normalized score
    for s in quiz_subs:
        if s["total_marks"] > 0:
            qs_map[(s["student_id"], s["quiz_id"])] = (s["score"] or 0) / s["total_marks"]
            
    as_map = {} # (student_id, asgn_id) -> normalized_score
    asgn_max_map = {a["id"]: a.get("max_score", 0) for a in assignments}
    for s in asgn_subs:
        max_sc = asgn_max_map.get(s["assignment_id"], 0)
        if max_sc > 0 and s["score"] is not None:
            as_map[(s["student_id"], s["assignment_id"])] = s["score"] / max_sc

    # 4. Build extended feature vectors
    X = []
    student_identities = [] # Keep track of (student_id, course_id)
    
    logger.info(f"Processing {len(course_students)} courses...")
    
    for cid, students in course_students.items():
        course_quizzes = [q["id"] for q in quizzes if q["course_id"] == cid]
        course_asgns = [a["id"] for a in assignments if a["course_id"] == cid]
        
        n_dims = len(course_quizzes) + len(course_asgns)
        if n_dims == 0:
            continue
            
        for sid in students:
            # Topic-wise skills
            skill_vec = np.zeros(n_dims, dtype=float)
            q_scores = []
            a_scores = []
            
            # Quizzes
            for i, qid in enumerate(course_quizzes):
                sc = qs_map.get((sid, qid), 0.0)
                skill_vec[i] = sc
                if (sid, qid) in qs_map:
                    q_scores.append(sc)
                    
            # Assignments
            for i, aid in enumerate(course_asgns):
                sc = as_map.get((sid, aid), 0.0)
                skill_vec[len(course_quizzes) + i] = sc
                if (sid, aid) in as_map:
                    a_scores.append(sc)
            
            # Aggregated Metrics
            avg_quiz = np.mean(q_scores) if q_scores else 0.0
            avg_assign = np.mean(a_scores) if a_scores else 0.0
            completion_rate = len(a_scores) / len(course_asgns) if course_asgns else 0.0
            
            # We want all student vectors across different courses to be in the same feature space.
            # But courses have different numbers of quizzes/assignments!
            # Solution: We can't easily cluster raw skill_vecs if they change length per course.
            # For general clustering across ALL students, we should cluster on the *aggregated* metrics only,
            # or pad/reshape.
            # 
            # *Decision*: For cross-course clustering, we use aggregated metrics:
            # [avg_quiz, avg_assign, completion_rate, active_participation]
            # Since the implementation plan calls for appending to the skill_vec, and peer_match_api
            # needs cluster_labels, the simplest robust ML approach is:
            # 
            # Train model ONLY on the 3 universal aggregated metrics.
            # 
            features = np.array([avg_quiz, avg_assign, completion_rate])
            X.append(features)
            student_identities.append((sid, cid))
            
    return np.array(X), student_identities

def main():
    logger.info("Initializing K-Means Training Pipeline...")
    
    # 1. Fetch data
    X, identities = fetch_training_data()
    if len(X) < 3:
        logger.error(f"Not enough data to train. Found {len(X)} records. Need at least 3.")
        return
        
    logger.info(f"Extracted feature matrix shape: {X.shape}")
    
    # 2. Scale features
    logger.info("Scaling features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 3. Determine optimal K using Elbow Method
    max_k = min(8, len(X) - 1)
    if max_k >= 2:
        logger.info(f"Running Elbow Method (K=2 to {max_k})...")
        inertias = []
        K_range = range(2, max_k + 1)
        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(X_scaled)
            inertias.append(kmeans.inertia_)
            logger.debug(f"K={k}, Inertia={kmeans.inertia_:.2f}")
    else:
        logger.info("Not enough samples for Elbow Method.")
        
    # We will hardcode K=3 for simplicity and educational context
    # ("Struggling", "Average", "High Achiever")
    # In a real pipeline, we'd programmatically find the elbow point.
    optimal_k = min(3, len(X))
    if len(X) <= 3:
        optimal_k = max(1, len(X) - 1) # Prevent exact match if possible, but fallback to 1 if needed
    
    logger.info(f"Selected Optimal K = {optimal_k}")
    
    # 4. Train final model
    logger.info(f"Training final KMeans model with K={optimal_k}...")
    final_model = KMeans(n_clusters=optimal_k, random_state=42, n_init=20)
    final_model.fit(X_scaled)
    
    # 5. Analyze clusters
    labels = final_model.labels_
    unique, counts = np.unique(labels, return_counts=True)
    distribution = dict(zip(unique, counts))
    logger.info(f"Cluster Distribution: {distribution}")
    
    centroids = final_model.cluster_centers_
    # Inverse transform centroids to original scale for interpretability
    centroids_unscaled = scaler.inverse_transform(centroids)
    
    for i, centroid in enumerate(centroids_unscaled):
        logger.info(f"Cluster {i} Centroid (Avg Quiz, Avg Assign, Comp Rate): "
                    f"[{centroid[0]:.2f}, {centroid[1]:.2f}, {centroid[2]:.2f}]")
        
    # 6. Save Model
    dump_data = {
        "model": final_model,
        "scaler": scaler,
        "n_clusters": optimal_k,
        "features": ["avg_quiz", "avg_assign", "completion_rate"]
    }
    
    logger.info(f"Saving model to {MODEL_PATH}")
    joblib.dump(dump_data, MODEL_PATH)
    logger.info("✅ Training pipeline completed successfully.")

if __name__ == "__main__":
    main()
