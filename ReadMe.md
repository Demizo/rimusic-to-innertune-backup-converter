Tool to convert RiMusic backups into InnerTune backups.

Steps to import a RiMusic backup into InnerTune:

1. Export the database from RiMusuc
2. Export the backup from InnerTune
3. Extract the InnerTune backup
4. Run the migrate script with the RiMusic database as the `sourdb`ce. and the Innertune `song.db` as the `target.db` (`song.db` will be overwritten where possible)
5. Zip up `song.db` with `settings.preferences_db`. Use the `Zip` compression method and ensure the file name ends with `.backup`
6. Import your newly created zip backup into InnerTune
