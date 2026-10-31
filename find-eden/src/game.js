(function(root){'use strict';
 function isHit(x,y,rect,width,height){
  if(![x,y,width,height].every(Number.isFinite)||x<0||x>1||y<0||y>1||width<=0||height<=0)return false;
  const cx=(rect[0]+rect[2])/2,cy=(rect[1]+rect[3])/2;
  const rx=Math.max((rect[2]-rect[0])/2,22/width),ry=Math.max((rect[3]-rect[1])/2,22/height);
  return Math.abs(x-cx)<=rx&&Math.abs(y-cy)<=ry;
 }
 function freshState(index=0){return {index,found:false,hint:0,choices:false,cursor:{x:.5,y:.5},cursorVisible:false};}
 function dailyIndex(count,date=new Date()){
  if(!Number.isInteger(count)||count<1)throw new RangeError('A garden count is required');
  const days=Math.floor((Date.UTC(date.getFullYear(),date.getMonth(),date.getDate())-Date.UTC(2026,9,31))/86400000);
  return ((days%count)+count)%count;
 }
 function mount(scenes,now=()=>new Date()){
  let state=freshState(),zoom=1;
  const get=id=>document.getElementById(id),sceneBox=get('scene'),picture=get('picture'),ring=get('search-ring'),mark=get('found-ring');
  function message(text){get('feedback').textContent=text;}
  function position(node,x,y){node.style.left=(x*100)+'%';node.style.top=(y*100)+'%';}
  picture.addEventListener('error',()=>{if(!state.found)message('The garden picture could not load. You can still choose a place using the buttons below.');});
  function render(){
   const s=scenes[state.index];picture.src=s.image||s.asset_path||('wallpapers/'+s.file);picture.alt=s.name+', a garden with flowers and butterflies. Eden is hiding somewhere in the picture.';
   picture.width=s.width;picture.height=s.height;
   get('scene-name').textContent=s.name;get('scene-count').textContent='Garden '+(state.index+1)+' of '+scenes.length;
   get('hint-text').textContent=state.hint?s.hint:'';
   get('hint').textContent=state.hint?'Show me where':'Give me a hint';get('hint').disabled=state.found;
   get('next').hidden=!state.found;get('next').textContent=state.index===scenes.length-1?'Play again':'Next garden';
   get('choices').hidden=!state.choices;get('choice-toggle').setAttribute('aria-expanded',String(state.choices));
   mark.hidden=!(state.found||state.hint>=2);position(mark,(s.rect[0]+s.rect[2])/2,(s.rect[1]+s.rect[3])/2);
   mark.style.width=((s.rect[2]-s.rect[0])*100+3)+'%';mark.style.height=((s.rect[3]-s.rect[1])*100+3)+'%';
   ring.hidden=!state.cursorVisible;position(ring,state.cursor.x,state.cursor.y);
   get('choices').replaceChildren(...s.choices.map((label,i)=>{const b=document.createElement('button');b.textContent=label;b.type='button';b.onclick=()=>checkChoice(i);b.disabled=state.found;return b;}));
   get('scene').setAttribute('aria-label',s.name+' search picture');
  }
  function found(){if(state.found)return;state.found=true;message('You found Eden! She was playing hide-and-seek.');render();get('next').focus();}
  function check(x,y){if(state.found)return;const r=sceneBox.getBoundingClientRect();if(isHit(x,y,scenes[state.index].rect,r.width,r.height))found();else message('Keep looking. Eden is hiding somewhere else. There is no hurry.');}
  function checkChoice(index){if(state.found)return;if(index===scenes[state.index].answer)found();else message('Try another place. You can ask for a hint.');}
  sceneBox.addEventListener('click',e=>{const r=sceneBox.getBoundingClientRect();check((e.clientX-r.left)/r.width,(e.clientY-r.top)/r.height);});
  sceneBox.addEventListener('keydown',e=>{
   if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Enter',' '].includes(e.key))return;e.preventDefault();
   if(e.key==='Enter'||e.key===' '){check(state.cursor.x,state.cursor.y);return;}
   state.cursorVisible=true;const delta=e.shiftKey?.01:.025;
   if(e.key==='ArrowLeft')state.cursor.x=Math.max(0,state.cursor.x-delta);
   if(e.key==='ArrowRight')state.cursor.x=Math.min(1,state.cursor.x+delta);
   if(e.key==='ArrowUp')state.cursor.y=Math.max(0,state.cursor.y-delta);
   if(e.key==='ArrowDown')state.cursor.y=Math.min(1,state.cursor.y+delta);
   ring.hidden=false;position(ring,state.cursor.x,state.cursor.y);ring.scrollIntoView({block:'nearest',inline:'nearest'});
  });
  get('hint').onclick=()=>{state.hint=Math.min(2,state.hint+1);render();message(state.hint===1?scenes[state.index].hint:'The white ring shows where Eden is hiding. Tap inside it to find her.');};
  get('choice-toggle').onclick=()=>{state.choices=!state.choices;render();if(state.choices)get('choices').querySelector('button').focus();};
  function changeScene(index){state=freshState(index);zoom=1;get('zoom').value='1';sceneBox.style.width='100%';render();message('Can you find Eden in this garden?');sceneBox.focus();}
  get('next').onclick=()=>changeScene((state.index+1)%scenes.length);
  get('today').onclick=()=>changeScene(dailyIndex(scenes.length,now()));
  get('zoom').onchange=e=>{zoom=Number(e.target.value);sceneBox.style.width=(zoom*100)+'%';};
  get('listen').onclick=()=>{const voices='speechSynthesis'in window?speechSynthesis.getVoices():[];const voice=voices.find(v=>v.localService&&/^en[-_]/i.test(v.lang));if(!voice){message('No local English voice is available. You can use the picture, hints and words.');return;}speechSynthesis.cancel();const u=new SpeechSynthesisUtterance('Find Eden! Look for the blonde-haired girl in the blue dress. '+(state.hint?scenes[state.index].hint:'Tap where you think she is hiding.'));u.voice=voice;u.rate=.85;speechSynthesis.speak(u);};
  get('contrast').onchange=e=>document.body.classList.toggle('contrast',e.target.checked);
  render();message('Look for Eden: blonde hair, a blue dress and a little yellow butterfly clip.');
 }
 const api={isHit,freshState,dailyIndex,mount};if(typeof module!=='undefined')module.exports=api;else root.FindEden=api;
})(globalThis);
