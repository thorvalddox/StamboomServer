#stamboomserver

Voor de gene die dit leest, ik weet dat dit een gigantische rommel is.
Als ge eraan uit wilt kunnen zou ik dit aan mij persoonlijk (Thorvald Dox) vragen.

Als ge de code download en in het correcte framework stopt zal deze waarschijnlijk werken maar zal het onmogelijk zijn om in te loggen. Dit komt omdat de gebruikersnamen en wachtwoord-generatie-seed alleen op de server zijn opgeslagen. 

##Werking van de command-API

<user> <command> <arguments>

user: degene die het commando heeft doorgevoert
command: het commando
arguments: de argumenten. Argumenten zijn altijd stings (dus typ geen ''). Deze worden letterlijk gebruikt, er is dus geen executie mogelijk.

Als het argument een naam is moet deze gescheiden worden door underscores, dus voornaam_achternaam
Als dit een datum is moet deze zoals 01/01/1990 ingegeven worden.

de user bestaat uit een teken plus een string. De tekens betekenen het volgende:

* $: admin user (ook voor commandos dat het programma intern zelf maakt)
* \#: ingelogde users (gevolgt door naam)
* ?: niet ingelogde users, hierna volgt het ip address.

De commando's zien er als volgt uit:
```
user person person_name 01/01/1900 01/01/2000 -> maakt een persoon aan of bewerkt een bestaande persoon
user family parent_1 parent_2 child_1 child_2 -> stelt een familie samen
user divorce person_1 person_2                -> duid een familie aan als gescheiden
user head person_name                         -> decaptiated gebruik nu /view/

user remarry person_1 person_2                -> duid een familie aan als niet gescheiden
user delete person_name                       -> verwijderd een persoon en alle conecties
user disband person_1 person_2                -> als deze 2 verbonden zijn worden deze ontkoppeld. ontkoppeld ook alle kinderen
user parents child parent_1 parent_2          -> verwijderd de familie waarvan "child" een kind is en voeg deze toe aan de familie gedefinieerd door parent_1 parent_2
user sibling person_1 person_2                -> delete ties of person_2 and gives him the same parents as person_1
user merge person_1 person_2                  -> verwijderd persoon 2 en voegt alle verbindingen toe aan persoon_1
```
Lege argumenten worden aangeduid met *

De eertse 4 functies worden ook gecreerd bij de computer gegeneerde comandos

Als ergens de naam van een niet-bestaande persoon wordt opgegeven wordt deze aangemaakt.

##TO DO

Noteer dingen op de lijst als:
- [ ] To do
- [x] Bezig
-     In Orde


Verwijder ze van de lijst als ze in orde zijn.

###TO DO list

- [ ] Docs moeten de :param arg: tags correct tonen (om een of andere reden doen ze dat niet.
- [ ] Koppelen van logins aan personen
- [ ] Inschrijvingsformulieren, gekoppeld aan personen
- [ ] Naamkaartjes
- [ ] meer login functies (wachtwoord wijzigen, herstellen), (nieuwe accounts)
- [ ] Aanpassen van tekenalgorimte zodat niet alleen nakomelingen en partners hiervan getekend worden maar ook die hun voorouders
- Aanpassen van downloadcode voor support voor IE en Google Chrome (postscript?)
- [ ] Maken van een blacklist van users die genegreerd worden in het creatiecommando (shadowban)
- [ ] Comprimeren (of ten minste opslaan) van de stamboom om deze sneller te laden. Deze moet aangepast worden telkens al er een commando bij op de lijst komt. (json?)
- Website moet volledig offline werken zodat deze kan aangepast worden op het doxenfeest zelf en dat de stamboom getest kan worden zonder hem te uploaden.
- [ ] Github moet de documenatie kunnen lezen
- [ ] Github moet een wiki krijgen met daarin het gebruik (dus niet de werking, da moet in de docs) van alle functies van de site.
- [ ] cathing van meerdere errors (403,400) enz en correcte catching van 500
- [ ] Fix de autoupdate zodat deze blijft runnen als de server crashed (gedeeltelijk gedaan met de @cath_error decorator)
- [ ] automatisch de docs generenen op "git push"
- [ ] meer admin controle
- [ ] betere interface voor de console
- [ ] meer bewerk opties (bv naam wijzigen, ...)
- [ ] commando om de ministamboom in het groot te doen
- [ ] geslachten
- [ ] anders tonen van gescheiden families
- [ ] comprimeren van fotos na uploaden (nieuw formaat max 600x400) om geheugenruimte te sparen
- [ ] verwijderen van ongebruikte fotos met toestemming van de admin (rollback)


- [ ] betere layout en css
- [ ] volledigere docs & docstrings
- [ ] statistieken
- [ ] meer informatie zoals sterrenbeelden
- [ ] homepage
- [ ] meer/duidelijkere interlinking
- [ ] Profiler/optimising
- [ ] fix docs :param:
- [ ] overall cleanup & refractor


