from fastapi import FastAPI
from pydantic import BaseModel
from feast import FeatureStore
import mlflow.pyfunc
import pandas as pd
import os

app = FastAPI(title="StreamFlow Churn Prediction API")

# --- Config ---
REPO_PATH = "/repo"
MODEL_NAME = "streamflow_churn"
MODEL_URI = f"models:/{MODEL_NAME}/Production"

# Optionnel mais utile : MLflow regarde cette variable pour contacter le tracking server
os.environ.setdefault("MLFLOW_TRACKING_URI", os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"))

try:
    store = FeatureStore(repo_path=REPO_PATH)
    model = mlflow.pyfunc.load_model(MODEL_URI)
except Exception as e:
    print(f"Warning: init failed: {e}")
    store = None
    model = None


class UserPayload(BaseModel):
    user_id: str


@app.get("/health")
def health():
    return {"status": "ok"}


# (Tu peux garder ton endpoint existant)
@app.get("/features/{user_id}")
def get_features(user_id: str):
    if store is None:
        return {"error": "Feature store not initialized"}

    features = [
        "subs_profile_fv:months_active",
        "subs_profile_fv:monthly_fee",
        "subs_profile_fv:paperless_billing",
    ]

    feature_dict = store.get_online_features(
        features=features,
        entity_rows=[{"user_id": user_id}],
    ).to_dict()

    simple = {name: values[0] for name, values in feature_dict.items()}

    return {"user_id": user_id, "features": simple}


@app.post("/predict")
def predict(payload: UserPayload):
    if store is None or model is None:
        return {"error": "Model or feature store not initialized"}

    features_request = [
        "subs_profile_fv:months_active",
        "subs_profile_fv:monthly_fee",
        "subs_profile_fv:paperless_billing",
        "subs_profile_fv:plan_stream_tv",
        "subs_profile_fv:plan_stream_movies",
        "subs_profile_fv:net_service",
        "usage_agg_30d_fv:watch_hours_30d",
        "usage_agg_30d_fv:avg_session_mins_7d",
        "usage_agg_30d_fv:unique_devices_30d",
        "usage_agg_30d_fv:skips_7d",
        "usage_agg_30d_fv:rebuffer_events_7d",
        "payments_agg_90d_fv:failed_payments_90d",
        "support_agg_90d_fv:support_tickets_90d",
        "support_agg_90d_fv:ticket_avg_resolution_hrs_90d",
    ]

    # Récupérer les features online
    feature_dict = store.get_online_features(
        features=features_request,
        entity_rows=[{"user_id": payload.user_id}],
    ).to_dict()

    # DataFrame 1 ligne (k -> scalaire)
    X = pd.DataFrame({k: [v[0]] for k, v in feature_dict.items()})

    # Si user_id inexistant ou hors fenêtre matérialisée => valeurs None => on renvoie une erreur propre
    if X.isnull().any().any():
        missing = X.columns[X.isnull().any()].tolist()
        return {
            "error": f"Missing features for user_id={payload.user_id}",
            "missing_features": missing,
        }

    # Nettoyage minimal
    X = X.drop(columns=["user_id"], errors="ignore")

    # Prédiction via modèle MLflow pyfunc
    y_pred = model.predict(X)

    return {
        "user_id": payload.user_id,
        "prediction": int(y_pred[0]),
        "features_used": X.to_dict(orient="records")[0],
    }
