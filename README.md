# Cubbie Clash

**Your grades power your attacks.** Cubbie Clash is a [Cubbie](https://hackathon.cubbie.ai) Skill that turns a
student's Canvas grades into Points and Mana, then lets them duel their friends in a retro, GamePigeon-style game that
runs in the browser. Friends see Points and battle results. They never see grades.

Built for the Cubbie Hackathon, Track 1.

## Try it

1. Text Cubbie this repo link: `https://github.com/jrao06/DevHacks26`. Cubbie asks before it installs.
2. Text **start clash**. Cubbie asks for a display name and your okay to sync, connects to your Canvas, and sets up a
   daily grade check at 8 PM.
3. To join friends, text **join clash `<code>`** with the squad code one of them shares. Without a code, Cubbie
   creates a new squad and gives you the code to share yourself.
4. Open the game link Cubbie sends. Pick a squadmate and challenge them.

Other things to text: **clash** (new game link), **mute clash**, **leave clash** (deletes your game data), and
**set up my rhythm** for the daily and weekly rundowns below.

## How grades become power

Every graded assignment is worth `score % x type weight x course difficulty`, rounded.

| Assignment type | Weight |
| --- | --- |
| Final exam | 100 |
| Capstone or project | 80 |
| Test | 60 |
| Quiz | 25 |
| Homework | 10 |

- **Points** are the total. They show on the squad board after a daily update (8 AM Phoenix), so a sudden jump
  can't be traced to one grade.
- **Mana** is granted once per assignment, equal to its Points. A grade change never raises it again. It caps at 200
  and expires after 14 days, so recent work counts most.
- **Shields** come from a perfect score on a final, capstone or test. You can hold 3.
- **Course difficulty** is a 1.0 to 1.5 multiplier that Cubbie picks from the course level, subject and
  workload, then remembers so a course always counts the same.

## The game

A turn-based duel between two squadmates. Nobody has to be online at the same time: each player makes a move when
they open the game, like GamePigeon.

- Both fighters start with 100 HP. The challenger moves first.
- **Strike:** 15 energy, 18 damage. **Blast:** 40 energy, 40 damage. **Guard:** halves the next hit.
  **Charge:** +25 energy.
- Starting energy is half your Mana and stays hidden from your opponent.
- Your public Points add up to +25% damage.
- A Shield blocks one hit completely and is used up.
- It ends at 0 HP, or after 60 total moves (higher HP wins). If your opponent hasn't moved in 48 hours, you can
  claim the win.

Cubbie can only text its own student, so it can't ping your opponent. Instead, the 8 PM check-in adds a line when a
challenge or your turn is waiting, and the student tells their friend to open the game.

## Daily rhythm (same Skill)

The Skill also sets up four scheduled check-ins, at times the student picks:

| When | What Cubbie sends |
| --- | --- |
| Every day, 6 AM | What's due and what's on your calendar today |
| Every day, 9 PM | Tomorrow's deadlines and events, and anything still unsubmitted |
| Saturday | A recap of the week: what got done and graded, and what's still open |
| Sunday | The week ahead by day, flagging the heaviest day |

It reads Canvas and Google Calendar through Cubbie. Clash works with or without these.

## Privacy

Grades stay with the student. What leaves their machine:

- **Sent to the game server:** the score percentage, assignment type and course difficulty for each graded
  assignment, plus a display name.
- **Not sent:** assignment names, course names, raw Canvas IDs, or your Canvas login. The Skill hashes assignment and
  course identifiers with a salt only the student's token knows, before anything is uploaded.
- **Tokens:** the server stores only a hash of each player's token. Game links are single-use and expire in 7 days.
  Opening one gives a 30-day session cookie.
- **What friends see:** names, public Points, win-loss records and battle moves. Not Mana, energy totals, Shields,
  grades or courses. Opponents see HP and a damage bonus, so they can't work out your grades from a fight.
- **Honest limits:** the server operator can see each player's score percentages, just not which assignment they
  belong to. Points are public to the squad, so a friend could guess roughly how a student is doing overall. The
  Skill asks for a yes before the first sync, and **leave clash** deletes everything.

Cubbie never messages friends, and the Skill never does graded work for a student.

## How it works

```
Canvas ──> Cubbie ──> scripts/clash.py ──HTTPS──> game server (Next.js + Postgres on Vercel)
 grades   reads them   hashes + posts only        points, squads, battles
                         percentages
Cubbie texts the student their results and a one-tap game link. The game runs in the browser.
```

- The Skill is pull-based: a scheduled check-in reads Canvas, runs the script, and texts the result. Scripts can't
  call Cubbie's abilities, so Cubbie fetches the grades first and passes them to the script as a file.
- `scripts/clash.py` is standard-library Python. Commands: `optin`, `sync`, `link`, `leave`, `reset`.
- The game server is in a separate repository, `jrao06/clash-server`: Next.js 14, `pg`, Postgres on Neon, deployed on
  Vercel. The rules engine is pure TypeScript with its own tests.

## Repository layout

| Path | What it is |
| --- | --- |
| `SKILL.md` | The Skill: consent text, setup, grade sync, rundowns, rules for Cubbie |
| `scripts/clash.py` | Client that hashes grades and talks to the game server |
| `LICENSE` | License |
