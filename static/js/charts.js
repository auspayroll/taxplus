$(document).ready(function() {

	var chartColours = ['#88bbc8', '#ed7a53', '#9FC569', '#bbdce3', '#9a3b1b', '#5a8022', '#2c7282'];

//-------------------------------------- end of stacked bar chart--------------------------------------------
	$("div.stacked-bars-chart").each(function(){
		data_div = $(this).siblings(".chart_data");
		data = $(data_div).html();
		data = eval("("+ data + ")");
		x_labels = data["x_labels"];
		tick_numbers = x_labels.length;
		data = data["data"];


		var data_array = new Array();
		for(var i=0;i<data.length;i++)
		{
			data_obj = data[i];
			obj = new Object();
			if(x_labels==undefined||x_labels==null)
			{
				obj.label = i+1;
			}
			else
			{
				obj.label = data_obj['label'];
			}
			obj.data = data_obj['data'];
			data_array.push(obj);
		}
		var stack = 0, bars = true, lines = false, steps = false;

		var options = {
				grid: {
					show: true,
				    aboveData: false,
				    color: "#3f3f3f" ,
				    labelMargin: 5,
				    axisMargin: 0, 
				    borderWidth: 0,
				    borderColor:null,
				    minBorderMargin: 5 ,
				    clickable: true, 
				    hoverable: true,
				    autoHighlight: true,
				    mouseActiveRadius: 20
				},
		        series: {
		        	grow: {active:false},
					stack: stack,
	                lines: { show: lines, fill: true, steps: steps },
	                bars: { show: bars, barWidth: 0.5, fill:1}
		        },
				yaxis: { min: 0 },
				xaxis: {ticks:tick_numbers, tickDecimals: 0},
		        legend: { position: "ne" },
		        colors: chartColours,
				shadowSize:1,
		        tooltip: true, //activate tooltip
				tooltipOpts: {
					content: "%s : %y.0",
					shifts: {
						x: -30,
						y: -50
					}
				}
		};


		var placeholder = $(this);
		$.plot(placeholder, data_array, options);
		$(placeholder).find("div.xAxis div.tickLabel").each(function(index){
			$(this).html(x_labels[index]);
		});

	}); 

//-------------------------------------- end of stacked bar chart--------------------------------------------



//-------------------------------------- start of simple pie--------------------------------------------
	$("div.simple-pie").each(function(){
		data_div = $(this).siblings(".chart_data");
		data = $(data_div).html();
		data = eval("("+ data + ")");

		 $.plot($(".simple-pie"), data, 
		{
			series: {
				pie: { 
					show: true,
					highlight: {
						opacity: 0.1
					},
					radius: 1,
					stroke: {
						color: '#fff',
						width: 2
					},
					startAngle: 2,
				    combine: {
	                    color: '#353535',
	                    threshold: 0.05
	                },
	                label: {
	                    show: true,
	                    radius: 1,
	                    formatter: function(label, series){
	                        return '<div class="pie-chart-label">'+label+'&nbsp;'+Math.round(series.percent)+'%</div>';
	                    }
	                }
				},
				grow: {	active: false}
			},
			legend:{show:true},
			grid: {
	            hoverable: true,
	            clickable: true
	        },
	        tooltip: true, //activate tooltip
			tooltipOpts: {
				content: "%s : %y.1"+"%",
				shifts: {
					x: -30,
					y: -50
				}
			}
		});
	}); 
//-------------------------------------- end of simple pie--------------------------------------------



//-------------------------------------- start of line chart--------------------------------------------
	$("div.lines-chart").each(function(){
		data_div = $(this).siblings(".chart_data");
		data = $(data_div).html();
		data = eval("("+ data + ")");
		x_labels = data["x_labels"];
		data = data["data"];


		data_array = [];
		for(var i=0;i<data.length;i++)
		{
			data_obj = data[i];
			obj = new Object();
			color_obj = new Object();
			if(x_labels==undefined||x_labels==null)
			{
				obj.label = i+1;
			}
			else
			{
				obj.label = data_obj['label'];
			}
			obj.data = data_obj['data'];
			color_obj.fillColor = chartColours[i];
			obj.lines = color_obj;
			data_array.push(obj);
		}

		//define placeholder class
		var placeholder = $(this);
		//graph options
		var options = {
			grid: {
				show: true,
				aboveData: true,
				color: "#3f3f3f" ,
				labelMargin: 5,
				axisMargin: 0, 
				borderWidth: 0,
				borderColor:null,
				minBorderMargin: 5 ,
				clickable: true, 
				hoverable: true,
				autoHighlight: true,
				mouseActiveRadius: 20
			},
		    series: {
		        grow: {active:false},
		        lines: {
	            	show: true,
	            	fill: false,
	            	lineWidth: 2,
	            	steps: false
		            },
		        points: {show:false}
		    },
		    //legend: { position: "se" },
			legend: { position: "ne" },
		    yaxis: { min: 0 },
		    xaxis: {ticks:11, tickDecimals: 0},
		    colors: chartColours,
		    shadowSize:1,
		    tooltip: true, //activate tooltip
			tooltipOpts: {
				content: "%s : %y.0",
				shifts: {
					x: -30,
					y: -50
				}
			}
		};   
        $.plot(placeholder, data_array, options);
		$(placeholder).find("div.xAxis div.tickLabel").each(function(index){

			$(this).html(x_labels[index]);
		});


	}); 
//-------------------------------------- end of line chart--------------------------------------------




//-------------------------------------- start of bar chart--------------------------------------------
	$("div.order-bars-chart").each(function(){
		data_div = $(this).siblings(".chart_data");
		data = $(data_div).html();
		data = eval("("+ data + ")");
		x_labels = data["x_labels"];
		tick_numbers = x_labels.length;
		data = data["data"];


		data_array = [];
		for(var i=0;i<data.length;i++)
		{
			data_obj = data[i];
			
			obj = new Object();
			order_obj = new Object();
			if(x_labels==undefined||x_labels==null)
			{
				obj.label = i+1;
			}
			else
			{
				obj.label = data_obj['label'];
			}
			obj.data = data_obj['data'];
			order_obj.order = data_obj['bars']['order'];
			obj.bars = order_obj;
			data_array.push(obj);
		}

		
		var options = {
				bars: {
					show:true,
					barWidth: 0.2,
					fill:1
				},
				grid: {
					show: true,
				    aboveData: false,
				    color: "#3f3f3f" ,
				    labelMargin: 5,
				    axisMargin: 0, 
				    borderWidth: 0,
				    borderColor:null,
				    minBorderMargin: 5 ,
				    clickable: true, 
				    hoverable: true,
				    autoHighlight: false,
				    mouseActiveRadius: 20
				},
		        series: {
		        	grow: {active:false}
		        },
				yaxis: { min: 0 },
				xaxis: {ticks:tick_numbers, tickDecimals: 0},
		        legend: { position: "ne" },
		        colors: chartColours,
		        tooltip: true, //activate tooltip
				tooltipOpts: {
					content: "%s : %y.0",
					shifts: {
						x: -30,
						y: -50
					}
				}
		};

		var placeholder = $(this);
		$.plot(placeholder, data_array, options);
		$(placeholder).find("div.xAxis div.tickLabel").each(function(index){
			$(this).html(x_labels[index]);
		});

	}); 
//-------------------------------------- end of bar chart--------------------------------------------























}); 	