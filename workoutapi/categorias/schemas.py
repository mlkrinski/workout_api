from typing import Annotated
from pydantic import UUID4, Field
from workoutapi.contrib.schemas import BaseSchema


class CategoriaIn(BaseSchema):
    nome: Annotated[str, Field(description="Categoria do atelta", example="Scale")]


class CategoriaOut(CategoriaIn):
    id: Annotated[UUID4, Field(description="Identificador da categoria")]
