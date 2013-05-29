g = new Dygraph(
    document.getElementById("graphdiv1"),
    "csv_agg/be_ch_de_lu_fr_nl",
    {
      axes: {
              y: {
                  valueFormatter: function(y) {
                      return y.toPrecision(8);
                      },
                  axisLabelFormatter: function(y) {
                      return y.toPrecision(5);
                      },
                 }
            },
      legend: 'always',
      rollPeriod: 7,
      showRoller: true,
      logscale : true,
      yAxisLabelWidth: 50,
      xAxisLabelWidth: 60
    }
);

