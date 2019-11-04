# Backup reminder

A simple application to remind me to run a back up each day.

It has options to cancel the backup or shutdown once the backup is complete. It
will also inhibit the screen saver to avoid suspending during the backup.

## Usage

If you want to modify this for your own use, you'll likely want to change the
backup command (I use `duply`) as well as the commands to suspend and resume
the screen saver (I use `xset`). You'll also want to call it each day from a
cron job.

## Licence

Copyright 2019 David Purton

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see https://www.gnu.org/licenses/.
