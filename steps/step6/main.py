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


async def route_user_list(request):
    users = await db_get_users()
    print(users)
    return JSONResponse(users)


async def route_user_delete(request):
    id = int(request.path_params["id"])
    await db_delete_user(id)
    return JSONResponse("User deleted")


async def db_delete_user(id):
    await database.execute("DELETE FROM users WHERE id = :id", {"id": id})


async def db_get_users():
    result = await database.fetch_all("SELECT * FROM users")
    users = []
    for row in result:
        users.append({"id": row["id"], "name": row["name"]})
    return users

app = Starlette(
    debug=True,
    routes=[
        Route("/users", route_user_create, methods=["POST"]),
        Route("/users", route_user_list, methods=["GET"]),
        Route("/users/{id}", route_user_delete, methods=["DELETE"]),
    ],
    on_startup=[database.connect],
    on_shutdown=[database.disconnect],
)
