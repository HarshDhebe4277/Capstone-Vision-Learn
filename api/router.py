"""API router — registers all controller routers in one place."""
from fastapi import APIRouter

from api.controllers import lecture_controller, pipeline_controller, audio_controller, notes_controller

api_router = APIRouter()

api_router.include_router(lecture_controller.router)
api_router.include_router(pipeline_controller.router)
api_router.include_router(audio_controller.router)
api_router.include_router(notes_controller.router)

