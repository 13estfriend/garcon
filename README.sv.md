# GARCON — Garmin Connect → ChatGPT 🇸🇪

[English documentation](README.md) · [Garmins officiella Personal API](https://developer.garmin.com/gc-developer-program/personal/personal-api/) · [MIT-licens](LICENSE)

**Låt ChatGPT analysera din Garmin-träning utan att manuellt mata in eller skärmdumpa varje pass.**

GARCON är ett kostnadsfritt, fristående Python-skript byggt mot **Garmins officiella Personal API**. Det hämtar utvalda tränings- och återhämtningsvärden till en JSON-fil. Du kan köra det automatiskt via **GitHub Actions i ditt eget PRIVATA repo** eller helt **lokalt på din dator**. ChatGPT kan läsa filen via en ansluten GitHub-integration när den funktionen är tillgänglig på ditt konto, alternativt via vanlig filuppladdning.

GARCON är **inte** en officiell tjänst från Garmin eller OpenAI. Ingen central GARCON-server lagrar dina uppgifter. Varje användare ansvarar för sitt eget konto, sin API-nyckel och sin lagring.

## 🚨 VIKTIGT: DIN PERSONLIGA HÄLSO- OCH TRÄNINGSDATA LAGRAS PÅ GITHUB

> **ANVÄNDER DU DEN AUTOMATISKA GITHUB-SYNKEN LAGRAR DU DIN PERSONLIGA HÄLSO- OCH TRÄNINGSDATA PÅ GITHUB.**
>
> **VI REKOMMENDERAR Å DET STARKASTE ATT DU ANVÄNDER ETT PRIVAT REPOSITORY. LÄGG ALDRIG PERSONLIG HÄLSODATA I ETT PUBLIKT REPO.**
>
> JSON-filen kan innehålla **puls, träningspass, datum och klockslag, distans, effekt, kalorier, sömn och HRV**. Namn på aktiviteter kan också avslöja platser eller annat privat.
>
> **Privat på GitHub betyder inte att bara du tekniskt sett kan läsa all data.** GitHub lagrar innehållet och **Git-historiken**, och användare eller integrationer som du ger åtkomst kan läsa det. Om du ansluter ChatGPT till ditt repo ger du också ChatGPT åtkomst till den information som finns där. Kontrollera tjänsternas sekretessvillkor.
>
> **Inbyggd säkerhetsspärr:** Den medföljande GitHub Actions-synken kontrollerar att repot verkligen är **PRIVAT** och **vägrar köra uppladdningen om repot är PUBLIKT**. Detta är en extra skyddsåtgärd, inte en ersättning för att själv kontrollera inställningen.
>
> **Vill du inte lagra hälsodata på GitHub?** Kör skriptet **lokalt** i stället. Läs [Kör helt lokalt](#kör-helt-lokalt-utan-att-lagra-data-på-github).

Det här publika källkodsrepot innehåller **inga riktiga träningspass, inga API-nycklar och inga personliga hälsodata**.

## Vad gör GARCON?

- Hämtar utvalda aktiviteter från Garmin Connect: träningsform, datum, tid, längd, puls, effekt, förbrukning och träningsbelastning när uppgifterna finns.
- Försöker hämta sömn, HRV och dagliga värden när Garmin har registrerat dem.
- Skriver **data/training.json**, som ChatGPT kan analysera.
- Sparar **inte GPS-spår, exakta koordinater, kontolösenord eller API-nyckeln i JSON-filen**.
- Vid första körningen hämtas upp till **90 dagars aktivitetsdata**. Vid senare körningar uppdateras senaste **30 dagarna**. Tidigare aktiviteter behålls upp till **365 dagar** i den aktuella JSON-filen.
- Hämtar hälsosammanfattningar från senaste **8 kalenderdagarna**.
- Använder Garmins officiella Python-klient, Python 3.12 eller senare.

Garmins Personal API är avsett för att en person ska komma åt **sin egen data**. Se [Garmins frågor och svar](https://developer.garmin.com/gc-developer-program/personal/personal-faq). Den här lösningen är inte en central tjänst för andras Garmin-konton.

## Snabbstart: automatisk synkning via GitHub

### Steg 1 – Skapa ett EGET PRIVAT repo

1. Gå till [GARCON på GitHub](https://github.com/13estfriend/garcon).
2. Klicka på **Use this template → Create a new repository** (så snart template-funktionen är aktiverad av projektägaren).
3. Välj ditt eget GitHub-konto och döp repot till exempelvis **my-garmin-data**.
4. Välj **PRIVATE**. Kontrollera en gång extra.
5. Klicka på **Create repository**.

**VARNING:** Starta inte automatisk synk i det ursprungliga, **publika** GARCON-repot. Använd inte heller en publik fork för dina riktiga träningsuppgifter.

Syns inte knappen **Use this template**? Då måste projektägaren först slå på **Settings → General → Template repository**. Du kan även ladda ned koden och köra den lokalt.

### Steg 2 – Skapa din Garmin API-nyckel

1. Logga in på [Garmin Connect](https://connect.garmin.com/) på webben.
2. Öppna [Garmins officiella instruktioner för Personal API-nyckel](https://developer.garmin.com/gc-developer-program/personal/personal-api/).
3. Följ länken till sidan **Personal API Key**. Välj **Create Key**, acceptera villkoren, välj hur länge den ska gälla och skapa nyckeln.
4. **Kopiera nyckeln direkt.** Den visas bara en gång och ska hanteras som ett lösenord.

Nyckeln har en begränsad giltighetstid (högst ett år). När den löper ut behöver du skapa en ny och uppdatera hemligheten på GitHub.

### Steg 3 – Lägg in nyckeln i ett GitHub Secret

Du ska befinna dig i **ditt eget PRIVATA repo**.

1. Klicka på **Settings** i repot.
2. Välj **Secrets and variables → Actions**.
3. Klicka på **New repository secret**.
4. Under **Name**, skriv exakt:

   ~~~text
   GARMIN_PERSONAL_API_KEY
   ~~~

5. Klistra in din hemliga Garmin-nyckel under **Secret**.
6. Klicka på **Add secret**.

**Skicka aldrig API-nyckeln till ChatGPT eller lägg den i README, koden, en commit, en issue eller en skärmdump.**

### Steg 4 – Kör första synkningen

1. Öppna fliken **Actions** i ditt privata repo.
2. Om GitHub ber dig aktivera Actions, granska flödet och aktivera det.
3. Klicka på **Sync Garmin training data** i vänsterspalten.
4. Klicka på **Run workflow** och välj din standardbranch, vanligtvis **main**.
5. Kör och öppna jobbet. Vänta tills alla steg är gröna.
6. Öppna sedan filen **data/training.json** i repot. Den ska nu innehålla dina träningsvärden.

Vid meddelandet **GARCON SAFETY STOP** är repot publikt. Skapa ett **privat** repo i stället för att försöka stänga av spärren.

Vid meddelandet **Missing GARMIN_PERSONAL_API_KEY**, kontrollera att nyckeln ligger som secret i rätt repo och att namnet är exakt rätt.

### Steg 5 – Färdigt!

Nu uppdateras datafilen automatiskt enligt schemat. Standard är **06.25 och 20.25 svensk tid** varje dag. Du kan också köra flödet manuellt efter ett pass. GitHub kan ibland senarelägga schemalagda körningar.

Du hittar filen på:

~~~text
https://github.com/DITT-ANVÄNDARNAMN/DITT-PRIVATA-REPO/blob/main/data/training.json
~~~

## Ändra synktider och hur ofta synken ska köras

Öppna **ditt privata repo → .github/workflows/sync.yml**. Klicka på pennan för att redigera och välj sedan **Commit changes**.

I början av filen finns:

~~~yaml
on:
  workflow_dispatch:
  schedule:
    - cron: '25 6,20 * * *'
      timezone: 'Europe/Stockholm'
~~~

Detta betyder **kl. 06.25 och 20.25 varje dag i svensk tid**. Tidszonen följer svensk sommar- och vintertid. **cron** anger **minut timme dag-i-månaden månad veckodag**.

Några färdiga alternativ (byt ut hela **schedule**-blocket):

**Varje dag 07.15:**

~~~yaml
schedule:
  - cron: '15 7 * * *'
    timezone: 'Europe/Stockholm'
~~~

**Två gånger om dagen 06.25 och 20.25:**

~~~yaml
schedule:
  - cron: '25 6,20 * * *'
    timezone: 'Europe/Stockholm'
~~~

**Var fjärde timme:**

~~~yaml
schedule:
  - cron: '0 */4 * * *'
    timezone: 'Europe/Stockholm'
~~~

**Endast vardagar kl. 18.10:**

~~~yaml
schedule:
  - cron: '10 18 * * 1-5'
    timezone: 'Europe/Stockholm'
~~~

**Andra länder:** Ändra **timezone** till exempelvis **Europe/London**, **America/New_York** eller **Australia/Sydney**. Utan timezone använder GitHub UTC.

**Vill du bara synka manuellt?** Ta bort hela **schedule**-blocket och behåll **workflow_dispatch:**. Då kan du starta synkningen på Actions-sidan när du själv vill.

För de allra flesta räcker en eller två synkningar per dag. Att köra mycket oftare ökar användningen av GitHub Actions och belastningen på Garmins API. GitHub kan senarelägga körningar.

Referens: [GitHubs dokumentation om schemaläggning](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

## Koppla ditt GitHub-repo till ChatGPT

**VIKTIGT:** GARCON-koden skapar **inte** någon direkt Garmin-connector i ChatGPT. Den skriver en JSON-fil i ditt privata repo. ChatGPT behöver sedan kunna **läsa den filen via GitHub-integrationen**, om funktionen ingår i ditt abonnemang och det ChatGPT-läge du använder.

**Vi kan inte lova att GitHub-integrationen fungerar i vanliga ChatGPT-chattar på gratisabonnemanget.** Tillgängligheten varierar. Alternativet är att ladda upp JSON-filen manuellt till ChatGPT.

Så här gör du när GitHub-integrationen finns tillgänglig:

1. Öppna **ChatGPT → Settings → Plugins**.
2. Hitta **GitHub** och välj **Connect** eller motsvarande.
3. Logga in och godkänn anslutningen hos GitHub.
4. Välj helst **Only select repositories** och ge åtkomst till **endast ditt privata GARCON-repo**.
5. Spara behörigheterna.
6. Återgå till ChatGPT. Det kan ta ungefär fem minuter innan ett nyligen anslutet repo blir synligt.
7. Be ChatGPT läsa **data/training.json** från ditt specifika repo.

Exempel på fråga:

> Läs data/training.json i mitt GitHub-repo DITT-ANVÄNDARNAMN/DITT-PRIVATA-REPO. Analysera de senaste sju dagarnas träning, skilj mellan låg- och högintensiv träning och kommentera återhämtningen om sömn och HRV finns. Ange senaste synktid och var tydlig med uppgifter som saknas. Hitta inte på några pass.

Om ChatGPT inte hittar repot, kontrollera GitHub-anslutningen under **Settings → Plugins → GitHub**, eller [GitHubs installerade appar](https://github.com/settings/installations). Godkänn det nya repot separat om det behövs.

**Sekretess:** Att ansluta ett privat repo gör det inte publikt, men du ger ChatGPT behörighet att läsa innehållet i det repo som du väljer.

Officiell hjälp: [OpenAI – Connecting GitHub to ChatGPT](https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt).

### Om GitHub-pluginen inte fungerar med ditt ChatGPT-abonnemang

Öppna **data/training.json** i ditt privata GitHub-repo, välj **Raw/Download** medan du är inloggad och ladda sedan upp filen till ChatGPT. Det är ett manuellt steg, men du slipper dela hela repot. Filuppladdningar kan ha användningsgränser.

## Kör helt lokalt (utan att lagra data på GitHub)

Du kan använda samma kod **utan GitHub Actions och utan GitHub-lagring**. Då stannar JSON-filen på din dator tills du själv väljer att överföra eller dela den.

Du behöver Python **3.12 eller senare**, Garmin Connect med en personlig API-nyckel och eventuellt Git.

### 1. Ladda ned koden

~~~bash
git clone https://github.com/13estfriend/garcon.git
cd garcon
~~~

Du kan också klicka **Code → Download ZIP** i GARCON-repot, packa upp ZIP-filen och öppna en terminal i mappen.

### 2. Installera beroenden

**macOS/Linux:**

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
~~~

**Windows PowerShell:**

~~~powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
~~~

### 3. Kör skriptet

**macOS/Linux:**

~~~bash
python scripts/sync_garmin.py
~~~

**Windows PowerShell:**

~~~powershell
.\.venv\Scripts\python.exe scripts/sync_garmin.py
~~~

Skriptet ber om din Garmin-nyckel i terminalen om den inte redan finns i miljövariabeln **GARMIN_PERSONAL_API_KEY**. När du skriver nyckeln visas inga tecken, vilket hjälper till att undvika att den hamnar i terminalens kommandohistorik.

Resultatet skapas här:

~~~text
data/training.json
~~~

Filtypen är ignorerad i **.gitignore** vid lokal användning så att den inte lätt råkar följa med i en commit. **Lägg aldrig in filen i ett publikt Git-repo**, inte ens tillfälligt.

Du kan sedan ladda upp den direkt till ChatGPT för analys. Vill du köra igen använder du samma kommando. Det går också att schemalägga lokalt med Windows Aktivitetsschemaläggaren, cron eller motsvarande verktyg.

**Kom ihåg:** Lokal lagring ger dig mer direkt kontroll men skyddar inte automatiskt mot virus, obehöriga lokala användare eller osäkra säkerhetskopior.

## Vilken information sparas?

| Del i JSON-filen | Exempel |
|---|---|
| **activities** | Aktivitetstyp, eventuell titel, starttid, duration, distans, puls, effekt, kalorier, träningsbelastning |
| **sleep** | Total sömn, djupsömn, REM, uppvaknanden och poäng om värden finns |
| **hrv** | Nattens HRV, veckosnitt och status när Garmin lämnar ut det |
| **daily** | Exempelvis vilopuls, steg, stress och energi om uppgifterna finns |
| **sync_status** | Antal hämtade poster och fel per datakategori |
| **last_sync_utc** | Tidpunkten för den senaste sparade sammanställningen |

Inga GPS-spår eller rena koordinatfält exporteras avsiktligt. **Det betyder inte att filen är anonym**: tidpunkter, aktivitetstitlar och kroppsliga mätvärden är fortfarande personlig information. GARCON gissar inte heller vilken träningsform ett pass som Garmin kallar **Other/Annan** egentligen är.

Sömn och HRV kan saknas tills klockan har samlat in data och Garmin har gjort dem tillgängliga.

## Radera data, historik och åtkomst

**Att ta bort data/training.json innebär inte att alla gamla värden är raderade.** Tidigare versioner kan finnas i Git-historiken och eventuella säkerhetskopior. Du kan också tidigare ha lämnat uppgifterna till ChatGPT eller andra anslutna appar.

Vill du stoppa fortsatt synk: inaktivera det schemalagda jobbet, ta bort GitHub-secreten och återkalla Garmin-nyckeln i Garmin Connect. Om du vill ta bort lagringen behöver du även hantera historik, kopior och eventuella filuppladdningar. För känslig information kan det vara enklare att skapa ett nytt tomt repo och radera det gamla än att försöka skriva om Git-historiken.

**Om du någon gång exponerat data i ett PUBLIKT repo måste du betrakta den som potentiellt röjd.** Att göra repot privat efteråt återkallar inte automatiskt tidigare nedladdningar eller kopior.

## Felsökning

| Symptom | Kontrollera |
|---|---|
| **GARCON SAFETY STOP** | Ditt repo är publikt. Skapa ett **privat** repo |
| **Missing GARMIN_PERSONAL_API_KEY** | Rätt namn i **Settings → Secrets and variables → Actions** |
| **401/403 från Garmin** | Nyckeln kan ha löpt ut, återkallats eller vara felaktig |
| **data/training.json saknas** | Öppna körningen under **Actions** och läs felsteget |
| **Git push nekas** | Kontrollera GitHub Actions-behörigheter och eventuell organisationspolicy |
| **Ingen sömn/HRV** | Kontrollera först att Garmin Connect faktiskt visar sådan data |
| **ChatGPT ser inte repot** | Kontrollera GitHub-plugin, beviljade reporättigheter och tillgängligt läge/abonnemang |
| **Schemat kör inte** | Kontrollera att Actions är aktiverat och att workflow finns på standardbranchen |

Testa logiken utan Garmin-nyckel:

~~~bash
python -m unittest discover -s tests -v
~~~

## Licens och friskrivning

GARCON är släppt under **MIT-licensen**. Garmins officiella Python-klient är ett separat beroende under **Apache 2.0**.

GitHub Actions kan ofta köras inom GitHubs gratisnivå för små privata projekt. Kostnader och kvoter kan ändras; funktioner och abonnemang för ChatGPT är separata från GARCON.

Projektet är självständigt och har **ingen officiell koppling till eller sponsring från Garmin eller OpenAI**.

Träningsanalyser är vägledning och ska inte tolkas som medicinska bedömningar.

Lycka till med träningen! 💪
