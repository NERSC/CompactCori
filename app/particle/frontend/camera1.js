pc.script.attribute("elevation", "number", -30);
pc.script.attribute("distance", "number", 5);
pc.script.attribute("positionFactor", "number", 0.2);
pc.script.attribute("rotationFactor", "number", -0.2);

pc.script.create('camera1', function (context) {
    // Creates a new Camera instance
    var Camera = function (entity) {
        this.entity = entity;
        
        this.target = null;
        this.type = 0;
    };

    Camera.prototype = {
        // Called once after all resources are loaded and before the first update
        initialize: function () {
            this.target = context.root.findByName("Alpha");
        },

        // Called every frame, dt is time in seconds since last update
        postUpdate: function (dt) {
            if (this.type === 0) {
                this.updateFixedFollow(dt);
            } else if (this.type === 1) {
                this.updateTrailingFollow(dt);    
            } else if (this.type === 2) {
                this.updateLookAt();
            }
            
            // cycle through camera types
            if (context.keyboard.wasPressed(pc.input.KEY_SPACE)) {
                this.type++;
                if (this.type > 2) {
                    this.type = 0;
                }
            }
        },
        
        updateLookAt: function (dt) {
            this.entity.lookAt(this.target.getPosition());
        },
        
        updateFixedFollow: function (dt) {
            this.entity.setPosition(this.target.getPosition());
            this.entity.setRotation(this.target.getRotation());
            this.entity.rotateLocal(this.elevation, 180, 0);
            this.entity.translateLocal(0, 0, this.distance);
        },
        
        updateTrailingFollow: function (dt) {
            var pos = new pc.Vec3();
            var rot = new pc.Quat();
            
            // store initial position and rotation
            pos.copy(this.entity.getPosition());
            rot.copy(this.entity.getRotation());
            
            // set entity to be at target position and rotation
            this.entity.setPosition(this.target.getPosition());
            this.entity.setRotation(this.target.getRotation());
            this.entity.rotateLocal(this.elevation, 0, 0);
            this.entity.translateLocal(0, 0, this.distance);
            
            // interpolate start pos/rot to target pos/rot
            pos.lerp(pos, this.entity.getPosition(), this.positionFactor);
            rot.slerp(rot, this.entity.getRotation(), this.rotationFactor);
            
            // Set to interpolated position
            this.entity.setPosition(pos);
            this.entity.setRotation(rot);
        }
        
    };

    return Camera;
});