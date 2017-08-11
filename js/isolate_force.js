var canvas = document.querySelector("canvas"),
    context = canvas.getContext("2d"),
    width = canvas.width,
    height = canvas.height;

// set dimensions of each state's "small multiple" on the canvas
var m_width = 320,
    m_height = 200;

// functions to calculate the midpoint of each "small multiple"
function mid_width(d) {
  return (d.state_index % 3 * m_width  + (m_width/2));
}

function mid_height(d) {
  return (Math.floor(d.state_index / 3) * m_height) + (m_height/2);
}

var color_scale = d3.scaleOrdinal()
  .domain(['D', 'R', 'I', 'Multi', 'Vacant', 'Third'])
  .range(['#64b5f6', '#e57373', '#90a4ae', '#9575cd', '#F6F6F6', '#fff176']);

d3.json('data/state_upper_houses2.json', function(error, data) {
  
  data.forEach(function(d) {
    d.state = d.state;
    d.state_index = +d.state_index;
    d.id = d.id;
    d.party = d.party;
    d.sequence = d.sequence;
  });

  //var data2 = data.slice(0,500);

  var simulation = d3.forceSimulation(data)  //make force layout - have to add adjustment factors due to drift at the edges of the canvas
    .force("y", d3.forceY(function(d) { return mid_height(d) + (25 - d.state_index)/25 * 50; }))  // controls vertical displacement of the nodes
    .force("democrat", isolate(d3.forceX(function(d) { if(d.state_index % 3 === 0) { return mid_width(d) - (m_width / 8) + 40; }  // controls horizontal displacement of the nodes
                                                       else if(d.state_index % 3 === 2) { return mid_width(d) - (m_width / 8) - 40; }
                                                       else { return mid_width(d) - (m_width / 8); }}),
                                         function(d) { return d.party === "D"; }))
    .force("republican", isolate(d3.forceX(function(d) { if(d.state_index % 3 === 0) { return mid_width(d) + (m_width / 8) + 40; }
                                                       else if(d.state_index % 3 === 2) { return mid_width(d) + (m_width / 8) - 40; }
                                                       else { return mid_width(d) + (m_width / 8); }}), 
                                         function(d) { return d.party === "R"; }))
    .force("other", isolate(d3.forceX(function(d) { if(d.state_index % 3 === 0) { return mid_width(d) + 40; }
                                                       else if(d.state_index % 3 === 2) { return mid_width(d) - 40; }
                                                       else { return mid_width(d); }}), 
                                      function(d) { return (d.party === "I" || d.party === "Multi" || d.party === "Vacant" || d.party === "Third"); }))  
    .force("charge", d3.forceManyBody().strength(-5))  // controls how spread out nodes in the same group are from each other
    .on("tick", ticked); 

  function labelState(d) {
    context.font = "11px sans-serif";
    context.fillStyle = "black";
    context.textAlign = "center";
    context.fillText(d.state, mid_width(d), mid_height(d) - 80);
  }

  function drawNode(d) {
    context.beginPath();
    context.moveTo(d.x + 3, d.y);
    context.arc(d.x, d.y, 3, 0, 2 * Math.PI);
    context.fillStyle = color_scale(d.party);
    context.fill();
    context.strokeStyle = d.party === 'Vacant' ? '#7a7a7a' : '#F6F6F6';
    context.stroke();
  }

  function ticked() {
    context.clearRect(0, 0, width, height);
    context.save();
    data.forEach(drawNode);
    data.forEach(function(d) {if(d.sequence==="0") {labelState(d);} }); //only write the state name when the first district is called
    context.restore();                                                  //so we don't have the state name printed multiple times
  }

  function isolate(force, filter) {
    var initialize = force.initialize;
    force.initialize = function() { initialize.call(force, data.filter(filter)); };
    return force;
  }
});