<div dir="rtl" lang="he">

# איך זה עובד, ואיך מוסיפים תוכנה

עברית · [English](en/protocol.md)

## שלוש דרכים להגיע לתוכנה

| סוג | איפה הסקריפט רץ | למה זה משמש |
|---|---|---|
| `socket` | בתוך התוכנה, ב־thread הראשי שלה | תוכנות עם מנוע סקריפטים משלהן: Blender, Rhino, 3ds Max, SketchUp, FreeCAD, Maya, Fusion, Cinema 4D, Houdini, QGIS |
| `runner` | בתהליך עזר קצר־חיים ליד השרת, כשאובייקטי האוטומציה של התוכנה כבר מחוברים | תוכנות עם ממשק אוטומציה חיצוני: AutoCAD ותוכנות COM אחרות, Archicad ‏(JSON API), ‏Tekla ‏(‎.NET) |
| `revit`, `unreal` | בתוך התוכנה, דרך ערוץ שכבר קיים בה | pyRevit Routes, הרצת Python מרחוק של Unreal |

כל תוכנה היא רשומה אחת ב־`src/workit/registry.py`.

## פרוטוקול הגשר הפנימי

בקשה אחת לכל חיבור TCP, על `127.0.0.1` בלבד. שורת JSON אחת לכל כיוון.

בקשה:

```json
{"token": "...", "id": "ab12", "op": "exec", "code": "result = 1 + 1",
 "mode": "read", "label": "AI: add walls", "timeout": 120}
```

- `op`: ‏`ping`, ‏`exec` או `screenshot` (עם `path`, ‏`width`, ‏`height`).
- `mode`: ‏`read` או `modify`. רק `modify` נעטף בצעד ה־Undo של התוכנה.
- `token`: התוכן של `~/.workit/token`. בקשה בלי הטוקן נדחית. בקשה שהשורה הראשונה שלה
  אינה JSON תקין נזרקת בלי תשובה, כך שדפדפן לא יכול להגניב בקשה.

תשובה:

```json
{"id": "ab12", "ok": true, "result": 2, "stdout": "", "elapsed_ms": 3}
{"id": "ab12", "ok": false, "error": "NameError: ...", "traceback": "...", "stdout": ""}
```

התוצאה היא המשתנה `result` של הסקריפט אם הוא הוגדר, ואחרת הערך של הביטוי האחרון.
ערכים ש־JSON לא יכול לשאת חוזרים כ־`repr` שלהם. התשובה נבנית כ־JSON ב־ASCII בלבד
(`ascii_json`), כי המקודד של IronPython 2.7 נכשל על תווים מ־U+0080 עד U+00FF.

פורטים: לכל תוכנה יש פורט בסיס (Blender 47810, ‏Rhino 47820, ‏3ds Max 47830,
SketchUp 47840, ‏FreeCAD 47850, ‏Maya 47860, ‏Fusion 47870, ‏Cinema 4D 47880,
Houdini 47890, ‏QGIS 47900). מופע שני של אותה תוכנה מקבל את הפורט הבא, עד חמישה.
`cad_apps` מציג אותם, וכל כלי מקבל פרמטר `instance` אופציונלי.

## בעיית ה־thread הראשי

כל אחת מהתוכנות האלה דורשת שה־API שלה ייקרא מה־thread הראשי, בעוד שבקשת רשת מגיעה
ב־thread אחר. הקובץ `workit_core.py` (קובץ אחד בלי תלויות, Python 2.7 עד 3.13) פותר את
זה פעם אחת:

- ה־thread של ה־socket רק מפענח את הבקשה ושם משימה בתור;
- שכבת ההתאמה גורמת לתוכנה לקרוא ל־`bridge.pump()` ב־thread הראשי שלה, מתוך טיימר
  (`bpy.app.timers` ב־Blender, ‏`QTimer` של Qt ב־3ds Max, ‏FreeCAD ו־QGIS) או לפי דרישה
  דרך קריאת `wake` ‏(`InvokeOnUiThread` ב־Rhino, ‏`executeDeferred` ב־Maya, אירועים
  מותאמים ב־Fusion, ‏`SpecialEventAdd` ב־Cinema 4D, ‏`hdefereval` ב־Houdini);
- ה־thread של ה־socket ממתין למשימה ושולח את התשובה.

על `ping` עונה ה־thread של ה־socket בעצמו, כך שתוכנה עסוקה עדיין מוצגת כמחוברת.

## הוספת תוכנה שיש לה קונסולת Python

1. כותבים שכבת התאמה של כ־60 שורות, ליד האחרות ב־`src/workit/bridges/`:

   ```python
   import workit_core as core
   bridge = core.Bridge(
       "myapp", 47910,
       namespace={"api": the_apps_module},     # names scripts can use
       wrap=run_inside_one_undo_step,           # optional: wrap(fn, label)
       screenshot=save_viewport_png,            # optional: (path, width, height)
       wake=schedule_pump_on_main_thread,       # or call bridge.pump() from a timer
   )
   bridge.start()
   ```
2. מוסיפים ל־`registry.py` רשומת `App(...)` עם `kind="socket"` ואותו פורט.
3. מוסיפים ב־`installers.py` מתקין שמעתיק את שכבת ההתאמה ואת `workit_core.py` לתיקיית
   הטעינה האוטומטית של התוכנה.
4. כותבים את `skills/myapp.md`: שמות, יחידות, חמש דוגמאות, והמלכודות שנתקלתם בהן.
   תוספת ישראלית, אם צריך, נכתבת ב־`skills/il/myapp.md`.
5. מריצים `pytest`: בדיקות העקביות מוודאות שהפורט, מזהה התוכנה, המדריך והמתקין
   מתאימים זה לזה.

## הוספת תוכנת COM

מוסיפים רשומת `App(...)` עם `runner="com"` וה־ProgID שלה, ופונקציית "flavour" קטנה
ב־`runners/com.py` שנותנת שמות לאובייקטים שהסקריפטים מקבלים. ה־runner מתחבר לתוכנה
הפועלת, רושם מסנן הודעות COM כדי שתוכנה עסוקה תקבל ניסיון חוזר במקום להיכשל עם
"call was rejected by callee", מריץ את הסקריפט ויוצא.

## בדיקות

```bash
pytest
```

בדיקות הפרוטוקול משתמשות בתוכנה מדומה: thread רגיל שמשחק את ה־thread הראשי של תוכנה.
הן לא דורשות שום תוכנת CAD.

</div>
