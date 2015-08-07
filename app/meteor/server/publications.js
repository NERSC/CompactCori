/**
 * @author Elizabeth Wang
 * @version 3 August 2015
 *
 * Returns all elements of the Fish collection and the TankWorker collection
 */

/**
 * Returns an array of all the Fish, by returning all of the fish that do not have a fake ID.
 *
 * @param dummyId - string ID that doesn't match up to any of the real IDS
 * @return array of Fish objects that do not have the dummy ID (aka all of them)
 */
Meteor.publish('fish', function (dummyId) {
    return Fish.find({_id: {$ne: dummyId}});
});

/**
 * Returns an array of all the TankWorkers, by returning all of the tank workers that do not have a fake ID.
 *
 * @param dummyId - string ID that doesn't match up to any of the real IDS
 * @return array of Tank Worker objects that do not have the dummy ID (aka all of them)
 */

Meteor.publish('tankWorker', function (dummyId) {
    return TankWorker.find({_id: {$ne: dummyId}});
});
