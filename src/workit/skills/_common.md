## Rules that apply to every app

- **Returning data.** Set `result = ...` or end the script with an expression. Use plain
  dicts, lists, numbers and strings. Anything else comes back as its `repr`. Printed
  text also comes back. Never return thousands of items: count, filter or slice first.
- **Read or modify.** `cad_read` is for scripts that change nothing. Anything that
  creates, edits, deletes, saves or exports goes through `cad_modify`.
- **Small steps.** One short script per step, then check. A long script that fails on
  line 80 teaches you less than three short ones.
- **Look before you build.** Query the units, the active document and what is already
  there before you add geometry. Do not assume an empty model.
- **Verify.** After a change, read it back or call `cad_screenshot`. Report what you
  measured, not what you intended.
- **Never** save over, close or delete the user's file unless they asked for exactly that.
- **Dialogs block everything.** Do not call anything that opens a dialog or waits for a
  click. If a script times out, a dialog is probably open: tell the user.
