import pickle

data = {"label": "Crea un backup del sistema", "level": "admin"}

async def newEvent(system, event, parameters):
    system_backup = pickle.dumps({"name": system.name, "users": system.users, "operators": system.operators})
    with open("./system.backup", "wb") as bu:
        bu.write(system_backup)
    await event.reply(
        system.name,
        file="./system.backup"
    )