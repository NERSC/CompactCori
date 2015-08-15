# PiCalculator
Pi Calculator Application Documentation

Version 1.0.0
3 August 2015

Contents
1. Introduction                                           1
    1.1 Purpose                                         1
    1.2     Parallel Computing                                  1
    1.3 Webstorm Background                                 1
    1.4 Meteor Background                                   1
2. Setting Up Your Development Environment                2
2.1     Git Setup                                           2
2.2     Webstorm                                            2
2.3 Meteor                                          2
3. Customizing Content and Options                    2-3
    3.1 Overview                                                2
    3.2 Running the Application                                 3
4. Customizing and Extending the Project                  3-4
    4.1 Meteor Mongo                                    3-4
    4.4     Profile Pictures                                        4
5. Project Structure                                          5
    5.1 Files                                               5



1   Introduction

1.1 Purpose
The Pi Calculator is an application designated to compute the value of pi in parallel. The value gets more and more accurate as time progresses and/or more and more clients join the application. This simulation supports client-based computation, as opposed to the more conventional server-based computation. Each client using the Meteor MD Simulation works together to create and calculate their values of pi. The server inserts the client-processed values in an array and then returns an aggregated, more accurate version of pi.

1.2 Parallel Computing
Parallel computing is a form of computation in which multitudes of devices simultaneously perform calculations simpler than the overall problem the devices are attempting to solve. The aforementioned devices each return their results to a central server, which then processes and/or analyzes each result and later combines all of them into the answer to the problem the devices are trying to solve.

1.3 Webstorm Background
Webstorm is a popular IDE that has a multi-language platform. Other IDE’s can, of course, also be used for this project. However, Webstorm was chosen because of its auto-fill in features and its aforementioned platform.

1.4 Meteor Background
Meteor is a platform for building mobile applications and was used in this project. Every Meteor project must have at least three files: one javascript file for back-end developing, one html file for front-end developing, and one css file also for front-end developing. Meteor was chosen and used for this project due to the fact that users can access the application using their computers or phones.



2   Setting Up Your Development Environment

2.1 Git Setup
Run the command
    git clone https://github.com/NERSC/CompactCori.git
on terminal window to clone the project.

2.2     Meteor
Download the Meteor IDE 1.1.0.2 at
https://www.meteor.com/
or install the latest official Meteor release from the terminal window using this command line:
curl http://install.meteor.com/ | sh

2.3 Webstorm
Follow the instructions on the website
https://www.jetbrains.com/webstorm/download/
to install Meteor 10. Either sign up for a free thirty day trial or purchase the application, depending on how often and long this app is planning to be run.



3   Customizing Content and Options

3.1 Overview
To customize content and options, follow the instructions below to run the application.


3.2 Running the Application
To run the application, first go to the internal terminal window, making sure that it is in the directory the project is located and run
meteor

The application will be shown on
localhost:3000



4   Customizing and Extending the Project

4.1 Meteor Mongo
To debug the program, check each database and collection, list objects, or quit the Mongo shell, go to the Terminal application and run Meteor application through its internal Terminal window using the command
meteor
making sure that the Terminal application is currently in the same directory the Meteor application is in.

Next, run the commands
meteor mongo
help

To check the databases and/or the collections:
show collections
show databases

To look at each element inside a database/collection:
db.nameOfCollection.find().fetch()

To count each element inside a database/collection:
db.nameOfCollection.find().count()

To remove specific elements with undesired objects inside a database/collection:
db.nameOfCollection.remove({object: object})

To remove all elements inside a database/collection:
db.nameOfCollection.remove({})

4.2 Profile Pictures
The profile pictures were designated to appeal to the users and help them navigate through the web page. There are four profile pictures, which are chosen out at random.

4.4 Packages Used

Package Name
Package Description
Installation Instructions
autopublish


Publishes the entire database to all clients
meteor add autopublish
ian:accounts-ui-bootstrap
Bootstrap styled accounts-ui with language support
meteor add ian:accounts-ui-bootstrap

insecure


Allow all database writes by default
meteor-platform
meteor add insecure
meteor-platform
Include a standard set of Meteor packages in app
meteor add meteor-platform





5   Project Structure

5.1 Files
public - Folder with pictures
pi.js - Main file that calculates the value of pi on the client end and then returns it to the server end, which refines that said value
pi.html - Displays server and client values of pi, profile pictures, points calculated, points generated, and speed of calculation
