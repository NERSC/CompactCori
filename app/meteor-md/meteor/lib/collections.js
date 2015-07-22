/**
 * @author Elizabeth Wang
 * @version 3 August Monday
 * @type {Mongo.Collection}
 *
 * Creating and initializing the TankWorker and the Fish collections. The TankWorker collection stores the user IDs and
 *  arrays of the fish each user is responsible for. The Fish collection stores fish objects.
 */
TankWorker = new Mongo.Collection('tankWorker');
Fish = new Mongo.Collection('fish');
