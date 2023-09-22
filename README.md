# Grades Notifier

## TL;DR

As U of T doesn't send notifications when final grades or course averages are released, this script polls a student account for changes and will email the account holder when a new grade is out!

## Technical Details

Built in Python, using Selenium and BeautifulSoup. This script stores the data found on one's transcript and on each subsequent run, it compares the new data to the old data. If there are any changes, it sends an email to the account holder with the new grades.

This script is capable of sending five types of notification emails: 
1) to the account holder only, containing their final grade
2) to anyone who wishes to be notified when a new grade is released so that they may check their own student account
3) to anyone who wishes to be notified when a course average is released
4) to the account holder if an error occurs in the script
5) to the account holder periodically, indicating that the script is still running


## Keep in Mind

Please don't abuse a script like this. It is designed to run **less frequently** than a human would check their grades by logging onto the portal manually. Please don't disrespect your university community by spamming its server with requests. Thank you <3

