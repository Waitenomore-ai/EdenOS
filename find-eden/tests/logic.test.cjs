const {test}=require('node:test'),assert=require('node:assert/strict');
let game;try{game=require('../src/game.js')}catch{game={}}
const rect=[.63,.36,.68,.51];
test('finds visible character without accepting the rest of the scene',()=>{
 assert.equal(game.isHit(.65,.4,rect,1000,563),true);
 assert.equal(game.isHit(.1,.1,rect,1000,563),false);
 assert.equal(game.isHit(.635,.36,rect,1000,563),true);
});
test('small screens give the character a minimum 44 pixel target',()=>{
 assert.equal(game.isHit(.61,.4,rect,200,112),true);
 assert.equal(game.isHit(.9,.4,rect,200,112),false);
});
test('invalid and off-image clicks cannot find Eden',()=>{
 for(const [x,y,w,h]of [[NaN,.4,1000,563],[Infinity,.4,1000,563],[-.1,.4,1000,563],[.65,1.1,1000,563],[.65,.4,0,563]])assert.equal(game.isHit(x,y,rect,w,h),false);
});
test('new scenes start without revealing or remembering previous answers',()=>{
 const a=game.freshState(1);a.found=true;a.hint=2;
 const b=game.freshState(2);assert.deepEqual(b,{index:2,found:false,hint:0,choices:false,cursor:{x:.5,y:.5},cursorVisible:false});
});

test('daily garden uses local calendar dates with wrap and no time-of-day drift',()=>{
 for(const [date,expected] of [[new Date(2026,9,31,23,59),0],[new Date(2026,10,1),1],[new Date(2026,10,27),27],[new Date(2026,10,28),0],[new Date(2026,9,30),27]])assert.equal(game.dailyIndex(28,date),expected);
 // Stub getters deliberately disagree with the underlying timestamp, testing local date extraction.
 assert.equal(game.dailyIndex(28,{getFullYear:()=>2026,getMonth:()=>10,getDate:()=>2}),2);
 assert.throws(()=>game.dailyIndex(0),RangeError);
});
