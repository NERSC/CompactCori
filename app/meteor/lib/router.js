/**
 * @author Elizabeth Wnag
 * @version 3 August 2015
 *
 * Configures and sets the router to show different pages: one for the user and one for the endpoints.
 */

Router.configure({
    layoutTemplate: "layout",
    waitOn: function(dummyId){
        return [Meteor.subscribe('tankWorker', dummyId), Meteor.subscribe('fish', dummyId)];
    }
});

Router.route('/api/v1/get_particles', {name: "dataTemp"});
Router.route('/', {name: "userTemp"});
