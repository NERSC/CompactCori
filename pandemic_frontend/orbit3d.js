//Orbit Camera controlled by mouse input which will rotate around scene at a given distance.
//Either enable OrbitCamera entity or AlphaCamera entity, but not both.

pc.script.create('Orbit3d', function (context) {
    // Creates a new Orbit3d instance
    var Orbit3d = function (entity) {
        this.entity = entity;
    };

    Orbit3d.prototype = {
        // Called once after all resources are loaded and before the first update
        initialize: function () {
            this.factor = 1;
            
            this.cam = this.entity;
            this.cam.camera.nearClip = 0.01;
            this.cam.camera.farClip = 1000000;
            this.cam_xyz = new pc.Vec3();
            
            this.target = context.root.findByName("Root");
            this.target_xyz = new pc.Vec3();
            
            
            context.mouse.on(pc.input.EVENT_MOUSEMOVE, this.onMouseMove, this);
            context.mouse.on(pc.input.EVENT_MOUSEDOWN, this.onMouseDown, this);
            context.mouse.on(pc.input.EVENT_MOUSEUP, this.onMouseUp, this);
            
            this.cam_distance = 12; //r       //CRUCIAL KEY TO CHANGING DISTANCE OF CAMERA
            
            this.cam_ex = 30;  //phi
            this.cam_ez = 30;  //theta
            this.cam_ez_range = 160; 
            
            this.cam_state = 'idle';
            
        },

        // Called every frame, dt is time in seconds since last update
        update: function (dt) {
            this.target_xyz = this.target.getPosition();
            this.cam_xyz = this.cam.getPosition();
            
            
            /*
            X= r*cos(phi)*sin(theta);
            Z= r*sin(phi)*sin(theta);
            Y= r*cos(theta);            
            */
            
            this.cam_xyz.x = ((this.cam_distance)*Math.cos(this.cam_ex)*Math.sin(this.cam_ez)+this.target_xyz.x);
            this.cam_xyz.z = ((this.cam_distance)*Math.sin(this.cam_ex)*Math.sin(this.cam_ez)+this.target_xyz.z);
            this.cam_xyz.y = ((this.cam_distance)*Math.cos(this.cam_ez)+this.target_xyz.x);
            
            this.cam.setPosition(this.cam_xyz);
            this.cam.lookAt(this.target_xyz);
            
            //console.log(this.cam_state);
            
            
            
        },
        
        onMouseMove: function(event){
            
            //console.log("MOVE");
            if(this.cam_state === 'go'){
                this.cam_ex += event.dx/(100/this.factor);
                this.cam_ez += event.dy/(100/this.factor);
               
              
                
                
            }
        },
        
         onMouseDown: function(event){
            if(event.button === pc.input.MOUSEBUTTON_LEFT){
                this.cam_state = 'go';
            }
        },
         onMouseUp: function(event){
            if(event.button === pc.input.MOUSEBUTTON_LEFT){
                this.cam_state = 'idle';
            }          
            
        }
        
        
    };

    return Orbit3d;
});

/*
pc.script.create('orbit', function (context) {
    // Creates a new Orbit instance
    var Orbit = function (entity) {
        this.entity = entity;
    };
    
    var rSpeed = 0.25;
    var time = 0;

    Orbit.prototype = {
        // Called once after all resources are loaded and before the first update
        initialize: function () {
            ball = context.root.findByName('Box');
            cam = this.entity;
            this.target = new pc.Vec3();
        },

        // Called every frame, dt is time in seconds since last update
        update: function (dt) {
             this.target = ball.getPosition();
           
            time += rSpeed;
            var xLoc = (Math.sin(time * (Math.PI / 180)) * 20 + this.target.x);
            var zLoc = (Math.cos(time * (Math.PI / 180)) * 20 + this.target.z);
            cam.setPosition(xLoc, this.target.y+10, zLoc);
            cam.lookAt(this.target);
            
            
            
        }
    };

    return Orbit;
});

*/
