# Twitter-Clone---Database-Driven-Tweet-Management-System-
A fully functional, CLI-based Twitter-like system, enabling secure user interactions, tweet management, and optimized data handling, input validation, pagination, and real-world social media features.
Introduction
Your task in this project is to build a system for managing enterprise data in a database providing services to users. Data storage will be implemented using a SQLite database, and you will write code to access it. Your code will create a simple command line interface. While you have the option to implement a GUI interface, there will be no support or bonus for choosing this route. You are also free to write your code in Python, Java, C++, or any other language suitable for the task. If you opt for a language other than Python, please inform the instructor and your lab TA in advance.

Database Specification
You are given the following relational schema:

users(usr, name, email, phone, pwd) 

follows(flwer, flwee, start_date)

lists(owner_id, lname)

include(owner_id, lname, tid)

tweets(tid, writer_id, text, tdate, ttime, replyto_tid)

retweets(tid, retweeter_id, writer_id, spam, rdate)

hashtag_mentions(tid,term)

Each user has a unique user id (usr), in addition to their name, email (emails must have @ and period (.)), phone and password (pwd).

The table "follows" records each following by storing the follower's id (flwer), the followee's id (flwee), and the date of following (start_date).

User tweets are recorded in the table "tweets". Each tweet has a unique identifier (tid), id of the user who wrote the tweet (writer_id), the text, the date (tdate), and the time (ttime). If the tweet is a reply to another tweet, it will store the original tweet's id (replyto_tid)

Table "retweets" records the id of the tweet (tid), id of the retweeter (retweeter_id), and the tweet's writer (writer_id). It also stores a flag indicating whether it is spam (spam), and the date of the retweet (rdate). Spam=0 indicates it's NOT a spam. 

A user's favorite list is stored in the "lists" table that records the user's id (owner_id) and the list name (lname). A user can have multiple favorite lists. The include table consists of the user’s id (owner_id), list name (lname), and tweet id (tid).

 The SQL commands to create the tables of the system are here. Use the given schema and DO NOT change any table/column names as we will be testing your project using our database with the given schema. 

Note: Foreign key constraints must be turned on for each session in SQLite3. This can be done using: PRAGMA foreign_keys = ON;


Login Screen

The first screen should provide options for both registered and unregistered users. There must also be an option to exit the program at any stage of the program. Registered users should be able to log in using a valid user ID and password, respectively referred to as usr and pwd in table users. Passwords in the user table (column pwd) are stored as plain text. This is for the ease of testing. Any encryption or hashing will complicate the demo process and can result in mark losses.


After a registered user signs in, the system should list all tweets and retweets (that are not spam) from users who are being followed; the tweets should be ordered based on date from the latest to the oldest. Return the tweet type (tweet/ retweet), tid, date, time, spam flag.  If there are more than 5 such tweets, show 5 of them and give the user the option to see more (when prompted it should show the next 5). 


Unregistered users should be able to sign up by providing a name, email, phone, and password. The user ID (i.e. the field usr in table users) should be provided by the system and be unique. For the ID, use the integer after the current largest user. For example, if the largest value of ID is now 8, the newest user should have ID 9. After a successful login or signup, users should be able to perform the subsequent operations from a menu as discussed below.

System Functionalities
After a successful login, users should be able to perform all of the following tasks:

1. Search for tweets: The user should be able to enter one or more keywords (separated by commas) and the system should retrieve every tweet that matches at least one of the keywords. As the output format, display: tid, writer_id, date, time, text. A tweet matches a keyword if:

The keyword has the prefix # and is mentioned by the tweet as a hashtag in the hashtag_mentions table. Hashtags are defined as anything that lies between # and the next whitespace. 

OR

The keyword doesn't have the prefix # but it appears in the tweet text. (The symbol # is not part of any keyword and only indicates that the keyword that follows is expected to appear as a hashtag). 

