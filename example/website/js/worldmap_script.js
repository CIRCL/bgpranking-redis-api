$(function(){
  $('#world-map').vectorMap(
    {
      map: 'world_mill_en',
      series: {
        regions: [{
          values: ranks,
          scale: ['#C8EEFF', '#0071A4'],
          normalizeFunction: 'polynomial'
        }]
      },
      onLabelShow: function(e, el, code){
        el.html(el.html()+' (GDP - '+gdpData[code]+')');
      }
    }
  );
});

