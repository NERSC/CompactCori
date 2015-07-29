var spawncount = 0;

pc.script.create('spawnH20', function (app) {
    
    // Creates a new SpawnH20 instance
    var SpawnH20 = function (entity) {
        this.entity = entity;
        //this.time = 0;
        this.entities = [];
    };

    SpawnH20.prototype = {
        // Called once after all resources are loaded and before the first update    
        initialize: function () {
            this.moleculeTemplate = app.root.findByName("H20 Molecule");
            for (i = 0; i < 5; i++){
                this.spawn_molecule(spawncount);
                spawncount += 1;
            }
        },

        // Called every frame, dt is time in seconds since last update
        update: function (dt) {
            //this.time+=dt;
//             if(app.root.findByName("Comm").script.ajax.length() > spawncount){
//                 var spawn_increase = spawncount;
//                 for (i = spawn_increase; i < app.root.findByName("Comm").script.ajax.length(); i++){
//                     this.spawn_molecule(spawncount);
//                     spawncount += 1;
//                 }
//             }
            
//             if(app.root.findByName("Comm").script.ajax.length() < spawncount){
//                 var spawn_decrease = spawncount;
//                 for (i = spawn_decrease; i > app.root.findByName("Comm").script.ajax.length(); i--){
//                     SpawnH20.entities[i-1].entity.destroy();
//                     SpawnH20.entities.splice(i-1, 1);
//                     spawncount -= 1;
//                 }
//             }
        },
        
        spawn_molecule: function(num){
            var e = this.moleculeTemplate.clone();
            e.setPosition(this.entity.getPosition());
            e.translate(pc.math.random(-25,25),0,pc.math.random(-25,25));
            e.rigidbody.syncEntityToBody();
            //console.log("numtostring: ", num.toString());
            var text = num.toString();
            //console.log("number text: ", text);
            //console.log("E: ", e);
            e.name = text; 
            app.root.addChild(e);
            this.entities.push({ entity: e });
        }
    };

    return SpawnH20;
});
