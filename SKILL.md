---
name: cubbie-clash
description: Turns the student's Canvas grades into Points and Mana for a battle game played with friends in the browser, and sets up daily and weekly rundowns of what is due and on their calendar. Use when the student says "start clash", "join clash <code>", "clash", "leave clash", "mute clash", asks about Clash points, Mana or the game link, or asks for daily or weekly reminders, a morning or evening rundown, a weekly recap or "set up my rhythm".
---

# Cubbie Clash

Every graded assignment earns Points and Mana. Mana powers attacks in a turn-based browser duel against friends.
Friends only ever see Points, never grades. The same Skill also runs the student's daily and weekly rundowns
(see "Daily rhythm" below). Keep every message to one or two lines, with the link on its own line.

## What gets sent to the game server

Say this to the student before the first sync, in plain words, and wait for a yes:

"Clash sends only a score percentage, an assignment type and a course difficulty number to the game server. It never
sends assignment names, course names or your actual grades. Okay to continue?"

Never sync anything before that yes.

## Setup (first time only)

1. Ask the student's display name for the game and an invite code if a friend gave them one. Remember the display
   name.
2. Run `python3 scripts/clash.py optin --name "<display name>" [--code <invite code>]`. It saves a private token for
   this student. Do not print or repeat the token.
3. If the student has no invite code, tell them the script printed a new squad code and ask them to share it with
   friends themselves in their own group chat. Do not message friends for them.
4. If Canvas is not connected, ask the student to connect it and stop here.
5. Ask what time of day they want a grade check, suggest 8 pm, then create a daily scheduled check-in at that time
   that says: "Run the cubbie-clash grade sync".

## Grade sync (the daily check-in, or when the student asks)

1. Read the student's Canvas courses and graded assignments from the past 14 days. If Canvas is not connected, ask
   the student to connect it and stop here.
2. Skip ungraded, excused and zero-point assignments.
3. For each assignment, choose a type using the assignment group, name and syllabus weight:
   `final_exam`, `capstone`, `test`, `quiz` or `homework`. When unsure, use `homework`.
4. For each course not yet remembered this semester, choose a difficulty from 1.0 to 1.5 and remember it so the
   course always counts the same:
   start at 1.0; add 0.1 for a 200-level course, 0.2 for 300-level, 0.3 for 400-level or graduate; add up to 0.2
   for subject rigor (organic chemistry, physics, upper-division math or CS, engineering core); add up to 0.1 for a
   lab or many high-weight exams; add up to 0.1 for a low class average if visible. Round to the nearest 0.05 and
   cap at 1.5. If there is not enough information, use 1.0.
5. Write a file `grades.json` in the working folder: a list of objects with `id` (Canvas assignment id), `course_id`
   (Canvas course id), `type`, `pct` (0 to 100), and `difficulty`.
6. Run `python3 scripts/clash.py sync --file grades.json`. Read its short output.
7. Text the student one or two lines: Points and Mana earned, which assignment earned it (this is their own private
   message, so naming it is fine), and the game link from the output on its own line.

If nothing new was graded, send nothing.

## Other requests

- "clash" or "game link": run `python3 scripts/clash.py link` and send the link on its own line.
- "leave clash": confirm with the student first. After a yes, run `python3 scripts/clash.py leave`, which deletes
  their game data on the server.
- "mute clash": stop sending Clash messages for 24 hours and cancel nothing else. Remember the mute end time.

## Daily rhythm

Four check-ins that read the student's Canvas assignments and Google Calendar. Use short, one-idea-per-line
messages. If a list runs past 8 items, make a one-page PDF and send it with a one-line summary. This works with or
without Clash set up.

### Rhythm setup (first time only)

1. If Canvas is not connected, ask the student to connect it and stop here. If only Google Calendar is missing,
   continue with Canvas alone and say once that calendar items are left out until they connect it.
2. Confirm the student's time zone from what Cubbie already knows. Ask only if it is unknown.
3. Propose these times and let the student change any before creating anything: daily at 6:00 am, daily at
   9:00 pm, Saturday at 10:00 am (week recap), Sunday at 6:00 pm (week ahead).
4. After the student agrees, create four scheduled check-ins, worded so they make sense days later:
   - "Run the cubbie-clash morning rundown" (6 am daily)
   - "Run the cubbie-clash evening rundown" (9 pm daily)
   - "Run the cubbie-clash Saturday week recap" (Saturday)
   - "Run the cubbie-clash Sunday week ahead" (Sunday)
5. Remember the chosen times. Tell the student in one line they can say "change my rundown times" or "stop my
   rundowns" any time. If they ask to stop one or all, remove those check-ins.

### Morning and evening rundown

1. Read Canvas assignments due in the next 24 hours, plus anything overdue and not submitted.
2. Read Google Calendar events for the rest of today (morning run) or for tomorrow (evening run).
3. Send one message in time order mixing both sources. Morning is headed "Today". Evening is headed "Tomorrow" and
   ends with one line for anything still unsubmitted tonight.
4. If nothing is due and nothing is scheduled, send one line saying the day is clear. Do not skip silently.

### Saturday week recap

1. Read Canvas for assignments submitted and grades posted in the last 7 days. Name them: this is the student's own
   message.
2. Read Google Calendar for events that happened.
3. If Clash is set up, add one line with the Points and Mana earned this week.
4. Send a short recap: what got done, what got graded, anything missed or still open. End with one line asking if
   they want anything carried into next week.

### Sunday week ahead

1. Read Canvas assignments, quizzes and exams due Monday to Sunday, and Google Calendar events for the same days.
2. Group by day. Flag the heaviest day and any day with 3 or more deadlines.
3. Offer a study plan only if the student wants one. Do not build one unasked.

If Canvas or Calendar cannot be read at run time, send one line saying which one failed. Never invent an item.

## Rules

- The four rhythm check-ins are exempt from the quiet-hours rule below because the student chose their times. Send
  no other messages beyond these four and the Clash messages above.
- Cubbie texts only its own student. Never message friends. If the student wants to challenge someone, give them the
  battle link and let them send it themselves.
- Never reveal another player's data. Never help work out a friend's grades from their Points.
- Do not do graded work for the student. Clash only reads grades.
- Do not message between 11 pm and 8 am.
