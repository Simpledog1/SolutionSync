# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

One developer (a beginner computer science student) who practices on HackerRank and
Exercism and backs up completed solutions to two public GitHub repositories. They open
the local dashboard at any time of day, in bright or dim rooms, mainly to confirm the
automation is healthy and nothing failed.

## Product Purpose

SolutionSync finds genuinely completed HackerRank and Exercism solutions, checks which
are already on GitHub, and uploads the missing ones a few files per Philippine calendar
day (default 4, shared across both platforms), verifying every upload against GitHub.
Success: the user can tell in seconds that the system is running, what was published,
and whether anything needs attention.

## Positioning

A careful, slow-drip backup: it never overwrites, never duplicates, never guesses a
status (GitHub unreachable reads "Unable to Verify", never "Missing"), and spreads
uploads over days instead of dumping them.

## Operating Context

- Runs on the user's Windows PC: a Python engine (`py -m solsync`), Windows Task
  Scheduler (06:00 daily plus sign-in/unlock), and a local web dashboard on 127.0.0.1.
- Data comes from Exercism's API (token in Windows Credential Manager) and HackerRank's
  account export file; GitHub state comes from git and the repos' remote listing.
- Repositories: Simpledog1/HackerRank-Problems, Simpledog1/Exercism-Problems.

## Capabilities and Constraints

- Dashboard actions: Scan Solutions, Refresh GitHub Status, Run Sync, Pause/Resume
  Automation, change the daily upload limit (0 to the safety maximum, default 20).
- Statuses: Published, Missing, Pending, Failed, Unable to Verify.
- Every dashboard action runs the engine; the UI never counts, uploads or bypasses the
  quota. No external services, no paid APIs, standard library only, no build step.

## Evidence on Hand

Real data only: about 195 discovered solutions, upload ledger, activity events. No
testimonials, metrics or claims beyond what the local data shows.

## Product Principles

- Truth over reassurance: never show a status the system has not verified.
- Calm when healthy, unmistakable when something needs attention.
- The engine is the authority; the dashboard is a window and a set of switches.
- Must not feel like a generic corporate admin template.
