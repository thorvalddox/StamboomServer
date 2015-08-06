Voor de gene die dit leest, ik weet dat dit een gigantische rommel is.
Als ge eraan uit wilt kunnen zou ik dit aan mij persoonlijk (Thorvald Dox) vragen.

Als ge de code download en in het correcte framework stopt zal deze waarschijnlijk werken maar zal het onmogelijk zijn om in te loggen. Dit komt omdat de gebruikersnamen en wachtwoord-generatie-seed alleen op de server zijn opgeslagen. Bewerkt ook lieft niers in users.txt, dit zal waarschijnlijk leiden tot een merge-conflict wanneer ik deze inlaad in de server.

Werking van de command-API

<user> <command> <arguments>

user: degene die het commando heeft doorgevoert
command: het commando
arguments: de argumenten. Argumenten zijn altijd stings (dus typ geen ''). Deze worden letterlijk gebruikt, er is dus geen executie mogelijk.

Als het argument een naam is moet deze gescheiden worden door underscores, dus voornaam_achternaam
Als dit een datum is moet deze zoals 01/01/1990 ingegeven worden.

de user bestaat uit een teken plus een string. De tekens betekenen het volgende:

$ admin user (ook voor commandos dat het programma intern zelf maakt)
\# ingelogde users (gevolgt door naam)
? niet ingelogde users, hierna volgt het ip address.

De commando's zien er als volgt uit:
```
user person person_name 01/01/1900 01/01/2000 -> maakt een persoon aan of bewerkt een bestaande persoon
user family parent_1 parent_2 child_1 child_2 -> stelt een familie samen
user divorce person_1 person_2 -> duid een familie aan als gescheiden
user head person_name -> decaptiated
user delete person_name
user disband person_1 person_2
user parents child parent_1 parent_2
user merge person_1 person_2
```
Lege argumenten worden aangeduid met *

De eertse 4 functies worden ook gecreerd bij de computer gegeneerde comandos

Als ergens de naam van een niet-bestaande persoon wordt aangemaakt