/**
 * @author Elizabeth Wang
 * @version 3 August 2015
 *
 * Allows users to join the fish tank or leave the fish tank and updates both collections and redistributes the fish
 *  accordingly.
 */

var coordsValue;


Meteor.methods({
    /**
     * Checks to see if a client is trying to join the fish tank. If so, the server adds the client and redistributes the
     *  fish and the boundaries for each client.
     *
     * @param clientIdValue - the ID of the client that is attempting to join the fish tank
     */
    "joinFishTank": function (clientIdValue) {
        if (TankWorker.find({clientId: clientIdValue}).count() > 0) {
            return
        }

        TankWorker.insert({
            clientId: clientIdValue,
            coords: ({
                startX: 0,
                startY: 0,
                startZ: 0,
                endX: 0,
                endY: 0,
                endZ: 0
            }),
            fishIDs: [],
            version: 0,
            createTime: new Date(),
            lastUpdateTime: new Date()
        });

        var clients = TankWorker.find().fetch();

        var clientNum = clients.length;
        var clientCounter = 0;

        for (var i = 0; i < clientNum; i++) {
            var startX, endX;

            var startY = 0;
            var endY = tankHeight;

            var startZ = 0;
            var endZ = tankDepth;

            if (clientCounter == 0) {
                startX = 0;
                endX = tankWidth / clientNum;
            }
            else if (clientCounter == clientNum - 1) {
                startX = tankWidth - tankWidth / clientNum;
                endX = tankWidth;
            }
            else {
                startX = (tankWidth / clientNum) * (clientCounter - 1);
                endX = startX + tankWidth / clientNum;
            }
            clientCounter++;

            coordsValue = ({
                startX: startX,
                startY: startY,
                startZ: startZ,
                endX: endX,
                endY: endY,
                endZ: endZ
            });

            var fishArr = [];
            var fish = Fish.find().fetch();

            for (var z = 0; z < fish.length; z++) {
                var thisFish = fish[z];

                if (thisFish.coords[0] >= startX && thisFish.coords[1] >= startY
                    && thisFish.coords[0] < endX && thisFish.coords[1] < endY && thisFish.coords[2] >= startZ && thisFish.coords[2] < endZ) {
                    fishArr.push(thisFish._id);
                    Fish.update(
                        {
                            _id: thisFish._id
                        },
                        {
                            $set: {
                                userId: clients[i]._id,
                                clientId: clients[i].clientId
                            }
                        }
                    )
                }
            }
            TankWorker.update(
                {
                    _id: clients[i]._id
                },
                {
                    $set: {
                        coords: coordsValue,
                        fishIDs: fishArr,
                        version: 1,
                        lastUpdateTime: new Date()
                    }
                }
            );
        }
    },
    /**
     * Checks to see if a fish has left the area the client responsible for it is responsible for. If so, the server
     *  removes responsibility from that client and forces the client that is responsible for the area the fish is now in
     *  to take responsibility for calculating the coordinates of the fish.
     *
     * @param startX - upper left hand x coordinate the old client's area started at
     *        endX - lower right hand x coordinate the old client's area ended at
     *        startY - upper left hand y coordinate the old client's area started at
     *        endY - lower right hand y coordinate the old client's area ended at
     *        clientId - the ID of fish's old client
     */
    'checkIfFishIsOutOfArea': function (startX, startY, startZ, endX, endY, endZ, clientId) {
        var fishArr = [];
        var fish = Fish.find().fetch();

        for (var z = 0; z < fish.length; z++) {
            var thisFish = fish[z];

            if (thisFish.coords[0] >= startX && thisFish.coords[1] >= startY
                && thisFish.coords[0] < endX && thisFish.coords[1] < endY && thisFish.coords[2] >= startZ && thisFish.coords[2] < endZ) {
                fishArr.push(thisFish._id);
            }
        }
        TankWorker.update(
            {
                _id: clients[i]._id
            },
            {
                $set: {
                    coordinates: coordsValue,
                    fishIDs: fishArr,
                    version: 1,
                    lastUpdateTime: new Date()
                }
            }
        );
    },
    /**
     * Replacing the faulty dictionary in the collection with the updated one
     * @param updatedFish - updated fish whose elements need to be used as a template for updating another fish
     */
    'updateFishData': function (updatedFish) {
        Fish.update({_id: updatedFish._id},
            {
                $set: {
                    "coords": updatedFish.coords,
                    "thread_num": updatedFish.thread_num,
                    //"direction": updatedFish.direction,

                    "rotation": updatedFish.rotation,
                    "turningSpeed": updatedFish.turningSpeed,

                    "velocity": updatedFish.velocity,
                    "mass": updatedFish.mass,

                    //"neighbors": updatedFish.neighbors,

                    "version": updatedFish.version,
                    "lastUpdateTime": new Date()
                }
            }
        );
    },

    /**
     * Checks to see if a client is trying to leave the fish tank. If so, the server removes the client and redistributes
     *  the fish and the boundaries for each client.
     *
     * @param clientIdValue - the ID of the client that is attempting to leave the fish tank
     */
    'leaveFishTank': function (clientId) {
        Fish.update(
            {
                userId: clientId
            },
            {
                $set: {
                    userId: null
                }
            }
        );

        TankWorker.remove({
            clientId: clientId
        });

        var clients = TankWorker.find().fetch();

        var clientNum = clients.length;
        var clientCounter = 0;

        for (var i = 0; i < clientNum; i++) {
            var startX, endX;

            var startY = 0;
            var endY = tankHeight;

            var startZ = 0;
            var endZ = tankDepth;

            if (clientCounter == 0) {
                startX = 0;
                endX = tankWidth / clientNum;
            }
            else if (clientCounter == clientNum - 1) {
                startX = tankWidth - tankWidth / clientNum;
                endX = tankWidth;
            }
            else {
                startX = (tankWidth / clientNum) * (clientCounter - 1);
                endX = startX + tankWidth / clientNum;
            }
            clientCounter++;

            coordsValue = ({
                startX: startX,
                startY: startY,
                startZ: startZ,
                endX: endX,
                endY: endY,
                endZ: endZ
            });

            var fishArr = [];

            var fish = Fish.find().fetch();

            for (var z = 0; z < fish.length; z++) {
                var thisFish = fish[z];

                if (thisFish.coords[0] >= startX && thisFish.coords[1] >= startY // put in the array
                    && thisFish.coords[0] < endX && thisFish.coords[1] < endY && thisFish.coords[2] >= startZ && thisFish.coords[2] < endZ) {
                    fishArr.push(thisFish._id);
                    Fish.update(
                        {
                            _id: thisFish._id
                        },
                        {
                            $set: {
                                userId: clients[i]._id,
                                clientId: clients[i].clientId
                            }
                        }
                    )
                }
            }
            TankWorker.update(
                {
                    _id: clients[i]._id
                },
                {
                    $set: {
                        coords: coordsValue,
                        fishIDs: fishArr,
                        version: 1,
                        lastUpdateTime: new Date()
                    }
                }
            );
        }
    },

    /**
     * Checks to see if any fish are directly on the boundaries. If so, the fish are assigned to the client that is to
     *  the right of the one it is bordering.
     */
    'checkIfFishOnBoundaryBetweenDifferentClients': function () {
        var fishArr = Fish.find().fetch();
        var tankWorkerArr = TankWorker.find().fetch();
        for (var i = 0; i < fishArr.length; i++) {
            for (var z = 0; z < tankWorkerArr.length; z++) {
                var fish = fishArr[i];
                var worker = tankWorkerArr[z];

                if (fish.coords[0] == worker.startX || fish.coords[1] == worker.startY
                    || fish.coords[2] == worker.startZ) {
                    //tankWorkerArr[z].fishIDs.remove(fish._id);
                    //tankWorkerArr[z].fishIDs.push(fish);
                    TankWorker.update(
                        {
                            _id: tankWorkerArr[z]._id
                        },
                        {
                            $set: {
                                fishIDs: TankWorker.fishIDs.push(fish)
                            }
                        }
                    );
                }
            }
        }
    }
});
