# Thanksgiving Football Repo

> Thanksgiving fantasy football draft and scoring code.  
> Every year during Thanksgiving, my family has a fantasy football draft.  
> We only include the teams that are playing on Thanksgiving and limit the positions of the draft in order to keep it simple. This has become a holiday tradition and been 
> a nice distraction from the amount of calories I consume at the dinner table.  

> A few things to note:
> - The code is written in python (3.5) and uses `pandas.read_html` for web scrapping
> - There is a pseudo-draft section that I used to personally check the code. The player scores are grabbed from ESPN and columns are manipulated in order to return desired player stats. 
> - There are a few different ways to run the code (assuming the draft has take place, and the `draft_sheet.xlsx` has been filled out):
>     + `python Thanks_Fball.py` in command line will run the code without any interactive shell
>     + Launch `ipython` and use `%run Thanks_Fball.py` will run the code and allow you to use some of the defined functions (a little more interactivity)
>     + Launch `ipython` and use `%run Thanks_Fball.py` or import it and copy the `main()` function to run each line. This isn't the best option (to be fixed), but will give you a lot of meta data to work with.

