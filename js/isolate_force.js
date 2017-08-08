var canvas = document.querySelector("canvas"),
    context = canvas.getContext("2d"),
    width = canvas.width,
    height = canvas.height;

var color_scale = d3.scaleOrdinal()
  .domain(['D', 'R', 'I', 'Multi', 'Vacant', 'Third'])
  .range(['#64b5f6', '#e57373', '#90a4ae', '#9575cd', , '#fff176']);

d3.json('data/al_upper_houses.json', function(error, data) {
  
  data.forEach(function(d) {
    d.id = +d.id;
    d.party = d.party;
  });

  var simulation = d3.forceSimulation(data)
      .force("y", d3.forceY())
      .force("democrat", isolate(d3.forceX(-width / 6), function(d) { return d.party === "D"; }))
      .force("republican", isolate(d3.forceX(width / 6), function(d) { return d.party === "R"; }))
      .force("independent", isolate(d3.forceX(width / 3), function(d) { return d.party === "I"; }))  // modify these lines to rearrange layout
      .force("multi-party", isolate(d3.forceX(width / 6), function(d) { return d.party === "Multi"; }))
      .force("vacant", isolate(d3.forceX(width / 6), function(d) { return d.party === "Vacant"; }))
      .force("third", isolate(d3.forceX(width / 6), function(d) { return d.party === "Third"; }))
      .force("charge", d3.forceManyBody().strength(-10))
      .on("tick", ticked);

  function ticked() {
    context.clearRect(0, 0, width, height);
    context.save();
    context.translate(width / 2, height / 2);
    data.forEach(drawNode);
    context.restore();
  }

  function drawNode(d) {
    context.beginPath();
    context.moveTo(d.x + 3, d.y);
    context.arc(d.x, d.y, 3, 0, 2 * Math.PI);
    context.fillStyle = color_scale(d.party);  //add stroke for vacant seats
    context.fill();
  }

  function isolate(force, filter) {
    var initialize = force.initialize;
    force.initialize = function() { initialize.call(force, data.filter(filter)); };
    return force;
  }
});