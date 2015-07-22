/**
 * @author Elizabeth Wang
 * @version 3 August 2015
 *
 * Creates fish objects and adds them to the Fish collection
 */

/**
 * Creates a designated amount of fish, each with coords, thread_num, direction, turningSpeed, velocity, rotation, mass
 *  radius, version, createTime, lastUpdateTime, userId, and clientId and inserts them into the Fish collection in order.
 */
Meteor.startup(function () {
    console.log("in initialization function");
    Fish._ensureIndex({version: 1});

    var numOfFishOnServer = Fish.find().count();
    if (numOfFishOnServer < numOfFish) {
        for (var i = 0; i < numOfFish - numOfFishOnServer; i++) {
            var fish = new Object();

            fish.coords = [Math.random()*tankWidth, Math.random()*tankHeight, Math.random()*tankDepth];
            fish.thread_num = clientCounter;

            fish.direction = [Math.random() * Math.PI * 2, Math.random() * Math.PI * 2, Math.random() * Math.PI * 2];
            fish.turningSpeed = [Math.random() - 0.8, Math.random() - 0.8, Math.random() - 0.8];
            fish.velocity = [(2 + Math.random() * 2) * 5.2, (2 + Math.random() * 2) * 5.2, (2 + Math.random() * 2) * 5.2];

            fish.rotation = [0, 0, 0];

            fish.mass = Math.random() * 10;
            fish.radius = radius;

            fish.version = 0;

            fish.createTime = new Date();
            fish.lastUpdateTime = new Date();

            fish.userId = '';
            fish.clientId = '';

            Fish.insert(fish);
        }
    }
});
