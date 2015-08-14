//Crucial script within project. Ajax calls are made to server running within python code on Compact Cori.
//Once Ajax call is successful, json object received is held within globaljson variable, which can be called
//from other scripts within project.

//Next 4 lines: Code that adds jQuery as a library to the Javascript. Found at http://stackoverflow.com/questions/1140402/how-to-add-jquery-in-js-file
var script = document.createElement('script');
script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js';
script.type = 'text/javascript';
document.getElementsByTagName('head')[0].appendChild(script);

var globaljson = [
    {"particle_id": 1, "position": [-2.5, 0, 0], "state": " "},
    {"particle_id": 2, "position": [0, 0, 0], "state": "o"},
    {"particle_id": 3, "position": [2.5, 0, 0], "state": "X"},
    {"particle_id": 4, "position": [0,0,2.5], "state": "I"}
];

var previousjson = [
    {"particle_id": 1, "position": [-2.5, 0, 0], "state": " "},
    {"particle_id": 2, "position": [0, 0, 0], "state": "o"},
    {"particle_id": 3, "position": [2.5, 0, 0], "state": "X"},
    {"particle_id": 4, "position": [0,0,2.5], "state": "I"}
];

//previousjson = globaljson
//globaljson - res

pc.script.create('ajax', function (app) {
    // Creates a new Ajax instance
    var Ajax = function (entity) {
        this.entity = entity;
    };

    Ajax.prototype = {
        // Called once after all resources are loaded and before the first update
        initialize: function () {
        },

        // Called every frame, dt is time in seconds since last update
        update: function (dt) {
            var vec = new pc.Vec3(0,0,0); 
            
            var urlstring = "http://128.55.8.137:8888/";  //http://128.55.8.137:8888/  , Rai
            
            //jQuery ajax call to get json object from server within MD simulation or Meteor application
            $.ajax({
                url: urlstring, //Elizabeth's url: "http://128.55.19.109:3000/api/get_particles"
                type: "GET",
                dataType: "json",
                success: function(res) {
                    
                    globaljson = res;                //this is where received json object is put into global json object
                },
                error: function(xhr, status, error) {
                }
                
            });
            
//             num_workers_changed = false;
//             if (globaljson.params.num_active_workers != app.root.findByName("Comm").script.KeyboardInput.params().num_workers){
//                 num_workers_changed = true;
//             }
            
            //Loop that checks every particle and updates position and color, according to number of nodes being used.
            
            for (i = 0; i < globaljson.length; i++){
                var id_num = globaljson[i].particle_id;
                app.root.findByName(id_num.toString()).script.Force.updatePosition(globaljson[i].position[0], globaljson[i].position[1], globaljson[i].position[2]);
                
                if(globaljson.length === previousjson.length){
                    if(globaljson[i].state != previousjson[i].state){
                        //console.log("THE STATUS OF PERSON", id_num.toString(), " CHANGED!!!");
                        if(globaljson[i].state === "X"){
                            app.root.findByName(id_num.toString()).script.Force.updateModel(1);
                        }else if(globaljson[i].state === "I"){
                            app.root.findByName(id_num.toString()).script.Force.updateModel(2);
                        }else if(globaljson[i].state === "o"){
                            app.root.findByName(id_num.toString()).script.Force.updateModel(3);
                        }else if(globaljson[i].state === " "){
                            app.root.findByName(id_num.toString()).script.Force.updateModel(4);
                        }
                    }
                }
                
                
                //app.root.findByName(id_num.toString()).script.Force.updatePosition(globaljson[i].x, globaljson[i].y, globaljson[i].z);  //Elizabeth code
//                 if (num_workers_changed){
//                     app.root.findByName(id_num.toString()).script.Force.setColor(globaljson.particles[i].thread_num);
//                 }
            }
            previousjson = globaljson;
        },
        
        //crucial function which returns json object to any script which asks for it. Called by every molecule
        send: function () {
            return globaljson;
        },
        
        length: function () {
            return globaljson.length;
        },
        
        //toggle function call which is called from KeyboardInput.js
        toggle: function (num){
            global_toggle = num;
        }
    };

    return Ajax;
});