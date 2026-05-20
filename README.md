# KI-Chatbot Lehrtool

Dieses Repository enthält ein kleines, bewusst transparent aufgebautes Lehrtool, mit dem man nachvollziehen kann, wie ein einfacher KI-Chatbot aus Frontend, Backend und Provider-API zusammengesetzt wird.

Das Projekt orientiert sich optisch an bekannten Chat-Oberflächen wie ChatGPT, Gemini und Claude. Es ist aber kein Produktiv-Clone, sondern ein Lernprojekt: Die Oberfläche zeigt bewusst, welche Daten für eine Chatbot-Anfrage benötigt werden, wie ein System Prompt wirkt und wie ein Python-Backend Anfragen an unterschiedliche KI-Anbieter weiterleitet.

## Was Erstellt Wurde

Erstellt wurde eine lauffähige Web-App mit drei Bestandteilen:

1. Ein HTML/CSS/JavaScript-Frontend in `static/index.html`
2. Ein Python-Backend in `server.py`
3. Eine kleine Dependency-Liste in `requirements.txt`

Das Frontend bietet:

- Eine Chat-Oberfläche mit User- und Assistant-Nachrichten
- Eine Provider-Auswahl für OpenAI, Anthropic und Gemini
- Ein Eingabefeld für den eigenen API-Key
- Ein Eingabefeld für das Modell
- Ein Eingabefeld für den System Prompt
- Eine kurze technische Erklärung direkt in der Oberfläche
- Lokale Validierung, zum Beispiel wenn kein API-Key eingetragen wurde
- Responsives Layout, bei dem der Chat-Eingabebereich auch in schmalen Browserfenstern sichtbar bleibt

Das Backend bietet:

- Einen lokalen HTTP-Server mit Python-Standardbibliothek
- Auslieferung der statischen Frontend-Dateien
- Einen API-Endpunkt `POST /api/chat`
- Provider-spezifische Übersetzung der Chat-History in die Formate von OpenAI, Anthropic und Gemini
- HTTPS-Requests mit Zertifikatsprüfung über `certifi`
- Fehlerbehandlung für ungültige Eingaben, Provider-Fehler und Netzwerkfehler

## Projektziel

Das Ziel ist nicht nur, dass ein Chat funktioniert. Das Ziel ist, dass man versteht, wie ein Chat funktioniert.

Viele KI-Tutorials verstecken wichtige Details hinter SDKs, Frameworks oder fertigen Komponenten. Dieses Projekt geht bewusst einen Schritt darunter:

- Der Browser sammelt die Eingaben.
- Das Frontend sendet JSON an das eigene Backend.
- Das Backend prüft und normalisiert die Daten.
- Das Backend baut daraus eine Anfrage für den gewählten Anbieter.
- Der Anbieter antwortet mit JSON.
- Das Backend extrahiert den Antworttext.
- Das Frontend zeigt die Antwort als Chat-Nachricht an.

Damit sieht man den gesamten Weg von einer Texteingabe bis zur KI-Antwort.

## Warum Ein Python-Backend?

Ein Backend ist für einen KI-Chatbot wichtig, weil API-Keys normalerweise nicht direkt im Browser liegen sollten.

In diesem Lehrtool darf man den API-Key im Frontend eingeben, damit der Lernfluss sichtbar bleibt. Das ist didaktisch praktisch, aber in einer produktiven Anwendung würde man API-Keys anders behandeln:

- API-Keys liegen serverseitig in Umgebungsvariablen.
- Der Browser kennt den Provider-Key nicht.
- Das Backend kontrolliert Modelle, Limits, Logging und Sicherheit.
- Rate Limits, Abuse-Schutz und Kostenkontrolle werden serverseitig umgesetzt.

Python eignet sich hier gut, weil es leicht lesbar ist und ohne viel Projektsetup einen lokalen Server starten kann. Das Backend verwendet bewusst `http.server`, `urllib.request` und Standardbibliotheken, damit der Code möglichst nachvollziehbar bleibt.

## Warum Kein Großes Framework?

Das Projekt verwendet kein Flask, FastAPI, Django, React, Vue oder Vite.

Das ist Absicht. Für ein Lehrtool hat ein kleiner Stack Vorteile:

- Weniger Installation
- Weniger Magie
- Weniger Build-Schritte
- Mehr sichtbare Grundlagen
- Einfacher Einstieg für Anfängerinnen und Anfänger

Später kann man dieses Projekt problemlos ausbauen, zum Beispiel mit FastAPI im Backend oder React im Frontend. Die Kernidee bleibt aber gleich: Frontend sendet Chatdaten an Backend, Backend spricht mit Provider.

## Dateien Im Überblick

