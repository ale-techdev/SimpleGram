import pickle

data = {"label": "Restaura una copia de seguridad", "level": "admin"}

async def newFile(system, event, file):
    sender = event.sender
    if file.split('/')[-1].endswith(".backup"):
        system_backup = pickle.loads(open(file, "rb").read())
        system.name = system_backup["name"]
        system.operators = system_backup["operators"]
        system.users = system_backup["users"]
        await event.reply(f"`Backup restaurado`")