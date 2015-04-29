<!doctype>
<head>
  <link rel="stylesheet" href="rickshaw.min.css">
  <link rel="stylesheet" href="//code.jquery.com/ui/1.10.4/themes/smoothness/jquery-ui.css">
  <link rel="stylesheet" href="style.css">
	<script src="http://d3js.org/d3.v3.min.js" charset="utf-8"></script>
  <script src="//code.jquery.com/jquery-1.9.1.js"></script>
  <script src="//code.jquery.com/ui/1.10.4/jquery-ui.js"></script>

	<script src="rickshaw.min.js"></script>

<style>
  .rickshaw-chart {
      font: 10px sans-serif;
      float: left;
      margin-top: 70px;
            }
  .rickshaw-y-axis {
      font: 10px sans-serif;
      float: left;
      margin-top: 70px;
  }
  .rickshaw-legend {
      float: left;
      margin-left: 15px;
      margin-top: 70px;
  }

  .rickshaw-slider {
      float:left;
      margin-top: : 100px;
  }
</style>
</head>
<body>
    <section id="buttons">
% for stat in stats:

        <button id="{{stat}}button" onclick='show_stat("{{stat}}")'> show {{stat}} </button>
% end
    </section>
% for stat in stats:
    <section id="{{stat}}" style="display:none">
		<span> <h1> {{stat.capitalize()}} </h1> </span>
		<div class="rickshaw-y-axis" id="bearcart_y_axis_id_{{stat}}"></div>
		<div class="rickshaw-chart" id="bearcart_{{stat}}"></div>
		<div class="rickshaw-legend" id="bearcart_legend_id_{{stat}}"></div>
		<div class="rickshaw-slider" id="bearcart_slider_id_{{stat}}"></div>
	</section>
% end

<script>
var draw_graph = function(stat, json) {

    var render_plot = (function(){

        var palette = new Rickshaw.Color.Palette( {scheme: 'spectrum14'} );

	var series = [];
	for (var i = 0; i < json.length; i++) {
		series.push({name: json[i].name,
			     color: palette.color(),
			     data: json[i].data})
	}
        var graph = new Rickshaw.Graph( {
                element: d3.select("#bearcart_" + stat).node(),
                min: 'auto',
                width: 750,
                height: 400,
                renderer: 'line',
                series: series
                })

        var x_axis = new Rickshaw.Graph.Axis.Time( { graph: graph } );

        var y_axis = new Rickshaw.Graph.Axis.Y( {
		graph: graph,
		orientation: 'left',
		height: 400,
		tickFormat: Rickshaw.Fixtures.Number.formatKMBT,
		element: d3.select("#bearcart_y_axis_id_" + stat).node()
	} );

        var hoverDetail = new Rickshaw.Graph.HoverDetail( {
	    graph: graph,

	} );

        var legend = new Rickshaw.Graph.Legend({
		graph: graph,
		element: d3.select("#bearcart_legend_id_" + stat).node()
	});

	var shelving = new Rickshaw.Graph.Behavior.Series.Toggle({
	    graph: graph,
	    legend: legend
	});

        var slider = new Rickshaw.Graph.RangeSlider({
	    graph: graph,
	    element: d3.select("#bearcart_slider_id_" + stat).node()
	});

        graph.render();

    })();
}

var show_stat = function(stat) {
    // draw the graphs
    d3.json(stat + "_{{interval}}.json", function(error, json) {
        draw_graph(stat, json);
    });

    // show the section
    document.getElementById(stat).style.display='block'

    // hide the button if it exists
    document.getElementById(stat + "button").style.display='none';
}
</script>
</body>
