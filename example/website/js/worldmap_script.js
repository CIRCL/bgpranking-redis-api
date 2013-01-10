$(function(){
  $('#world-map').vectorMap(
    {
      map: 'world_mill_en',
      series: {
        regions: [{
          values: ranks,
          scale: ['#00FF00', '#FFFF00', '#ff0000'],
          normalizeFunction: 'polynomial'
        }]
      },
      onLabelShow: function(e, el, code){
        el.html(el.html()+' (GDP - ' + ranks[code]+')');
      }
    }
  );
});

