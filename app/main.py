from fastapi import FastAPI
from .batch.lifespan import lifespan
from .entities.base_entity import Base
from .routers.base_router import router
from .connection.connection import engine

# create the database tables
Base.metadata.create_all(
    engine
)  # 스키마생성 => 개발할때 사용 => entity 신규추가되면 테이블 자동 생성

# Base.metadata.drop_all(engine)  # 스키마 제거
# Base.metadata.bind = engine # 스키마 바인드 => entity 신규추가되더라도 테이블 자동생성안됨


app = FastAPI(
    title="Auto trade",
    description="Auto Trade stock api",
    lifespan=lifespan,  # 스케쥴러 등록
)

# 라우터 바인드
app.include_router(router)
