#stamboomserver

Voor de gene die dit leest, ik weet dat dit een gigantische rommel is.
Als ge eraan uit wilt kunnen zou ik dit aan mij persoonlijk (Thorvald Dox) vragen.

Als ge de code download en in het correcte framework stopt zal deze waarschijnlijk werken maar zal het onmogelijk zijn om in te loggen. Dit komt omdat de gebruikersnamen en wachtwoord-generatie-seed alleen op de server zijn opgeslagen. 


##TO DO

Noteer dingen op de lijst als:
- [ ] To do
- [x] Bezig
-     In Orde

Documenteer u code! plz

Verwijder ze van de lijst als ze in orde zijn.

###TO DO list
####Very high priority
- [ ] SQL database moet werken
- [ ] Gebruik van flask-security en flask-social om "login with facebook/login with google/login with twitter" knoppen te maken, en de clusterfuck da de logins nu zijn te verwijderen.
- [ ] Maken van een blacklist van users die genegreerd worden in het creatiecommando (shadowban)

####high priority
- [ ] Inschrijvingsformulieren, gekoppeld aan personen
- [ ] Naamkaartjes
- [ ] Fix de autoupdate zodat deze blijft runnen als de server crashed (gedeeltelijk gedaan met de @cath_error decorator)
- [ ] anders tonen van gescheiden families (dit is geimplementeerd maar werkt niet).

####normal priority
- [ ] Docs moeten de :param arg: tags correct tonen (om een of andere reden doen ze dat niet).
- [ ] Github moet een wiki krijgen met daarin het gebruik (dus niet de werking, da moet in de docs) van alle functies van de site.
- [ ] Correcte catching van 500
- [ ] automatisch de docs generenen op "git push" of op autoupdate
- [ ] geslachten
- [ ] comprimeren van fotos na uploaden (nieuw formaat max 600x400) om geheugenruimte te sparen
- [ ] betere layout en css
- [ ] meer/duidelijkere interlinking

####low priority
- [ ] Koppelen van logins aan personen
- [ ] Aanpassen van tekenalgorimte zodat niet alleen nakomelingen en partners hiervan getekend worden maar ook die hun voorouders
- [ ]Website moet volledig offline werken zodat deze kan aangepast worden op het doxenfeest zelf en dat de stamboom getest kan worden zonder hem te uploaden.
- [ ] Github moet de documenatie kunnen lezen
- [ ] meer admin controle
- [ ] betere interface voor de console
- [ ] verwijderen van ongebruikte fotos met toestemming van de admin (rollback)
- [ ] statistieken
- [ ] meer informatie zoals sterrenbeelden
- [ ] homepage
- [ ] wapen van de doxen in de rechterbovenhoek.

##Werking van de command-API
!! Is bezig met vervangen te worden door de sql-server.
!! Het opslagen van de data wordlt binnenkort vervangen door sql maar deze zal blijven in gebruik genomen worden voor Rollback puporses


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

## Storage in SQL

2 tables

People:

bevat:

name: string: naam van persoon
birth: date: geboortedatum of null
dead: date: sterftedatum of null


