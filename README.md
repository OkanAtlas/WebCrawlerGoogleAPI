# WebCrawlerGoogleAPI
A web crawler with integration of Google Drive and Gmail APIs. Made for a case for AnalyticaHouse.

**To be able to run the script, the users have to create a 'data' folder to the root folder of the project. URL Excel and private authentication key of the user will be stored in this data folder. Program will also write the output to an Excel file called 'output.xlsx' to this folder and later on upload said file to the Google Drive.**


Example Output URL: https://docs.google.com/spreadsheets/d/1xb8mU535MC6vTY3KOyEL4iI4rxjKnMco/edit?usp=drivesdk&ouid=118221096563552554787&rtpof=true&sd=true

**#Used Libraries**
- requests : To make HTML content requests to the URLs
- pandas : Data frame applications to manage, sort and write data
- google_auth_oauthlib : To authenticate the Google user via O2Authentication
- lxml : To parse HTML codes to a tree
- email.mime : To create mails
- googleapiclient : To build Google APIs and use their functionalities
- base64 : To decode and encode bytes

**#Challenges Faced**

-The biggest challange of this project was the implementation of Google APIs. This have few reasons. First and most infrutiating one was the broken UI of the Google's developer dashboard. On the desktop version of the developer dashboard page, the layout was so broken, it blocked me from seeing some important parameters for my project. This made authentication setup for the APIs longer than it needed to be. On the second part of API implementation, Google's security requests made real hard to pass valid authentication to the running script.

**#What I Learned**

-This project was my first time building a web scraper and also using any sort of API. Upon completion of this project I learned the basics of web scraping and HTML parsing as well as correct implementation and usage of Google's various APIs. I also got familiar with Google's developer dashboard and gathered a firm understanding of different authentication methods used for different APIs.

**#Answeres to Additional Questions**

_If I’d have 10.000 URLs that I should visit, then it takes hours to finish. What can we make to fasten this process?_

-We can apply the divide and conquer methodology to the scraping process. Instead of having one scraper, we can divide the URLs between 10 scrapers running simultaneously on different threads to make the scraping process time-efficient. This approach lowers the runtime to the cost of extra computation power and increased complexity in the code.

_What can we make or use to automate this process to run once a day? Write your recommendations_

-Easiest way to achieve this is to set up a Task Scheduler. Task Scheduler could be set up either to the developer's pc or to the main server of the company. Since the main server's uptime is almost continuous, there is less of a chance to miss a scheduled execution.

_Please briefly explain what an API is and how it works._

-Application Programming Interfaces, or briefly APIs, can be described as software that lets two or more applications talk to each other, share, request, and interpret data.
