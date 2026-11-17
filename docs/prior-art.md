<div dir="rtl" lang="he">

# פרויקטים קיימים

עברית · [English](en/prior-art.md)

הסקירה נעשתה על ידי פרויקט OmniBridge המקורי ב־14.11.2026. מספרי הכוכבים והרישיונות
נלקחו מה־API של GitHub באותו יום, והם משתנים עם הזמן. "אין קובץ רישיון" פירושו
שמשפטית אי אפשר לעשות שימוש חוזר בריפו כמו שהוא, לא משנה מה כתוב ב־README שלו.
WORKIT STUDIO MCP, כמו OmniBridge שעליו הוא מבוסס, לא כולל קוד מאף אחד מהפרויקטים האלה.

## מה השתנה ב־2026: היצרנים מפיצים שרתים משלהם

| שרת של היצרן | מצב | הערות |
|---|---|---|
| Blender Lab MCP ‏(`projects.blender.org/lab/blender_mcp`) | שוחרר, Blender 5.1 ומעלה | GPL-3.0, כולל `execute_blender_code` כללי |
| McNeel RhinoAI ‏(`github.com/mcneel/rhinoai`) | בבטא של Rhino 9; ב־Rhino 8 דרך Package Manager | MIT, ‏Grasshopper 1 ו־2, מריץ סקריפטים |
| Maxon Cinema 4D MCP Server | מובנה מגרסה 2026.4 | כבוי כברירת מחדל, אימות בטוקן, `exec_python` |
| Epic Unreal MCP plugin | ניסיוני, UE 5.8 | HTTP בלבד על 127.0.0.1:8000, בלי stdio |
| Autodesk Fusion MCP | זמין לכולם | HTTP מקומי על 127.0.0.1:27182 |
| Autodesk Revit Public MCP Server | תצוגה טכנית מקדימה, Revit 2027.2 בלבד | כלים קבועים, בלי הרצת קוד |
| Autodesk AutoCAD / Civil 3D MCP | בתוך התוכנה | שמיש רק מתוך Autodesk Assistant |
| Autodesk Inventor MCP | הוכרז עם 2027.2 | מקומי |
| Graphisoft Archicad MCP | בטא, Archicad 30, תוכניות בתשלום | stdio |
| pyRevit Agent Runtime ‏(`pyrevit mcp`) | יצא עם pyRevit 7.0 | Named pipe, ‏`run_query` / `run_modify` |
| Trimble SketchUp Connector | שוחרר | ענן בלבד: לא שולט ב־SketchUp שעל המחשב |
| IfcOpenShell `ifcopenshell-mcp` | 0.9.0 | עריכת IFC בלי תוכנה פתוחה |
| Bentley MicroStation MCP | גישה מוקדמת | למשתמשים מורשים בלבד |

**איפה הפרויקט הזה משתלב:** כל אחד מהשרתים האלה קשור לתוכנה אחת, לעיתים קרובות
לגרסה החדשה ביותר שלה, ולפעמים לתוכנית בתשלום או ללקוח AI אחד. WORKIT STUDIO MCP נותן
ממשק אחיד אחד לכל התוכנות והגרסאות (AutoCAD 2024, ‏Revit 2023, ‏Archicad 25,
Blender 3.x ועוד) ולכל הלקוחות. כשיש שרת של היצרן שמתאים לגרסה שלכם, הוא בחירה טובה
לאותה תוכנה. אפשר להתקין את שניהם זה לצד זה, אבל על מודל מסוים עובדים עם אחד בכל פעם.

## שרתים קהילתיים לפי תוכנה

