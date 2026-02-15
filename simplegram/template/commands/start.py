data = {"label": "Comenzar sistema", "level": "user"}

async def newEvent(system, event, parameters):
    sender = event.sender
    await event.reply(
        f"**{system.name}**")