/**
 * @author Elizabeth Wang
 * @version 3 August 2015
 *
 * Calculates new positions for the fish and moves them accordingly.
 */

var workerHandle;
var fishHandle;

var tick;
var fishCreatedOnClientArr = [];

clientId = getFishTankKey();

var dummyId = 'dummy';
Session.set('dummyId', dummyId);
workerHandle = Meteor.subscribe('tankWorker', dummyId);

/**
 * Checks to see if the fish are created. If not, the fish are promptly created and copied over from the fishOnServer
 *  parameter
 *
 *  @param fishOnServer - fish object from server end
 */
fishHandle = Meteor.subscribe('fish', dummyId, function () {
    if (!initialized) {
        tick = 0.1;
        Fish.find({}, {sort: {_id: 1}}).forEach(function (fishOnServer) {
            var fishCreatedOnClient = new Object();
            fishCreatedOnClient._id = fishOnServer._id;

            fishCreatedOnClient.coords = fishOnServer.coords;
            fishCreatedOnClient.thread_num = fishOnServer.thread_num;

            fishCreatedOnClient.direction = fishOnServer.direction;
            fishCreatedOnClient.turningSpeed = fishOnServer.turningSpeed;

            fishCreatedOnClient.velocity = fishOnServer.velocity;
            fishCreatedOnClient.mass = fishOnServer.mass;
            fishCreatedOnClient.radius = fishOnServer.radius;

            //fishCreatedOnClient.neighbors = fishOnServer.neighbors;
            fishCreatedOnClientArr.push(fishCreatedOnClient);
        });
        initialized = true;
    }
});

/**
 * Calculates and moves each fish accordingly. If two fish are close to each other, one of the fish randomly bounce off.
 *  If a fish is close to the boundaries of the fish tank, it too bounces off. The velocity and coordinates of the fish
 *  are changed accordingly. Afterwards, the fish are updated using the server method updateFish(clientId)
 */
Deps.autorun(function (c) {
    workerHandle = Meteor.subscribe('tankWorker', Session.get('dummyId'));
    fishHandle = Meteor.subscribe('fish', Session.get('dummyId'), function () {
        if (initialized) {
            requestAnimationFrame(animate);

            function animate() {
                var m = 0;
                Fish.find({}, {sort: {_id: 1}}).forEach(function (fishOnServer) {
                    fishCreatedOnClientArr[m]._id = fishOnServer._id;
                    fishCreatedOnClientArr[m].coords = fishOnServer.coords;
                    fishCreatedOnClientArr[m].thread_num = fishOnServer.thread_num;

                    fishCreatedOnClientArr[m].direction = fishOnServer.direction;
                    fishCreatedOnClientArr[m].rotation = fishOnServer.rotation;

                    fishCreatedOnClientArr[m].turningSpeed = fishOnServer.turningSpeed;
                    fishCreatedOnClientArr[m].velocity = fishOnServer.velocity;

                    fishCreatedOnClientArr[m].mass = fishOnServer.mass;
                    fishCreatedOnClientArr[m].radius = fishOnServer.radius;
                    m++;
                });
                var fishArr = Fish.find({'clientId': clientId}).fetch();
                var updatedFishArr = [];

                for (var z = 0; z < fishArr.length; z++) {
                    for (var b = z + 1; b < fishArr.length; b++) {
                        var finalVelocityZ = Math.sqrt(Math.pow(fishArr[z].velocity[0], 2) +
                            Math.pow(fishArr[z].velocity[1], 2) + Math.pow(fishArr[z].velocity[2], 2));

                        var finalVelocityB = Math.sqrt(Math.pow(fishArr[b].velocity[0], 2) +
                            Math.pow(fishArr[b].velocity[1], 2) + Math.pow(fishArr[b].velocity[2], 2));

                        if (Math.sqrt(Math.pow(fishArr[z].coords[0] - fishArr[b].coords[0], 2)
                                + Math.pow(fishArr[z].coords[1] - fishArr[b].coords[1], 2)
                                + Math.pow(fishArr[z].coords[2] - fishArr[b].coords[2], 2)) < radius) {

                            var randDirect = floatToInt(Math.random() * 3);

                            if (randDirect == 0) {
                                fishArr[z].velocity[0] = -fishArr[z].velocity[0];
                                fishArr[b].velocity[0] = -fishArr[b].velocity[0];
                            }
                            else if (randDirect == 1) {
                                fishArr[z].velocity[1] = -fishArr[z].velocity[1];
                                fishArr[b].velocity[1] = -fishArr[b].velocity[1];
                            }
                            else {
                                fishArr[z].velocity[2] = -fishArr[z].velocity[2];
                                fishArr[b].velocity[2] = -fishArr[b].velocity[2];
                            }
                        }
                        fishArr[z].coords = [fishArr[z].velocity[0]*tick + fishArr[z].coords[0], fishArr[z].velocity[1]*tick
                            + fishArr[z].coords[1], fishArr[z].velocity[2]*tick + fishArr[z].coords[2]];

                        fishArr[b].coords = [fishArr[b].velocity[0]*tick + fishArr[b].coords[0], fishArr[b].velocity[1]*tick
                        + fishArr[b].coords[1], fishArr[b].velocity[2]*tick + fishArr[b].coords[2]];
                    }
                }

                for (var i = 0; i < fishArr.length; i++) {
                    var fish = fishArr[i];

                    if (fish.coords[0] <= 0) {
                        fish.velocity[0] = Math.abs(fish.velocity[0]);
                    }

                    if (fish.coords[1] <= 0) {
                        fish.velocity[1] = Math.abs(fish.velocity[1]);
                    }

                    if (fish.coords[2] <= 0) {
                        fish.velocity[2] = Math.abs(fish.velocity[2]);
                    }

                    if (fish.coords[0] >= tankWidth) {
                        fish.velocity[0] = - fish.velocity[0];
                    }

                    if (fish.coords[1] >= tankHeight) {
                        fish.velocity[1] = - fish.velocity[1];
                    }

                    if (fish.coords[2] >= tankDepth) {
                        fish.velocity[2] = -fish.velocity[2];
                    }
                    fish.coords = [fish.coords[0] + fish.velocity[0]*tick, fish.coords[1] + fish.velocity[1]*tick,
                        fish.coords[2] + fish.velocity[2]*tick];

                    var aFishDataSet = new fishDataSet();

                    aFishDataSet._id = fish._id;

                    aFishDataSet.coords = fish.coords;
                    aFishDataSet.thread_num = fish.thread_num;

                    aFishDataSet.rotation = fish.rotation;
                    aFishDataSet.turningSpeed = fish.turningSpeed;

                    aFishDataSet.velocity = fish.velocity;
                    aFishDataSet.mass = fish.mass;

                    aFishDataSet.radius = fish.radius;
                    //aFishDataSet.neighbors = fish.neighbors;

                    aFishDataSet.lastUpdateTime = new Date().getMilliseconds();
                    aFishDataSet.version = fish.version + 1;

                    updatedFishArr.push(aFishDataSet);
                }
                for (var i = 0; i < updatedFishArr.length; i++) {
                    var updatedFish = updatedFishArr[i];
                    Meteor.call('updateFishData', updatedFish);
                }
                sleep(200);
                Session.set('dummyId', 'dummy' + new Date().getTime());
            }
        }
    });
});

/**
 * Calls the server method leaveFishTank(clientId) when the user tries to leave the page
 */
window.addEventListener('beforeunload', function () {
    alert("deleting tank worker.");
    Meteor.call("leaveFishTank", clientId);
});
