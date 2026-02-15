from telethon import events, Button
import pkgutil, importlib, shlex, time, os, asyncio, mimetypes, unicodedata, re, random, urllib, sys
current_working_dir = os.getcwd()
if current_working_dir not in sys.path:
    sys.path.insert(0, current_working_dir)
from config import ACCESS, MESSAGES
from ..utils.FastTelethon import download_file

class FileGram:
    @classmethod
    async def fileManager(self, system, event, parameters):
        file = system.files[parameters[0]]
        if parameters[1] == "delete":
            try:
                os.unlink(file)
            except:
                pass
            msg = await event.get_message()
            await msg.edit("`[ --- ELIMINADO --- ]`\n\n__Este archivo ha sido eliminado manualmente.__", buttons=None)

def sanitize_filename(text: str, ext: str, max_length: int = 200) -> str:
    if not text:
        return f"document_{time.time()}{ext}"
    first_line = text.splitlines()[0].strip()
    if not first_line:
        return f"document_{time.time()}{ext}"
    nfkd = unicodedata.normalize('NFKD', first_line)
    ascii_only = ''.join(c for c in nfkd if ord(c) < 128)
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', ascii_only)
    cleaned = cleaned.strip(' .')
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        *(f'COM{i}' for i in range(1, 10)),
        *(f'LPT{i}' for i in range(1, 10))
    }
    if cleaned.upper() in reserved_names:
        cleaned = f"_{cleaned}"
    if len(cleaned) == 0:
        cleaned = f"document_{time.time()}{ext}"
    elif len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip(' ._')
    return cleaned
def formating(mensajes, datos):
    mensajes_formateados = {}
    for clave, valor in mensajes.items():
        mensajes_formateados[clave] = valor.format(**datos)
    return mensajes_formateados
class Timer:
    def __init__(self, time_between=2):
        self.start_time = time.time()
        self.time_between = time_between

    def can_send(self):
        if time.time() > (self.start_time + self.time_between):
            self.start_time = time.time()
            return True
        return False
class Download:
    def __init__(self, system, event, autoprocess=None, refresh=3):
        self.timer = Timer(time_between=refresh)
        self.last = {"current": 0, "text": ""}
        self.event = event
        self.system = system
        self.start_time = time.time()
        self.finish_time = 0
        self.autoprocess = autoprocess
        self.filename = None
        self.totalsize = 0
    def genbar(self, porcentaje, ancho=20):
        porcentaje = max(0, min(100, porcentaje))
        completos = int(round(ancho * porcentaje / 100))
        vacios = ancho - completos
        barra = f"⟦{'▣' * completos}{'▢' * vacios}⟧"
        return barra
    def sizeof_fmt(self, num, suffix='B'):
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(num) < 1024.0:
                return "%3.2f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.2f%s%s" % (num, 'Yi', suffix)
    async def callback(self, current, total):
        self.totalsize = total
        if self.timer.can_send():
            if self.last["current"] == current:
                return
            velocity = (current - self.last["current"])/3
            self.last["current"] = current
            text = f"**[ {round(current*100/total,2)} % ]** `{self.filename}`\n\n__{self.sizeof_fmt(current)} / {self.sizeof_fmt(total)} - {self.sizeof_fmt(velocity)}ps__\n`{self.genbar(current*100/total)}`"
            if not text == self.last["text"]:
                self.last["text"] = text
                await self.msg.edit(text)
    async def start(self):
        self.msg = await self.event.reply("Espere un momento...")
        os.makedirs("./files", exist_ok=True)
        ext = mimetypes.guess_extension(self.event.message.document.mime_type or 'application/octet-stream') or ''
        if self.event.file.name:
            self.filename = self.event.file.name.replace("[","").replace("]","")
        else:
            self.filename = f"""document_{str(time.time()).replace(".","_")}{ext}"""
        with open("./files/"+self.filename, "wb") as out:
            await download_file(self.event.client, self.event.document, out, progress_callback=self.callback)
        self.finish_time = time.time()
        self.total_time = self.finish_time - self.start_time
        code = str(random.randint(1000000,9999999))
        self.system.files[code] = "./files/"+self.filename
        buttons = []
        newFiles = []
        for cmd in pkgutil.iter_modules(self.system.commands.__path__):
            submodule = importlib.import_module(self.system.commands.__name__+"."+cmd.name)
            importlib.reload(submodule)
            if hasattr(submodule, "newFile"):
                newFiles.append(submodule)
        if not newFiles == []:
            await self.system.client.delete_messages(self.event.sender.id, self.msg.id)
            for f in newFiles:
                if os.path.exists(self.system.files[code]):
                    await f.newFile(self.system, self.event, self.system.files[code])
            return
        buttons.append([Button.inline("ELIMINAR", f"file {code} delete".encode())])
        await self.msg.edit(f"`[ --- ARCHIVO DESCARGADO --- ]`\n\n**[ {self.sizeof_fmt(self.totalsize)} ]** {self.filename}", buttons=buttons)
        self.system.callbacks["file"] = FileGram.fileManager

        
