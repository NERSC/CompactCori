// commit and push to git

var radius = 20;
var numOfFish = 20;

//var tankWidth = screen.availWidth; // make as wide and as tall as the screen
//var tankHeight = screen.availHeight;

//var clientTankWidth = screen.width; // not working :(
//var clientTankHeight = screen.height;

var tankWidth = 800;
var tankHeight = 600;

var getId = function () {
    if (Meteor.user().services.password) // if you're signed in with a local account
        return Meteor.user().emails[0].address;
}

//var clientEmailId = "FIRST";
//var clientEmailId = this.userId;
var clientEmailId = this._id;

tankWorkerCollection = new Mongo.Collection('tankWorker');
fishCollection = new Mongo.Collection('fish');

var floatToInt = function (num) {
    return num | 0;
}

var normalizeDirection = function (rawDirection) {
    while (rawDirection < 0) {
        rawDirection += Math.PI * 2;
    }

    while (rawDirection > 2 * Math.PI) {
        rawDirection -= Math.PI * 2;
    }
    return rawDirection;
}

var clientCounter = 0;

if (Meteor.isClient) {
    Meteor.call("joinFishTank", clientEmailId);
    var renderer = PIXI.autoDetectRenderer(tankWidth, tankHeight);
    /*
    Template.fish.helpers({
        fish: function () {
            return fishCollection.find();
        }
    });

    Template.tankWorker.helpers({
        tankWorker: function () {
            return tankWorkerCollection.find();
        }
    });
    */
    Template.fishTankTemplate.helpers({
        'run': function () { // going through everything
            //Meteor.call("joinFishTank", _id);

            document.body.appendChild(renderer.view);
            var stage = new PIXI.Container();

            var sprites = new PIXI.ParticleContainer(10000, {
                scale: true,
                position: true,
                rotation: true,
                uvs: true,
                alpha: true
            });
            stage.addChild(sprites);
            var fishCreatedOnClientArr = [];

            //var totalSprites = renderer instanceof PIXI.WebGLRenderer ? 10 : 10;

            var boundsPadding = 100;
            var bounds = new PIXI.Rectangle(-boundsPadding,
                -boundsPadding,
                renderer.width + boundsPadding * 2,
                renderer.height + boundsPadding * 2);

            var tick = 0;
            var allFish = fishCollection.find({}, {sort: {_id: 1}}).fetch();

            console.log(tankWorkerCollection.find({
                _id: clientEmailId
            }).coords.startX);

            console.log(tankWorkerCollection.find({
                _id: clientEmailId
            }).coords.startY);

            for (var m = 0; m < allFish.length; m++) { // update
                var fishOnServer = allFish[m];
                var fishCreatedOnClient = PIXI.Sprite.fromImage(fishOnServer.imageUrl);

                fishCreatedOnClient._id = fishOnServer._id;
                fishCreatedOnClient.tint = fishOnServer.tint;

                // set the anchor point so the texture is centerd on the sprite
                fishCreatedOnClient.anchor.set(fishOnServer.anchor);

                fishCreatedOnClient.scale.set(fishOnServer.scale);

                fishCreatedOnClient.x = fishOnServer.x;
                fishCreatedOnClient.y = fishOnServer.y;

                // create a random direction in radians
                fishCreatedOnClient.direction = fishOnServer.direction; // from zero to 2pi
                //console.log("direction: " + fishCreatedOnClient.direction);

                // this number will be used to modify the direction of the sprite over time
                fishCreatedOnClient.turningSpeed = fishOnServer.turningSpeed;

                fishCreatedOnClient.speed = fishOnServer.speed;

                fishCreatedOnClient.offset = fishOnServer.offset;
                fishCreatedOnClientArr.push(fishCreatedOnClient);

                sprites.addChild(fishCreatedOnClient);
            }

            Tracker.autorun(function(){
                // retrieve fish moving information from the server database
                var allFish = fishCollection.find({}, {sort: {_id: 1}}).fetch();

                // update the local fish with the update moving information.
                for (var m = 0; m < allFish.length; m++) { // update
                    var fishOnServer = allFish[m];

                    fishCreatedOnClientArr[m]._id = fishOnServer._id;
                    fishCreatedOnClientArr[m].anchor.set(fishOnServer.anchor);

                    fishCreatedOnClientArr[m].scale.set(fishOnServer.scale);

                    // scatter them all
                    fishCreatedOnClientArr[m].x = fishOnServer.x;
                    fishCreatedOnClientArr[m].y = fishOnServer.y;

                    fishCreatedOnClientArr[m].tint = fishOnServer.tint;
                    fishCreatedOnClientArr[m].direction = fishOnServer.direction; // from zero to 2pi

                    fishCreatedOnClientArr[m].rotation = fishOnServer.rotation;

                    fishCreatedOnClientArr[m].turningSpeed = fishOnServer.turningSpeed;
                    fishCreatedOnClientArr[m].speed = fishOnServer.speed;

                    fishCreatedOnClientArr[m].offset = fishOnServer.offset;
                }
            });
            requestAnimationFrame(animate);

            function animate() {
                var worker = tankWorkerCollection.findOne({clientId: clientEmailId});
                var myfishIDs = worker.fishIDs;

                var fishArr = fishCollection.find({_id: {$in: myfishIDs}}).fetch();
                for (var z = 0; z < fishArr.length; z++) { // skipping over this loop -> fish arr is equal to 0?
                    for (var b = z + 1; b < fishArr.length; b++) {
                        if (Math.sqrt(Math.pow(fishArr[z].x - fishArr[b].x, 2) + Math.pow(fishArr[z].y - fishArr[b].y, 2)) < radius) { // update
                            var randDirect = floatToInt(Math.random() * 2);

                            if (randDirect == 0) { // get the value of the
                                fishArr[z].direction += Math.PI;
                                fishArr[b].direction += Math.PI;
                            }
                            else {
                                fishArr[z].direction = -fishArr[z].direction;
                                fishArr[b].direction = -fishArr[b].direction;
                            }
                            fishArr[z].direction = normalizeDirection(fishArr[z].direction);
                            fishArr[b].direction = normalizeDirection(fishArr[b].direction);
                        }
                    }
                }

                for (var i = 0; i < fishArr.length; i++) {
                    var fish = fishArr[i];

                    if (fish.x <= 0) {
                        if (fish.direction > Math.PI / 2 && fish.direction < 3 * Math.PI / 2) {
                            fish.direction = normalizeDirection(fish.direction - Math.PI / 2);
                        }
                    }

                    if (fish.y <= 0) {
                        if (fish.direction > Math.PI && fish.direction < 2 * Math.PI) {
                            fish.direction = normalizeDirection(2 * Math.PI - fish.direction);
                        }
                    }

                    if (fish.x >= renderer.width) {
                        if ((fish.direction >= 0 && fish.direction < Math.PI / 2) || (fish.direction > 3 * Math.PI / 2 && fish.direction <= 2 * Math.PI)) {
                            fish.direction = normalizeDirection(Math.PI - fish.direction);
                        }
                    }

                    if (fish.y >= renderer.height) {
                        if (fish.direction > 0 && fish.direction < Math.PI) {
                            fish.direction = normalizeDirection(2 * Math.PI - fish.direction);
                        }
                    }

                    fish.x += Math.cos(fish.direction) * (fish.speed * fish.scale);
                    fish.y += Math.sin(fish.direction) * (fish.speed * fish.scale);

                    fish.scale = 0.95 + Math.sin(tick + fish.offset) * 0.05;
                    fish.direction += fish.turningSpeed * 0.01;
                    fish.direction = normalizeDirection(fish.direction);
                    fish.rotation = -fish.direction + Math.PI;
                }


                for(var i = 0; i < fishArr.length; i++){
                    var fish = fishArr[i];
                    fishCollection.update({_id: fish._id},
                        {$set: {
                            "imageUrl" : fish.imageUrl,
                            "tint" : fish.tint,
                            "anchor" : fish.anchor,
                            "scale" : fish.scale,
                            "x" : fish.x,
                            "y" : fish.y,
                            "direction" : fish.direction,
                            "rotation": fish.rotation,
                            "turningSpeed" : fish.turningSpeed,
                            "speed" : fish.speed,
                            "offset" : fish.offset
                        }
                    });
                }

                // increment the ticker
                tick += 0.1;

                // time to render the stage !
                renderer.render(stage);

                // request another animation frame...
                requestAnimationFrame(animate);

                clientCounter++;
            }
        }
    });
}

