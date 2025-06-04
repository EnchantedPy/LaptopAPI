from fastapi import FastAPI
from src.presentation.api.account_service.router import AccountRouter
from src.presentation.api.auth_service.router import AuthRouter

routers = [AccountRouter, AuthRouter]

def apply_routers(app: FastAPI):
	for router in routers:
		app.include_router(router)