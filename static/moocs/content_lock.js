/* Discourage copying examination content with ordinary mouse and keyboard actions. */
(function(){
  const stop=event=>{
    event.preventDefault();
    event.stopPropagation();
  };

  ['copy','cut','contextmenu','dragstart','selectstart'].forEach(type=>{
    document.addEventListener(type,stop,{capture:true});
  });

  document.addEventListener('keydown',event=>{
    const modifier=event.ctrlKey||event.metaKey;
    const blocked=modifier&&['a','c','x','s','p','u'].includes(event.key.toLocaleLowerCase());
    if(blocked||event.key==='PrintScreen')stop(event);
  },{capture:true});
})();
