# HLTVDemoDownloader
Downloads demo files from HLTV based on an `Event ID`. Compatible with the new HLTV design.

This is written in pure python so it should run on any system that can run Python 2.7. Because it uses raw_input, it will not run directly from any editor that does not allow standard input (i.e., Atom) and must be run through a command line.    

This program starts by asking the user for the `Event ID` given by HLTV. The IDs can be found in the [Event Archive](https://www.hltv.org/events/archive) on HLTV. For example, the URL for ECS Season 3 North America is https://www.hltv.org/events/2729/ecs-season-3-north-america, thus the `Event ID` is 2729.

The script takes the `Event ID` and plugs it into a URL to display the list of matches. It then downloads that page as HTML and uses a regular expression to make an array of `Match IDs`.

Next, it uses multithreading to open each `Match ID` in a URL to find the respective `Demo ID`. It adds the `Demo IDs` to a new array.

After that, the script asks the user to enter the name for the competition. The script then creates a folder with that name. The new folder is in the same directory as the script.

Finally, the script uses multithreading to loop through the `Demo IDs` and downloads them to inside the folder created earlier.
