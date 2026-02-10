import{j as c,bN as d,c as g,k as h,bO as p}from"./index-BIyIgwS4.js";const x=h`
  50% {
    color: rgba(0, 0, 0, 0);
  }
`,y=g("span",{target:"edlqvik0"})(({includeDot:e,shouldBlink:n,theme:t})=>({...e?{"&::before":{opacity:1,content:'"•"',animation:"none",color:t.colors.grayTextColor,margin:`0 ${t.spacing.twoXS}`}}:{},...n?{color:t.colors.redTextColor,animationName:`${x}`,animationDuration:"0.5s",animationIterationCount:5}:{}}),""),b=({dirty:e,value:n,inForm:t,maxLength:a,className:m,type:r="single",allowEnterToSubmit:u=!0})=>{const o=[],i=(s,l=!1)=>{o.push(c.jsx(y,{includeDot:o.length>0,shouldBlink:l,children:s},o.length))};if(u){const s=t?"submit form":"apply";if(r==="multiline"){const l=p()?"⌘":"Ctrl";i(`Press ${l}+Enter to ${s}`)}else r==="single"&&i(`Press Enter to ${s}`)}return a&&(r!=="chat"||e)&&i(`${n.length}/${a}`,e&&n.length>=a),c.jsx(d,{"data-testid":"InputInstructions",className:m,children:o})};export{b as e};