-->  If the search query is #abcd it should return all tweets containing “#abcd”. I recommend utilizing the hastag_mentions table for this.

--> If the search query is “abcd” it should return all tweets containing “abcd”. it should also return tweets containing "#abcd"


Everything except the pwd is case-insensitive, there might be #HasHtag, #HASHtag, #HashTaG..... within the tweets.


Hence, make sure your code is able to handle these by normalizing the inputs and the hashtags in the hashtag_mentions table and comparing the normalized search term with the term in the table. 


The tweets should be ordered based on the latest date to the oldest. If there are more than 5 such tweets, only 5 will be shown and the user will be given the option to see more (when prompted it should show the next 5). 

The user should be able to select a tweet and see some statistics about the tweet including the number of retweets and the number of replies. Also, the user should be able to compose a reply to a tweet (see the section on composing a tweet), or retweet it (i.e. repost it to all people who follow the user). For replying to tweets, or selecting tweets, consider the tweets currently in view. The user should also be able to add a tweet to a selected favorite list (Remember a user can have multiple favorite lists)


2. Search for users: The user should be able to enter a keyword and the system should retrieve all users whose names contain the keyword. A keyword can be interpreted as a sequence of alphanumeric characters. 

The search query DOES NOT need to match the username exactly, for example, if you search "foy", it should show results: Foy, Malfoy. The outputs should display both the user id and the user name so that users with the same names can be distinguished.  The result would be sorted in an ascending order of name length. 


If there are more than 5 matching users, only 5 would be shown and the user would be given an option to see more but again 5 at a time. The user should be able to select a user (consider the ones currently in view) and see more information about the user including the number of tweets, the number of users being followed by the user, the number of followers, and up to 3 most recent tweets. The user should be given the option to follow the user or see more tweets.


3. Compose a tweet: The user should be able to compose a tweet. A tweet can have hashtags that are marked with a # before each hashtag. Information about hashtags must be stored in table hashtag_mentions. One tweet can have multiple hashtags but not multiple instances of the same hashtag. 

4. List followers: The user should be able to list all users who follow them. From the list, the user should be able to select a follower and see more information about the follower including the number of tweets, the number of users being followed, the number of followers, and up to 3 most recent tweets. The user should be given the option to follow the selected user or see more tweets.

If there are more than 5 followers users, only 5 would be shown and the user would be given an option to see more but again 5 at a time. If there are less than or equal to 5, display them all.

5. List favorite lists: The user should be able to retrieve all of his favorite lists and the TIDs stored in them. The output is expected to contain the name of the list and the tids in that list. For example, if a user has two favorite lists:

List 1: tid1, tid2, tid3

List 2: tid4, tid5


5. Logout: There must be an option to log out of the system. Upon logout, it should NOT exit the program. It should go back to the initial stage where you can login with id and pwd.

 

String matching: Except for the password which is case-sensitive, all other string matches (including searches for tweets and users) are case-insensitive. This means jonathan will match Jonathan, JONATHAN, and jonathaN, and you cannot make any assumption on the case of the strings in the database. The database can have strings in uppercase, lowercase, or any mixed format.

SQL injection attacks and password entry: You are expected to counter SQL injection attacks and make the password non-visible at the time of typing.

Error checking: Every good programmer should do some basic error checking to make sure the data entered is correct. We cannot say how much error checking you should or should not do, or detail out all possible checkings. However, we can say that we won't be trying to break down your system but your system also should not break down when the user makes a mistake.

Testing
At development time, you will be testing your programs with your own data sets but conforming to the project specification. You have been provided a small sample DB, but you should add more data to it as you deem necessary for your development purpose. 

At demo time, you will be given a database file name that has our test data (e.g., prj-test.db), and you will be passing the file name to your application as a command line argument. Don't hard-code the database name in your application since the database name is not known in advance, and you don't want to change your code at demo time (see next). The database will include the tables given above and our own test data. 

