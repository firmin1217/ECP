
# API FastAPI pour la recommandation de culture
# Endpoint : POST /predict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import os

# 1. INITIALISATION DE L'APPLICATION

app = FastAPI(
    title="API Recommandation de Culture - Côte d'Ivoire",
    description="Prédit la meilleure culture agricole selon les caractéristiques du sol et du climat",
    version="1.0.0"
)

# 2. CONFIGURATION CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. CHARGEMENT DU MODÈLE ET DU LABEL ENCODER AU DÉMARRAGE
# Chemin absolu pour éviter les erreurs selon le dossier de lancement

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "..", "models")

modele = joblib.load(os.path.join(MODELS_DIR, "modele_recommandation_culture.joblib"))
label_encoder = joblib.load(os.path.join(MODELS_DIR, "label_encoder.joblib"))

print(f"✓ Modèle chargé : {type(modele).__name__}")
print(f"✓ Cultures disponibles : {list(label_encoder.classes_)}")

# 4. SCHÉMA DE VALIDATION DES DONNÉES (Pydantic)

class SolInput(BaseModel):
    N: float = Field(..., ge=0, le=200, description="Azote (kg/ha)")
    P: float = Field(..., ge=0, le=200, description="Phosphore (kg/ha)")
    K: float = Field(..., ge=0, le=250, description="Potassium (kg/ha)")
    temperature: float = Field(..., ge=0, le=50, description="Température (°C)")
    humidity: float = Field(..., ge=0, le=100, description="Humidité (%)")
    ph: float = Field(..., ge=0, le=14, description="pH du sol")
    rainfall: float = Field(..., ge=0, le=5000, description="Pluviométrie (mm/an)")

    class Config:
        json_schema_extra = {
            "example": {
                "N": 45, "P": 55, "K": 42,
                "temperature": 26.8, "humidity": 81.0,
                "ph": 6.3, "rainfall": 1650.0
            }
        }

# 5. SCHÉMA DE LA RÉPONSE

class PredictionOutput(BaseModel):
    culture_recommandee: str
    confiance: float
    toutes_probabilites: dict

# 6. ROUTE DE TEST

@app.get("/")
def accueil():
    return {
        "message": "API de recommandation de culture - Côte d'Ivoire",
        "status": "en ligne",
        "cultures_disponibles": list(label_encoder.classes_)
    }

# 7. ROUTE PRINCIPALE — PRÉDICTION EN TEMPS RÉEL

@app.post("/predict", response_model=PredictionOutput)
def predire_culture(donnees: SolInput):
    try:
        X_input = pd.DataFrame([{
            "N": donnees.N,
            "P": donnees.P,
            "K": donnees.K,
            "temperature": donnees.temperature,
            "humidity": donnees.humidity,
            "ph": donnees.ph,
            "rainfall": donnees.rainfall
        }])

        prediction = modele.predict(X_input)
        culture_predite = label_encoder.inverse_transform(prediction)[0]

        probabilites = modele.predict_proba(X_input)[0]

        toutes_probas = {
            culture: round(float(proba) * 100, 2)
            for culture, proba in sorted(
                zip(label_encoder.classes_, probabilites),
                key=lambda x: x[1],
                reverse=True
            )
        }

        confiance = toutes_probas[culture_predite]

        return PredictionOutput(
            culture_recommandee=culture_predite,
            confiance=confiance,
            toutes_probabilites=toutes_probas
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur de prédiction : {str(e)}")