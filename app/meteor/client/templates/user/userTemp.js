/**
 * @author Elizabeth Wang
 * @version 3 August 2015
 *
 * Calculates number of particles user is responsible for, number of fish, and percentage of particles user is responsibl
 *  for
 */

/**
 * Joins the fish tank using the clientId
 */
Template.userTemp.onCreated(function () {
    Meteor.call("joinFishTank", clientId);
});

Template.userTemp.helpers({
    /**
     * Calculates and returns number of particles user is responsible for
     *
     * @returns number of particles user is responsible for
     */
    'getNumOfParticlesUserIsResponsibleFor': function () {
        return numOfFish / TankWorker.find().count();
    },

    /**
     * Returns number of fish.
     *
     * @returns numOfFish - number of fish in all.
     */
    'getNumFish': function () {
        return numOfFish;
    },

    /**
     * Calculates and returns percentage of particles user is responsible for
     *
     * @returns percentage of particles user is responsible for
     */
    'getPercentageOfParticlesUserIsResponsibleFor': function () {
        return (1 / TankWorker.find().count()) * 100;
    }
});