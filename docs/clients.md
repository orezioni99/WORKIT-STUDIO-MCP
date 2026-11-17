<div dir="rtl" lang="he">

# חיבור לקוח AI

עברית · [English](en/clients.md)

הפקודה `workit config <client>` מדפיסה את ההגדרה עם הנתיב הנכון למחשב שלכם. הדף הזה
מסביר מה כל לקוח יכול ומה לא. מיקומי קובצי ההגדרות נבדקו מול התיעוד של כל יצרן
בנובמבר 2026. הם משתנים, ולכן אם דף היצרן אומר אחרת, סמכו עליו.

## לקוחות שמפעילים את השרת בעצמם (הכי פשוט)

הלקוחות האלה רצים על המחשב שלכם ומפעילים את השרת כתוכנה מקומית (stdio). שום דבר לא
נחשף לרשת.

| לקוח | איפה שמים את ההגדרה |
|---|---|
| Claude Desktop | `%APPDATA%\Claude\claude_desktop_config.json` ‏(Settings > Developer > Edit Config) |
| Claude Code | `claude mcp add workit -- workit` |
| Cursor | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code עם GitHub Copilot | `.mcp.json` בתיקיית השורש של סביבת העבודה |
| Gemini CLI | `%USERPROFILE%\.gemini\settings.json` |
| Antigravity | `%USERPROFILE%\.gemini\config\mcp_config.json` |
| Codex CLI | `%USERPROFILE%\.codex\config.toml` |
| LM Studio (מודלים מקומיים) | לשונית Program > Install > Edit mcp.json |

כולם, חוץ מ־Codex, משתמשים באותו מבנה JSON:

```json
{
  "mcpServers": {
    "workit": { "command": "workit", "args": [] }
  }
}
```

Codex משתמש ב־TOML:

```toml
[mcp_servers.workit]
command = "workit"
args = []
```

אם הלקוח לא מוצא את `workit`, השתמשו בנתיב המלא ש־`workit config <client>` מדפיס.
כשהשרת מותקן בתוך `.venv` של הפרויקט, זה בדרך כלל המצב.

## לקוחות שצריכים כתובת URL

ChatGPT, אפליקציית Gemini, מחברים מותאמים ב־Claude.ai ו־Open WebUI לא יכולים להפעיל
תוכנה על המחשב שלכם. מריצים את השרת במצב HTTP:

```bash
workit serve --transport http --port 8765
```

השרת זמין אז בכתובת `http://127.0.0.1:8765/mcp`.

- **Open WebUI וכלים אחרים על אותו מחשב** יכולים להשתמש בכתובת הזו ישירות
  (מתוך Docker: `http://host.docker.internal:8765/mcp`).
- **ChatGPT, אפליקציית Gemini ומחברי Claude.ai** רצים בענן של היצרן, ולכן הם צריכים
  כתובת HTTPS ציבורית שמעבירה למחשב שלכם: Secure MCP Tunnel של OpenAI, או tunnel כמו
  cloudflared או ngrok. את הכתובת שמתקבלת (`https://.../mcp`) מוסיפים בלקוח כשרת MCP
  מותאם.

**קראו לפני שפותחים tunnel.** למצב ה־HTTP אין התחברות. כל מי שמגיע לכתובת יכול להריץ
סקריפטים בתוכנות ה־CAD שלכם. השתמשו ב־tunnel שאוכף אימות, אל תפרסמו את הכתובת, וסגרו
את ה־tunnel כשסיימתם. לעבודה יומיומית עדיף לקוח מהטבלה הראשונה.

## מודלים מקומיים

כל מודל מקומי עובד דרך לקוח שמדבר MCP: ‏LM Studio, או Ollama מאחורי Open WebUI או
`ollmcp`. התוצאות תלויות מאוד במודל: כתיבת סקריפטים ל־API של תוכנת CAD דורשת מודל קוד
חזק. הכלי `cad_skill` קיים כדי לתת למודלים קטנים את העובדות שחסרות להם.

</div>
