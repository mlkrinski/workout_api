from uuid import uuid4
from fastapi import APIRouter, Body, status, HTTPException
from pydantic import UUID4
from workoutapi.contrib.dependencies import DataBaseDependency
from workoutapi.Centro_treinamento.schemas import CentroTreinamentoIn, CentroTreinamentoOut
from workoutapi.Centro_treinamento.models import CentroTreinamentoModel
from sqlalchemy.future import select

router = APIRouter()


@router.post(
    "/",
    summary="Criar um novo centro de treinamento",
    status_code=status.HTTP_201_CREATED,
    response_model=CentroTreinamentoOut,
)
async def post(
    db_session: DataBaseDependency, centro_treinamento_out_in: CentroTreinamentoIn = Body(...)
) -> CentroTreinamentoOut:
    centro_treinamento_out = CentroTreinamentoOut(id=uuid4(), **centro_treinamento_out_in.model_dump())
    centro_treinamento_model = CentroTreinamentoModel(**centro_treinamento_out.model_dump())

    db_session.add(centro_treinamento_model)
    await db_session.commit()

    return centro_treinamento_out


@router.get(
    "/",
    summary="Consultar todos os centros de treinamento",
    status_code=status.HTTP_200_OK,
    response_model=list[CentroTreinamentoOut],
)
async def query(db_session: DataBaseDependency) -> list[CentroTreinamentoOut]:
    centros_treinamento_out: list[CentroTreinamentoOut] = (
        (await db_session.execute(select(CentroTreinamentoModel))).scalars().all()
    )

    return centros_treinamento_out


@router.get(
    "/{id}",
    summary="Consultar um centro de treinamento pelo id",
    status_code=status.HTTP_200_OK,
    response_model=CentroTreinamentoOut,
)
async def query(id: UUID4, db_session: DataBaseDependency) -> CentroTreinamentoOut:
    centro_treinamento_out: CentroTreinamentoOut = (
        (await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))).scalars().first()
    )

    if not centro_treinamento_out:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Centro de treinamento não encontrado no id: {id}"
        )

    return centro_treinamento_out
