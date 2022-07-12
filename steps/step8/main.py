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


async def route_user_update(request):
    body = await request.json()
    id = int(request.path_params["id"])
    name = body.get("name")
    if name == "":
        return JSONResponse({"error": "Name is required"}, status_code=400)
    user = await db_update_user(id, name)
    print(user)
    return JSONResponse(user)


async def db_update_user(id, name):
    row = await database.execute("UPDATE users SET name = :name WHERE id = :id RETURNING (id, name);", {"id": id, "name": name})
    return {"id": row[0], "name": row[1]}


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
        Route("/users/{id}", route_user_delete, methods=["PATCH"]),
    ],
    on_startup=[database.connect],
    on_shutdown=[database.disconnect],
)
