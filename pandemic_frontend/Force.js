//Crucial script within program. This is attached to every H20 molecule and will determine how it moves.

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
            this.ball = app.root.findByName("Ball");                             //locate the green ball in the scene.
        },

        // Called every frame, dt is time in seconds since last update
        update: function (dt) {
            
            if (app.keyboard.wasReleased(pc.input.KEY_L)) {
                this.entity.script.Force.updateModel(parseInt(this.entity.name, 10));
                console.log("L Key Pressed");
            }
            
            
//             var gravity = new pc.Vec3(0, 9.8, 0);
//             var goToHere = new pc.Vec3();
//             goToHere = this.ball.getPosition().sub(this.entity.getPosition());   //get position of green ball, create vector from it
//             goToHere.normalize().scale(1);
//             this.entity.rigidbody.applyForce(gravity);                           //apply a force that negates downward gravity force within PlayCanvas
//             this.entity.rigidbody.applyForce(goToHere);                          //apply a force that pushes molecule towards green ball

            
            //Code Below: Previous code which is able to find particle_id number from json object once and set it as name of molecule forever. 
            
//             var holder = {};
//             holder = app.root.findByName("Comm").script.ajax.send();
            
//             for (i = 0; i<holder.length; i++){
//                 if (this.entity.name == holder[i].particle_id){ //This is the comparison that means the most. must find typeof .name and .particle_id
//                     this.entity.setLocalPosition(holder[i].position[0], holder[i].position[1], holder[i].position[2]);
//                 }
//             }
            
//             if (!(global_num_found)){
//                 for (i = 0; i<holder.length; i++){
//                     if (this.entity.name == holder[i].particle_id){ //This is the comparison that means the most. must find typeof .name and .particle_id
//                         global_num_particle = i;
//                         global_num_found = true;
//                         this.entity.setLocalPosition(holder[i].position[0], holder[i].position[1], holder[i].position[2]);
//                     }
//                 }
//             }
//             else {
//                 this.entity.setLocalPosition(holder[global_num_particle].position[0], holder[global_num_particle].position[1], holder[global_num_particle].position[2]);
//             }
            
        },
        
        //Crucial function which other scripts can call and set position of H20 molecule to which this script is attached
        updatePosition: function (x, y, z) {
            this.entity.setLocalPosition(x, y, z);
        }, 
        
        updateModel: function (num) {
            if(num === 1){
                var number = (Math.random() < 0.5 ? 180 : 0);
                this.entity.setLocalEulerAngles(number , Math.random() * (89 - (-89)) + (-89), number );
                this.entity.model.asset = app.assets.find("Jill", "model");
                this.entity.animation.play("zombie_idle (1)", 0.1);
            }else if (num === 2){
                var number1 = (Math.random() < 0.5 ? 180 : 0);
                this.entity.setLocalEulerAngles(number1 , Math.random() * (89 - (-89)) + (-89), number1 );
                this.entity.model.asset = app.assets.find("Alpha", "model");
                this.entity.animation.play("mutant_flexing_muscles", 0.1);
            }else if (num === 3){
                var number2 = (Math.random() < 0.5 ? 180 : 0);
                this.entity.setLocalEulerAngles(number2 , Math.random() * (89 - (-89)) + (-89), number2 );
                this.entity.model.asset = app.assets.find("Mia_Business", "model");
                this.entity.animation.play("scared", 0.1);
            }else if (num === 4){
                var number3 = (Math.random() < 0.5 ? 180 : 0);
                this.entity.setLocalEulerAngles(number3 , Math.random() * (89 - (-89)) + (-89), number3 );
                this.entity.model.asset = app.assets.find("Zombiegirl_W_Kurniawan", "model");
                this.entity.animation.play("zombie_idle", 0.1);
            }
        }
    };

    return Force;
});