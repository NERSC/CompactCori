var script = document.createElement('script');
script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js';
script.type = 'text/javascript';
document.getElementsByTagName('head')[0].appendChild(script);

pc.script.create('manipulate', function (app) {
    // Creates a new Manipulate instanc
    var Manipulate = function (entity) {
        this.entity = entity;
        this.time = 0;
    };

    Manipulate.prototype = {
        // Called once after all resources are loaded and before the first update
        initialize: function () {
            this.ball2 = app.root.findByName("Ball2");
            //if(this.entity.name=="Ball2"){
            //    this.entity.rigidbody.linearVelocity = new pc.Vec3(pc.math.random(-5,5),pc.math.random(0,5),pc.math.random(-5,5));
            //} 
        },

        // Called every frame, dt is time in seconds since last update
        update: function (dt) { 
            //var holder = {};
            //holder = app.root.findByName("Comm").script.ajax.send();
            //this.entity.setLocalPosition(holder[0].position[0], holder[0].position[1], holder[0].position[2]);
        }
    };

    return Manipulate;
});

/*
pc.script.create('Force', function (app) {
    // Creates a new Force instance
    var Force = function (entity) {
        this.entity = entity;
    };
    Force.prototype = {
        // Called once after all resources are loaded and before the first update
        initialize: function () {
            if(this.entity.name=="H20 Molecule"){
                this.entity.rigidbody.linearVelocity = new pc.Vec3(pc.math.random(-5,5),pc.math.random(0,5),pc.math.random(-5,5));
            } 
            this.ball = app.root.findByName("Ball");
        },
        // Called every frame, dt is time in seconds since last update
        update: function (dt) {
            var gravity = new pc.Vec3(0, 9.8, 0);
            var goToHere = new pc.Vec3();
            goToHere = this.ball.getPosition().sub(this.entity.getPosition());
            goToHere.normalize().scale(9);
            this.entity.rigidbody.applyForce(gravity);
            this.entity.rigidbody.applyForce(goToHere);
        }
    };
    return Force;
});
*/