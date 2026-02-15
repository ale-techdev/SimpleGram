from telethon import TelegramClient
import os, sys, shutil

def main():
    cmd = sys.argv[1:]
    def start(vars):
        current_working_dir = os.getcwd()
        if current_working_dir not in sys.path:
            sys.path.insert(0, current_working_dir)
        try:
            import commands
        except:
            print("\n    [ ERROR ] No hay comandos establecidos")
            sys.exit()
        try:
            from config import SESSION_NAME, BOT_TOKEN, API_HASH, API_ID
        except:
            print("\n    [ ERROR ] No hay archivo de configuración o faltan variables")
            sys.exit()
        from .utils.system import System
        client = TelegramClient(SESSION_NAME, api_id=API_ID, api_hash=API_HASH).start(bot_token=BOT_TOKEN)
        system = System(vars["-n"], client)
        system.setCommands(commands)
        print(f"\n    [ INFO ] {vars['-n']} INICIADO")
        client.run_until_disconnected()
    def install(vars):
        pathcurrent = os.path.dirname(os.path.abspath(__file__))
        origen = pathcurrent+"/template"
        destino = "."
        for item in os.listdir(origen):
            s = os.path.join(origen, item)
            d = os.path.join(destino, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        print("\n    [ INFO ] PLANTILLA INSTALADA")
    functions = {"start": start, "install": install, "s": start, "i": install}
    skip = False
    index = 0
    vars = {"-n": "SimpleGram"}
    toexecute = []
    for c in cmd:
        if skip:
            index += 1
            skip = False
            continue
        if "-" in c or "--" in c:
            skip = True
            vars[c] = cmd[index+1]
            continue
        for o in functions.keys():
            if c == o:
                toexecute.append(functions[o])
        index += 1
    for exe in toexecute:
        exe(vars)

if __name__ == "__main__":
    main()