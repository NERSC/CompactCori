var numOfPointsToTryPerClient = 100000000000;
var batchSizePerUpdate = 5000000;

PIData = new Mongo.Collection('pidata');
var n = 5;

var initialized = false;

var getCurrentTime = function () {
    return Date.now();
};

var getId = function () {
    return Math.random().toString(16).substr(2,4);
}

var startTime = getCurrentTime();

if (Meteor.isClient) {
    var emailValue = getId();

    var startDate = new Date();
    var prevVal = 0;
    var counter = 0;
    var currentProcessingRatePerNSeconds = 0;
    var startingValue = 0;
    var perSecondCounter = 0;

    Meteor.subscribe('piData');

    Template.registerHelper('calcPi', function (ptInsideCir, totalNumOfPts) {
        if (totalNumOfPts === 0) {
            return 0.0;
        } else {
            return (4.0 * ptInsideCir / totalNumOfPts).toFixed(20);
        }
    });

    Template.registerHelper('serverPiData', function () {
            return PIData.findOne({email: 'server', trial: 'server'});
        }
    );

    Template.serverPi.helpers({
        'serverPiData': function () {
            return PIData.findOne({email: 'server', trial: 'server'});
        },
        'calculatePerformanceSpeed': function () {
            if (perSecondCounter == 0) {
                startingValue = PIData.findOne({email: "server", trial: "server"}).totalNumOfPts;
                perSecondCounter++;
            }
            var elapsedTime = getCurrentTime() - startTime;
            return ((PIData.findOne({
                email: "server",
                trial: "server"
            }).totalNumOfPts - startingValue) / elapsedTime).toFixed(2);
        },
        'calculatePointsComputedEveryNSeconds': function () {
            if (counter == 0) {
                prevVal = PIData.findOne({email: "server", trial: "server"}).totalNumOfPts;
                counter++;
            }
            var currentDate = new Date();

            if (currentDate - startDate > n * 1000) {
                var currentVal = PIData.findOne({email: "server", trial: "server"}).totalNumOfPts;
                currentProcessingRatePerNSeconds = currentVal - prevVal;
                startDate = currentDate;
                prevVal = currentVal
            }
            return currentProcessingRatePerNSeconds;
        }
    });

    Template.piTrials.helpers({
        'piTrialsData': function () {
            pidata = PIData.find({email: {$ne: 'server'}, trial: {$ne: 'server'}});
            return pidata;
        },
        'getProfilePicture': function () {
            var random = Math.floor(Math.random()*4+1);

            if (!initialized) {
                initialized = true;
                switch(random) {
                    case 1:
                        return "/img/anonymousPicture.png";
                    case 2:
                        return "/img/secondProfilePicture.png";
                    case 3:
                        return "/img/thirdProfilePicturePicture.png";
                    default:
                        return "/img/fourthProfilePicture.png";
                }
            }
        }
    });

    Template.mypi.helpers({
        'isTrialNameSet': function () {
            return !!Session.get('trialName');
        }
    });

    Template.setTrialName.helpers({});
    Template.setTrialName.events({
        'submit .trialForm': function (event) {
            event.preventDefault();
            var trialName = event.target.trialName.value;

            Session.set('trialName', trialName);

            var trialData = PIData.findOne({email: emailValue, trial: trialName});
            if (!trialData) {
                Meteor.call('insertPIData', emailValue, trialName, 0, 0);
            }
            trialData = PIData.findOne({email: emailValue, trial: trialName});
            launchWorker();
        }
    });

    Template.bspi.events({
        'submit .setTrialName': function (event) {
            event.preventDefault();
            var trialName = event.target.trialName.value;

            Session.set('trialName', trialName);
            var trialData = PIData.findOne({email: emailValue, trial: trialName});
            if (!trialData) {
                Meteor.call('insertPIData', emailValue, trialName, 0, 0);
            }
            trialData = PIData.findOne({email: emailValue, trial: trialName});
            launchWorker();
        }
    });
}

var launchWorker = function () {
    if (!!window.Worker) {
        var myWorker = new Worker("/js/worker.js");
        var trial = Session.get('trialName');

        myWorker.postMessage([numOfPointsToTryPerClient, batchSizePerUpdate]);

        myWorker.onmessage = function (e) {
            Meteor.call('updatePIData', emailValue, trial, e.data[0], e.data[1]);
        }
    }
};

if (Meteor.isServer) {
    Meteor.startup(function () {
        var serverData = PIData.findOne({email: 'server', trial: 'server'});
        if (!serverData) {
            PIData.insert({email: 'server', trial: 'server', ptInsideCir: 0, totalNumOfPts: 0});
        }
    });

    Meteor.publish('piData', function () {
        return PIData.find({});
    });

    Meteor.methods({
        "updatePIData": function (emailValue, trialValue, ptInsideCirValue, totalNumOfPtsValue) {
            PIData.update(
                {
                    email: emailValue,
                    trial: trialValue
                },
                {
                    $inc: {
                        ptInsideCir: ptInsideCirValue,
                        totalNumOfPts: totalNumOfPtsValue
                    }
                }
            );
            PIData.update(
                {
                    email: 'server',
                    trial: 'server'
                },
                {
                    $inc: {
                        ptInsideCir: ptInsideCirValue,
                        totalNumOfPts: totalNumOfPtsValue
                    }
                }
            );
        },
        'insertPIData': function (emailValue, trialValue, ptInsideCirValue, totalNumOfPtsValue) {
            PIData.insert(
                {
                    email: emailValue,
                    trial: trialValue,
                    ptInsideCir: ptInsideCirValue,
                    totalNumOfPts: totalNumOfPtsValue
                }
            );
        }
    });
}