```text
.
├── README.md
├── requirements.txt
├── server.py
└── static
    └── index.html
```

### `server.py`

`server.py` startet den lokalen Python-Server.

Der Server erfüllt zwei Aufgaben:

1. Er liefert die Dateien aus dem Ordner `static` aus.
2. Er nimmt Chat-Anfragen auf `/api/chat` entgegen.

Der wichtigste Ablauf ist:

```text
Browser
  -> POST /api/chat
  -> Python Backend
  -> OpenAI / Anthropic / Gemini
  -> Python Backend
  -> Browser
```

### `static/index.html`

Diese Datei enthält das gesamte Frontend:

- HTML-Struktur
- CSS-Layout
- JavaScript-Logik

Die App ist bewusst in einer Datei gehalten, damit man als Lernende oder Lernender schnell versteht, welche Teile zusammengehören.

### `requirements.txt`

Enthält aktuell:

```text
certifi>=2025.10.5
```

`certifi` wird verwendet, damit Python beim Verbinden zu den Provider-APIs ein aktuelles CA-Zertifikat-Bundle nutzt. Das verhindert typische lokale Fehler wie:

```text
SSL: CERTIFICATE_VERIFY_FAILED
```

## Installation

Voraussetzung:

- Python 3
- Internetverbindung
- API-Key von mindestens einem unterstützten Anbieter

Optional, aber empfohlen:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Dependencies installieren:

```bash
python3 -m pip install -r requirements.txt
```

Server starten:

```bash
python3 server.py
```

Dann im Browser öffnen:

```text
http://127.0.0.1:5173
```

Falls Port `5173` bereits belegt ist, kann ein anderer Port verwendet werden:

```bash
PORT=8000 python3 server.py
```

Dann öffnen:

```text
http://127.0.0.1:8000
```

## Bedienung

1. Anbieter auswählen: OpenAI, Anthropic oder Gemini
2. API-Key eintragen
3. Modell prüfen oder ändern
4. System Prompt anpassen
5. Nachricht in das Chatfeld schreiben
6. Senden klicken

Die Antwort wird anschließend als Assistant-Nachricht im Chat angezeigt.

## Unterstützte Anbieter

### OpenAI

OpenAI wird über die Responses API angesprochen:

```text
POST https://api.openai.com/v1/responses
```

Das Backend sendet:

- `model`
- `instructions` als System Prompt
- `input` als Chatverlauf

Beispielmodell im Frontend:

```text
gpt-5-mini
```

### Anthropic

Anthropic wird über die Messages API angesprochen:

```text
POST https://api.anthropic.com/v1/messages
```

Das Backend sendet:

- `model`
- `system` als System Prompt
- `messages` als Chatverlauf
- `max_tokens`

Beispielmodell im Frontend:

```text
claude-opus-4-1-20250805
```

### Gemini

Gemini wird über `generateContent` angesprochen:

```text
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
```

Das Backend sendet:

- `contents` als Chatverlauf
- `systemInstruction` als System Prompt

Beispielmodell im Frontend:

```text
gemini-2.5-flash
```

## Wie Der Chatverlauf Funktioniert

Das Frontend speichert den Chatverlauf im Browser in einem JavaScript-Array:

```js
const messages = [];
```

Jede Nachricht hat diese Struktur:

```json
{
  "role": "user",
  "content": "Hallo!"
}
```

Oder:

```json
{
  "role": "assistant",
  "content": "Hallo! Wie kann ich helfen?"
}
```

Bei jeder neuen Anfrage wird der bisherige Verlauf mitgesendet. Das ist wichtig, weil viele Chat-APIs zustandslos sind. Das bedeutet: Der Anbieter weiß nicht automatisch, was vorher im Chat passiert ist. Das Backend muss den bisherigen Verlauf erneut mitschicken.

## Was Ist Ein System Prompt?

Der System Prompt legt fest, wie sich der Chatbot verhalten soll.

Beispiel:

```text
Du bist ein hilfreicher Tutor. Erkläre verständlich, zeige kurze Beispiele und frage nach, wenn etwas unklar ist.
```

Der System Prompt ist keine normale User-Nachricht. Er ist eine übergeordnete Anweisung an das Modell. Typische Einsatzzwecke:

- Rolle definieren
- Tonalität festlegen
- Antwortlänge steuern
- Formatvorgaben machen
- Zielgruppe beschreiben
- Grenzen setzen

In diesem Lehrtool kann man den System Prompt direkt verändern und beobachten, wie sich die Antworten dadurch ändern.

## API-Key Sicherheit

Dieses Projekt ist ein Lehrtool. Deshalb kann man den API-Key im Frontend eingeben.

Wichtig: Für produktive Anwendungen ist das nicht ideal.

