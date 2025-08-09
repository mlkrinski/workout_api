from fastapi import APIRouter
from workoutapi.atleta.controller import router as atleta
from workoutapi.categorias.controller import router as categorias
from workoutapi.Centro_treinamento.controller import router as centro_treinamento

api_router = APIRouter()
api_router.include_router(atleta, prefix="/atletas", tags=["atletas"])
api_router.include_router(categorias, prefix="/categorias", tags=["categorias"])
api_router.include_router(centro_treinamento, prefix="/centros_treinamento", tags=["centros_treinamento"])
