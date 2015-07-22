Template.dataTemp.helpers({
    fishData: function() {
        return Tracker.nonreactive(function() {
            return JSON.stringify(Fish.find().fetch());
        });
    },
    paramData: function() {
        return JSON.stringify(params);
    }
});