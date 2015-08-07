/**
 * @author Elizabeth Wang
 * @version 3 August 2015
 * @type {number}
 *
 * File with all global variables and methods used in both the server and the client side.
 */

radius = 20;
numOfFish = 20;

tankWidth = 600;
tankHeight = 600;
tankDepth = 600;

initialized = false;

clientCounter = 0;

params = ({
    "num_particles": numOfFish,
    "num_active_workers": TankWorker.find().count(),
    "simulation_height": tankHeight,
    "simulation_width": tankWidth,
    "simulation_depth": tankDepth
});

/**
 * Returns integer version of parameter.
 *
 * @param num - float intended to be converted to int
 * @returns integer version of num
 */
floatToInt = function (num) {
    return num | 0;
}

/**
 * Checks if the direction is greater than 2PI radians or less than 0. If so, the direction is changed so that the final
 *  direction is greater than 0 and less than 2PI.
 *
 * @param rawDirection - direction intended to be refined, may be refined already
 * @returns rawDirection - converted version of rawDirection so that it is greater than 0 and less than 2PI.
 */
normalizeDirection = function (rawDirection) {
    while (rawDirection < 0) {
        rawDirection += Math.PI * 2;
    }

    while (rawDirection > 2 * Math.PI) {
        rawDirection -= Math.PI * 2;
    }
    return rawDirection;
}

/**
 * Pauses the program for a specific amount of time. Used during performance tuning.
 *
 * @param milliseconds - millseconds the program is expected to pause for
 */
sleep = function (milliseconds) {
    var start = new Date().getTime();
    for (var i = 0; i < 1e7; i++) {
        if ((new Date().getTime() - start) > milliseconds) {
            break;
        }
    }
}

/**
 * Empty function.
 */
fishDataSet = function() {
};

/**
 * Helper method that creates a guid and is used for getFishTankKey()
 *
 * @returns random string
 */
createGuid = function ()
{
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random()*16|0, v = c === 'x' ? r : (r&0x3|0x8);
        return v.toString(16);
    });
}

/**
 * Generates and returns an unique user ID a new client.
 *
 * @returns unique user ID
 */
getFishTankKey = function(){
    var clientIdKey = "nersc_fish_tank_client_uuid_key";
    var clientIdKeyValPair = new StoredVar(clientIdKey);
    var clientId = clientIdKeyValPair.get();
    if(!clientId){
        clientId = createGuid();
        clientIdKeyValPair.set(clientId);
    }
    return clientId;
}