### AutoCAD ותוכנות תואמות
- [daobataotie/CAD-MCP](https://github.com/daobataotie/CAD-MCP): ‏MIT, כ־700 כוכבים. COM דרך pywin32 ל־AutoCAD, ‏GstarCAD ו־ZWCAD.
- [puran-water/autocad-mcp](https://github.com/puran-water/autocad-mcp): ‏MIT, כ־650 כוכבים. מנתב AutoLISP עם תקשורת בקבצים, וכך הוא מגיע גם ל־AutoCAD LT.
- [AnCode666/multiCAD-mcp](https://github.com/AnCode666/multiCAD-mcp): ‏Apache-2.0. ‏AutoCAD, ‏ZWCAD, ‏GstarCAD, ‏BricsCAD.

### Revit
- [mcp-servers-for-revit/mcp-servers-for-revit](https://github.com/mcp-servers-for-revit/mcp-servers-for-revit): ‏MIT, כ־450 כוכבים. תוסף C#‎, ‏WebSocket.
- [mcp-servers-for-revit/mcp-server-for-revit-python](https://github.com/mcp-servers-for-revit/mcp-server-for-revit-python): ‏MIT. ‏pyRevit Routes, אותו ערוץ שהפרויקט הזה משתמש בו.
- [Sam-AEC/aec-model-bridge](https://github.com/Sam-AEC/aec-model-bridge): ‏GPL-3.0. סט כלים גדול.

### Archicad
- [ENZYME-APD/tapir-archicad-automation](https://github.com/ENZYME-APD/tapir-archicad-automation): ‏MIT. התוסף שהפרויקט הזה קורא לו.
- [SzamosiMate/tapir-archicad-MCP](https://github.com/SzamosiMate/tapir-archicad-MCP): ‏MIT. פקודות Tapir שנוצרו אוטומטית, מאחורי כלי list / schema / call.
- [lgradisar/archicad-mcp](https://github.com/lgradisar/archicad-mcp): ‏MIT.

### Navisworks
- [HorizunGroup/naviscoord-mcp](https://github.com/HorizunGroup/naviscoord-mcp): ‏MIT. תוסף ‎.NET, ‏53 כלים.
- [bimwright/nwd-mcp](https://github.com/bimwright/nwd-mcp): ‏Apache-2.0. תוסף שרץ בתוך התוכנה ומריץ C#‎. הדרך הזו מגיעה ל־Clash Detective, מה שדרך ה־COM של הפרויקט הזה לא יכולה.

### Rhino ו־Grasshopper
- [jingcheng-chen/rhinomcp](https://github.com/jingcheng-chen/rhinomcp): ‏MIT, כ־1,200 כוכבים. תוסף C#‎, הרצת סקריפטים, כלי Grasshopper.

### 3ds Max
- [cl0nazepamm/3dsmax-mcp](https://github.com/cl0nazepamm/3dsmax-mcp): ‏MIT, כ־390 כוכבים. תוסף C++‎ מקורי, יותר מ־160 כלים.

### SketchUp
- [mhyrr/sketchup-mcp](https://github.com/mhyrr/sketchup-mcp): כ־550 כוכבים, אין קובץ רישיון. הרחבת Ruby, ‏`eval_ruby`.
- [zinin/sketchup-mcp2](https://github.com/zinin/sketchup-mcp2): ‏MIT. שרת Ruby מבוסס טיימר, אותה גישת threading שהפרויקט הזה משתמש בה.

### Blender
- [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp): ‏MIT, כ־34 אלף כוכבים. הפרויקט שהפך את התבנית של תוסף + socket לנפוצה.

### FreeCAD, ‏Fusion, ‏SOLIDWORKS, ‏Inventor, ‏CATIA
- [neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp): ‏MIT, כ־3,300 כוכבים.
- [faust-machines/fusion360-mcp-server](https://github.com/faust-machines/fusion360-mcp-server): ‏MIT.
- [eyfel/mcp-server-solidworks](https://github.com/eyfel/mcp-server-solidworks): ‏AGPL-3.0. ‏[vespo92/SolidworksMCP-TS](https://github.com/vespo92/SolidworksMCP-TS): ‏MIT.
- [NeonGlay/inventor-mcp](https://github.com/NeonGlay/inventor-mcp): ‏MIT.
- [daiemon12/catia-v5-mcp-server](https://github.com/daiemon12/catia-v5-mcp-server): ‏MIT.

### קונסטרוקציה, Tekla ו־GIS
- [rclab-auth/csi-mcp](https://github.com/rclab-auth/csi-mcp): ‏MIT. ‏ETABS ו־SAP2000.
- [teknovizier/tekla_mcp_server](https://github.com/teknovizier/tekla_mcp_server): ‏GPL-3.0.
- [nkarasiak/qgis-mcp](https://github.com/nkarasiak/qgis-mcp): ‏GPL-2.0.

### Maya, ‏Cinema 4D, ‏Houdini, ‏Unreal
- [PatrickPalmer/MayaMCP](https://github.com/PatrickPalmer/MayaMCP): ‏MIT.
- [ttiimmaacc/cinema4d-mcp](https://github.com/ttiimmaacc/cinema4d-mcp): ‏MIT.
- [healkeiser/fxhoudinimcp](https://github.com/healkeiser/fxhoudinimcp): ‏MIT.
- [runreal/unreal-mcp](https://github.com/runreal/unreal-mcp): ‏MIT. משתמש בהרצת Python מרחוק, כמו הפרויקט הזה.

### פרויקטים לכמה תוכנות
- הארגון `dcc-mcp` ב־GitHub מפרסם מתאמים ל־Maya, ‏3ds Max, ‏Houdini ו־Cinema 4D.
- [Cai-aa/CAD-Agent-Hub](https://github.com/Cai-aa/CAD-Agent-Hub): ‏MIT. ‏CATIA, ‏SOLIDWORKS, ‏NX, ‏Fusion.

## החלטות תכנון שנלקחו מהסקירה

- **טווח פורטים משלו (47810 עד 47909).** פורט 9876 הוא ברירת המחדל של לפחות חמישה
  פרויקטים אחרים (Blender, ‏SketchUp, ‏Houdini, ‏FreeCAD, ‏Fusion), ולכן הם מתנגשים.
- **טוקן בכל גשר.** רוב הגשרים הקהילתיים מקבלים כל חיבור מקומי.
- **הרצת סקריפטים כממשק הראשי.** גם השרתים של היצרנים עצמם (Blender, ‏Rhino,
  Cinema 4D, ‏Fusion) הגיעו בסוף לחשוף את האפשרות הזו.
- **COM היכן שהוא קיים.** AutoCAD, ‏SOLIDWORKS, ‏Inventor ואחרות לא צריכות שום התקנה
  בתוך התוכנה.

</div>
