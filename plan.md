# Goal
- I need to create a python script that will connect to a jellyfin instance and iterate trough a movie library then rename files and folders asociated with every item in the library on the disk based on information returned from jellyfin (movie name and year)
-
- Add a option to select library by name
- Add a dry run option

## Jellyfin api
 -Use opensource jellyfin documentation for the api
 -Use safe best practices to deal with jellyfin connection


## File and folder structure
- Each Library from Jellyfin is stored in a base folder
- Each movie in the library should be stored in a folder with the movie name and year (if available)
Example of a folder name: "Little Asians Vol. 9 (2023)"
- Each movie file should have the following format Movie Name (Year).movie extension
Example of a file name: "Little Asians Vol. 9 (2023).mp4"


