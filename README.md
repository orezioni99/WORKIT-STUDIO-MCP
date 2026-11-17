<div dir="rtl" lang="he">

# WORKIT STUDIO MCP

עברית · [English](docs/en/README.md)

**שרת MCP אחד. כל תוכנת CAD, BIM ותלת־ממד שאפשר לכתוב לה סקריפטים. כל מודל AI.**

WORKIT STUDIO MCP מאפשר ל־Claude, ChatGPT, Gemini, Cursor, Copilot או מודל מקומי לעבוד
בתוך תוכנות התכנון שעל המחשב שלכם: לקרוא את המודל, לשרטט, לערוך, לבדוק ולהסתכל על
התוצאה. הוא מדבר ב־[Model Context Protocol](https://modelcontextprotocol.io), ולכן כל
לקוח MCP יכול להשתמש בו.

הפרויקט הוא פורק של [OmniBridge MCP](https://github.com/ayoubmep/omnibridge-mcp),
מותאם לעבודה בישראל. ראו [התאמה לישראל](#התאמה-לישראל) ו[קרדיטים](#קרדיטים).

</div>

```
 Claude / ChatGPT / Gemini / Cursor / local model
                    |  MCP (stdio or HTTP)
           WORKIT STUDIO MCP server        5 tools, the same for every app
                    |
   +----------------+-----------------+----------------------+
   | in-app bridge  | automation      | the app's own channel|
   | (script runs   | (COM / .NET /   | (pyRevit Routes,     |
   |  inside)       |  JSON API)      |  Unreal remote exec) |
   +----------------+-----------------+----------------------+
   Blender, Rhino,   AutoCAD, SOLIDWORKS,  Revit, Unreal
   3ds Max, SketchUp Archicad, Navisworks,
   FreeCAD, Maya ... Inventor, Tekla ...
```

<div dir="rtl" lang="he">

## מה זה עושה

במקום לעטוף כל תוכנה במאות פקודות קבועות, השרת נותן למודל דרך להריץ סקריפט קצר בתוך
התוכנה, ומדריך שמסביר איך לכתוב את הסקריפט הזה נכון. לכן יש לו חמישה כלים בלבד, זהים
לכל התוכנות:

| כלי | מה הוא עושה |
|---|---|
| `cad_apps` | מציג את כל התוכנות הנתמכות ואילו מהן זמינות כרגע |
| `cad_skill` | מחזיר את מדריך הסקריפטים של תוכנה אחת: שפה, שמות מוגדרים מראש, יחידות, דוגמאות ומלכודות |
| `cad_read` | מריץ סקריפט שרק קורא מהמודל |
| `cad_modify` | מריץ סקריפט שמשנה את המודל, כצעד Undo אחד היכן שהתוכנה מאפשרת |
| `cad_screenshot` | מחזיר תמונה של חלון התוכנה, כדי שהמודל יבדוק את העבודה של עצמו |

קריאה ושינוי הם כלים נפרדים בכוונה: לקוח ה־MCP יכול לאשר קריאה אוטומטית ולבקש את
אישורכם לפני כל שינוי.

### דוגמה לשימוש

כותבים ל־AI בעברית רגילה, למשל:

> השתמש ב־WORKIT STUDIO MCP. כמה קירות, דלתות וחלונות יש במודל הפתוח ב־Revit בכל מפלס?

> ב־Revit, בתצוגה הפתוחה, הוסף מידות מהספוטים שבחדר האמבטיה אל פני הקירות, והראה לי
> צילום מסך.

דוגמאות נוספות: [examples/prompts.md](examples/prompts.md).

## התקנה, צעד אחר צעד

### מה צריך לפני שמתחילים

- Windows 10 או 11.
- [Python](https://www.python.org/downloads/) בגרסה 3.10 ומעלה. בהתקנה סמנו "Add Python to PATH".
- [Git](https://git-scm.com/download/win), כדי להוריד את הפרויקט.
- לקוח AI שתומך ב־MCP, למשל Claude Desktop או Claude Code.
- בשביל Revit: [pyRevit](https://github.com/pyrevitlabs/pyRevit/releases) מותקן.

### שלב 1: הורדת הפרויקט

פתחו PowerShell בתיקייה שבה אתם רוצים לשמור את הפרויקט, והריצו:

```bash
git clone https://github.com/orezioni99/WORKIT-STUDIO-MCP.git
```

```bash
cd WORKIT-STUDIO-MCP
```

### שלב 2: התקנת השרת

יוצרים סביבת Python נפרדת לפרויקט ומתקינים לתוכה:

```bash
python -m venv .venv
```

```bash
.venv\Scripts\pip install -e .
```

### שלב 3: בדיקה שההתקנה עובדת

```bash
.venv\Scripts\workit apps
```

הפקודה מדפיסה את רשימת התוכנות ואת המצב של כל אחת (`connected`, `not running` וכדומה).
אם קיבלתם רשימה, השרת מותקן.

### שלב 4: חיבור לקוח ה־AI

הפקודה הבאה מדפיסה את ההגדרה המדויקת למחשב שלכם:

```bash
.venv\Scripts\workit config claude-code
```

אפשר להחליף את `claude-code` ב־`claude-desktop`, `cursor`, `vscode`, `gemini`, `codex`,
`lmstudio`, `chatgpt` או `all`.

- **Claude Code:** מריצים את פקודת `claude mcp add` שהודפסה. הוסיפו `--scope user` כדי
  שהשרת יהיה זמין בכל הפרויקטים.
- **Claude Desktop:** מדביקים את קטע ה־JSON שהודפס בקובץ ההגדרות
  (Settings > Developer > Edit Config) ומפעילים מחדש את Claude Desktop.

הכלים מופיעים רק בשיחה חדשה. פירוט לכל לקוח: [docs/clients.md](docs/clients.md).

### שלב 5: חיבור התוכנות

**AutoCAD, SOLIDWORKS, Archicad ותוכנות אוטומציה אחרות** לא צריכות התקנה: מפעילים את
התוכנה ופותחים קובץ.

**Revit** צריך הרחבה קטנה בתוך pyRevit:

1. מתקינים את ההרחבה:

   ```bash
   .venv\Scripts\workit install revit
   ```

2. רושמים את התיקייה ב־pyRevit. הפקודה המדויקת מודפסת בסוף הצעד הקודם, והיא נראית כך:

   ```bash
   pyrevit extensions paths add "%USERPROFILE%\.workit\pyrevit"
   ```

   אם הפקודה `pyrevit` לא מזוהה, היא נמצאת ב־`%APPDATA%\pyRevit-Master\bin\pyrevit.exe`.

3. ב־Revit: לשונית pyRevit > Settings > Routes, ומסמנים את הפעלת שרת ה־Routes.
4. לוחצים על **Reload** בלשונית pyRevit.

**SketchUp, Blender, Rhino, 3ds Max ותוכנות אחרות עם גשר פנימי:**

```bash
.venv\Scripts\workit install sketchup
```

במקום `sketchup` אפשר לכתוב `blender`, `rhino`, `3dsmax`, `freecad`, `fusion`, `maya`,
`c4d`, `houdini`, `qgis`, או `all` לכל התוכנות שנמצאו במחשב. הפקודה מדפיסה את הצעד
הידני שנשאר, אם יש כזה (למשל הפעלה מחדש של התוכנה או סימון התוסף).

### שלב 6: שימוש ראשון

1. פותחים את התוכנה (למשל Revit) עם קובץ. מומלץ להתחיל על עותק ולא על קובץ העבודה.
2. פותחים שיחה חדשה בלקוח ה־AI.
3. כותבים: "השתמש ב־WORKIT STUDIO MCP. אילו תוכנות פתוחות אצלי?"

אפשר גם להריץ סקריפט ישירות מהטרמינל, לצורך בדיקה:

```bash
.venv\Scripts\workit run revit "result = doc.Title"
```

### פתרון בעיות

| מה רואים | מה לעשות |
|---|---|
| `Route does not exits: workit/ping` או "extension is not loaded" | ההרחבה לא נטענה. ודאו שרשמתם את התיקייה (שלב 5, צעד 2) ולחצו Reload ב־pyRevit. |
| Revit לא עונה (timeout) | Revit עסוק: באמצע Reload, באמצע פקודה, או שיש דיאלוג פתוח. סגרו את הדיאלוג ונסו שוב. |
| `revit ... not running` למרות ש־Revit פתוח | ודאו ש־Routes מופעל בהגדרות pyRevit. אם פתוח יותר מ־Revit אחד, השני מאזין על פורט 48885. |
| AutoCAD מופיע כ־"not running" מיד אחרי הפעלה | AutoCAD עדיין בטעינה. המתינו כמה שניות ונסו שוב. |
| הכלים לא מופיעים ב־Claude | פתחו שיחה חדשה. ב־Claude Desktop הפעילו את התוכנה מחדש. |
| הפקודה `workit` לא מזוהה | הריצו אותה עם הנתיב המלא: `.venv\Scripts\workit`. |

### עדכון והסרה

עדכון לגרסה האחרונה (מתוך תיקיית הפרויקט):

```bash
git pull
```

אחרי עדכון, הריצו שוב `workit install revit` ולחצו Reload ב־pyRevit, כדי שגם ההרחבה
שבתוך Revit תתעדכן.

הסרת הגשר מתוכנה:

```bash
.venv\Scripts\workit uninstall revit
```

הסרת השרת מ־Claude Code:

```bash
claude mcp remove "workit" -s user
```

## תוכנות נתמכות

"נבדק במקור" פירושו שמפתחי OmniBridge המקוריים הריצו את התוכנה מקצה לקצה לפני הפורק.
"נבדק בפורק" פירושו שהורץ גם תחת WORKIT STUDIO MCP. כל השאר נכתב לפי התיעוד הרשמי של
היצרן ועדיין לא הורץ בתוכנה אמיתית, כך שצפויים תיקונים קטנים בריצה הראשונה.

| תוכנה | איך מתחברים | שפת הסקריפט | מצב |
|---|---|---|---|
| **AutoCAD** (וגם Civil 3D, Plant 3D, Map 3D, MEP) | אוטומציית COM, בלי התקנה | Python | נבדק במקור (AutoCAD 2024) |
| BricsCAD, ZWCAD, GstarCAD, nanoCAD | אוטומציית COM (תואם AutoCAD) | Python | לא נבדק |
| **Revit** | הרחבת pyRevit ‏(Routes) | Python ‏(Revit API) | נבדק במקור (Revit 2026) **ונבדק בפורק (Revit 2025)** |
| **Archicad** | JSON API ותוסף Tapir | Python עם העוזר `ac` | נבדק במקור (Archicad 29) |
| Navisworks Manage / Simulate | אוטומציית COM (API ישן) | Python | ניסיוני |
| Rhino 7 / 8 / 9 ו־Grasshopper | גשר Python פנימי | Python | לא נבדק |
| 3ds Max 2021 ומעלה | גשר pymxs פנימי | Python ו־MAXScript | לא נבדק |
| SketchUp 2021 ומעלה | גשר Ruby פנימי | Ruby | לא נבדק |
| **Blender** 3.2 ומעלה | תוסף | Python ‏(bpy) | נבדק במקור (Blender 5.2) |
| FreeCAD 0.21 ומעלה | גשר בתיקיית Mod | Python | לא נבדק |
| Autodesk Fusion | תוסף | Python ‏(adsk) | לא נבדק |
| **SOLIDWORKS** | אוטומציית COM, בלי התקנה | Python | נבדק במקור (SOLIDWORKS 2025) |
| Inventor, CATIA V5, Solid Edge | אוטומציית COM | Python | לא נבדק |
| MicroStation | אוטומציית COM | Python | לא נבדק |
| Tekla Structures | Open API דרך pythonnet | Python | לא נבדק |
| ETABS, SAP2000, Robot | אוטומציית COM | Python | לא נבדק |
| Maya, Cinema 4D, Houdini | גשר Python פנימי | Python | לא נבדק |
| **Unreal Engine 5** | הרצת Python מרחוק, מובנית | Python | נבדק במקור (UE 5.8) |
| QGIS 3.28 ומעלה / 4 | תוסף | Python ‏(PyQGIS) | לא נבדק |

**לא אפשרי היום** (אין לתוכנות האלה ממשק סקריפטים): Twinmotion, Lumion, D5 Render,
Enscape, Shapr3D, Plasticity, AutoCAD LT ו־Navisworks Freedom. Vectorworks, Allplan
ו־NX מאפשרות רק תוספים שרצים בתוך התוכנה, והן בתוכנית העבודה.

פירוט מלא של מה נבדק ועל מה: [docs/status.md](docs/status.md).

## התאמה לישראל

כל מדריך ש־`cad_skill` מחזיר מסתיים בכללים לעבודה בישראל, ול־Revit, ל־AutoCAD (ולתוכנות
התואמות לו), ל־SketchUp ול־QGIS יש תוספות משלהם. הקבצים נמצאים ב־`src/workit/skills/il/`,
בנפרד מהמדריכים המקוריים, והם מכסים:

- **עברית:** שמות וטקסטים עוברים כמו שהם, בלי היפוך ובלי תרגום; תצוגה מימין לשמאל; פונטים.
- **יחידות:** סנטימטרים בתוכניות אדריכליות, מטרים בתוכניות מדידה ופיתוח.
- **קואורדינטות:** רשת ישראל החדשה (ITM, ‏EPSG:2039) ורשת ישראל הישנה (EPSG:28193).
- **תקנות ותקנים:** המודל מודד ומדווח, אבל לעולם לא קובע שתכנון עומד בתקן.
- **מילון מונחים:** עברית–אנגלית למונחי בנייה נפוצים (קיר, מפלס, ממ"ד, תב"ע ועוד).

המדריכים עצמם כתובים באנגלית עם מונחים בעברית, כי מי שקורא אותם הוא מודל ה־AI.

## בטיחות

מנוע סקריפטים בידי AI בתוך תוכנת התכנון שלכם הוא כלי חזק. התייחסו אליו בהתאם.

- **הסקריפטים לא רצים בארגז חול.** סקריפט יכול לעשות כל מה שהתוכנה יכולה, כולל מחיקת
  גיאומטריה וכתיבת קבצים. השאירו את בקשת האישור של `cad_modify` פעילה, עבדו על עותק
  של מודלים חשובים, ושמרו לפני שמתחילים.
- **צעד Undo אחד.** היכן שהתוכנה תומכת בכך, כל `cad_modify` הוא פעולה אחת בהיסטוריה,
  עם שם שמתאר מה ה־AI עשה.
- **טוקן סודי.** הגשרים מסרבים לכל בקשה שלא מכילה את הטוקן השמור ב־`~/.workit/token`.
  דף אינטרנט לא יכול לקרוא את הקובץ הזה.
- **גשרים פנימיים מאזינים רק למחשב המקומי** (`127.0.0.1`).
- **Revit הוא חריג:** שרת ה־Routes של pyRevit מאזין על כל כרטיסי הרשת (`0.0.0.0`) ואין
  לו אימות משלו. נקודות הקצה של WORKIT STUDIO MCP בודקות את הטוקן, אבל נקודות קצה אחרות
  של Routes במחשב לא. ברשת משרדית ודאו שחומת האש של Windows חוסמת את פורט 48884 מבחוץ.
- **מצב HTTP מיועד לרשת מהימנה בלבד.** ל־`workit serve --transport http` אין התחברות
  משלו. אם חושפים אותו דרך tunnel בשביל ChatGPT, השתמשו ב־tunnel שדורש אימות וסגרו
  אותו בסיום.

## איך זה עובד

- [docs/protocol.md](docs/protocol.md): הפרוטוקול, ואיך מוסיפים תוכנה (כ־60 שורות קוד
  לתוכנה שיש לה קונסולת Python).
- [docs/prior-art.md](docs/prior-art.md): שרתי MCP קיימים לכל תוכנה, השרתים של היצרנים
  עצמם, ובמה הפרויקט הזה שונה. אם אתם צריכים תוכנה אחת בלבד, ייתכן ששרת ייעודי יתאים
  לכם יותר.
- [docs/status.md](docs/status.md): מה בדיוק נבדק, ועל מה.

## קרדיטים

WORKIT STUDIO MCP מבוסס על [OmniBridge MCP](https://github.com/ayoubmep/omnibridge-mcp)
מאת OmniBridge contributors, ברישיון MIT. השרת, הגשרים והמדריכים המקוריים הם העבודה
שלהם. הפורק הזה שינה את השם, הוסיף את השכבה הישראלית, תיקן באגים שהתגלו בעבודה מול
Revit ותרגם את התיעוד לעברית.

OmniBridge עצמו נשען על הרעיונות של [pyRevit](https://github.com/pyrevitlabs/pyRevit),
[Tapir](https://github.com/ENZYME-APD/tapir-archicad-automation),
[blender-mcp](https://github.com/ahujasid/blender-mcp),
[rhinomcp](https://github.com/jingcheng-chen/rhinomcp) ושל הפרויקטים הרבים שמופיעים
ב־[docs/prior-art.md](docs/prior-art.md). הפרויקט לא כולל קוד מהם.

## רישיון

MIT. ראו [LICENSE](LICENSE). הודעת זכויות היוצרים המקורית של OmniBridge נשמרת בקובץ,
כנדרש ברישיון.

</div>
