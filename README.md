# dl-lifecubby
Thank you hawson for the work you put into this. This is almost entirely their work but slightly updated for the sunsetting of lifecubby.

This is a small python script to pull down pictures and videos from lifecubby.

This script will download all of the entries in life cubby into the current directory. For each entry, it will create a folder (along with date) and in that folder download all of the pictures and videos along with the pdf report for it and a text file with the description, title and date. The structure of the folders will look like "current directory/date/entry id/files."

If the script fails during the run, it can be restarted and will automatically pick back up where it failed. As of now, it shouldn't be able to miss the report, photos, or videos but if it fails on the text file it might not update it and will continue with the next entry. To force it to skip that entry on a rerun, create the file metadata.txt in "current directory/date/entry id/" for the failed entry with any data in it.

FYI, the script takes a long time to run. I want to say it took about 4 hours for me to download 2 years of entries. Please remember to start this early and update your computers sleep settings so it isn't interrupted but it will restart fine if it goes to sleep.

If you are not familiar with python, then skip this paragraph. If you are, then this likely should be easy to run however you feel most comfortable. There is a requirements.txt file and all you need to do is create a credentials.json file with your credentials. There is an example in credentials-example.json. Then just run main.py

If you are not familiar with python or especially unix/powershell, then this might be a bit rough. Here is some general steps/documentation about it.
* Download this directory as a zip and unzip it. There should be a button that says "<> Code" on this page which you can download the zip from.
* Rename the file called credentials-example.json to credentials.json and update the info inside to include your actual life cubby login information.
    * This will not be shared with anyone other than life cubby's servers. Other than to authenticate you to them it stays local on your computer.
* Install python
    * [Download link](https://www.python.org/downloads/)
    * [More specific documentation about it](https://wiki.python.org/moin/BeginnersGuide/Download)
* Notes on running python
    * [Windows](https://docs.python.org/3/faq/windows.html#how-do-i-run-a-python-program-under-windows)
    * Mac
        * [Use the terminal app](https://support.apple.com/guide/terminal/welcome/mac)
* Navigate to the directory that you downloaded
    * [Windows Powershell](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cd)
    * [Mac (specifically "How to access other folders/directories")](https://www.macworld.com/article/221277/command-line-navigating-files-folders-mac-terminal.html)
    * Windows example in Powershell that was downloaded to the current user's download folder and uncompressed there
         *  ```cd ~\downloads\dl-lifecubby-mainline\dl-lifecubby-mainline\```
* Install the packages required for the script
    * [Documentation](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#using-a-requirements-file)
    * Example continued from above
        * ```python3 -m pip install -r requirements.txt```
* Run main.py
    * Example continued from above
        * ```python3 main.py```
    * If it fails and the terminal/powershell window stays open then you can just rerun the script with the above command. If it fails with the same error twice then it probably won't work running it a 3rd time.
    * To force it to skip that entry on a rerun, create the file metadata.txt in "current directory/date/entry id/" for the failed entry with any data in it.
    * If the terminal/powershell closes you will need to navigate to the directory that you downloaded