if (Meteor.isServer) {
    Meteor.startup(function () {
        var numOfFishOnServer = fishCollection.find().count();
        if (numOfFishOnServer < numOfFish) {
            for (var i = 0; i < numOfFish - numOfFishOnServer; i++) {
                // create a new Sprite
                var fish = new Object();

                fish.imageUrl = '_assets/small_fish.png';
                fish.tint = Math.random() * 0xE8D4CD;

                // set the anchor point so the texture is centerd on the sprite
                fish.anchor = 0.5;

                fish.scale = 0.8 + Math.random() * 0.3;

                // scatter them all
                fish.x = Math.random(); // * tankWidth
                fish.y = Math.random() * tankHeight; // * tankHeight

                fish.tint = Math.random() * 0x808080;

                // create a random direction in radians
                fish.direction = Math.random() * Math.PI * 2; // from zero to 2pi

                // this number will be used to modify the direction of the sprite over time
                fish.turningSpeed = Math.random() - 0.8;
                fish.speed = (2 + Math.random() * 2) * 0.2;

                fish.offset = Math.random() * 100;

                //push the fish into the fishOnServer collection so that clients can access them.
                fishCollection.insert(fish);
            }
        }
    });

    Meteor.publish('fishData', function () {
        return fishCollection.find({});
    });

    Meteor.publish('workerData', function () {
        return tankWorkerCollection.find({});
    });

    var coordsValue;
    var prevClientNum = tankWorkerCollection.find().count(); // check if new clientNum and prevClientNum are the same or not

    Meteor.methods({
        "joinFishTank": function (clientIdValue) { // set stuff up when a new client joins
            if (tankWorkerCollection.find({clientId: clientIdValue}).count() > 0) {
                return
            }

            tankWorkerCollection.insert({ // dummy data
                clientId: clientIdValue,
                coords: ({
                    startX: 0,
                    startY: 0,
                    endX: 0,
                    endY: 0
                }),
                fishIDs: []
            });

            var clients = tankWorkerCollection.find().fetch();

            var clientNum = clients.length;
            var clientCounter = 1;

            for (var i = 0; i < clientNum; i++) {
                var startX, endX;

                var startY = 0; // always these values
                var endY = tankHeight;

                if (clientCounter == 0) {
                    startX = 0;
                    endX = tankWidth / clientNum;
                }
                else if (clientCounter == clientNum) {
                    startX = tankWidth - tankHeight / clientNum;
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
                    endX: endX,
                    endY: endY
                });

                var fishArr = [];
                var fish = fishCollection.find().fetch();

                for (var z = 0; z < fish.length; z++) {
                    var thisFish = fish[z];

                    if (thisFish.x >= startX && thisFish.y >= startY // put in the array
                        && thisFish.x < endX && thisFish.y < endY) {
                        fishArr.push(thisFish._id);
                    }
                }
                tankWorkerCollection.update( // call this more frequently in animate method
                    {
                        _id: clients[i]._id
                    },
                    {
                        $set: {
                            coords: coordsValue,
                            fishIDs: fishArr
                        }
                    }
                );
            }
        },
        'printCoords': function () {

        },
        'checkIfFishIsOutOfArea': function (startX, startY, endX, endY, clientId) {
            var fishArr = [];
            var fish = fishCollection.find().fetch();

            for (var z = 0; z < fish.length; z++) {
                var thisFish = fish[z];

                if (thisFish.x >= startX && thisFish.y >= startY // put in the array
                    && thisFish.x < endX && thisFish.y < endY) {
                    fishArr.push(thisFish._id);
                }
            }
            tankWorkerCollection.update( // call this more frequently in animate method
                {
                    _id: clients[i]._id
                },
                {
                    $set: {
                        coordinates: coordsValue,
                        fishIDs: fishArr
                    }
                }
            );
        }
    });
}
