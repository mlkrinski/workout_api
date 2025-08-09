from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4
from typing import Optional
from sqlalchemy.exc import IntegrityError
from workoutapi.contrib.dependencies import DataBaseDependency
from workoutapi.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate, AtletaListOut
from workoutapi.atleta.models import AtletaModel
from sqlalchemy.future import select
from workoutapi.categorias.models import CategoriaModel
from workoutapi.Centro_treinamento.models import CentroTreinamentoModel
from fastapi_pagination import Page, add_pagination, paginate
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate


router = APIRouter()


# ---------------------------
# Criar novo atleta
# ---------------------------
@router.post("/", summary="Criar novo atleta", status_code=status.HTTP_201_CREATED, response_model=AtletaOut)
async def create_atleta(db_session: DataBaseDependency, atleta_in: AtletaIn = Body(...)):
    categoria_name = atleta_in.categoria.nome
    centro_treinamento_nome = atleta_in.centro_treinamento.nome

    categoria = (
        (await db_session.execute(select(CategoriaModel).filter_by(nome=categoria_name))).scalars().first()
    )
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A categoria {categoria_name} não foi encontrada.",
        )

    centro_treinamento = (
        (await db_session.execute(select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome)))
        .scalars()
        .first()
    )
    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"O Centro de Treinamento {centro_treinamento_nome} não foi encontrado.",
        )

    atleta_out = AtletaOut(
        id=uuid4(), created_at=datetime.now().replace(tzinfo=None), **atleta_in.model_dump()
    )
    atleta_model = AtletaModel(**atleta_out.model_dump(exclude={"categoria", "centro_treinamento"}))
    atleta_model.categoria_id = categoria.pk_id
    atleta_model.centro_treinamentos_id = centro_treinamento.pk_id

    db_session.add(atleta_model)

    try:
        await db_session.commit()
    except IntegrityError:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f"Já existe um atleta cadastrado com o cpf: {atleta_in.cpf}",
        )

    return atleta_out


# ---------------------------
# Consultar todos os atletas (com filtros opcionais)
# ---------------------------
@router.get(
    "/",
    summary="Consultar todos os Atletas com paginação",
    response_model=Page[AtletaOut],
)
async def list_atletas(db_session: DataBaseDependency, nome: Optional[str] = None, cpf: Optional[str] = None):
    stmt = select(AtletaModel)

    if nome:
        stmt = stmt.filter(AtletaModel.nome.ilike(f"%{nome}%"))
    if cpf:
        stmt = stmt.filter(AtletaModel.cpf == cpf)

    # Use o paginate do fastapi_pagination.ext.sqlalchemy para paginar a query
    result = await sqlalchemy_paginate(db_session, stmt)

    # O resultado já é um objeto Page com os dados e meta info
    return result


# ---------------------------
# Consultar atleta pelo ID
# ---------------------------
@router.get(
    "/{id}",
    summary="Consultar um atleta pelo id",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def get_atleta(id: UUID4, db_session: DataBaseDependency) -> AtletaOut:
    atleta = (await db_session.execute(select(AtletaModel).filter_by(id=id))).scalars().first()
    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Atleta não encontrado no id: {id}"
        )
    return atleta


# ---------------------------
# Editar atleta pelo ID
# ---------------------------
@router.patch(
    "/{id}",
    summary="Editar um atleta pelo id",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def update_atleta(
    id: UUID4, db_session: DataBaseDependency, atleta_up: AtletaUpdate = Body(...)
) -> AtletaOut:
    atleta = (await db_session.execute(select(AtletaModel).filter_by(id=id))).scalars().first()
    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Atleta não encontrado no id: {id}"
        )

    atleta_update = atleta_up.model_dump(exclude_unset=True)
    for key, value in atleta_update.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)
    return atleta


# ---------------------------
# Deletar atleta pelo ID
# ---------------------------
@router.delete("/{id}", summary="Deletar um atleta pelo id", status_code=status.HTTP_204_NO_CONTENT)
async def delete_atleta(id: UUID4, db_session: DataBaseDependency) -> None:
    atleta = (await db_session.execute(select(AtletaModel).filter_by(id=id))).scalars().first()
    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Atleta não encontrado no id: {id}"
        )

    await db_session.delete(atleta)
    await db_session.commit()
