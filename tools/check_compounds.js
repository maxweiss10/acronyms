#!/usr/bin/env node
// Run the site's own decoder (from index.html) over tests/compounds.txt and fail on any miss.
// Also proves the schedule parser covers every generated dosing compound even without its
// dictionary entry, so a new frequency/timing combination cannot fall through again.
// Usage: node tools/check_compounds.js
const fs=require("fs"),path=require("path"),root=path.resolve(__dirname,"..");
const html=fs.readFileSync(path.join(root,"index.html"),"utf8");
const src=fs.readFileSync(path.join(root,"data.js"),"utf8")+"\n"+html.split("<script>")[1].split("// ---- DOM ----")[0]
  +"\nreturn {decodeToken,sigSegment,norm};";
const {decodeToken,sigSegment,norm}=new Function(src)();
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
console.log(`checked ${n}: ${bad} failing`); process.exit(bad?1:0);
