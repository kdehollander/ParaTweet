graph = function() {
  var width = 5000;
  var height = 5000;

  var strs = []; 

  $.ajax({
    async: false,
    type: 'GET',
    url: 'http://52.53.184.154:80/posts.txt',
    success: function(file) {
      let posts = file.split('\n');
      for(let i = 0; i < posts.length; i++) {
        strs.push(posts[i]);
      }
     }
  }); 
  var labels = [];
  for(let i = 0; i < strs.length; i++) {
    labels.push(i);
  }
  //console.log(strs); 
  var nodes = [];
  for(let i = 0; i < strs.length; i++) {
    nodes.push({});
  }
  //console.log(nodes);
  var links = []; 
  for(let i = 0; i < strs.length - 1; i++) {
    for(let j = i+1; j < strs.length; j++) {
      links.push({source: i, target: j});
    }
  }
  //console.log(links);
  var svg = d3.select('body').append('svg')
  .attr('width', '100%')
  .attr('height', height)
  .attr('class', 'svg');


     var force = d3.layout.force()
     .size([width, height])
     .nodes(nodes)
     .links(links);

     force.linkDistance(function(d) {
      let source = strs[d.source.index]   
      let target = strs[d.target.index]   
      let min_length = Math.min(source.length, target.length);
      let max_length = 0;
      let shortest_str = "";
      let longest_str = "";
      if(min_length == source.length) {
        shortest_str = source;
        longest_str = target;
        let m_wds = longest_str.split(' ');
        max_length = m_wds.length;
      } else {
        shortest_str = target;
        longest_str = source;
        let m_wds = longest_str.split(' ');
        max_length = m_wds.length;
      }
      words = shortest_str.split(' ');
      num_similar_words = 0;
      for(let i = 0; i < words.length; i++) {
        if(longest_str.includes(words[i])) {
          num_similar_words++;
        }
      }
      length = (1 - (num_similar_words / max_length));
      /*
      console.log({
        'source': d.source.index,
        'target': d.target.index,
        'similar': num_similar_words,
        'max_length': max_length,
        'length': length
      })
      */
      return length * 2000;
     });

     var link = svg.selectAll('.link')
     .data(links)
     .enter().append('line')
     .attr('class', 'link');

     var node = svg.selectAll('.node')
     .data(nodes)
     .enter().append('circle')
     .attr('class', 'node');

     var label = svg.selectAll('.label')
     .data(labels)
     .enter().append('text')
     .attr('class', 'label')
     .attr('font-family', 'sans-serif')
     .attr('font-size', '20px')
     .attr('fill', 'red');

     force.on('end', function() {

           let loc_x = [];
           let loc_y = [];

           node.attr('r', 10)
              .attr('cx', function(d) {
                 loc_x.push(d.x); 
                 return d.x; })
              .attr('cy', function(d) {
                 loc_y.push(d.y); 
                 return d.y; })
              .attr('id', function(d) {return d.index; });

           link.attr('x1', function(d) {
                 return d.source.x; })
              .attr('y1', function(d) {
                    return d.source.y; })
              .attr('x2', function(d) {
                    return d.target.x; })
              .attr('y2', function(d) {
                    return d.target.y; })
              .attr('source', function(d) { return d.source.index; })
              .attr('target', function(d) { return d.target.index; });

            label.attr('x', function(d) { return loc_x[d] - 10; })
                 .attr('y', function(d) { return loc_y[d] - 10; })
                 .attr('id', function(d) { return d; })
                 .text(function(d) { return ''; });

     });

  force.start();
}
graph();
