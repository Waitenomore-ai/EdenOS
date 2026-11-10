"use strict";
const {app,BrowserWindow,shell,Menu,session}=require("electron");
const path=require("path");
const HOME="https://www.edensgarden.uk/app/unified/";
let mainWindow=null;
function allowedAppUrl(value){
 try{const u=new URL(value);return u.protocol==="https:"&&u.hostname==="www.edensgarden.uk"&&u.pathname.startsWith("/app/unified/")}
 catch{return false}
}
function openExternal(value){
 try{const u=new URL(value);if(u.protocol==="https:"||u.protocol==="http:")shell.openExternal(u.href).catch(()=>{})}
 catch{}
}
function createWindow(){
 const win=new BrowserWindow({
  width:1280,height:820,minWidth:720,minHeight:550,
  title:"Eden's Garden",
  backgroundColor:"#f4f9ed",
  icon:path.join(__dirname,"build","icon.png"),
  show:false,
  webPreferences:{
   nodeIntegration:false,
   contextIsolation:true,
   sandbox:true,
   webSecurity:true,
   devTools:false
  }
 });
 mainWindow=win;
 const contents=win.webContents;
 contents.setWindowOpenHandler(({url})=>{if(!allowedAppUrl(url))openExternal(url);return {action:"deny"}});
 contents.on("will-navigate",(event,url)=>{if(!allowedAppUrl(url)){event.preventDefault();openExternal(url)}});
 contents.on("did-fail-load",(_event,code,_desc,url,isMainFrame)=>{
  if(!isMainFrame||code===-3)return;
  if(!allowedAppUrl(url))return;
  win.loadFile(path.join(__dirname,"offline.html")).catch(()=>{});
 });
 win.once("ready-to-show",()=>win.show());
 win.loadURL(HOME).catch(()=>win.loadFile(path.join(__dirname,"offline.html")));
 win.on("closed",()=>{if(mainWindow===win)mainWindow=null});
}
app.whenReady().then(()=>{
 // No background network permissions, microphone, location or notifications.
 const activeSession=session.defaultSession;
 activeSession.setPermissionRequestHandler((_webContents,_permission,callback)=>callback(false));
 const menu=Menu.buildFromTemplate([
  {label:"Eden's Garden",submenu:[{label:"Home",click:()=>mainWindow?.loadURL(HOME)},{label:"Reload",role:"reload"},{type:"separator"},{role:"quit"}]},
  {label:"View",submenu:[{role:"zoomIn"},{role:"zoomOut"},{role:"resetZoom"},{role:"togglefullscreen"}]}
 ]);
 Menu.setApplicationMenu(menu);
 createWindow();
 app.on("activate",()=>{if(BrowserWindow.getAllWindows().length===0)createWindow()});
});
app.on("window-all-closed",()=>{if(process.platform!=="darwin")app.quit()});
