# TheRealBicingBot™

TheRealBicingBot, un bot de Telegram que permet obtenir informació en temps real sobre el servei del Bicing. Especialment útil per als operaris que asseguren una bona distribució de les bicicletes, transportant-les amunt i avall en camió.
Segon projecte de programació d'[AP2](https://www.fib.upc.edu/ca/estudis/graus/grau-en-ciencia-i-enginyeria-de-dades/pla-destudis/assignatures/AP2-GCED)! Enunciat disponible [aquí](https://github.com/jordi-petit/ap2-bicingbot-2019).

Podeu provar el bot des d'aquí: [t.me/TheRealBicingBot](https://t.me/TheRealBicingBot)

## Getting Started

D'entrada, cal clonar aquest repositori a la vostra màquina local, feu-ho amb la comanda següent:

```
git clone https://github.com/rorencio/BicingBot.git
```
En cas de no tenir `git` instal·lat, podeu obtenir-lo des d'[aquí](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

### Prerequisits

Per a instal·lar el projecte, es requereix Python 3. Si no el teniu, podeu descarregar-lo des de la [web oficial](https://www.python.org/).

### Instal·lació

Sigui quin sigui el vostre sistema operatiu, per a fer la instal·lació tan sols cal que obriu un terminal a aquest directori i feu:
```
pip3 install -r requirements.txt
```
Això instal·larà automàticament tots els paquets que fan falta. I ja està, no cal res més!

Ara podeu provar localment les funcions de l'arxiu `data.py` o bé executar el vostre propi bot (vegeu [Deployment](#Deployment)).

## Execució dels tests

Per a testejar les funcions, simplement invoqueu-les des del programa `data.py` amb els paràmetres que vulgueu.

## Deployment

Per a disposar del vostre propi bot de Telegram, farà falta crear-lo (vegeu [BotFather](https://core.telegram.org/bots#6-botfather)). Un cop tingueu el vostre token deseu-lo al mateix directori on teniu el nostre projecte en un arxiu anomenat `token.txt`. Llavors, des d'un ordinador amb connexió a Internet llenceu el programa `bot.py` (tot fent `python3 bot.py`).
Mentre estigui corrent, podreu usar el bot. Si voleu executar-lo de forma més consistent, considereu usar un servidor.

## Eines usades

### Llibreries principals
* [NetworkX](https://atom.io/packages/hydrogen) - Creació i gestió de grafs
* [Pandas](https://pandas.pydata.org/) - Tractament de les dades
* [StaticMap](https://github.com/komoot/staticmap) - Ploteig dels mapes
* [Haversine](https://pypi.org/project/haversine/) - Càlcul de distàncies a partir de coordenades
* [GeoPy](https://geopy.readthedocs.io/en/stable/#) - Traducció d'adreces a coordenades

### Entorn de programció
* [Hydrogen](https://atom.io/packages/hydrogen) - Execució de codi de forma interactiva
* [Jupyter Notebook](https://jupyter.org/) - Execució de codi per blocs



## Autors

* **Marc Vernet** - [marc.vernet@est.fib.upc.edu](mailto:marc.vernet@est.fib.upc.edu)
* **Marc Gàllego** - [marc.gallego.asin@est.fib.upc.edu](mailto:marc.gallego.asin@est.fib.upc.edu)

Vegeu també la llista de [col·laboradors](https://github.com/rorencio/BicingBot/contributors) que han participat del projecte.

## Agraïments

* Part del codi ha estat desenvolupada pels nostres professors d'Algorísmia i Programació II, en Jordi Petit i en Jordi Cortadella.