class System:
    def __init__(self, system_name, client):
        self.name = system_name
        self.admin = {}
        self.operators = {}
        self.users = {}
        self.queue = {}
        self.autoprocess = None
        self.callbacks = {}
        self.files = {}
        self.commands = None
        self.client = client
        self.plugins = []
        @client.on(events.NewMessage())
        async def newMessage(event):
            await self.newEvent(event)
        @client.on(events.NewMessage(pattern="/"))
        async def newCommand(event):
            global MESSAGES
            member = self.isMember(event.sender)
            if not member:
                return
            MESSAGES = formating(MESSAGES, {"username": event.sender.username, "userid": event.sender.id})
            input = shlex.split(event.text)
            command = input[0][1:]
            parameters = input[1:]
            for cmd in pkgutil.iter_modules(self.commands.__path__):
                if command == cmd.name:
                    submodule = importlib.import_module(self.commands.__name__+"."+cmd.name)
                    importlib.reload(submodule)
                    level_access = False
                    if not hasattr(submodule, "data"):
                        submodule.data["level"] = "user"
                    if not "level" in submodule.data:
                        submodule.data["level"] = "user"
                    if member["permission"] == "user" and submodule.data["level"] == "user":
                        level_access = True
                    elif member["permission"] == "operator" and (submodule.data["level"] == "user" or submodule.data["level"] == "operator"):
                        level_access = True
                    elif member["permission"] == "admin":
                        level_access = True
                    if level_access:
                        if hasattr(submodule, "newEvent"):
                            await submodule.newEvent(self, event, parameters)
                            return
                    else:
                        await event.respond(MESSAGES["noCommandPermission"])
            await event.respond(MESSAGES["noCommandExists"])
        @client.on(events.CallbackQuery)
        async def newCallback(event):
            sender = event.sender
            data = shlex.split(event.data.decode('utf-8'))
            await self.callbacks[data[0]](self, event, data[1:])
        @client.on(events.NewMessage(incoming=True, func=lambda e: e.file))
        async def newFile(event):
            member = self.isMember(event.sender)
            if not member:
                return
            async def worker(userid):
                while True:
                    try:
                        process = await self.queue[userid].get()
                    except:
                        await asyncio.sleep(2)
                        continue
                    try:
                        await process.start()
                    except:
                        await client.send_message(event.sender.id, "`[ --- ERROR FATAL --- ]`\n\n__Hubo un error en alguno de los procesos de la cola.__")
                    finally:
                        self.queue[userid].task_done()
            if not event.sender.id in self.queue:
                self.queue[event.sender.id] = asyncio.Queue()
                asyncio.create_task(worker(event.sender.id))
            download = Download(self, event, self.autoprocess)
            await self.queue[event.sender.id].put(download)
            await self.queue[event.sender.id].join()
            
    async def newEvent(self, event):
        global MESSAGES
        sender = event.sender
        MESSAGES = formating(MESSAGES, {"username": event.sender.username, "userid": event.sender.id})
        member = self.isMember(event.sender)
        if member:
            return
        if self.admin == {}:
            self.admin = {sender.id: {"username": sender.username ,"permission": "admin"}}
            await event.respond(MESSAGES["newAdmin"])
        elif ACCESS and not sender.id in self.users:
            self.users[sender.id] = {"username": sender.username ,"permission": "user"}
            await event.respond(MESSAGES["newUser"])
        elif not (ACCESS and sender.id in self.users):
            await event.respond(MESSAGES["permissionDenied"])
    def setCommands(self, commands):
        self.commands = commands
    def isMember(self, sender):
        if sender.id in self.admin:
            return self.admin[sender.id]
        elif sender.id in self.users:
            return self.users[sender.id]
        elif sender.id in self.operators:
            return self.operators[sender.id]
        return None
