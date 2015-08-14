var spawncount = 0;    // variable to keep track of number of people in scene

pc.script.create('spawn', function (app) {
    // Creates a new Spawn instance
    var Spawn = function (entity) {
        this.entity = entity;
        //this.time = 0;
        this.entities = [];
        this.time = 0;
    };

    Spawn.prototype = {
        // Called once after all resources are loaded and before the first update
        initialize: function () {
            this.personTemplate = app.root.findByName("Jill");
            var globaljson_holder = app.root.findByName("Comm").script.ajax.send(); //getting json object from ajax.js through locally defined send() function
            for (i = 0; i < globaljson_holder.length; i++){
                var num_mol_id = globaljson_holder[i].particle_id;
                this.spawn_person(num_mol_id);
                spawncount += 1;
            }
        },

        // Called every frame, dt is time in seconds since last update
        update: function (dt) {
            if(app.root.findByName("Comm").script.ajax.length() != spawncount){
                   var globaljson_holder3 = app.root.findByName("Comm").script.ajax.send();
                   for (i = this.entities.length; i > 0; i--){
                       this.entities[i-1].entity.destroy();
                       this.entities.splice(i-1, 1);
                       spawncount -= 1;
                   }
                   for (i = 0; i < globaljson_holder3.length; i++){
                       var num_mol_id = globaljson_holder3[i].particle_id;
                       this.spawn_person(num_mol_id);
                       spawncount += 1;
                   }
               }
        },
        
        spawn_person: function(num){
            var e = this.personTemplate.clone();                             //clone body of H20 molecule
            e.setPosition(this.entity.getPosition());
            e.translate(pc.math.random(-25,25),0,pc.math.random(-25,25));      //spawn clone from a random position
            //e.rigidbody.syncEntityToBody();                                    //sync rigidbody with cloned body
            var text = num.toString();
            e.name = text;                                                     //store passed parameter of particle_id into name attribute of entity
            app.root.addChild(e);                                              //add entity to the project heirarchy
            this.entities.push({ entity: e });                                 //push entity to list/array so it can be found easily later and deleted
        }
    };

    return Spawn;
});