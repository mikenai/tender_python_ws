import databases
from starlette.applications import Starlette
from starlette.config import Config
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

config = Config(".env")
database = databases.Database(config("DB_URL"))


async def route_user_create(request):
    body = await request.json()
    name = body.get("name")
    if name == "":
        return JSONResponse({"error": "Name is required"}, status_code=400)
    id = await db_create_user(name)
    return JSONResponse({"id": id})


async def db_create_user(name):
    id = await database.execute("INSERT INTO users (name) VALUES (:name) RETURNING id", {"name": name})
    return id


app = Starlette(
    debug=True,
    routes=[
        Route("/users", route_user_create, methods=["POST"]),

    ],
    on_startup=[database.connect],
    on_shutdown=[database.disconnect],
)
