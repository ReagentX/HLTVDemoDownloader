# HLTVDemoDownlaoder
Downloads demo files from HLTV based on an event ID.

This is written in pure python so it should run on any system that can run Python 2.7. Because it uses raw_input, it will not run directly from any editor that does not allow standard input (i.e., Atom) and must be run through a command line.    

This program works by using the `Event ID` given by HLTV. Go to the [Event Archive](http://www.hltv.org/?pageid=184) on HLTV and find the event from which you wish to download the demos. For IEM Sydney, the URL is http://www.hltv.org/?pageid=357&eventid=2713 and the `Event ID` is everything after `&eventid=`, in this case, 2713.

Next, the user is asked to enter the name for the competition. The script then creates a folder with that name. The new folder is in the same directory as the script.

The script takes the `Event ID` and plugs it into the URL to display the demos. It then downloads that page as HTML and uses a regular expression to make an array of `Demo IDs`. Finally, it loops through the `Demo IDs` and downloads them to a folder inside the folder created earlier.
