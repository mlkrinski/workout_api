from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from typing import Annotated
from workoutapi.configs.database import get_session

DataBaseDependency = Annotated[AsyncSession, Depends(get_session)]
