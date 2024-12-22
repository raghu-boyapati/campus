from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers.studentRouter import router as student_router
from .routers.groupRouter import router as group_router
from .routers.postRouter import router as post_router
from .routers.commentRouter import router as comment_router
from .routers.studentGroupRouter import router as student_group_router


def create_app():
    app = FastAPI(title="Student Management API")

    # Database setup
    # Base.metadata.create_all(bind=engine)

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(student_router)
    app.include_router(group_router)
    app.include_router(post_router)
    app.include_router(comment_router)
    app.include_router(student_group_router)

    return app


app = create_app()
