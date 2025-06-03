from fastapi import FastAPI
from src.core.account_service.router import AccountRouter
from src.core.auth_service.router import AuthRouter

routers = [AccountRouter, AuthRouter]

def apply_routers(app: FastAPI):
	for router in routers:
		app.include_router(router)