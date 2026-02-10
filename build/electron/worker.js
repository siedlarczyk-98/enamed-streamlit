var de=Object.create;var J=Object.defineProperty;var ue=Object.getOwnPropertyDescriptor;var ge=Object.getOwnPropertyNames;var me=Object.getPrototypeOf,fe=Object.prototype.hasOwnProperty;var pe=(r,e)=>()=>(e||r((e={exports:{}}).exports,e),e.exports);var he=(r,e,t,o)=>{if(e&&typeof e=="object"||typeof e=="function")for(let n of ge(e))!fe.call(r,n)&&n!==t&&J(r,n,{get:()=>e[n],enumerable:!(o=ue(e,n))||o.enumerable});return r};var I=(r,e,t)=>(t=r!=null?de(me(r)):{},he(e||!r||!r.__esModule?J(t,"default",{value:r,enumerable:!0}):t,r));var B=pe((Re,z)=>{"use strict";function w(r){if(typeof r!="string")throw new TypeError("Path must be a string. Received "+JSON.stringify(r))}function W(r,e){for(var t="",o=0,n=-1,i=0,a,l=0;l<=r.length;++l){if(l<r.length)a=r.charCodeAt(l);else{if(a===47)break;a=47}if(a===47){if(!(n===l-1||i===1))if(n!==l-1&&i===2){if(t.length<2||o!==2||t.charCodeAt(t.length-1)!==46||t.charCodeAt(t.length-2)!==46){if(t.length>2){var u=t.lastIndexOf("/");if(u!==t.length-1){u===-1?(t="",o=0):(t=t.slice(0,u),o=t.length-1-t.lastIndexOf("/")),n=l,i=0;continue}}else if(t.length===2||t.length===1){t="",o=0,n=l,i=0;continue}}e&&(t.length>0?t+="/..":t="..",o=2)}else t.length>0?t+="/"+r.slice(n+1,l):t=r.slice(n+1,l),o=l-n-1;n=l,i=0}else a===46&&i!==-1?++i:i=-1}return t}function _e(r,e){var t=e.dir||e.root,o=e.base||(e.name||"")+(e.ext||"");return t?t===e.root?t+o:t+r+o:o}var L={resolve:function(){for(var e="",t=!1,o,n=arguments.length-1;n>=-1&&!t;n--){var i;n>=0?i=arguments[n]:(o===void 0&&(o=process.cwd()),i=o),w(i),i.length!==0&&(e=i+"/"+e,t=i.charCodeAt(0)===47)}return e=W(e,!t),t?e.length>0?"/"+e:"/":e.length>0?e:"."},normalize:function(e){if(w(e),e.length===0)return".";var t=e.charCodeAt(0)===47,o=e.charCodeAt(e.length-1)===47;return e=W(e,!t),e.length===0&&!t&&(e="."),e.length>0&&o&&(e+="/"),t?"/"+e:e},isAbsolute:function(e){return w(e),e.length>0&&e.charCodeAt(0)===47},join:function(){if(arguments.length===0)return".";for(var e,t=0;t<arguments.length;++t){var o=arguments[t];w(o),o.length>0&&(e===void 0?e=o:e+="/"+o)}return e===void 0?".":L.normalize(e)},relative:function(e,t){if(w(e),w(t),e===t||(e=L.resolve(e),t=L.resolve(t),e===t))return"";for(var o=1;o<e.length&&e.charCodeAt(o)===47;++o);for(var n=e.length,i=n-o,a=1;a<t.length&&t.charCodeAt(a)===47;++a);for(var l=t.length,u=l-a,h=i<u?i:u,c=-1,m=0;m<=h;++m){if(m===h){if(u>h){if(t.charCodeAt(a+m)===47)return t.slice(a+m+1);if(m===0)return t.slice(a+m)}else i>h&&(e.charCodeAt(o+m)===47?c=m:m===0&&(c=0));break}var _=e.charCodeAt(o+m),R=t.charCodeAt(a+m);if(_!==R)break;_===47&&(c=m)}var S="";for(m=o+c+1;m<=n;++m)(m===n||e.charCodeAt(m)===47)&&(S.length===0?S+="..":S+="/..");return S.length>0?S+t.slice(a+c):(a+=c,t.charCodeAt(a)===47&&++a,t.slice(a))},_makeLong:function(e){return e},dirname:function(e){if(w(e),e.length===0)return".";for(var t=e.charCodeAt(0),o=t===47,n=-1,i=!0,a=e.length-1;a>=1;--a)if(t=e.charCodeAt(a),t===47){if(!i){n=a;break}}else i=!1;return n===-1?o?"/":".":o&&n===1?"//":e.slice(0,n)},basename:function(e,t){if(t!==void 0&&typeof t!="string")throw new TypeError('"ext" argument must be a string');w(e);var o=0,n=-1,i=!0,a;if(t!==void 0&&t.length>0&&t.length<=e.length){if(t.length===e.length&&t===e)return"";var l=t.length-1,u=-1;for(a=e.length-1;a>=0;--a){var h=e.charCodeAt(a);if(h===47){if(!i){o=a+1;break}}else u===-1&&(i=!1,u=a+1),l>=0&&(h===t.charCodeAt(l)?--l===-1&&(n=a):(l=-1,n=u))}return o===n?n=u:n===-1&&(n=e.length),e.slice(o,n)}else{for(a=e.length-1;a>=0;--a)if(e.charCodeAt(a)===47){if(!i){o=a+1;break}}else n===-1&&(i=!1,n=a+1);return n===-1?"":e.slice(o,n)}},extname:function(e){w(e);for(var t=-1,o=0,n=-1,i=!0,a=0,l=e.length-1;l>=0;--l){var u=e.charCodeAt(l);if(u===47){if(!i){o=l+1;break}continue}n===-1&&(i=!1,n=l+1),u===46?t===-1?t=l:a!==1&&(a=1):t!==-1&&(a=-1)}return t===-1||n===-1||a===0||a===1&&t===n-1&&t===o+1?"":e.slice(t,n)},format:function(e){if(e===null||typeof e!="object")throw new TypeError('The "pathObject" argument must be of type Object. Received type '+typeof e);return _e("/",e)},parse:function(e){w(e);var t={root:"",dir:"",base:"",ext:"",name:""};if(e.length===0)return t;var o=e.charCodeAt(0),n=o===47,i;n?(t.root="/",i=1):i=0;for(var a=-1,l=0,u=-1,h=!0,c=e.length-1,m=0;c>=i;--c){if(o=e.charCodeAt(c),o===47){if(!h){l=c+1;break}continue}u===-1&&(h=!1,u=c+1),o===46?a===-1?a=c:m!==1&&(m=1):a!==-1&&(m=-1)}return a===-1||u===-1||m===0||m===1&&a===u-1&&a===l+1?u!==-1&&(l===0&&n?t.base=t.name=e.slice(1,u):t.base=t.name=e.slice(l,u)):(l===0&&n?(t.name=e.slice(1,a),t.base=e.slice(1,u)):(t.name=e.slice(l,a),t.base=e.slice(l,u)),t.ext=e.slice(a,u)),l>0?t.dir=e.slice(0,l-1):n&&(t.dir="/"),t},sep:"/",delimiter:":",win32:null,posix:null};L.posix=L;z.exports=L});var q=require("node:worker_threads");var C=I(B(),1),K="/home/pyodide",x=r=>`${K}/${r}`,E=(r,e)=>r==null?C.default.resolve(K,e):C.default.resolve(x(r),e);function X(r,e){let t=C.default.normalize(e),n=C.default.dirname(t).split(/(?=\/)/),i="";for(let a of n){i+=a;let l=r.FS.analyzePath(i);if(l.exists&&l.object){if(!r.FS.isDir(l.object.mode))throw new Error(`"${i}" already exists and is not a directory.`);continue}try{r.FS.mkdir(i)}catch(u){throw console.error(`Failed to create a directory "${i}"`),u}}}function U(r,e,t,o){X(r,e),r.FS.writeFile(e,t,o)}function G(r,e,t){X(r,t),r.FS.rename(e,t)}var ye="(<=>!~";var be=new RegExp(`[${"["+ye+";@"}]`);function ve(r){return r.split(be)[0].trim()}function M(r){return r.forEach(t=>{let o;try{o=new URL(t)}catch{return}if(o.protocol==="emfs:"||o.protocol==="file:")throw new Error(`"emfs:" and "file:" protocols are not allowed for the requirement (${t})`)}),r.filter(t=>ve(t)==="streamlit"?(console.warn(`Streamlit is specified in the requirements ("${t}"), but it will be ignored. A built-in version of Streamlit will be used.`),!1):!0)}async function Se(r){let e=typeof process<"u"&&process.versions?.node,t;e?t=(await import("node:path")).sep:t="/";let o=r.slice(0,r.lastIndexOf(t)+1);if(r.endsWith(".mjs")){if(e){let n=await import("node:path"),i=await import("node:url");!r.includes("://")&&n.isAbsolute(r)&&(r=i.pathToFileURL(r).href)}return{scriptURL:r,pyodideIndexURL:o,isESModule:!0}}else return{scriptURL:r,pyodideIndexURL:o,isESModule:!1}}async function Q(r,e){let{scriptURL:t,pyodideIndexURL:o,isESModule:n}=await Se(r),i;return n?i=(await import(t)).loadPyodide:(importScripts(t),i=self.loadPyodide),i({...e,indexURL:o})}function V(r){r.runPython(`
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
`)}function we(r,e,t){let o=r.pyimport("pyodide"),n=c=>o.code.find_imports(c).toJs(),i=t.map(c=>n(c)),u=Array.from(new Set(i.flat())).filter(c=>!r.runPython(`__import__('importlib').util.find_spec('${c}')`)).map(c=>r._api._import_name_to_package_name.get(c)).filter(c=>c);if(u.length===0)return Promise.resolve();let h=r.loadPackage(u);return e(u,h),h.then()}function $(r,e,t){let o=we(r,e,t);r.runPython(`
def __set_module_auto_load_promise__(promise):
    from streamlit.runtime.scriptrunner import script_runner
    script_runner.moduleAutoLoadPromise = promise

__set_module_auto_load_promise__`)(o)}async function Y(r,e,t){let{line:o,column:n}=t,i=r.Script(e);if(o>i._code_lines.length)return[];let a=i.complete.callKwargs({line:o,column:n,fuzzy:!1}),l=[];for(let u of a.toJs())l.push({name:u.name,type:u.$type,docstring:u.docstring.callKwargs({raw:!0}),complete:u.complete}),u.destroy();return l}var j=null,Z=Promise.resolve(),H=!1;async function ke(r,e,t,o,n){let{files:i,archives:a,requirements:l,prebuiltPackageNames:u,wheels:h,installs:c,pyodideUrl:m=r,streamlitConfig:_,idbfsMountpoints:R,nodefsMountpoints:S,moduleAutoLoad:N,env:P,languageServer:O}=t,b=M(l);j?(n("Pyodide is already loaded."),console.debug("Pyodide is already loaded.")):(n("Loading Pyodide."),console.debug("Loading Pyodide."),j=Q(m,{stdout:console.log,stderr:console.error}),console.debug("Loaded Pyodide"));let s=await j;if(P){console.debug("Setting environment variables",P);let d=s.pyimport("os");d.environ.update(s.toPy(P)),console.debug("Set environment variables",d.environ)}let g=!1;R&&(g=!0,R.forEach(d=>{s.FS.mkdir(d),s.FS.mount(s.FS.filesystems.IDBFS,{},d)}),await new Promise((d,p)=>{s.FS.syncfs(!0,v=>{v?p(v):d()})})),S&&Object.entries(S).forEach(([d,p])=>{s.FS.mkdir(d),s.FS.mount(s.FS.filesystems.NODEFS,{root:p},d)}),n("Mounting files.");let f=[];await Promise.all(Object.keys(i).map(async d=>{let p=i[d];d=E(e,d);let v;"url"in p?(console.debug(`Fetch a file from ${p.url}`),v=await fetch(p.url).then(k=>k.arrayBuffer()).then(k=>new Uint8Array(k))):v=p.data,console.debug(`Write a file "${d}"`),U(s,d,v,i.opts),d.endsWith(".py")&&f.push(d)})),n("Unpacking archives."),await Promise.all(a.map(async d=>{let p;"url"in d?(console.debug(`Fetch an archive from ${d.url}`),p=await fetch(d.url).then(ce=>ce.arrayBuffer())):p=d.buffer;let{format:v,options:k}=d;console.debug("Unpack an archive",{format:v,options:k}),s.unpackArchive(p,v,k)})),await s.loadPackage("micropip");let y=s.pyimport("micropip");n("Mocking some packages."),console.debug("Mock pyarrow"),V(s),console.debug("Mocked pyarrow"),n("Installing packages."),console.debug("Installing the prebuilt packages:",u),await s.loadPackage(u),console.debug("Installed the prebuilt packages");let A=async()=>{console.debug("Installing the packages:",{requirements:b,systemPackagesInstalled:H});let d=[];H||(console.debug("System packages will be installed"),h&&(d.push(h.streamlit),d.push(h.stliteLib)),O&&d.push("jedi"));let p=[...d,...b];console.debug("Installing the packages:",p),await y.install.callKwargs(p,{keep_going:!0}),d.length>0&&(console.debug("Installed the system packages"),H=!0),console.debug("Installed the packages")},F=Z.then(()=>A());if(Z=F.catch(d=>{console.error("Package installation failed:",d)}),await F,c&&(console.debug("Installing the additional requirements"),await Promise.all(c.map(({requirements:d,options:p})=>{let v=M(d);return console.debug("Installing the requirements:",v),y.install.callKwargs(v,p??{})}))),N){let d=f.map(p=>s.FS.readFile(p,{encoding:"utf8"}));$(s,o,d)}await s.runPythonAsync(`
import importlib
importlib.invalidate_caches()
`),n("Loading streamlit package."),console.debug("Loading the Streamlit package"),await s.runPythonAsync(`
import streamlit.runtime
  `),console.debug("Loaded the Streamlit package"),n("Setting up the loggers."),console.debug("Setting the loggers"),await s.runPythonAsync(`
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
`);let T=(d,p)=>{d>=40?console.error(p):d>=30?console.warn(p):d>=20?console.info(p):console.debug(p)},oe=s.runPython(`
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

__setup_loggers__`),ne=(_?.["logger.level"]??"INFO").toString(),se=_?.["logger.messageFormat"]??"%(asctime)s %(message)s";if(oe(ne,se,T),console.debug("Set the loggers"),n("Mocking some Streamlit functions for the browser environment."),console.debug("Mocking some Streamlit functions"),await s.runPythonAsync(`
import streamlit

def is_cacheable_msg(msg):
  return False

streamlit.runtime.runtime.is_cacheable_msg = is_cacheable_msg
`),console.debug("Mocked some Streamlit functions"),g){n("Setting up the IndexedDB filesystem synchronizer."),console.debug("Setting up the IndexedDB filesystem synchronizer");let d=!1,p=()=>{console.debug("The script has finished. Syncing the filesystem."),d||(d=!0,s.FS.syncfs(!1,k=>{d=!1,k&&console.error(k)}))};(await s.runPython(`
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

__setup_script_finished_callback__`))(p),console.debug("Set up the IndexedDB filesystem synchronizer")}console.debug("Setting up the Streamlit configuration");let{load_config_options:ae}=s.pyimport("stlite_lib.bootstrap"),ie={"browser.gatherUsageStats":!1,..._,"runner.fastReruns":!1},le=e!=null;ae(s.toPy(ie),le),console.debug("Set up the Streamlit configuration");let D;if(O){n("Loading auto-completion engine."),console.debug("Loading Jedi");try{D=await s.pyimport("jedi"),console.debug("Loaded Jedi")}catch(d){console.error("Failed to load Jedi:",d),D=void 0}}return{pyodide:s,micropip:y,jedi:D,initData:t}}async function ee(r,e,t){let o=E(e,t);console.debug("Preparing the Streamlit environment");let{prepare:n}=r.pyimport("stlite_lib.bootstrap");n(o,[]),console.debug("Prepared the Streamlit environment"),console.debug("Booting up the Streamlit server");let a=r.pyimport("stlite_lib.server.Server")(o,e?x(e):void 0);return await a.start(),console.debug("Booted up the Streamlit server"),a}function te(r,e,t,o){function n(h){e({type:"event:loadProgress",data:{message:h}})}let i=(h,c)=>{let m=new MessageChannel;e({type:"event:moduleAutoLoad",data:{packagesToLoad:h}},[m.port2]),c.then(_=>{m.port1.postMessage({type:"moduleAutoLoad:success",data:{loadedPackages:_}}),m.port1.close()}).catch(_=>{throw m.port1.postMessage({type:"moduleAutoLoad:error",error:_}),m.port1.close(),_})},a=null,l=null,u=async h=>{let c=h.data;if(c.type==="initData"){let s=c.data,g={...t,...s};console.debug("Initial data",g),a=ke(r,o,g,i,n),a.then(({pyodide:f})=>(n("Booting up the Streamlit server."),l=ee(f,o,g.entrypoint),l)).then(()=>{e({type:"event:loadFinished"})}).catch(f=>{console.error(f),e({type:"event:loadError",data:{error:f}})});return}if(!a)throw new Error("Pyodide initialization has not been started yet.");if(!l)throw new Error("Streamlit server has not been started yet.");let m=await a,_=m.pyodide,R=m.micropip,S=m.jedi,{moduleAutoLoad:N}=m.initData,P=await l,O=h.ports[0];function b(s){O.postMessage(s)}try{switch(c.type){case"reboot":{console.debug("Reboot the Streamlit server",c.data);let{entrypoint:s}=c.data;P.stop(),console.debug("Booting up the Streamlit server"),l=ee(_,o,s),await l,console.debug("Booted up the Streamlit server"),b({type:"reply"});break}case"websocket:connect":{console.debug("websocket:connect",c.data);let{path:s}=c.data;P.start_websocket(s,(g,f)=>{if(f){let y=g;try{let A=y.toJs(),F=A.buffer.slice(A.byteOffset,A.byteOffset+A.byteLength);e({type:"websocket:message",data:{payload:F}},[F])}finally{y.destroy()}}else e({type:"websocket:message",data:{payload:g}})}),b({type:"reply"});break}case"websocket:send":{console.debug("websocket:send",c.data);let{payload:s}=c.data;P.receive_websocket_from_js(s);break}case"http:request":{console.debug("http:request",c.data);let{request:s}=c.data,g=(f,y,A)=>{let F=new Map(y.toJs()),T=A.toJs();console.debug({statusCode:f,headers:F,body:T}),b({type:"http:response",data:{response:{statusCode:f,headers:F,body:T}}})};P.receive_http_from_js(s.method,decodeURIComponent(s.path),s.headers,s.body,g);break}case"file:write":{let{path:s,data:g,opts:f}=c.data,y=E(o,s);N&&typeof g=="string"&&y.endsWith(".py")&&(console.debug(`Auto install the requirements in ${y}`),$(_,i,[g])),console.debug(`Write a file "${y}"`),U(_,y,g,f),b({type:"reply"});break}case"file:rename":{let{oldPath:s,newPath:g}=c.data,f=E(o,s),y=E(o,g);console.debug(`Rename "${f}" to ${y}`),G(_,f,y),b({type:"reply"});break}case"file:unlink":{let{path:s}=c.data,g=E(o,s);console.debug(`Remove "${g}`),_.FS.unlink(g),b({type:"reply"});break}case"file:read":{let{path:s,opts:g}=c.data;console.debug(`Read "${s}"`);let f=_.FS.readFile(s,g);b({type:"reply:file:read",data:{content:f}});break}case"install":{let{requirements:s,options:g}=c.data,f=M(s);console.debug("Install the requirements:",f),await R.install.callKwargs(f,g??{}).then(()=>{console.debug("Successfully installed"),b({type:"reply"})});break}case"setEnv":{let{env:s}=c.data;_.pyimport("os").environ.update(_.toPy(s)),console.debug("Successfully set the environment variables",s),b({type:"reply"});break}case"code_completion":{if(!S)throw new Error("Jedi is not installed");let{code:s,line:g,column:f}=c.data,y=await Y(S,s,{line:g,column:f});b({type:"reply:code_completion",data:{codeCompletions:y}});break}case"run_python":{let{code:s}=c.data;console.debug("Run python code",s);let g=await _.runPythonAsync(s),f;g instanceof _.ffi.PyProxy?(console.debug("The result is a PyProxy object"),f=g.toJs(),g.destroy(),console.debug("Converted the result to a JS object",f)):(f=g,console.debug("The result is a JS primitive",f)),b({type:"reply:run_python",data:{result:f}});break}case"add_mock_package":{let{name:s,version:g,modules:f,persistent:y}=c.data;console.debug("Add a mock package:",{name:s,version:g,modules:f,persistent:y}),R.add_mock_package.callKwargs({name:s,version:g,modules:_.toPy(f),persistent:y}),b({type:"reply"});break}}}catch(s){if(console.error(s),!(s instanceof Error))throw s;let g=new Error(s.message);g.name=s.name,g.stack=s.stack,b({type:"reply",error:g})}};return e({type:"event:envSetup"}),u}function re(){let r=process.env.NODEFS_MOUNTPOINTS;if(!r)return;let e;try{e=JSON.parse(r)}catch{console.error(`Failed to parse NODEFS_MOUNTPOINTS as JSON: ${r}`);return}if(typeof e!="object"){console.error(`NODEFS_MOUNTPOINTS is not an object: ${r}`);return}if(Array.isArray(e)){console.error(`NODEFS_MOUNTPOINTS is an array: ${r}`);return}if(Object.keys(e).some(t=>typeof t!="string")){console.error(`NODEFS_MOUNTPOINTS has non-string keys: ${r}`);return}if(Object.values(e).some(t=>typeof t!="string")){console.error(`NODEFS_MOUNTPOINTS has non-string values: ${r}`);return}return e}var Pe=r=>{console.debug("[worker thread] postMessage from worker",r),q.parentPort?.postMessage(r)},Ae=te(process.env.PYODIDE_URL,Pe,{nodefsMountpoints:re()});q.parentPort?.on("message",({data:r,port:e})=>{console.debug("[worker thread] parentPort.onMessage",{data:r,port:e}),Ae({data:r,ports:[e]})});
