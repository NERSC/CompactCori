var global_num_particle;
var global_num_found = false;

pc.script.create('Force', function (app) {
    // Creates a new Force instance
    var Force = function (entity) {
        this.entity = entity;
    };

    Force.prototype = {
        // Called once after all resources are loaded and before the first update
        initialize: function () {
            console.log(this.entity.name);
            this.ball = app.root.findByName("Ball");
            //console.log("My name when Initialized: ", this.entity.name);
            //console.log("My getName() when Initialized: ", this.entity.getName());
        },

        // Called every frame, dt is time in seconds since last update
        update: function (dt) {
            
            /*
            var gravity = new pc.Vec3(0, 9.8, 0);
            var goToHere = new pc.Vec3();
            goToHere = this.ball.getPosition().sub(this.entity.getPosition());
            goToHere.normalize().scale(1);
            this.entity.rigidbody.applyForce(gravity);
            this.entity.rigidbody.applyForce(goToHere);
            //console.log("Name inside Force: ", this.entity.name);
            //console.log("getName() inside Force: ", this.entity.getName());
            
            var holder = {};
            holder = app.root.findByName("Comm").script.ajax.send();
            
            for (i = 0; i<holder.length; i++){
                if (this.entity.name == holder[i].particle_id){ //This is the comparison that means the most. must find typeof .name and .particle_id
                    this.entity.setLocalPosition(holder[i].position[0], holder[i].position[1], holder[i].position[2]);
                }
            }
            
            if (!(global_num_found)){
                for (i = 0; i<holder.length; i++){
                    if (this.entity.name == holder[i].particle_id){ //This is the comparison that means the most. must find typeof .name and .particle_id
                        global_num_particle = i;
                        global_num_found = true;
                        this.entity.setLocalPosition(holder[i].position[0], holder[i].position[1], holder[i].position[2]);
                    }
                }
            }
            else {
                this.entity.setLocalPosition(holder[global_num_particle].position[0], holder[global_num_particle].position[1], holder[global_num_particle].position[2]);
            }
            */
        },
        
        updatePosition: function (x, y, z) {
            this.entity.setLocalPosition(x, y, z);
        }
    };

    return Force;
});
