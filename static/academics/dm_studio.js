// Data Mining Algorithm Animation Studio
(function () {
  'use strict';
  var W = 560, H = 380, PAD = 32;
  var DMA_COLORS = ['#1677ff', '#0f9d72', '#dc3545', '#7c3aed', '#e8590c', '#0ea5e9'];

  function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;var t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
  function clamp01(v){return Math.max(0,Math.min(1,v));}
  function avg(arr){return arr.reduce(function(s,v){return s+v;},0)/arr.length;}
  function px(x){return PAD + x*(W-2*PAD);}
  function py(y){return PAD + y*(H-2*PAD);}
  function combos(arr,k){var res=[];(function rec(s,sel){if(sel.length===k){res.push(sel.slice());return;}for(var i=s;i<arr.length;i++){sel.push(arr[i]);rec(i+1,sel);sel.pop();}})(0,[]);return res;}

  function clr(ctx){ctx.fillStyle='#f8fbff';ctx.fillRect(0,0,W,H);ctx.textAlign='left';}
  function rrect(ctx,x,y,w,h,r){ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);ctx.closePath();}
  function dot(ctx,x,y,r,fill,stroke){ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fillStyle=fill;ctx.fill();if(stroke){ctx.lineWidth=1.5;ctx.strokeStyle=stroke;ctx.stroke();}}
  function star(ctx,cx,cy,r,color){ctx.save();ctx.translate(cx,cy);ctx.fillStyle=color;ctx.beginPath();for(var i=0;i<5;i++){var a=-Math.PI/2+i*2*Math.PI/5;ctx.lineTo(Math.cos(a)*r,Math.sin(a)*r);var a2=a+Math.PI/5;ctx.lineTo(Math.cos(a2)*r*0.45,Math.sin(a2)*r*0.45);}ctx.closePath();ctx.fill();ctx.restore();}
  function sq(ctx,cx,cy,s,color){ctx.fillStyle=color;ctx.fillRect(cx-s/2,cy-s/2,s,s);ctx.lineWidth=2;ctx.strokeStyle='#fff';ctx.strokeRect(cx-s/2,cy-s/2,s,s);}
  function line(ctx,x1,y1,x2,y2,color,w){ctx.strokeStyle=color||'#8093a7';ctx.lineWidth=w||2;ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();}
  function arrow(ctx,x1,y1,x2,y2,color){line(ctx,x1,y1,x2,y2,color,2);var a=Math.atan2(y2-y1,x2-x1);ctx.fillStyle=color||'#8093a7';ctx.beginPath();ctx.moveTo(x2,y2);ctx.lineTo(x2-9*Math.cos(a-0.4),y2-9*Math.sin(a-0.4));ctx.lineTo(x2-9*Math.cos(a+0.4),y2-9*Math.sin(a+0.4));ctx.closePath();ctx.fill();}
  function text(ctx,x,y,t,color,size,weight){ctx.fillStyle=color||'#243b53';ctx.font=(weight||'700')+' '+(size||13)+'px Inter,Arial,sans-serif';ctx.fillText(t,x,y);}
  function wrapText(ctx,t,x,y,maxw,lh){var words=String(t).split(' ');var ln='';var yy=y;for(var i=0;i<words.length;i++){var test=ln+words[i]+' ';if(ctx.measureText(test).width>maxw&&ln){ctx.fillText(ln,x,yy);ln=words[i]+' ';yy+=lh;}else ln=test;}ctx.fillText(ln,x,yy);}
  function rbox(ctx,x,y,w,h,label,o){o=o||{};ctx.fillStyle=o.active?'#1677ff':o.done?'#edfbf6':'#fff';ctx.strokeStyle=o.active?'#1677ff':o.done?'#9fe3c8':'#bcccdc';ctx.lineWidth=o.active?3:1.5;rrect(ctx,x,y,w,h,10);ctx.fill();ctx.stroke();ctx.fillStyle=o.active?'#fff':o.done?'#087b58':'#243b53';ctx.font='700 13px Inter,Arial,sans-serif';wrapText(ctx,label,x+10,y+19,w-20,16);}
  function gauss(rng){var u=0,v=0;while(u===0)u=rng();while(v===0)v=rng();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);}

  function buildKMeans(){
    var rng=mulberry32(11);
    var blobs=[[0.3,0.32],[0.72,0.3],[0.5,0.76]];
    var pts=[];
    blobs.forEach(function(b){for(var i=0;i<15;i++)pts.push({x:clamp01(b[0]+gauss(rng)*0.062),y:clamp01(b[1]+gauss(rng)*0.062)});});
    var nearest=function(p,cents){var best=0,bd=1e9;cents.forEach(function(c,ci){var d=(p.x-c[0])*(p.x-c[0])+(p.y-c[1])*(p.y-c[1]);if(d<bd){bd=d;best=ci;}});return best;};
    var assignAll=function(cents){return pts.map(function(p){return nearest(p,cents);});};
    var cents=[[0.18,0.62],[0.86,0.6],[0.5,0.14]];
    var frames=[{cents:cents.map(function(c){return {x:c[0],y:c[1]};}),assign:null,mode:'init'}];
    var cur=cents.map(function(c){return [c[0],c[1]];});
    var assign=assignAll(cur);
    var steps=[{title:'Initialize k centroids',text:'Place k = 3 initial centroids (stars). The three natural blobs are not yet separated.'}];
    for(var it=1; it<=5; it++){
      frames.push({cents:cur.map(function(c){return {x:c[0],y:c[1]};}),assign:assign.slice(),mode:'assign'});
      steps.push({title:'Iteration '+it+': assign points',text:'Assign every point to the nearest centroid using squared Euclidean distance.'});
      var nc=cur.map(function(_,ci){var mem=pts.filter(function(p,pi){return assign[pi]===ci;});if(!mem.length)return [cur[ci][0],cur[ci][1]];return [avg(mem.map(function(m){return m.x;})),avg(mem.map(function(m){return m.y;}))];});
      frames.push({cents:nc.map(function(c){return {x:c[0],y:c[1]};}),assign:assign.slice(),mode:'update'});
      steps.push({title:'Iteration '+it+': move centroids',text:'Recompute each centroid as the mean of its assigned points.'});
      var shift=Math.max.apply(null,cur.map(function(c,ci){return Math.hypot(c[0]-nc[ci][0],c[1]-nc[ci][1]);}));
      assign=assignAll(nc); cur=nc;
      if(shift<0.012){frames.push({cents:cur.map(function(c){return {x:c[0],y:c[1]};}),assign:assign.slice(),mode:'result'});steps.push({title:'Converged',text:'Centroids barely moved, so the three clusters are stable.'});break;}
    }
    frames.push({cents:cur.map(function(c){return {x:c[0],y:c[1]};}),assign:assign.slice(),mode:'result'});
    steps.push({title:'Result',text:'Final clusters cleanly separate the three groups. This is the k-means execution.'});
    var render=function(ctx,idx){
      clr(ctx);
      var f=frames[Math.min(idx,frames.length-1)];
      if(f.assign&&f.mode!=='init'){pts.forEach(function(p,i){var c=f.assign[i];if(c>=0){var ct=f.cents[c];line(ctx,px(p.x),py(p.y),px(ct.x),py(ct.y),DMA_COLORS[c%DMA_COLORS.length]+'55',1.5);}});}
      pts.forEach(function(p,i){var c=f.assign?f.assign[i]:-1;var col=c>=0?DMA_COLORS[c%DMA_COLORS.length]:'#9fb3c8';dot(ctx,px(p.x),py(p.y),6,col,'#fff');});
      f.cents.forEach(function(c,ci){ctx.fillStyle=DMA_COLORS[ci%DMA_COLORS.length]+'22';ctx.beginPath();ctx.arc(px(c.x),py(c.y),26,0,7);ctx.fill();star(ctx,px(c.x),py(c.y),12,DMA_COLORS[ci%DMA_COLORS.length]);});
    };
    return {name:'k-means',summary:'k-means partitions n points into k clusters by repeatedly assigning points to the nearest centroid and moving each centroid to the mean of its members until convergence.',steps:steps,legend:[{label:'Cluster 1',color:DMA_COLORS[0]},{label:'Cluster 2',color:DMA_COLORS[1]},{label:'Cluster 3',color:DMA_COLORS[2]},{label:'Centroid',color:'#102a43'}],render:render};
  }

  function buildKMedoids(){
    var rng=mulberry32(21);
    var blobs=[[0.3,0.32],[0.72,0.3],[0.5,0.76]];
    var pts=[];
    blobs.forEach(function(b){for(var i=0;i<14;i++)pts.push({x:clamp01(b[0]+gauss(rng)*0.06),y:clamp01(b[1]+gauss(rng)*0.06)});});
    var d2=function(a,b){return (a.x-b.x)*(a.x-b.x)+(a.y-b.y)*(a.y-b.y);};
    var nearest=function(p,med){var best=0,bd=1e9;med.forEach(function(m,mi){var dd=d2(p,pts[m]);if(dd<bd){bd=dd;best=mi;}});return best;};
    var assignAll=function(med){return pts.map(function(p){return nearest(p,med);});};
    var cost=function(med){return pts.reduce(function(s,p){return s+Math.min.apply(null,med.map(function(m){return d2(p,pts[m]);}));},0);};
    var med=[pts.findIndex(function(p){return p.x<0.45&&p.y<0.5;}), pts.findIndex(function(p){return p.x>0.55&&p.y<0.5;}), pts.findIndex(function(p){return p.y>0.6;})];
    if(med[0]<0||med[1]<0||med[2]<0){med=[0,Math.floor(pts.length/3),Math.floor(2*pts.length/3)];}
    var frames=[{med:med.slice(),assign:null,mode:'init'}];
    var assign=assignAll(med);
    var steps=[{title:'Initialize medoids',text:'Choose k = 3 medoids, each an actual data point (squares). Points are unassigned.'}];
    var cur=med.slice();
    for(var it=1; it<=3; it++){
      frames.push({med:cur.slice(),assign:assign.slice(),mode:'assign'});
      steps.push({title:'Iteration '+it+': assign to nearest medoid',text:'Assign each point to the closest medoid by distance.'});
      var base=cost(cur);
      var bestSwap=null,bestCost=base;
      for(var c=0;c<3;c++){for(var j=0;j<pts.length;j++){if(cur.indexOf(j)>=0)continue;var trial=cur.slice();trial[c]=j;var cc=cost(trial);if(cc<bestCost-1e-6){bestCost=cc;bestSwap={c:c,j:j};}}}
      if(bestSwap){var tr=cur.slice();tr[bestSwap.c]=bestSwap.j;cur=tr;}
      assign=assignAll(cur);
      frames.push({med:cur.slice(),assign:assign.slice(),mode:'swap'});
      steps.push({title:'Iteration '+it+': swap medoid to lower cost',text:bestSwap?('Swap accepted: new total cost = '+bestCost.toFixed(3)+'.'):'No swap lowered the cost; medoids are stable.'});
    }
    frames.push({med:cur.slice(),assign:assign.slice(),mode:'result'});
    steps.push({title:'Result',text:'Final medoids (squares) and clusters. k-medoids is more robust to outliers than k-means.'});
    var render=function(ctx,idx){
      clr(ctx);
      var f=frames[Math.min(idx,frames.length-1)];
      if(f.assign){pts.forEach(function(p,i){var c=f.assign[i];var col=c>=0?DMA_COLORS[c%DMA_COLORS.length]:'#9fb3c8';dot(ctx,px(p.x),py(p.y),6,col,'#fff');});}
      else pts.forEach(function(p){dot(ctx,px(p.x),py(p.y),6,'#9fb3c8','#fff');});
      f.med.forEach(function(m,mi){sq(ctx,px(pts[m].x),py(pts[m].y),15,DMA_COLORS[mi%DMA_COLORS.length]);});
    };
    return {name:'k-medoids (PAM)',summary:'k-medoids selects k actual data points as medoids and minimizes the sum of dissimilarities. Swapping a medoid with a non-medoid lowers the total cost, making it robust to noise.',steps:steps,legend:[{label:'Cluster 1',color:DMA_COLORS[0]},{label:'Cluster 2',color:DMA_COLORS[1]},{label:'Cluster 3',color:DMA_COLORS[2]},{label:'Medoid',color:'#102a43'}],render:render};
  }

  function buildDBSCAN(){
    var rng=mulberry32(33);
    var blobs=[[0.3,0.35],[0.72,0.32]];
    var pts=[];
    blobs.forEach(function(b){for(var i=0;i<16;i++)pts.push({x:clamp01(b[0]+gauss(rng)*0.05),y:clamp01(b[1]+gauss(rng)*0.05)});});
    for(var n=0;n<8;n++)pts.push({x:clamp01(rng()),y:clamp01(rng())});
    var eps=0.11,minPts=4,eps2=eps*eps;
    var neigh=function(i){var r=[];pts.forEach(function(p,j){if((p.x-pts[i].x)*(p.x-pts[i].x)+(p.y-pts[i].y)*(p.y-pts[i].y)<=eps2)r.push(j);});return r;};
    var labels=new Array(pts.length).fill(0),visited=new Array(pts.length).fill(false),isCore=new Array(pts.length).fill(false);
    var cid=0;
    for(var i=0;i<pts.length;i++){if(visited[i])continue;visited[i]=true;var nb=neigh(i);if(nb.length<minPts){labels[i]=-1;continue;}cid++;isCore[i]=true;var stack=nb.slice();labels[i]=cid;nb.forEach(function(j){labels[j]=cid;});while(stack.length){var q=stack.pop();if(visited[q])continue;visited[q]=true;var nq=neigh(q);if(nq.length>=minPts){isCore[q]=true;nq.forEach(function(s){if(!visited[s])stack.push(s);if(labels[s]<=0)labels[s]=cid;})}}}
    for(var m=0;m<pts.length;m++){if(labels[m]===-1){neigh(m).forEach(function(j){if(labels[j]>0){labels[m]=labels[j];}});}}
    var steps=[{title:'Define parameters',text:'Set radius Eps = 0.11 and MinPts = 4. A point with at least MinPts neighbours within Eps is a core point.'}];
    var frames=[{assign:labels.map(function(){return -2;})}];
    for(var c=1;c<=cid;c++){frames.push({assign:labels.map(function(l){return l===c?c:-1;}),core:isCore,eps:eps});steps.push({title:'Discover cluster '+c,text:'Expand a density-connected region: core points (rings) pull in their Eps-neighbours.'});}
    frames.push({assign:labels.slice()});
    steps.push({title:'Noise points',text:'Points never reached by any cluster are outliers (grey). Clusters are found without specifying k.'});
    var render=function(ctx,idx){
      clr(ctx);
      var f=frames[Math.min(idx,frames.length-1)];
      pts.forEach(function(p,i){var c=f.assign[i];var col=c>=0?DMA_COLORS[(c-1)%DMA_COLORS.length]:(c===-2?'#cbd5e1':'#94a3b8');dot(ctx,px(p.x),py(p.y),6,col,'#fff');});
      if(f.core){pts.forEach(function(p,i){if(f.core[i]&&f.assign[i]>=0){ctx.strokeStyle=DMA_COLORS[(f.assign[i]-1)%DMA_COLORS.length]+'66';ctx.beginPath();ctx.arc(px(p.x),py(p.y),f.eps*(W-2*PAD),0,7);ctx.stroke();}});}
    };
    return {name:'DBSCAN',summary:'DBSCAN finds arbitrarily shaped clusters by density. Core points have at least MinPts neighbours within Eps; density-reachable points join the cluster; the rest are noise.',steps:steps,legend:[{label:'Cluster 1',color:DMA_COLORS[0]},{label:'Cluster 2',color:DMA_COLORS[1]},{label:'Noise / outlier',color:'#94a3b8'}],render:render};
  }

  function buildOutlier(){
    var rng=mulberry32(44);
    var pts=[];
    for(var i=0;i<26;i++)pts.push({x:clamp01(0.3+gauss(rng)*0.16),y:clamp01(0.5+gauss(rng)*0.18)});
    pts.push({x:0.85,y:0.18},{x:0.12,y:0.85},{x:0.9,y:0.8});
    var k=3;
    var dist=function(a,b){return Math.hypot(a.x-b.x,a.y-b.y);};
    pts.forEach(function(p,i){var ds=pts.map(function(q,j){return {j:j,d:dist(p,q)};}).filter(function(o){return o.j!==i;}).sort(function(a,b){return a.d-b.d;});p.knn=ds.slice(0,k);p.kd=ds[k-1].d;});
    var ks=pts.map(function(p){return p.kd;}).sort(function(a,b){return a-b;});
    var thr=ks[Math.floor(ks.length*0.8)];
    var steps=[{title:'Data set',text:'Plot all objects in feature space. Three points sit far from the dense region.'},{title:'Compute k-nearest-neighbour distance',text:'For each point find the distance to its k = 3rd nearest neighbour (k-dist).'},{title:'Set outlier threshold',text:'The 80th percentile of k-dist is '+thr.toFixed(2)+'. Points whose k-dist exceeds it are outliers.'},{title:'Flag outliers',text:'The three isolated points have large k-dist and are marked as distance-based outliers (red).'}];
    var frames=[{assign:pts.map(function(){return 0;})},{assign:pts.map(function(){return 0;}),showKnn:true},{assign:pts.map(function(){return 0;})},{assign:pts.map(function(p,i){return p.kd>thr?1:0;})}];
    var render=function(ctx,idx){
      clr(ctx);
      var f=frames[Math.min(idx,frames.length-1)];
      if(f.showKnn){pts.forEach(function(p){p.knn.forEach(function(o){line(ctx,px(p.x),py(p.y),px(pts[o.j].x),py(pts[o.j].y),'#bcccdc88',1);});});}
      pts.forEach(function(p,i){var out=f.assign[i]===1;dot(ctx,px(p.x),py(p.y),out?8:6,out?'#dc3545':'#1677ff','#fff');});
      if(idx===frames.length-1)text(ctx,18,H-18,'Threshold k-dist = '+thr.toFixed(2),'#627d98',12);
    };
    return {name:'Distance-based outlier detection',summary:'An object is an outlier if its distance to its k-th nearest neighbour is unusually large. No distribution assumption is needed; only a distance threshold and k.',steps:steps,legend:[{label:'Normal object',color:'#1677ff'},{label:'Outlier',color:'#dc3545'}],render:render};
  }

  function buildProbHier(){
    var rng=mulberry32(55);
    var pts=[];
    [[0.3,0.35],[0.42,0.3],[0.34,0.5]].forEach(function(b){for(var i=0;i<5;i++)pts.push({x:clamp01(b[0]+gauss(rng)*0.05),y:clamp01(b[1]+gauss(rng)*0.05)});});
    var d2=function(a,b){return (a.x-b.x)*(a.x-b.x)+(a.y-b.y)*(a.y-b.y);};
    var clusters=pts.map(function(p,i){return {id:i,members:[i]};});
    var frames=[{assign:clusters.map(function(c,ci){return ci;})}];
    var steps=[{title:'Start: singletons',text:'Each object begins as its own cluster. Probabilistic hierarchical clustering merges the most similar pair at every step.'}];
    function allClusters(){var a=[];clusters.forEach(function(c,ci){c.members.forEach(function(m){a[m]=ci;});});return a;}
    while(clusters.length>1){
      var bi=0,bj=1,bd=1e9;
      for(var i=0;i<clusters.length;i++)for(var j=i+1;j<clusters.length;j++){var s=0,n=0;clusters[i].members.forEach(function(a){clusters[j].members.forEach(function(b){s+=d2(pts[a],pts[b]);n++;});});var d=s/n;if(d<bd){bd=d;bi=i;bj=j;}}
      var merged={id:clusters[bi].id,members:clusters[bi].members.concat(clusters[bj].members)};
      clusters=clusters.filter(function(_,i){return i!==bi&&i!==bj;});clusters.push(merged);
      frames.push({assign:allClusters()});
      steps.push({title:'Merge closest clusters',text:'Join the two clusters with the smallest average linkage distance ('+bd.toFixed(3)+').'});
    }
    frames.push({assign:allClusters()});
    steps.push({title:'Dendrogram complete',text:'A tree of nested clusters is produced; cut it at any height to obtain the desired number of clusters.'});
    var render=function(ctx,idx){
      clr(ctx);
      var f=frames[Math.min(idx,frames.length-1)];
      var cmap={},ci=0;
      pts.forEach(function(p,i){var c=f.assign[i];if(!(c in cmap))cmap[c]=ci++;dot(ctx,px(p.x),py(p.y),6,DMA_COLORS[cmap[c]%DMA_COLORS.length],'#fff');});
    };
    return {name:'Probabilistic hierarchical clustering',summary:'Hierarchical clustering builds a tree of clusters by repeatedly merging the closest pair (using average linkage). No k is needed; a dendrogram shows all levels at once.',steps:steps,legend:[{label:'Cluster A',color:DMA_COLORS[0]},{label:'Cluster B',color:DMA_COLORS[1]},{label:'Cluster C',color:DMA_COLORS[2]}],render:render};
  }

  function buildDecisionTree(){
    var data=[
      {Outlook:'Sunny',Temp:'Hot',Humidity:'High',Wind:'Weak',Play:'No'},
      {Outlook:'Sunny',Temp:'Hot',Humidity:'High',Wind:'Strong',Play:'No'},
      {Outlook:'Overcast',Temp:'Hot',Humidity:'High',Wind:'Weak',Play:'Yes'},
      {Outlook:'Rain',Temp:'Mild',Humidity:'High',Wind:'Weak',Play:'Yes'},
      {Outlook:'Rain',Temp:'Cool',Humidity:'Normal',Wind:'Weak',Play:'Yes'},
      {Outlook:'Rain',Temp:'Cool',Humidity:'Normal',Wind:'Strong',Play:'No'},
      {Outlook:'Overcast',Temp:'Cool',Humidity:'Normal',Wind:'Strong',Play:'Yes'},
      {Outlook:'Sunny',Temp:'Mild',Humidity:'High',Wind:'Weak',Play:'No'},
      {Outlook:'Sunny',Temp:'Cool',Humidity:'Normal',Wind:'Weak',Play:'Yes'},
      {Outlook:'Rain',Temp:'Mild',Humidity:'Normal',Wind:'Weak',Play:'Yes'},
      {Outlook:'Sunny',Temp:'Mild',Humidity:'Normal',Wind:'Strong',Play:'Yes'},
      {Outlook:'Overcast',Temp:'Mild',Humidity:'High',Wind:'Strong',Play:'Yes'},
      {Outlook:'Overcast',Temp:'Hot',Humidity:'Normal',Wind:'Weak',Play:'Yes'},
      {Outlook:'Rain',Temp:'Mild',Humidity:'High',Wind:'Strong',Play:'No'}
    ];
    var attrs=['Outlook','Temp','Humidity','Wind'];
    function entropy(rows){var c={};rows.forEach(function(r){c[r.Play]=(c[r.Play]||0)+1;});var e=0,n=rows.length;for(var k in c){var p=c[k]/n;e-=p*Math.log2(p);}return e;}
    function gain(rows,a){var e=entropy(rows);var g={};rows.forEach(function(r){(g[r[a]]=g[r[a]]||[]).push(r);});var gg=e;for(var k in g)gg-=g[k].length/rows.length*entropy(g[k]);return gg;}
    var nodes=[{id:0,parent:-1,label:'',depth:0,x:0,y:0,kind:'root'}];
    var nid=1,reveal=[0];
    var steps=[{title:'Compute entropy of target',text:'Entropy(Play) = '+entropy(data).toFixed(3)+'. Lower entropy means purer splits.'}];
    function id3(rows,parent,depth){
      var counts={};rows.forEach(function(r){counts[r.Play]=(counts[r.Play]||0)+1;});
      var maj=Object.keys(counts).sort(function(a,b){return counts[b]-counts[a];})[0];
      if(rows.every(function(r){return r.Play===rows[0].Play;})){var id=nid++;nodes.push({id:id,parent:parent,label:rows[0].Play,depth:depth,kind:'leaf',x:0,y:0});reveal.push(id);steps.push({title:'Pure leaf',text:'All examples play = '+rows[0].Play+'. Stop and label the leaf.'});return id;}
      if(attrs.every(function(a){return rows.every(function(r){return r[a]===rows[0][a];});})){var id2=nid++;nodes.push({id:id2,parent:parent,label:maj,depth:depth,kind:'leaf',x:0,y:0});reveal.push(id2);steps.push({title:'No attributes left',text:'Use majority class = '+maj+'.'});return id2;}
      var best=attrs[0],bg=-1;attrs.forEach(function(a){var g=gain(rows,a);if(g>bg){bg=g;best=a;}});
      var id3n=nid++;nodes.push({id:id3n,parent:parent,label:best+'?',depth:depth,kind:'split',x:0,y:0});reveal.push(id3n);steps.push({title:'Split on '+best,text:'Gain('+best+') = '+bg.toFixed(3)+' is the highest, so it becomes the test attribute.'});
      var groups={};rows.forEach(function(r){(groups[r[best]]=groups[r[best]]||[]).push(r);});
      for(var val in groups){var child=id3(groups[val],id3n,depth+1);nodes[child].branch=val;}
      return id3n;
    }
    id3(data,-1,0);
    var byDepth={};nodes.forEach(function(n){(byDepth[n.depth]=byDepth[n.depth]||[]).push(n);});
    var maxDepth=Math.max.apply(null,nodes.map(function(n){return n.depth;}));
    for(var d in byDepth){var arr=byDepth[d];arr.forEach(function(n,i){n.x=(i+0.5)/arr.length;n.y=(Number(d)+0.5)/(maxDepth+1);});}
    var render=function(ctx,idx){
      clr(ctx);
      var revealed=new Set(reveal.slice(0,Math.min(idx+1,reveal.length)));
      var active=reveal[Math.min(idx,reveal.length-1)];
      nodes.forEach(function(n){if(!revealed.has(n.id))return;if(n.parent>=0&&revealed.has(n.parent)){var p=nodes[n.parent];arrow(ctx,px(p.x),py(p.y)+16,px(n.x),py(n.y)-14,'#9fb3c8');if(n.branch)text(ctx,(px(p.x)+px(n.x))/2,py(p.y)+36,n.branch,'#627d98',11);}});
      ctx.textAlign='center';
      nodes.forEach(function(n){if(!revealed.has(n.id))return;var w=72,h=30;var x=px(n.x)-w/2,y=py(n.y)-h/2;var c=n.kind==='leaf'?(n.label==='Yes'?'#0f9d72':'#dc3545'):'#102a43';ctx.fillStyle=(n.id===active)?'#1677ff':c;rrect(ctx,x,y,w,h,8);ctx.fill();ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.stroke();text(ctx,x+w/2,y+h/2+4,n.label,'#fff',13,'800');});
      ctx.textAlign='left';
    };
    return {name:'Generate decision tree (ID3)',summary:'ID3 builds a decision tree top-down. It picks the attribute with the highest information gain, splits the data, and recurses until every branch is pure. Entropy and gain guide the choices.',steps:steps,legend:[{label:'Internal test',color:'#102a43'},{label:'Play = Yes',color:'#0f9d72'},{label:'Play = No',color:'#dc3545'}],render:render};
  }

  function buildFPGrowth(){
    var txns=[['A','B','C'],['B','C','D'],['A','C','D'],['A','B','D'],['A','B','C']];
    var mins=2;
    var cnt={};txns.forEach(function(t){t.forEach(function(i){cnt[i]=(cnt[i]||0)+1;});});
    var freq=Object.keys(cnt).filter(function(i){return cnt[i]>=mins;}).sort(function(a,b){return cnt[b]-cnt[a]||a.localeCompare(b);});
    var order=freq;
    var root={item:null,count:0,children:{},parent:null,x:0,y:0};
    var header={};freq.forEach(function(f){header[f]=[];});
    function insert(path){var node=root;path.forEach(function(it){if(!node.children[it]){var nn={item:it,count:0,children:{},parent:node};node.children[it]=nn;header[it].push(nn);}node.children[it].count++;node=node.children[it];});}
    txns.forEach(function(t){var filt=t.filter(function(i){return freq.indexOf(i)>=0;}).sort(function(a,b){return order.indexOf(a)-order.indexOf(b);});if(filt.length)insert(filt);});
    var allNodes=[];(function walk(n){for(var k in n.children){allNodes.push(n.children[k]);walk(n.children[k]);}})(root);
    function depthOf(n){var d=0,p=n.parent;while(p){d++;p=p.parent;}return d;}
    var byDepth={};allNodes.forEach(function(n){var d=depthOf(n);(byDepth[d]=byDepth[d]||[]).push(n);});
    for(var d in byDepth){byDepth[d].forEach(function(n,i){n.x=(i+0.5)/byDepth[d].length;n.y=(Number(d)+0.5)/(Object.keys(byDepth).length+1);});}
    var steps=[{title:'Scan DB for frequent 1-itemsets',text:'Counts: '+freq.map(function(f){return f+'='+cnt[f];}).join(', ')+'. Keep those with support >= '+mins+'.'},{title:'Sort items by support',text:'Global order: '+order.join(' > ')+'. Each transaction is reordered by this order.'},{title:'Build FP-tree',text:'Insert each reordered transaction as a path; shared prefixes share nodes and their counts grow.'},{title:'Header table',text:'Each frequent item links to all its tree nodes for fast prefix traversal.'},{title:'Mine conditional patterns',text:'For each item (from rarest), collect its prefix paths to form conditional bases and grow frequent patterns.'}];
    var render=function(ctx,idx){
      clr(ctx);
      var revealCount=Math.min(idx+1,allNodes.length+1);
      ctx.font='700 12px Inter,Arial,sans-serif';
      text(ctx,18,22,'Header: '+order.join('  '),'#627d98',12);
      line(ctx,18,30,W-18,30,'#d9e2ec',1);
      var show=allNodes.slice(0,Math.max(0,revealCount-1));
      show.forEach(function(n){if(n.parent&&show.indexOf(n.parent)>=0)arrow(ctx,px(n.parent.x),py(n.parent.y)+12,px(n.x),py(n.y)-10,'#9fb3c8');});
      ctx.textAlign='center';
      show.forEach(function(n){var w=46,h=26;var x=px(n.x)-w/2,y=py(n.y)-h/2;ctx.fillStyle='#1677ff';rrect(ctx,x,y,w,h,7);ctx.fill();ctx.strokeStyle='#fff';ctx.lineWidth=1.5;ctx.stroke();ctx.fillStyle='#fff';ctx.fillText(n.item+' '+n.count,x+w/2,y+h/2+4);});
      ctx.textAlign='left';
      if(idx>=2)text(ctx,18,H-16,'FP-tree (nodes show item and count)','#627d98',12);
    };
    return {name:'FP-growth',summary:'FP-growth finds frequent itemsets without candidate generation. It compresses the database into an FP-tree ordered by item frequency, then mines conditional pattern bases recursively.',steps:steps,legend:[{label:'FP-tree node',color:'#1677ff'}],render:render};
  }

  function buildAprioriStudio(){
    var T=[['A','B','C'],['B','C','D'],['A','C','D'],['A','B','D'],['A','B','C']];
    var mins=2;
    var cnt={};T.forEach(function(t){t.forEach(function(i){cnt[i]=(cnt[i]||0)+1;});});
    var singles=Object.keys(cnt).filter(function(i){return cnt[i]>=mins;}).sort();
    var pairs=combos(singles,2).filter(function(p){return cnt[p[0]]>=mins&&cnt[p[1]]>=mins;});
    var triples=combos(singles,3).filter(function(tr){return T.filter(function(t){return tr.every(function(x){return t.indexOf(x)>=0;});}).length>=mins;});
    var L1=singles.map(function(s){return '{'+s+'}';});
    var L2=pairs.map(function(p){return '{'+p.join(',')+'}';});
    var L3=triples.map(function(t){return '{'+t.join(',')+'}';});
    var steps=[{title:'Scan DB: count 1-itemsets',text:'A, B, C, D each appear at least 2 times, so all are frequent (minsup count = 2).'},{title:'L1 frequent items',text:'Frequent 1-itemsets: '+L1.join(', ')+'.'},{title:'Generate C2 candidates',text:'Join L1 with itself; every 2-itemset is a candidate.'},{title:'L2 frequent pairs',text:'Frequent pairs: '+L2.join(', ')+'.'},{title:'Prune and generate C3',text:'Only {A,B,C} is frequent at level 3; others fall below support (Apriori pruning).'},{title:'L3 frequent',text:'Frequent triple: '+L3.join(', ')+'.'},{title:'Generate strong rules',text:'From {A,B,C}: A->BC, B->AC, C->AB each have confidence 2/3 = 66.7%.'}];
    var frames=[{},{},{l1:true},{l1:true},{l1:true,l2:true},{l1:true,l2:true},{l1:true,l2:true,l3:true}];
    var render=function(ctx,idx){
      clr(ctx);
      var f=frames[Math.min(idx,frames.length-1)];
      var y=60;
      if(f.l1){text(ctx,30,40,'L1',DMA_COLORS[0],14,'800');var x=30;L1.forEach(function(s){rbox(ctx,x,y,70,34,s,{done:true});x+=82;});y+=54;}
      if(f.l2){text(ctx,30,y-14,'L2',DMA_COLORS[1],14,'800');var x2=30;L2.forEach(function(s){rbox(ctx,x2,y,86,34,s,{done:true});x2+=96;});y+=54;}
      if(f.l3){text(ctx,30,y-14,'L3',DMA_COLORS[2],14,'800');var x3=30;L3.forEach(function(s){rbox(ctx,x3,y,90,34,s,{done:true});x3+=100;});}
    };
    return {name:'Apriori',summary:'Apriori finds frequent itemsets and association rules level by level. It generates candidates, counts their support, prunes those below minimum support using the Apriori property, then derives rules above minimum confidence.',steps:steps,legend:[{label:'L1',color:DMA_COLORS[0]},{label:'L2',color:DMA_COLORS[1]},{label:'L3',color:DMA_COLORS[2]}],render:render};
  }

  function buildSCAN(){
    var rng=mulberry32(66);
    var pts=[];
    [[0.3,0.35],[0.4,0.3],[0.32,0.48],[0.45,0.45]].forEach(function(b){for(var i=0;i<3;i++)pts.push({x:clamp01(b[0]+gauss(rng)*0.05),y:clamp01(b[1]+gauss(rng)*0.05)});});
    [[0.75,0.65],[0.82,0.55],[0.7,0.72]].forEach(function(b){for(var i=0;i<3;i++)pts.push({x:clamp01(b[0]+gauss(rng)*0.05),y:clamp01(b[1]+gauss(rng)*0.05)});});
    var eps=0.13,mu=2,eps2=eps*eps;
    var neigh=function(i){var r=[];pts.forEach(function(p,j){if((p.x-pts[i].x)*(p.x-pts[i].x)+(p.y-pts[i].y)*(p.y-pts[i].y)<=eps2)r.push(j);});return r;};
    var labels=new Array(pts.length).fill(-2);var cid=0;
    var steps=[{title:'Define structural similarity',text:'For each node count neighbours within Eps. A node with at least mu neighbours is a core; clusters are core-connected components.'}];
    var frames=[{assign:labels.slice()}];
    for(var i=0;i<pts.length;i++){if(labels[i]!==-2)continue;var nb=neigh(i);if(nb.length<mu)continue;cid++;labels[i]=cid;var stack=nb.slice();while(stack.length){var q=stack.pop();if(labels[q]!==-2)continue;labels[q]=cid;neigh(q).forEach(function(s){if(labels[s]===-2){stack.push(s);labels[s]=cid;}});}frames.push({assign:labels.slice()});steps.push({title:'Grow cluster '+cid,text:'Add structurally-similar (core-connected) nodes to the cluster.'});}
    for(var m=0;m<pts.length;m++)if(labels[m]===-2)labels[m]=-1;
    frames.push({assign:labels.slice()});steps.push({title:'Result',text:'Two communities are found on the graph; isolated nodes remain unclassified.'});
    var render=function(ctx,idx){clr(ctx);var f=frames[Math.min(idx,frames.length-1)];pts.forEach(function(p,i){for(var j=i+1;j<pts.length;j++){var inN=f.assign[i]>=0&&f.assign[j]>=0&&f.assign[i]===f.assign[j];if(inN)line(ctx,px(p.x),py(p.y),px(pts[j].x),py(pts[j].y),DMA_COLORS[(f.assign[i]-1)%DMA_COLORS.length]+'88',2);else if(f.assign[i]>=0&&f.assign[j]>=0)line(ctx,px(p.x),py(p.y),px(pts[j].x),py(pts[j].y),'#dbe2ea',1);}});pts.forEach(function(p,i){var c=f.assign[i];var col=c>=0?DMA_COLORS[(c-1)%DMA_COLORS.length]:'#94a3b8';dot(ctx,px(p.x),py(p.y),7,col,'#fff');});};
    return {name:'SCAN: clustering graph data',summary:'SCAN finds clusters and hubs in graph data using structural similarity. Core nodes with enough neighbours expand core-connected communities; the rest are outliers or hubs.',steps:steps,legend:[{label:'Community 1',color:DMA_COLORS[0]},{label:'Community 2',color:DMA_COLORS[1]},{label:'Outlier',color:'#94a3b8'}],render:render};
  }

  function buildBackprop(){
    var W1=[[0.4,-0.2],[0.1,0.3]];var b1=[0.1,0.0];
    var W2=[[0.5,-0.3]];var b2=[0.2];
    function sig(x){return 1/(1+Math.exp(-x));}
    var xin=[0.7,0.4];
    var hidden=xin.map(function(_,h){var s=b1[h];for(var i=0;i<2;i++)s+=W1[h][i]*xin[i];return {a:s,o:sig(s)};});
    var outa=b2[0]+W2[0][0]*hidden[0].o+W2[0][1]*hidden[1].o;var outo=sig(outa);
    var target=0.9;var err=0.5*(target-outo)*(target-outo);
    var steps=[{title:'Forward: input layer',text:'Inputs x1='+xin[0]+', x2='+xin[1]+' enter the network.'},{title:'Forward: hidden layer',text:'Each hidden unit computes z = w.x + b then sigmoid: h1='+hidden[0].o.toFixed(3)+', h2='+hidden[1].o.toFixed(3)+'.'},{title:'Forward: output layer',text:'Output y = sigmoid('+outa.toFixed(3)+') = '+outo.toFixed(3)+'.'},{title:'Compute error',text:'Error E = 1/2 (target - y)^2 = '+err.toFixed(4)+' for target '+target+'.'},{title:'Backpropagate',text:'Compute gradients dE/dw via the chain rule and update every weight by -eta * gradient.'},{title:'Iterate',text:'Repeat forward and backward passes; error decreases until the network fits the example.'}];
    var layers=[xin.map(function(v){return v.toFixed(2);}),hidden.map(function(h){return h.o.toFixed(3);}),[outo.toFixed(3)]];
    var render=function(ctx,idx){
      clr(ctx);
      var active=idx<1?0:(idx<3?1:2);
      var positions=[[[0.18,0.32],[0.18,0.68]],[[0.5,0.32],[0.5,0.68]],[[0.82,0.5]]];
      positions[0].forEach(function(a,ai){positions[1].forEach(function(b){var act=(active===1);line(ctx,px(a[0]),py(a[1]),px(b[0]),py(b[1]),act?'#1677ff':'#cbd5e1',act?2.5:1);});});
      positions[1].forEach(function(a){positions[2].forEach(function(b){var act=(active===2);line(ctx,px(a[0]),py(a[1]),px(b[0]),py(b[1]),act?'#0f9d72':'#cbd5e1',act?2.5:1);});});
      positions.forEach(function(layer,li){layer.forEach(function(p,pi){var col=li===0?'#9fb3c8':(li===1?'#1677ff':'#0f9d72');if(li===active)col='#7c3aed';ctx.fillStyle=col;ctx.beginPath();ctx.arc(px(p[0]),py(p[1]),22,0,7);ctx.fill();ctx.fillStyle='#fff';ctx.textAlign='center';ctx.font='700 12px Inter';ctx.fillText(layers[li][pi],px(p[0]),py(p[1])+4);});});
      ctx.textAlign='left';
      text(ctx,18,H-18,'Forward pass then backpropagation updates weights','#627d98',12);
    };
    return {name:'Backpropagation',summary:'Backpropagation trains a neural network by a forward pass that computes the output and error, followed by a backward pass that propagates the error gradient through the chain rule to update every weight.',steps:steps,legend:[{label:'Input',color:'#9fb3c8'},{label:'Hidden',color:'#1677ff'},{label:'Output',color:'#0f9d72'}],render:render};
  }

  function buildAdaBoost(){
    var rng=mulberry32(77);
    var pts=[];
    for(var i=0;i<10;i++){var x=clamp01(0.2+gauss(rng)*0.1),y=clamp01(0.2+gauss(rng)*0.1);pts.push({x:x,y:y,cls:0,id:i});}
    for(var j=0;j<10;j++){var x2=clamp01(0.7+gauss(rng)*0.1),y2=clamp01(0.7+gauss(rng)*0.1);pts.push({x:x2,y:y2,cls:1,id:10+j});}
    var w=pts.map(function(){return 1/pts.length;});
    var steps=[{title:'Initialize weights',text:'Every training point starts with equal weight 1/'+pts.length+'.'},{title:'Train weak learner 1',text:'A vertical split at x = 0.5 misclassifies the points crossing the boundary; its error e1 is computed.'},{title:'Compute alpha1',text:'alpha1 = 0.5 ln((1-e1)/e1) sets the learner importance; update weights to focus on mistakes.'},{title:'Train weak learner 2',text:'A horizontal split at y = 0.5 is trained on the reweighted data.'},{title:'Combine',text:'The final strong classifier is a weighted vote of all weak learners.'}];
    var frames=[{bx:0,by:0,showB:false,showH:false},{bx:0.5,by:0,showB:true,showH:false},{bx:0.5,by:0,showB:true,showH:false},{bx:0.5,by:0,showB:true,showH:false},{bx:0.5,by:0.5,showB:true,showH:true},{bx:0.5,by:0.5,showB:true,showH:true}];
    var render=function(ctx,idx){
      clr(ctx);
      var f=frames[Math.min(idx,frames.length-1)];
      if(f.showB){ctx.strokeStyle='#1677ff';ctx.setLineDash([6,5]);ctx.lineWidth=2.5;line(ctx,px(f.bx),PAD,px(f.bx),H-PAD,'#1677ff',2.5);ctx.setLineDash([]);}
      if(f.showH){ctx.strokeStyle='#dc3545';ctx.setLineDash([6,5]);ctx.lineWidth=2.5;line(ctx,PAD,py(f.by),W-PAD,py(f.by),'#dc3545',2.5);ctx.setLineDash([]);}
      pts.forEach(function(p){var r=7+(w[p.id]*pts.length)*10;dot(ctx,px(p.x),py(p.y),Math.max(5,Math.min(14,r)),p.cls===0?'#1677ff':'#0f9d72','#fff');});
    };
    return {name:'AdaBoost',summary:'AdaBoost builds a strong classifier from many weak learners. Each round trains a weak learner, weights it by accuracy, increases the weight of misclassified examples, and combines all learners by weighted voting.',steps:steps,legend:[{label:'Class 0',color:'#1677ff'},{label:'Class 1',color:'#0f9d72'},{label:'Boundary',color:'#dc3545'}],render:render};
  }

  function defaultAlgo(id){
    var map={
      'buc':{name:'BUC',summary:'BUC (Bottom-Up Computation) computes a data cube from the base cells upward. It aggregates smaller group-bys into larger ones, sharing computations and pruning with an anti-monotone condition.',steps:[{title:'Start at base cells',text:'Begin with the finest group-by (A, B, C) and its aggregated measure.'},{title:'Aggregate upward',text:'Group base cells into (A, B), (A, C), (B, C) by summing their measures.'},{title:'Reach apex',text:'Continue to (A), (B), (C), and finally the grand total (ALL).'},{title:'Share & prune',text:'Reuse ancestor aggregates and skip branches that fall below an interest threshold.'}]},
      'star-cubing':{name:'Star-Cubing',summary:'Star-Cubing is a multiway cube computation that explores shared dimensions simultaneously, using a star-tree to aggregate cells with shared dimension values in one pass.',steps:[{title:'Build star-trees',text:'Build a prefix-tree (star-tree) per dimension from the base table.'},{title:'Multiway aggregation',text:'Traverse shared dimensions together, aggregating cuboids that share dimension values.'},{title:'Shared dimensions',text:'Exploit shared (iceberg) dimensions to reduce the number of passes.'},{title:'Emit cuboids',text:'Produce the required cuboids efficiently by sharing partial aggregates.'}]},
      'frag-shells':{name:'Frag-Shells',summary:'Frag-Shells mines frequent itemsets by partitioning the search into shells of itemsets of fixed size, reducing the candidate space and sharing counts across closely related itemsets.',steps:[{title:'Define shells',text:'Group candidate itemsets into shells by their cardinality (size 1, 2, ...).'},{title:'Scan per shell',text:'Count itemsets within each shell using a single database pass.'},{title:'Prune by support',text:'Drop infrequent itemsets; keep shells whose counts meet minimum support.'},{title:'Combine results',text:'Union the frequent itemsets discovered across all shells.'}]},
      'bagging':{name:'Bagging',summary:'Bagging (Bootstrap Aggregating) builds many models on bootstrap samples drawn with replacement and combines their predictions by majority vote (classification) or averaging (regression).',steps:[{title:'Bootstrap samples',text:'Draw T samples of the same size with replacement from the training set.'},{title:'Train base models',text:'Train one model independently on each bootstrap sample.'},{title:'Aggregate',text:'Combine predictions by majority vote (or average) to reduce variance.'},{title:'Result',text:'The ensemble is more stable and accurate than any single model.'}]},
      'sequential-covering':{name:'Sequential covering',summary:'Sequential covering learns a set of rules one at a time. Each rule is grown to cover many positive examples, those examples are removed, and the process repeats until no positive examples remain.',steps:[{title:'Pick a class',text:'Choose the target class for the next rule.'},{title:'Grow a rule',text:'Add the best attribute-value precondition that improves coverage.'},{title:'Remove covered',text:'Remove the examples satisfied by the new rule.'},{title:'Repeat',text:'Continue until all positive examples of the class are covered.'}]},
      'attribute-oriented':{name:'Attribute-oriented induction',summary:'Attribute-oriented induction summarizes data by climbing concept hierarchies. Low-level values are replaced by higher-level, more general concepts until the data is concise enough to describe.',steps:[{title:'Collect task-relevant data',text:'Fetch the subset of data needed for the generalization.'},{title:'Apply concept hierarchies',text:'Replace specific values (e.g., city) with higher concepts (e.g., province, country).'},{title:'Roll-up / merge',text:'Group tuples with identical generalized descriptions and count them.'},{title:'Present',text:'Show the compact, generalized relation as the mined knowledge.'}]}
    };
    var b=map[id];
    return {name:b.name,summary:b.summary,steps:b.steps,legend:[],render:null};
  }

  var BUILDERS={
    'k-means':buildKMeans,'k-medoids':buildKMedoids,'dbscan':buildDBSCAN,'distance-outlier':buildOutlier,'prob-hierarchical':buildProbHier,
    'decision-tree':buildDecisionTree,'fp-growth':buildFPGrowth,'apriori':buildAprioriStudio,'scan':buildSCAN,'backprop':buildBackprop,'adaboost':buildAdaBoost,
    'buc':function(){return defaultAlgo('buc');},'star-cubing':function(){return defaultAlgo('star-cubing');},'frag-shells':function(){return defaultAlgo('frag-shells');},
    'bagging':function(){return defaultAlgo('bagging');},'sequential-covering':function(){return defaultAlgo('sequential-covering');},'attribute-oriented':function(){return defaultAlgo('attribute-oriented');}
  };
  var ORDER=['k-means','k-medoids','dbscan','distance-outlier','prob-hierarchical','decision-tree','fp-growth','apriori','scan','backprop','adaboost','buc','star-cubing','frag-shells','bagging','sequential-covering','attribute-oriented'];

  function defaultFlow(ctx,steps,idx){
    clr(ctx);
    var n=steps.length;
    var cols=n>6?2:1;
    var rows=Math.ceil(n/cols);
    var x0=40,y0=46,bw=(W-80)/cols-20,bh=Math.min(56,(H-90)/rows-12);
    var boxes=[];
    for(var i=0;i<n;i++){var r=Math.floor(i/cols),c=i%cols;boxes.push({x:x0+c*((W-80)/cols),y:y0+r*((H-80)/rows)});}
    for(var i=0;i<n-1;i++){var a=boxes[i],b=boxes[i+1];if(i%cols<cols-1)arrow(ctx,a.x+bw/2,a.y+bh+3,a.x+bw/2,a.y+bh+((H-80)/rows)-3,'#cbd5e1');else arrow(ctx,a.x+bw/2,a.y+bh+3,a.x+bw/2,a.y+((H-80)/rows),'#cbd5e1');}
    for(var i=0;i<n;i++){var active=i===idx,done=i<idx;rbox(ctx,boxes[i].x,boxes[i].y,bw,bh,(i+1)+'. '+steps[i].title,{active:active,done:done});}
    text(ctx,W/2,H-16,'Algorithm flow diagram: each box is one execution step','#627d98',11);
  }

  var canvas=document.getElementById('dma-canvas');
  if(!canvas)return;
  var ctx=canvas.getContext('2d');
  var select=document.getElementById('dma-select');
  var summary=document.getElementById('dma-summary');
  var status=document.getElementById('dma-status');
  var stepsBox=document.getElementById('dma-steps');
  var legend=document.getElementById('dma-legend');
  var progressBar=document.getElementById('dma-progress-bar');
  var playBtn=document.getElementById('dma-play'),prevBtn=document.getElementById('dma-prev'),nextBtn=document.getElementById('dma-next'),resetBtn=document.getElementById('dma-reset'),speedSel=document.getElementById('dma-speed');
  var current=null,index=0,timer=null;

  ORDER.forEach(function(id){
    var b=document.createElement('button');
    b.type='button';b.className='dma-algo-btn';b.textContent=BUILDERS[id]().name;b.dataset.id=id;
    b.addEventListener('click',function(){selectAlgo(id);});
    select.appendChild(b);
  });

  function selectAlgo(id){
    stopTimer();
    current=BUILDERS[id]();
    index=0;
    summary.textContent=current.summary;
    legend.innerHTML='';
    (current.legend||[]).forEach(function(l){var span=document.createElement('span');var i=document.createElement('i');i.style.background=l.color;span.appendChild(i);span.appendChild(document.createTextNode(' '+l.label));legend.appendChild(span);});
    stepsBox.innerHTML='';
    current.steps.forEach(function(s,i){var li=document.createElement('li');li.innerHTML='<b>'+(i+1)+'. '+s.title+'</b>'+s.text;stepsBox.appendChild(li);});
    select.querySelectorAll('.dma-algo-btn').forEach(function(x){x.classList.toggle('active',x.dataset.id===id);});
    render();
  }

  function render(){
    if(!current)return;
    if(current.render) current.render(ctx,index); else defaultFlow(ctx,current.steps,index);
    var s=current.steps[Math.min(index,current.steps.length-1)];
    status.innerHTML='<strong>'+(index+1)+'. '+s.title+'</strong><br>'+s.text;
    progressBar.style.width=((index+1)*100/current.steps.length)+'%';
    var lis=stepsBox.querySelectorAll('li');
    lis.forEach(function(li,i){li.classList.toggle('active',i===index);li.classList.toggle('done',i<index);});
    if(index>=current.steps.length-1)stopTimer();
  }

  function stopTimer(){clearInterval(timer);timer=null;playBtn.textContent='▶ Play';}
  function startTimer(){stopTimer();playBtn.textContent='❚❚ Pause';timer=setInterval(function(){if(index>=current.steps.length-1){stopTimer();return;}index++;render();},Number(speedSel.value));}
  playBtn.addEventListener('click',function(){if(!current)return;if(timer)stopTimer();else{if(index>=current.steps.length-1)index=0;startTimer();}});
  nextBtn.addEventListener('click',function(){if(!current)return;stopTimer();index=Math.min(current.steps.length-1,index+1);render();});
  prevBtn.addEventListener('click',function(){if(!current)return;stopTimer();index=Math.max(0,index-1);render();});
  resetBtn.addEventListener('click',function(){if(!current)return;stopTimer();index=0;render();});
  speedSel.addEventListener('change',function(){if(timer)startTimer();});

  selectAlgo('k-means');
})();