Warum?

- Browser-Code ist für Nutzer sichtbar.
- Eingegebene Keys können in Browser-Tools oder Logs auftauchen.
- Eine öffentliche Website darf niemals private Provider-Keys im Frontend ausliefern.

In echten Anwendungen sollte man API-Keys so speichern:

```bash
export OPENAI_API_KEY="..."
export ANTHROPIC_API_KEY="..."
export GEMINI_API_KEY="..."
```

Und dann im Backend lesen:

```python
os.environ["OPENAI_API_KEY"]
```

Für dieses Projekt wurde die Eingabe im Frontend trotzdem umgesetzt, weil explizit sichtbar werden soll, welche Rolle ein API-Key in der Provider-Kommunikation spielt.

## Fehlerbehandlung

Das Backend gibt JSON-Fehler zurück.

Beispiele:

Wenn keine Daten gesendet werden:

```json
{
  "error": "Request body is empty."
}
```

Wenn der Provider fehlt:

```json
{
  "error": "provider is required."
}
```

Wenn der API-Key falsch ist, kommt ein Provider-Fehler zurück, zum Beispiel:

```json
{
  "error": "Provider returned HTTP 401",
  "details": {
    "error": {
      "message": "Incorrect API key provided."
    }
  }
}
```

Wenn ein Zertifikatsproblem auftritt, hilft in der Regel:

```bash
python3 -m pip install -r requirements.txt
```

Das Projekt nutzt `certifi`, um Python ein aktuelles Zertifikat-Bundle zu geben.

## Warum Provider Unterschiedlich Behandelt Werden

OpenAI, Anthropic und Gemini erfüllen ähnliche Aufgaben, aber ihre APIs sind unterschiedlich aufgebaut.

Beispiele:

- OpenAI nutzt `instructions` für den System Prompt.
- Anthropic nutzt `system`.
- Gemini nutzt `systemInstruction`.
- OpenAI nennt Assistant- und User-Nachrichten anders als Gemini.
- Gemini verwendet für Assistant-Antworten die Rolle `model`.

Das Backend enthält deshalb getrennte Funktionen:

```python
call_openai(...)
call_anthropic(...)
call_gemini(...)
```

Diese Funktionen zeigen sehr gut, warum ein Backend als Übersetzungsschicht hilfreich ist.

## Validierung

Während der Entwicklung wurden folgende Checks durchgeführt:

```bash
python3 -m py_compile server.py
```

Außerdem wurde geprüft:

- Die Seite lädt im Browser.
- Der Eingabebereich bleibt im Viewport sichtbar.
- Die Fehlermeldung erscheint, wenn kein API-Key eingegeben wurde.
- Der Provider-Wechsel aktualisiert Modell und Anzeige.
- Ein falscher OpenAI-Key führt zu `HTTP 401` statt zu einem lokalen SSL-Fehler.

## Mögliche Erweiterungen

Dieses Projekt ist bewusst klein gehalten. Gute nächste Schritte wären:

- Streaming-Antworten per Server-Sent Events
- Speicherung von Chatverläufen
- Provider-Keys als Umgebungsvariablen
- FastAPI-Backend
- React- oder Vue-Frontend
- Markdown-Rendering für Assistant-Antworten
- Modell-Listen direkt von den Providern laden
- Token- und Kostenanzeige
- Temperatur- und Max-Token-Einstellungen
- System-Prompt-Vorlagen
- Export von Chatverläufen
- Rate-Limiting
- Login-System
- Deployment auf einem Server

## Bekannte Einschränkungen

- Der Chatverlauf wird nur im Browser gehalten und geht beim Neuladen verloren.
- Es gibt noch kein Streaming; Antworten erscheinen erst, wenn der Provider vollständig geantwortet hat.
- API-Keys werden im Frontend eingegeben, was nur für ein lokales Lehrtool gedacht ist.
- Es gibt keine Nutzerverwaltung.
- Es gibt keine Kostenkontrolle oder Rate-Limits.
- Provider-Modelle können sich ändern; falls ein Modell nicht mehr verfügbar ist, sollte das Modellfeld angepasst werden.

## Zusammenfassung

Dieses Projekt zeigt die Grundstruktur eines KI-Chatbots:

```text
Frontend
  sammelt Eingaben und zeigt Chat an

Backend
  validiert Daten und spricht mit KI-Anbietern

Provider API
  erzeugt die eigentliche KI-Antwort
```

Damit eignet sich das Repository als Einstiegspunkt, um zu lernen, wie moderne KI-Chatbots technisch aufgebaut sind und warum Frontend, Backend, System Prompt, Modellwahl und API-Key jeweils eigene Rollen haben.
