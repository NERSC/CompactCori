var script = document.createElement('script');
script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js';
script.type = 'text/javascript';
document.getElementsByTagName('head')[0].appendChild(script);


pc.script.create('alphacontrols', function (context) {
    // Creates a new Tankcontrols instance
    var Alphacontrols = function (entity) {
        this.entity = entity;
        this.force = new pc.Vec3();
        
        this.torque = 0.5;
        this.power = 10;
        this.time = 0;
    };

    Alphacontrols.prototype = {
        // Called once after all resources are loaded
        initialize: function () {
        },

        // Called every frame, dt is time in seconds since last update
        update: function (dt) {
            this.entity.rigidbody.applyForce(0, 9.8, 0);
            if (context.keyboard.isPressed(pc.input.KEY_LEFT)) {
                //this.entity.rigidbody.applyTorque(0, this.torque, 0);
                this.entity.rotate(0,30*dt,0);
            }
            if (context.keyboard.isPressed(pc.input.KEY_RIGHT)) {
                //this.entity.rigidbody.applyTorque(0, -this.torque, 0);
                this.entity.rotate(0,-30*dt,0);
            }
            if (context.keyboard.isPressed(pc.input.KEY_UP)) {
                //this.force.copy(this.entity.forward).scale(-this.power);
                //this.entity.rigidbody.applyForce(this.force);
                this.entity.translate(0,0,2.5*dt);
            }
            if (context.keyboard.isPressed(pc.input.KEY_DOWN)) {
                //this.force.copy(this.entity.forward).scale(this.power);
                //this.entity.rigidbody.applyForce(this.force);
                this.entity.translate(0,0,-2.5*dt);
            }
            
            /*
            if (context.keyboard.isPressed(pc.input.KEY_A)) {
                var text1 = "name=ifreke&age=26";
                $.ajax({
                    url: "http://localhost:8080/api/v1/post_parameters",
                    type: "POST",
                    data: text1,
                    success: function(data, status, jqXHR) {
                    },
                    error: function(xhr, status, error) {
                    }
                });
            }
            */
        }
    };

    return Alphacontrols;
});