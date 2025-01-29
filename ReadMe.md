Tool to convert RiMusic backups into InnerTune backups.

Steps to import a RiMusic backup into InnerTune:

1. Export a backup from RiMusuc
2. Export a backup from InnerTune
3. Extract the InnerTune backup
4. Run the migrate script with the RiMusic backup as `source.db` and the Innertune `song.db` as the `target.db`
5. Zip up `song.db` with `settings.preferences_db` to create a new InnerTune backup. Use the `Zip` compression method and ensure the file name ends with `.backup`
6. Import your newly created backup into InnerTune
