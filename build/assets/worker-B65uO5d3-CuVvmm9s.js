(function(){"use strict";function X(o){return o&&o.__esModule&&Object.prototype.hasOwnProperty.call(o,"default")?o.default:o}var M,$;function Q(){if($)return M;$=1;function o(i){if(typeof i!="string")throw new TypeError("Path must be a string. Received "+JSON.stringify(i))}function c(i,e){for(var t="",s=0,a=-1,d=0,r,l=0;l<=i.length;++l){if(l<i.length)r=i.charCodeAt(l);else{if(r===47)break;r=47}if(r===47){if(!(a===l-1||d===1))if(a!==l-1&&d===2){if(t.length<2||s!==2||t.charCodeAt(t.length-1)!==46||t.charCodeAt(t.length-2)!==46){if(t.length>2){var u=t.lastIndexOf("/");if(u!==t.length-1){u===-1?(t="",s=0):(t=t.slice(0,u),s=t.length-1-t.lastIndexOf("/")),a=l,d=0;continue}}else if(t.length===2||t.length===1){t="",s=0,a=l,d=0;continue}}e&&(t.length>0?t+="/..":t="..",s=2)}else t.length>0?t+="/"+i.slice(a+1,l):t=i.slice(a+1,l),s=l-a-1;a=l,d=0}else r===46&&d!==-1?++d:d=-1}return t}function m(i,e){var t=e.dir||e.root,s=e.base||(e.name||"")+(e.ext||"");return t?t===e.root?t+s:t+i+s:s}var g={resolve:function(){for(var e="",t=!1,s,a=arguments.length-1;a>=-1&&!t;a--){var d;a>=0?d=arguments[a]:(s===void 0&&(s=process.cwd()),d=s),o(d),d.length!==0&&(e=d+"/"+e,t=d.charCodeAt(0)===47)}return e=c(e,!t),t?e.length>0?"/"+e:"/":e.length>0?e:"."},normalize:function(e){if(o(e),e.length===0)return".";var t=e.charCodeAt(0)===47,s=e.charCodeAt(e.length-1)===47;return e=c(e,!t),e.length===0&&!t&&(e="."),e.length>0&&s&&(e+="/"),t?"/"+e:e},isAbsolute:function(e){return o(e),e.length>0&&e.charCodeAt(0)===47},join:function(){if(arguments.length===0)return".";for(var e,t=0;t<arguments.length;++t){var s=arguments[t];o(s),s.length>0&&(e===void 0?e=s:e+="/"+s)}return e===void 0?".":g.normalize(e)},relative:function(e,t){if(o(e),o(t),e===t||(e=g.resolve(e),t=g.resolve(t),e===t))return"";for(var s=1;s<e.length&&e.charCodeAt(s)===47;++s);for(var a=e.length,d=a-s,r=1;r<t.length&&t.charCodeAt(r)===47;++r);for(var l=t.length,u=l-r,k=d<u?d:u,w=-1,_=0;_<=k;++_){if(_===k){if(u>k){if(t.charCodeAt(r+_)===47)return t.slice(r+_+1);if(_===0)return t.slice(r+_)}else d>k&&(e.charCodeAt(s+_)===47?w=_:_===0&&(w=0));break}var P=e.charCodeAt(s+_),C=t.charCodeAt(r+_);if(P!==C)break;P===47&&(w=_)}var b="";for(_=s+w+1;_<=a;++_)(_===a||e.charCodeAt(_)===47)&&(b.length===0?b+="..":b+="/..");return b.length>0?b+t.slice(r+w):(r+=w,t.charCodeAt(r)===47&&++r,t.slice(r))},_makeLong:function(e){return e},dirname:function(e){if(o(e),e.length===0)return".";for(var t=e.charCodeAt(0),s=t===47,a=-1,d=!0,r=e.length-1;r>=1;--r)if(t=e.charCodeAt(r),t===47){if(!d){a=r;break}}else d=!1;return a===-1?s?"/":".":s&&a===1?"//":e.slice(0,a)},basename:function(e,t){if(t!==void 0&&typeof t!="string")throw new TypeError('"ext" argument must be a string');o(e);var s=0,a=-1,d=!0,r;if(t!==void 0&&t.length>0&&t.length<=e.length){if(t.length===e.length&&t===e)return"";var l=t.length-1,u=-1;for(r=e.length-1;r>=0;--r){var k=e.charCodeAt(r);if(k===47){if(!d){s=r+1;break}}else u===-1&&(d=!1,u=r+1),l>=0&&(k===t.charCodeAt(l)?--l===-1&&(a=r):(l=-1,a=u))}return s===a?a=u:a===-1&&(a=e.length),e.slice(s,a)}else{for(r=e.length-1;r>=0;--r)if(e.charCodeAt(r)===47){if(!d){s=r+1;break}}else a===-1&&(d=!1,a=r+1);return a===-1?"":e.slice(s,a)}},extname:function(e){o(e);for(var t=-1,s=0,a=-1,d=!0,r=0,l=e.length-1;l>=0;--l){var u=e.charCodeAt(l);if(u===47){if(!d){s=l+1;break}continue}a===-1&&(d=!1,a=l+1),u===46?t===-1?t=l:r!==1&&(r=1):t!==-1&&(r=-1)}return t===-1||a===-1||r===0||r===1&&t===a-1&&t===s+1?"":e.slice(t,a)},format:function(e){if(e===null||typeof e!="object")throw new TypeError('The "pathObject" argument must be of type Object. Received type '+typeof e);return m("/",e)},parse:function(e){o(e);var t={root:"",dir:"",base:"",ext:"",name:""};if(e.length===0)return t;var s=e.charCodeAt(0),a=s===47,d;a?(t.root="/",d=1):d=0;for(var r=-1,l=0,u=-1,k=!0,w=e.length-1,_=0;w>=d;--w){if(s=e.charCodeAt(w),s===47){if(!k){l=w+1;break}continue}u===-1&&(k=!1,u=w+1),s===46?r===-1?r=w:_!==1&&(_=1):r!==-1&&(_=-1)}return r===-1||u===-1||_===0||_===1&&r===u-1&&r===l+1?u!==-1&&(l===0&&a?t.base=t.name=e.slice(1,u):t.base=t.name=e.slice(l,u)):(l===0&&a?(t.name=e.slice(1,r),t.base=e.slice(1,u)):(t.name=e.slice(l,r),t.base=e.slice(l,u)),t.ext=e.slice(r,u)),l>0?t.dir=e.slice(0,l-1):a&&(t.dir="/"),t},sep:"/",delimiter:":",win32:null,posix:null};return g.posix=g,M=g,M}var V=Q(),E=X(V);const B="/home/pyodide",U=o=>`${B}/${o}`,R=(o,c)=>o==null?E.resolve(B,c):E.resolve(U(o),c);function z(o,c){const m=E.normalize(c),i=E.dirname(m).split(/(?=\/)/);let e="";for(const t of i){e+=t;const s=o.FS.analyzePath(e);if(s.exists&&s.object){if(!o.FS.isDir(s.object.mode))throw new Error(`"${e}" already exists and is not a directory.`);continue}try{o.FS.mkdir(e)}catch(a){throw console.error(`Failed to create a directory "${e}"`),a}}}function H(o,c,m,g){z(o,c),o.FS.writeFile(c,m,g)}function Y(o,c,m){z(o,m),o.FS.rename(c,m)}const Z="[",ee="(<=>!~",te=";",re="@",oe=new RegExp(`[${Z+ee+te+re}]`);function ne(o){return o.split(oe)[0].trim()}function T(o){return o.forEach(m=>{let g;try{g=new URL(m)}catch{return}if(g.protocol==="emfs:"||g.protocol==="file:")throw new Error(`"emfs:" and "file:" protocols are not allowed for the requirement (${m})`)}),o.filter(m=>ne(m)==="streamlit"?(console.warn(`Streamlit is specified in the requirements ("${m}"), but it will be ignored. A built-in version of Streamlit will be used.`),!1):!0)}async function se(o){const c=typeof process<"u"&&process.versions?.node;let m;c?m=(await Promise.resolve().then(function(){return j})).sep:m="/";const g=o.slice(0,o.lastIndexOf(m)+1);if(o.endsWith(".mjs")){if(c){const i=await Promise.resolve().then(function(){return j}),e=await Promise.resolve().then(function(){return j});!o.includes("://")&&i.isAbsolute(o)&&(o=e.pathToFileURL(o).href)}return{scriptURL:o,pyodideIndexURL:g,isESModule:!0}}else return{scriptURL:o,pyodideIndexURL:g,isESModule:!1}}async function ae(o,c){const{scriptURL:m,pyodideIndexURL:g,isESModule:i}=await se(o);let e;return i?e=(await import(m)).loadPyodide:(importScripts(m),e=self.loadPyodide),e({...c,indexURL:g})}function ie(o){o.runPython(`
import micropip
micropip.add_mock_package(
    "pyarrow", "0.0.1",
    modules={
        "pyarrow": """
__version__ = '0.0.1'  # TODO: Update when releasing


class Table:
    @classmethod
    def from_pandas(*args, **kwargs):
        raise NotImplementedError("stlite is not supporting this method.")


class Array:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("stlite is not supporting PyArrow.Array")


class ChunkedArray:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("stlite is not supporting PyArrow.ChunkedArray")
"""
    }
)
`)}function le(o,c,m){const g=o.pyimport("pyodide"),i=r=>g.code.find_imports(r).toJs(),e=m.map(r=>i(r)),a=Array.from(new Set(e.flat())).filter(r=>!o.runPython(`__import__('importlib').util.find_spec('${r}')`)).map(r=>o._api._import_name_to_package_name.get(r)).filter(r=>r);if(a.length===0)return Promise.resolve();const d=o.loadPackage(a);return c(a,d),d.then()}function J(o,c,m){const g=le(o,c,m);o.runPython(`
def __set_module_auto_load_promise__(promise):
    from streamlit.runtime.scriptrunner import script_runner
    script_runner.moduleAutoLoadPromise = promise

__set_module_auto_load_promise__`)(g)}async function ce(o,c,m){const{line:g,column:i}=m,e=o.Script(c);if(g>e._code_lines.length)return[];const t=e.complete.callKwargs({line:g,column:i,fuzzy:!1}),s=[];for(const a of t.toJs())s.push({name:a.name,type:a.$type,docstring:a.docstring.callKwargs({raw:!0}),complete:a.complete}),a.destroy();return s}let O=null,N=Promise.resolve(),D=!1;async function de(o,c,m,g,i){const{files:e,archives:t,requirements:s,prebuiltPackageNames:a,wheels:d,installs:r,pyodideUrl:l=o,streamlitConfig:u,idbfsMountpoints:k,nodefsMountpoints:w,moduleAutoLoad:_,env:P,languageServer:C}=m,b=T(s);O?(i("Pyodide is already loaded."),console.debug("Pyodide is already loaded.")):(i("Loading Pyodide."),console.debug("Loading Pyodide."),O=ae(l,{stdout:console.log,stderr:console.error}),console.debug("Loaded Pyodide"));const n=await O;if(P){console.debug("Setting environment variables",P);const f=n.pyimport("os");f.environ.update(n.toPy(P)),console.debug("Set environment variables",f.environ)}let p=!1;k&&(p=!0,k.forEach(f=>{n.FS.mkdir(f),n.FS.mount(n.FS.filesystems.IDBFS,{},f)}),await new Promise((f,y)=>{n.FS.syncfs(!0,S=>{S?y(S):f()})})),w&&Object.entries(w).forEach(([f,y])=>{n.FS.mkdir(f),n.FS.mount(n.FS.filesystems.NODEFS,{root:y},f)}),i("Mounting files.");const h=[];await Promise.all(Object.keys(e).map(async f=>{const y=e[f];f=R(c,f);let S;"url"in y?(console.debug(`Fetch a file from ${y.url}`),S=await fetch(y.url).then(A=>A.arrayBuffer()).then(A=>new Uint8Array(A))):S=y.data,console.debug(`Write a file "${f}"`),H(n,f,S,e.opts),f.endsWith(".py")&&h.push(f)})),i("Unpacking archives."),await Promise.all(t.map(async f=>{let y;"url"in f?(console.debug(`Fetch an archive from ${f.url}`),y=await fetch(f.url).then(be=>be.arrayBuffer())):y=f.buffer;const{format:S,options:A}=f;console.debug("Unpack an archive",{format:S,options:A}),n.unpackArchive(y,S,A)})),await n.loadPackage("micropip");const v=n.pyimport("micropip");i("Mocking some packages."),console.debug("Mock pyarrow"),ie(n),console.debug("Mocked pyarrow"),i("Installing packages."),console.debug("Installing the prebuilt packages:",a),await n.loadPackage(a),console.debug("Installed the prebuilt packages");const F=async()=>{console.debug("Installing the packages:",{requirements:b,systemPackagesInstalled:D});const f=[];D||(console.debug("System packages will be installed"),d&&(f.push(d.streamlit),f.push(d.stliteLib)),C&&f.push("jedi"));const y=[...f,...b];console.debug("Installing the packages:",y),await v.install.callKwargs(y,{keep_going:!0}),f.length>0&&(console.debug("Installed the system packages"),D=!0),console.debug("Installed the packages")},L=N.then(()=>F());if(N=L.catch(f=>{console.error("Package installation failed:",f)}),await L,r&&(console.debug("Installing the additional requirements"),await Promise.all(r.map(({requirements:f,options:y})=>{const S=T(f);return console.debug("Installing the requirements:",S),v.install.callKwargs(S,y??{})}))),_){const f=h.map(y=>n.FS.readFile(y,{encoding:"utf8"}));J(n,g,f)}await n.runPythonAsync(`
import importlib
importlib.invalidate_caches()
`),i("Loading streamlit package."),console.debug("Loading the Streamlit package"),await n.runPythonAsync(`
import streamlit.runtime
  `),console.debug("Loaded the Streamlit package"),i("Setting up the loggers."),console.debug("Setting the loggers"),await n.runPythonAsync(`
import logging
import streamlit.logger

streamlit.logger.get_logger = logging.getLogger
streamlit.logger.setup_formatter = None
streamlit.logger.update_formatter = lambda *a, **k: None
streamlit.logger.set_log_level = lambda *a, **k: None

for name in streamlit.logger._loggers.keys():
    if name == "root":
        name = "streamlit"
    logger = logging.getLogger(name)
    logger.propagate = True
    logger.handlers.clear()
    logger.setLevel(logging.NOTSET)

streamlit.logger._loggers = {}
`);const I=(f,y)=>{f>=40?console.error(y):f>=30?console.warn(y):f>=20?console.info(y):console.debug(y)},fe=n.runPython(`
def __setup_loggers__(streamlit_level, streamlit_message_format, callback):
    class JsHandler(logging.Handler):
        def emit(self, record):
            msg = self.format(record)
            callback(record.levelno, msg)


    root_message_format = "%(levelname)s:%(name)s:%(message)s"

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_formatter = logging.Formatter(root_message_format)
    root_handler = JsHandler()
    root_handler.setFormatter(root_formatter)
    root_logger.addHandler(root_handler)
    root_logger.setLevel(logging.DEBUG)

    streamlit_logger = logging.getLogger("streamlit")
    streamlit_logger.propagate = False
    streamlit_logger.handlers.clear()
    streamlit_formatter = logging.Formatter(streamlit_message_format)
    streamlit_handler = JsHandler()
    streamlit_handler.setFormatter(streamlit_formatter)
    streamlit_logger.addHandler(streamlit_handler)
    streamlit_logger.setLevel(streamlit_level.upper())

__setup_loggers__`),me=(u?.["logger.level"]??"INFO").toString(),pe=u?.["logger.messageFormat"]??"%(asctime)s %(message)s";if(fe(me,pe,I),console.debug("Set the loggers"),i("Mocking some Streamlit functions for the browser environment."),console.debug("Mocking some Streamlit functions"),await n.runPythonAsync(`
import streamlit

def is_cacheable_msg(msg):
  return False

streamlit.runtime.runtime.is_cacheable_msg = is_cacheable_msg
`),console.debug("Mocked some Streamlit functions"),p){i("Setting up the IndexedDB filesystem synchronizer."),console.debug("Setting up the IndexedDB filesystem synchronizer");let f=!1;const y=()=>{console.debug("The script has finished. Syncing the filesystem."),f||(f=!0,n.FS.syncfs(!1,A=>{f=!1,A&&console.error(A)}))};(await n.runPython(`
def __setup_script_finished_callback__(callback):
    from streamlit.runtime.app_session import AppSession
    from streamlit.runtime.scriptrunner import ScriptRunnerEvent

    def wrap_app_session_on_scriptrunner_event(original_method):
        def wrapped(self, *args, **kwargs):
            if "event" in kwargs:
                event = kwargs["event"]
                if event == ScriptRunnerEvent.SCRIPT_STOPPED_WITH_SUCCESS or event == ScriptRunnerEvent.SCRIPT_STOPPED_FOR_RERUN or event == ScriptRunnerEvent.SHUTDOWN:
                    callback()
            return original_method(self, *args, **kwargs)
        return wrapped

    AppSession._on_scriptrunner_event = wrap_app_session_on_scriptrunner_event(AppSession._on_scriptrunner_event)

__setup_script_finished_callback__`))(y),console.debug("Set up the IndexedDB filesystem synchronizer")}console.debug("Setting up the Streamlit configuration");const{load_config_options:he}=n.pyimport("stlite_lib.bootstrap"),_e={"browser.gatherUsageStats":!1,...u,"runner.fastReruns":!1},ye=c!=null;he(n.toPy(_e),ye),console.debug("Set up the Streamlit configuration");let q;if(C){i("Loading auto-completion engine."),console.debug("Loading Jedi");try{q=await n.pyimport("jedi"),console.debug("Loaded Jedi")}catch(f){console.error("Failed to load Jedi:",f),q=void 0}}return{pyodide:n,micropip:v,jedi:q,initData:m}}async function W(o,c,m){const g=R(c,m);console.debug("Preparing the Streamlit environment");const{prepare:i}=o.pyimport("stlite_lib.bootstrap");i(g,[]),console.debug("Prepared the Streamlit environment"),console.debug("Booting up the Streamlit server");const t=o.pyimport("stlite_lib.server.Server")(g,c?U(c):void 0);return await t.start(),console.debug("Booted up the Streamlit server"),t}function x(o,c,m,g){function i(d){c({type:"event:loadProgress",data:{message:d}})}const e=(d,r)=>{const l=new MessageChannel;c({type:"event:moduleAutoLoad",data:{packagesToLoad:d}},[l.port2]),r.then(u=>{l.port1.postMessage({type:"moduleAutoLoad:success",data:{loadedPackages:u}}),l.port1.close()}).catch(u=>{throw l.port1.postMessage({type:"moduleAutoLoad:error",error:u}),l.port1.close(),u})};let t=null,s=null;const a=async d=>{const r=d.data;if(r.type==="initData"){const n=r.data,p={...m,...n};console.debug("Initial data",p),t=de(o,g,p,e,i),t.then(({pyodide:h})=>(i("Booting up the Streamlit server."),s=W(h,g,p.entrypoint),s)).then(()=>{c({type:"event:loadFinished"})}).catch(h=>{console.error(h),c({type:"event:loadError",data:{error:h}})});return}if(!t)throw new Error("Pyodide initialization has not been started yet.");if(!s)throw new Error("Streamlit server has not been started yet.");const l=await t,u=l.pyodide,k=l.micropip,w=l.jedi,{moduleAutoLoad:_}=l.initData,P=await s,C=d.ports[0];function b(n){C.postMessage(n)}try{switch(r.type){case"reboot":{console.debug("Reboot the Streamlit server",r.data);const{entrypoint:n}=r.data;P.stop(),console.debug("Booting up the Streamlit server"),s=W(u,g,n),await s,console.debug("Booted up the Streamlit server"),b({type:"reply"});break}case"websocket:connect":{console.debug("websocket:connect",r.data);const{path:n}=r.data;P.start_websocket(n,(p,h)=>{if(h){const v=p;try{const F=v.toJs(),L=F.buffer.slice(F.byteOffset,F.byteOffset+F.byteLength);c({type:"websocket:message",data:{payload:L}},[L])}finally{v.destroy()}}else c({type:"websocket:message",data:{payload:p}})}),b({type:"reply"});break}case"websocket:send":{console.debug("websocket:send",r.data);const{payload:n}=r.data;P.receive_websocket_from_js(n);break}case"http:request":{console.debug("http:request",r.data);const{request:n}=r.data,p=(h,v,F)=>{const L=new Map(v.toJs()),I=F.toJs();console.debug({statusCode:h,headers:L,body:I}),b({type:"http:response",data:{response:{statusCode:h,headers:L,body:I}}})};P.receive_http_from_js(n.method,decodeURIComponent(n.path),n.headers,n.body,p);break}case"file:write":{const{path:n,data:p,opts:h}=r.data,v=R(g,n);_&&typeof p=="string"&&v.endsWith(".py")&&(console.debug(`Auto install the requirements in ${v}`),J(u,e,[p])),console.debug(`Write a file "${v}"`),H(u,v,p,h),b({type:"reply"});break}case"file:rename":{const{oldPath:n,newPath:p}=r.data,h=R(g,n),v=R(g,p);console.debug(`Rename "${h}" to ${v}`),Y(u,h,v),b({type:"reply"});break}case"file:unlink":{const{path:n}=r.data,p=R(g,n);console.debug(`Remove "${p}`),u.FS.unlink(p),b({type:"reply"});break}case"file:read":{const{path:n,opts:p}=r.data;console.debug(`Read "${n}"`);const h=u.FS.readFile(n,p);b({type:"reply:file:read",data:{content:h}});break}case"install":{const{requirements:n,options:p}=r.data,h=T(n);console.debug("Install the requirements:",h),await k.install.callKwargs(h,p??{}).then(()=>{console.debug("Successfully installed"),b({type:"reply"})});break}case"setEnv":{const{env:n}=r.data;u.pyimport("os").environ.update(u.toPy(n)),console.debug("Successfully set the environment variables",n),b({type:"reply"});break}case"code_completion":{if(!w)throw new Error("Jedi is not installed");const{code:n,line:p,column:h}=r.data,v=await ce(w,n,{line:p,column:h});b({type:"reply:code_completion",data:{codeCompletions:v}});break}case"run_python":{const{code:n}=r.data;console.debug("Run python code",n);const p=await u.runPythonAsync(n);let h;p instanceof u.ffi.PyProxy?(console.debug("The result is a PyProxy object"),h=p.toJs(),p.destroy(),console.debug("Converted the result to a JS object",h)):(h=p,console.debug("The result is a JS primitive",h)),b({type:"reply:run_python",data:{result:h}});break}case"add_mock_package":{const{name:n,version:p,modules:h,persistent:v}=r.data;console.debug("Add a mock package:",{name:n,version:p,modules:h,persistent:v}),k.add_mock_package.callKwargs({name:n,version:p,modules:u.toPy(h),persistent:v}),b({type:"reply"});break}}}catch(n){if(console.error(n),!(n instanceof Error))throw n;const p=new Error(n.message);p.name=n.name,p.stack=n.stack,b({type:"reply",error:p})}};return c({type:"event:envSetup"}),a}const K="abcdefghijklmnopqrstuvwxyz",ue=K.length;function ge(o){let c="";for(let m=0;m<o;m++){const g=Math.floor(Math.random()*ue);c+=K[g]}return c}const G="https://cdn.jsdelivr.net/pyodide/v0.28.2/full/pyodide.mjs";if("postMessage"in self)self.onmessage=x(G,(o,c)=>c?self.postMessage(o,c):self.postMessage(o));else{const o=[];self.onconnect=c=>{let m;do m=ge(4);while(o.includes(m));o.push(m),console.debug("SharedWorker mode.",{appId:m});const g=c.ports[0];g.onmessage=x(G,(i,e)=>e?g.postMessage(i,e):g.postMessage(i),void 0,m),g.start()}}var j=Object.freeze({__proto__:null})})();
//# sourceMappingURL=worker-B65uO5d3.js.map
