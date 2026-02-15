import os
from telethon import Button

data = {"label": "Buscar un usuario de telegram", "level": "operator"}

async def change(system, event, parameters):
    client = system.client
    userID = int(parameters[0])
    state = parameters[1]
    if userID in system.users:
        del system.users[userID]
    elif userID in system.operators:
        del system.operators[userID]
    user = await client.get_entity(int(userID))
    if state == "user":
        system.users[userID] = {"username": user.username, "permission": "user"}
    elif state == "operator":
        system.operators[userID] = {"username": user.username, "permission": "operator"}
    text, photo, buttons = await profile(system, event, userID, user=user)
    msg = await event.get_message()
    await msg.edit(text, file=photo, buttons=buttons)
    try:
        os.unlink(photo)
    except:
        pass

async def profile(system, event, search, user=None):
    sender = event.sender
    client = system.client
    if not user:
        user = await client.get_entity(search)
    photo = await client.download_profile_photo(user)
    state = "No"
    buttonsAdmin = [[Button.inline("Otorgar acceso", f"change {user.id} user".encode("utf-8"))]]
    buttonsOperator = [[Button.inline("Otorgar acceso", f"change {user.id} user".encode("utf-8"))]]
    if user.id in system.users:
        state = "Usuario"
        buttonsAdmin = [[Button.inline("Ascender a Operador", f"change {user.id} operator".encode("utf-8"))], [Button.inline("Denegar acceso", f"change {user.id} none".encode("utf-8"))]]
        buttonsOperator = [[Button.inline("Denegar acceso", f"change {user.id} none".encode("utf-8"))]]
    elif user.id in system.operators:
        state = "Operador"
        buttonsAdmin = [[Button.inline("Degradar a Usuario", f"change {user.id} user".encode("utf-8"))], [Button.inline("Denegar acceso", f"change {user.id} none".encode("utf-8"))]]
        buttonsOperator = []
    elif user.id in system.admin:
        state = "Administrador"
        buttonsAdmin = []
        buttonsOperator = []
    permission = system.isMember(sender)["permission"]
    if permission == "admin":
        buttons = buttonsAdmin
    elif permission == "operator":
        buttons = buttonsOperator
    else:
        buttons = []
    return f"""**Nombre:** __{user.first_name} {user.last_name if user.last_name else ""}__\n**ID:** __{user.id}__\n**Miembro:** {state}\n\n@{user.username}""", photo, None if buttons == [] else buttons

async def newEvent(system, event, parameters):
    if len(parameters) == 0:
        await event.reply("Falta el parámetro **UserID o @Username**")
    else:
        try:
            search = parameters[0]
            if "@" in search:
                search = search.replace("@", "")
            else:
                search = int(search)
            msg = await event.reply("Espere un momento")
            text, photo, buttons = await profile(system, event, search)
            await msg.edit(text, file=photo, buttons=buttons)
            system.callbacks["change"] = change
            try:
                os.unlink(photo)
            except:
                pass
        except:
            await event.reply("No existe el usuario buscado")
            