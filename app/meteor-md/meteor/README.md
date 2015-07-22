# Fishtank
Fishtank Backup

Contributers:
Elizabeth Wang
Jack Deslippe
Nicholas Fong
Ifreke Okpokowuruk

1	Introduction

1.1	Purpose
The Meteor MD Simulation is an application designated to simulate a tank of fish and how each fish interacts with each
other, thereby demonstrating parallel computing. This simulation supports client-based computation, as opposed to the
more conventional server-based computation. Each client using the Meteor MD Simulation works together to create and
calculate the positions for the fish they are responsible for. Every time a new client joins or leaves, the fish are
redistributed among the current clients.

1.2	Parallel Computing
Parallel computing is a form of computation in which multitudes of devices simultaneously perform calculations simpler
than the overall problem the devices are attempting to solve. The aforementioned devices each return their results to a
central server, which then processes and/or analyzes each result and later combines all of them into the answer to the
problem the devices are trying to solve.

1.3	Webstorm Background
Webstorm is a popular IDE that has a multi-language platform. Other IDE’s can, of course, also be used for this project.
However, Webstorm was chosen because of its auto-fill in features and its aforementioned platform.

1.4	Meteor Background
Meteor is a platform for building mobile applications and was used in this project. Every Meteor project must have at
least three files: one javascript file for back-end developing, one html file for front-end developing, and one css file
also for front-end developing.



2	Setting Up Your Development Environment

2.1	Git Setup
Run the command 
	git clone https://github.com/NERSC/CompactCori.git
on terminal window to clone the project.

2.2 	Meteor
Download the Meteor IDE 1.1.0.2 at 
https://www.meteor.com/
or install the latest official Meteor release from the terminal window using this command line:
curl http://install.meteor.com/ | sh

2.3	Webstorm
Follow the instructions on the website 
https://www.jetbrains.com/webstorm/download/
to install Meteor 10. Either sign up for a free thirty day trial or purchase the application, depending on how often and
long this app is planning to be run.



3	Customizing Content and Options

3.1	Overview
To add login buttons, further develop the user interface, or change the backend javascript, follow the instructions below.



3.2	Running the Application
To run the application, first go to the internal terminal window, making sure that it is in the directory the project is
located and run
meteor

The application will be shown on 
localhost:3000



4	Customizing and Extending the Project

4.1	Meteor Mongo
To debug the program, check each database and collection, list objects, or quit the Mongo shell, go to the Terminal
application and run Meteor application through its internal Terminal window using the command
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

4.2	Endpoints
Endpoints were used to connect this project with the front-end code. The raw values for the collection of fish and the
parameters for each fish were printed in JSON format to the localhost. These values were to be used to get the coordinates
to render each fish.

4.3	Iron Router
To add iron router, go to the native command line or the directory inside the terminal window and run
meteor add iron:router
Iron Router was used to divide the localhost into two sections: one page (at http://localhost:3000) for the user which
displays the amount of clients, the amount of fish that client is responsible for, and the percentage of fish the client
is responsible for and another page (at http://localhost:3000/api/v1/get_particles) that is responsible for passing the
data needed to the front end.

4.4	Packages Used

Package Name
Package Description
Installation Instructions
dispatch:stored-var
ReactiveVar cached on localStorage
meteor add dispatch:stored-var
iron:router
Routing specifically designed for Meteor
meteor add iron:router
jquery
Manipulate the DOM using CSS selectors
meteor add jquery
jquery-ui
jQuery user interface
meteor add jquery-ui
meteor-platform
Include a standard set of Meteor packages in application
meteor add meteor-platform
tracker
Dependency tracker to allow reactive callbacks
meteor add tracker
twbs:bootstrap
Front-end framework for developing responsive, mobile first projects on the web
meteor add twbs:bootstrap
webapp
Serves a Meteor app over HTTP
meteor add webapp



5	Project Structure

5.1	Files
client - Only runs on client end(s)
    templates - Javascript and HTML templates and calls for both the user and the endpoint side, files with client side computation
        applications - Formatting
            layout.html - Creates navbar
        data - Passes back parameters and values for the fish
            dataTemp.js - returns the static JSON formatted string of the parameters and the fish
            dataTemp.html - prints out the static JSON formatted string of the parameters and the fish
        includes - Formatting
            includes.html - Generates header
        user - Passes back data for the user
            userTemp.js - Calculates total number of particles user is responsible for, total number of particles, and
            the percentage of particles the user is responsible for
            userTemp.html - Prints out total number of particles user is responsible for, total number of particles, and
            the percentage of particles the user is responsible for
        main.html - Formatting
        main.js - Main client computational file. Fish bounce against each other and the wall. Velocity, turning speed,
        coordinates, and tick are calculated and set here.
lib - Runs on both client and server ends but loads last
    collections.js - Creates the fish collection and the client collection
    common.js - Global variables and methods used in both the server and the client
    router.js - Router used for client and endpoint pages.
server - Only runs on server end
    methods.js - Updates fish data when a client joins or leaves
    publications.js - Publishes the fish collection and the client collection
    startup.js - Creates all elements of each fish object
