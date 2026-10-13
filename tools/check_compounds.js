#!/usr/bin/env node
// Run the site's own decoder (from index.html) over tests/compounds.txt and fail on any miss.
// Also proves the schedule parser covers every generated dosing compound even without its
// dictionary entry, so a new frequency/timing combination cannot fall through again.
// Usage: node tools/check_compounds.js
const fs=require("fs"),path=require("path"),root=path.resolve(__dirname,"..");
const html=fs.readFileSync(path.join(root,"index.html"),"utf8");
const src=fs.readFileSync(path.join(root,"data.js"),"utf8")+"\n"+html.split("<script>")[1].split("// ---- DOM ----")[0]
  +"\nreturn {decodeToken,sigSegment,norm,LEX,PROC,COND};";
const {decodeToken,sigSegment,norm,LEX,PROC,COND}=new Function(src)();
const text=o=>!o?"":o.exact?o.exact.map(e=>e.m).join("; "):o.seg?o.seg.map(x=>x.e.m).join(" "):"";
const words=s=>s.toLowerCase().split(/[^a-z0-9]+/).filter(w=>w&&!["and","at","to","for"].includes(w));
let bad=0,n=0;
for(const ln of fs.readFileSync(path.join(root,"tests","compounds.txt"),"utf8").split("\n")){
  if(!ln.trim()||ln.startsWith("#")) continue; n++;
  const [inp,want]=ln.split("|"), got=text(decodeToken(inp)), have=new Set(words(got));
  const miss=words(want).filter(w=>!have.has(w));
  if(miss.length){bad++; console.log(`FAIL ${inp}: got "${got}", missing ${miss.join(", ")}`);}
}
for(const ln of fs.readFileSync(path.join(root,"specialty-data","dosing-sig-compounds.txt"),"utf8").split("\n")){
  const a=ln.split("|")[0]; if(!a) continue; n++;
  const k=norm(a); if(!sigSegment(k)&&!["qac","qpc","achs","pchs","wm"].includes(k)){bad++; console.log(`FAIL parser cannot split ${a}`);}
}
// Sweep: any acronym that has a procedure meaning, glued after s/p, must read "Status post" + a
// procedure; any with a condition meaning, glued after h/o, r/o, c/f, must read as that condition.
// Skips glued forms that are acronyms in their own right (SPMI, ROMI, HOPE), or plurals of one (SPCs).
const sweep=[["sp","Status post",PROC],["ho","History of",COND],["hx","History of",COND],["ro","Rule out",COND],["cf","Concern for",COND]];
for(const [p,pm,re] of sweep) for(const k of Object.keys(LEX)){
  if(k.length<2||LEX[p+k]||(k.endsWith("s")&&LEX[(p+k).slice(0,-1)])||!LEX[k].some(e=>e.spec!=="Compound modifier"&&re.test(e.m))) continue; n++;
  const o=decodeToken(p.toUpperCase()+k.toUpperCase());
  if(!o.seg||o.seg[0].e.m!==pm||!re.test(o.seg[1].e.m)){bad++; if(bad<40) console.log(`FAIL sweep ${p}+${k}: got "${text(o)}"`);}
}
console.log(`checked ${n}: ${bad} failing`); process.exit(bad?1:0);
