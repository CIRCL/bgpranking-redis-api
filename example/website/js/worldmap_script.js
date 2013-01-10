$(function(){
  $('#world-map').vectorMap(
    {
      map: 'world_mill_en',
      series: {
        regions: [{
          values: ranks,
          scale: ['#F0FFFF', '#00FF00', '#FFFF00', '#FF0000', '#000000'],
          normalizeFunction: 'polynomial'
        }]
      },
      onLabelShow: function(e, el, code){
        el.html(el.html()+' (GDP - ' + ranks[code]+')');
      }
    }
  );
});

