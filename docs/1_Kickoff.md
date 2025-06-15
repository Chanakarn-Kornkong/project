# Project One: Kickoff

- [Pre-Installatie](./1_Kickoff.md#pre-installatie)
- [Installatie](./1_Kickoff.md#installatie)
  - [Downloaden van de image ⏳](./1_Kickoff.md#downloaden-van-de-image-)
  - [Terugzetten van de image ⏳](./1_Kickoff.md#terugzetten-van-de-image-)
  - [Pi koppelen](./1_Kickoff.md#pi-koppelen)
  - [Pi klaarmaken voor verder gebruik](./1_Kickoff.md#pi-klaarmaken-voor-verder-gebruik)
- [Classroom clonen](./1_Kickoff.md#classroom-clonen)
- [⚠️ TODO: Demo project](./1_Kickoff.md#%EF%B8%8F-todo-demo-project)
  - [Aanmaken venv](./1_Kickoff.md#aanmaken-venv)
  - [Dependencies installeren](./1_Kickoff.md#dependencies-installeren)
  - [SQL importeren](./1_Kickoff.md#sql-importeren)
  - [Configuratie database](./1_Kickoff.md#configuratie-database)
- [⚠️ TODO: GPIO integreren](./1_Kickoff.md#%EF%B8%8F-todo-gpio)
- [⚠️ TODO: Eigen database](./1_Kickoff.md#%EF%B8%8F-todo-eigen-database)
- [OPGELET](./1_Kickoff.md#opgelet-eigen-project--venv--git)

---

## (Basic) checklist

Via [project1-mct-checklist.pages.dev](https://project1-mct-checklist.pages.dev/)

De todo's kunnen afgevinkt worden, dit wordt in localstorage opgeslagen (in uw eigen browser)

---

## Pre-Installatie: update RPi firmware

_Use Raspberry Pi Imager to write an EEPROM update image to a spare SD card. Select Misc utility images under the Operating System tab._  
(Zie: [rpi-eeprom](https://github.com/raspberrypi/rpi-eeprom))

Je kan dus een speciaal Micro SD kaartje maken om de firmware van uw RPi up te daten. Doe dit _voor_ je de start image hebt weggeschreven, of je zal de image opnieuw moeten wegschrijven.

## Installatie

### Downloaden van de image ⏳

- Download _[de gezipte image](https://studenthowest-my.sharepoint.com/:u:/g/personal/pieter-jan_beeckman_howest_be/EThYO_NN0plKlwzLkIKa9lQBVUjAhoPKJ_hMGbUixfHRWg?e=TWnMHN)_ naar je lokale computer.

### Terugzetten van de image ⏳

- ⚠ Unzip het bestand ⚠
- Plaats het bestand op een SD-kaartje van minstens 8GB (16GB) met Win32 Imager of Balena Etcher.
- Nadat de image geschreven is, kan je het SD-kaartje verwijderen en in je Pi steken.

### Pi koppelen

- Boot je Pi.
- Koppel de Pi aan je computer dmv een netwerkkabel en maak een SSH-connectie in _Putty_ naar 192.168.168.169 voor de user _student_ met als paswoord _P@ssw0rd_

> PAS OP: De image is in AZERTY gemaakt, mocht je direct via toetsenbord verbinden

### Pi klaarmaken voor verder gebruik

- _Na het inloggen moet je eerst nieuw wachtwoord instellen voor student gebruiker_
- `ssh student@192.168.168.169` ; huidig wachtwoord _P@ssw0rd_ ; nieuw wachtwoord en bevestigen
- log opnieuw in met nieuw wachtwoord
- ⚠ REBOOT de Pi (Dit kan enkele minuten duren opnieuw)

---

> ⚠️ OPGELET: alle bussen staan nog gedeactiveerd. Vergeet deze niet te activeren via Pi-config  
> **SSH** en **VNC** zijn wel reeds geactiveerd

---

## **Classroom clonen**

(reeds gedana of je hebt dit document niet)

Accepteer de invite url: [CLASSROOM](https://classroom.github.com/a/3T1YfLdF)

Open een nieuwe venster van vscode, en verbind met 192.168.168.169

Nadien kan je via de sourcecontrol tab binnen vscode de repo clonen

Voor de KICKOFF clone de repo naar ~/kickoff

(De repo map zal dan ~/kickoff/2024-2025-projectone-mct-uwnaam)

**Gebruik de https:// versie, niet de ssh://**

> **Pas (op zijn minst) de readme.md aan, en push deze**

(of je kan gewoon via terminal `cd ~/kickoff` om naar kickoff map te gaan, en vervolgens `git clone <url van repo>`)

Voor je kan comitten zal jegit user en email moeten configureren:

`git config --global user.name "FIRST_NAME LAST_NAME"`  
`git config --global user.email "MY_NAME@example.com"`

## ⚠️ TODO: Demo project

> De classroom bevat het FSWD demo project, laat dit werken

### Aanmaken venv

Zoals tijdens elk project van FSWD maken we een nieuwe venv aan door in de terminal volgend commando in te tikken:

- Voor ![Windows logo](https://icons.getbootstrap.com/assets/icons/windows.svg) : `py -m venv venv`
- Voor ![Mac logo](https://icons.getbootstrap.com/assets/icons/apple.svg) : `python3 -m venv venv`

Sluit hierna in VS Code de terminal en open een nieuwe en check of je in je venv aan het werken bent.
(of source venv/bin/activate)

### Dependencies installeren

Eerst zullen we nu de nodige packages installeren op onze nieuw gemaakte venv.
Voor het gemak hebben we alle nodige packages opgeslagen in het bestand requirements.txt.

Het installeren van de nodige packages kan met het volgende commando:

- Voor ![Windows logo](https://icons.getbootstrap.com/assets/icons/windows.svg) : `pip install -r ./requirements.txt`
- Voor ![Mac logo](https://icons.getbootstrap.com/assets/icons/apple.svg) : `pip install -r requirements.txt`

### SQL importeren

Open MySQLWorkbench en importeer het SQL-bestand.

(user: `root` ww: `r00tP@ss` ; gebruik SSH tunnel)

### Configuratie database

Maak een kopie van _config_example.py_ met de naam _config.py_ en vul het paswoord voor de database aan.

### Flask secret

Pas in app.py het secret van de Flask server aan, naar een willekeurige string

## Demo project testen

**Backend**

> `cd ~/kickoff/<repo_map>`  
> optional: `python3 -m venv venv`  
> `source venv/bin/activate`  
> optional: `pip install -r requirements.txt`  
> `python backend/app.py`

Je kan best ook rechts onderaan de python interpreter selecteren. Kies de python binary binnen de virtual environment.

**Front-end**

huis.html openen in vscode

Rechts klikken in je code en `open with live server` kiezen

In je browser ip aanpassen naar `192.168.168.169`

## **⚠️ TODO: GPIO**

De backend/app.py code moet aangepast worden zodat een fysieke knop werkt als toggle schakelaar voor lamp 3. Daarnaast moet ook een led de status van deze lamp weergeven (meegaan met de UI dus)

- Je moet dus GPIO setup uitvoeren zoals normaal
- De knop kan je via de meegeleverde klasse uitlezen
- Wanneer er op de knop gedrukt wordt moet kijken of de led brandt, en de omgekeerde toestand 'doorgeven' aan het systeem (= je server)
- Wanneer je server een verandering in toestand binnen krijgt, moet je niet alleen de data in databse steken (is er al) maar ook de toestand van lamp 3 (de led) mee aanpassen (indien het over lamp 3 gaat natuurlijk)

### Maak een kickoff branch

We zullen dit demo project binnen de kickoff branch aanmaken, en deze na merge in main niet verwijderen. Zo hebben we altijd een werkende referentie

### Voeg bovenaan **`app.py`** de standaard logging‑config toe.

```python
import logging

logging.basicConfig(
    level=logging.INFO,                    # alles ≥ INFO‑niveau tonen
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",         # Europees datum‑formaat
    force=True,                           # herconfigureer bij auto‑reload
)
logger = logging.getLogger(__name__)
```

2. **Waarom?**

   - `logging.basicConfig()` initialiseert één globale logger‑config voor de héle app.
   - Je krijgt timestamps, levels en module‑namen out‑of‑the‑box.
   - `logger.info()` **flusht** automatisch bij newline‑buffers, terwijl `print()` op een RPi vaak gebufferd wordt; zo zie je logs meteen wanneer er iets misgaat.
   - Je kunt later per module een eigen logger maken met `logging.getLogger("mijnmodule")`, maar ze volgen dezelfde configuratie.

### Hardware‑constanten

Definieer na de imports de constanten voor het project

```python
LED_PIN    = 17
BUTTON_PIN = 20
# ...
```

### Lifespan‑manager

1. **GPIO setup** (vlak vóór de `yield` in de bestaande `lifespan_manager`):

   ```python
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(...)
   #...
   logger.info("GPIO initialised")
   ```

2. **Thread starten** _na_ de setup:

   ```python
   threading.Thread(
       target=gpio_keep_alive,
       daemon=True               # 🔑 daemon‑threads stoppen automatisch bij app‑exit
   ).start()
   ```

   threading.Thread voor sync code (zoals RPi.GPIO)

   _`daemon=True`_ betekent dat deze achtergrondthread de applicatie **niet** tegenhoudt om af te sluiten. Zodra het hoofd‑proces eindigt, wordt de daemon‑thread hard gestopt – ideaal voor housekeeping‑threads zoals onze GPIO‑watcher.

3. **Cleanup** (net vóór FastAPI afsluit):

Bij `yield` gaan we over naar de FastAPI app, als we de server stoppen, gaat de code verder na dit punt

```python
# Geef controle aan FastAPI/Socket.IO
yield

# TODO: GPIO cleanup and goodbye
# ...
logger.info("GPIO cleaned up – bye!")
```

### `gpio_keep_alive` thread

thread voor GPIO operaties

- callback aanmaken die `DataRepository.update_status_lamp` aanroept

> Door sio.emit aan te roepen via `asyncio.run_coroutine_threadsafe`

```python

led_state = False  # globale staat bovenaan

def gpio_keep_alive():
    """Registreert de knop‑callback en houdt de thread ‘alive’."""

    def button_pressed(channel):
        global led_state

        # Doe GPIO en DB dingen

        # ⬇️ We zitten nu in een *andere* thread dan de FastAPI‑event‑loop
        future = asyncio.run_coroutine_threadsafe(
            sio.emit("B2F_verandering_lamp", {"id": 1, "status": led_state}),
            asyncio.get_running_loop()
        )
        # `run_coroutine_threadsafe` post de coroutine naar de hoofd‑event‑loop
        # en geeft een *Future* terug waarmee je (optioneel) op fouten kunt wachten.
        logger.debug("Emit scheduled from GPIO thread – future: %s", future)

    GPIO.add_event_detect(...)
    logger.info("gpio_keep_alive gestart; wacht op button events…")

    while True:
        time.sleep(1)  # de thread levend houden
```

### PATCH‑endpoint uitbreiden

De REST‑route heet (voorbeeld) **`PATCH /lampen/{lamp_id}`** in `app.py`.
Voeg het fysieke aansturen toe en geef de functie een duidelijke naam.

```python
@app.patch("/lampen/{lamp_id}")
async def patch_lamp_state(lamp_id: int, new_state: bool):
    """Update lamp in DB + hardware + clients."""
    DataRepository.update_status_lamp(lamp_id, new_state)

    if lamp_id == 1:                       # enkel lamp 1 hangt fysiek aan de Pi
        # doe iets

    # ...

```

### Route `/allesuit/` herwerken

```python
@app.get("/allesuit/")
async def allesuit():
    # ...
    DataRepository.update_status_alle_lampen(0)

    # SOME GPIO OPERATION(S) to turn the LED off
    GPIO.output(LED_PIN, False)


    # ...
```

> **Waarom hier `asyncio.sleep()`?**
> Dit pauzeert alléén de huidige coroutine zonder de volledige event‑loop te blokkeren. Socket.IO‑events blijven dus realtime binnenkomen.

---

## **⚠️ TODO: Merge branch**

Eens dit werkt, commit en merge kickoff branch

We zullen de repo nadien opnieuw clonen maar deze keer in _~/project_ map  
Zo hebben we 2 workspaces binnen VSCode, 1 met het kickoff FSWD project, de andere met uw project

## **⚠️ TODO: Eigen database**

## **⚠️ TODO: Eigen database**

Op de image is reeds maria-db voorzien, met een database voor de demo.
Zorg dat je via MySQL Workbench kan verbinden _en maak een nieuwe database_

> **maak hiervan een screenshot**

(user: `root` ww: `r00tP@ss` ; gebruik SSH tunnel)

zie [configuratie.md](./2_Configuration.md) voor meer details

> **Laat dit fysiek controleren**

- 2 workspaces: kickoff en project
- werkende demo project met GPIO
- verbinding met MySQL Workbench

## OPGELET: Eigen Project // venv // git

Je zal waarschijnlijk gebruik maken van een eigen venv voor uw eigen project, zorg dat je deze map dan ook in je `.gitignore` plaatst
