import fs from 'fs';
import path from 'path';

const root=path.resolve(import.meta.dirname,'..');
const scan=path.join(root,'moocs_pdf_scan');
const output=path.join(root,'static','moocs','pdf_archive_sets.js');
const read=name=>fs.readFileSync(path.join(scan,name),'utf8').replace(/\r/g,'');
const compact=value=>String(value||'').replace(/https?:\/\/\S+/g,' ').replace(/\f/g,' ').replace(/\s+/g,' ').trim();
const letterIndex=letter=>'ABCD'.indexOf(letter);

function oldPaper(file,answers,source){
  const text=read(file);
  const start=Math.max(0,text.search(/Note\s*:\s*This paper contains/i));
  const body=text.slice(start);
  const starts=[];
  for(let number=1;number<=50;number+=1){
    const pattern=new RegExp(`^\\s*${number}\\.\\s+`,'m');
    const offset=starts.length?starts[starts.length-1].index+starts[starts.length-1].length:0;
    const match=pattern.exec(body.slice(offset));
    starts.push(match?{number,index:offset+match.index,length:match[0].length}:null);
  }
  return starts.flatMap((entry,index)=>{
    if(!entry||answers[index]==='?')return [];
    const next=starts.slice(index+1).find(Boolean);
    let block=body.slice(entry.index+entry.length,next?next.index:body.length)
      .replace(/^.*(?:P\.T\.O\.|DÂ?—?87\d\d|JÂ?—?87\d\d).*$/gm,' ');
    const labels=[...block.matchAll(/\(([A-D])\)/g)];
    const firstByLetter={};
    labels.forEach(match=>{if(!firstByLetter[match[1]])firstByLetter[match[1]]=match});
    if(!'ABCD'.split('').every(letter=>firstByLetter[letter]))return [];
    const ordered=Object.values(firstByLetter).sort((a,b)=>a.index-b.index);
    const optionsByLetter={};
    ordered.forEach((match,position)=>{
      const end=position+1<ordered.length?ordered[position+1].index:block.length;
      optionsByLetter[match[1]]=compact(block.slice(match.index+3,end));
    });
    const options='ABCD'.split('').map(letter=>optionsByLetter[letter]);
    const question=compact(block.slice(0,ordered[0].index));
    const answer=letterIndex(answers[index]);
    if(!question||options.some(option=>!option)||answer<0)return [];
    return [{source,number:entry.number,question,options,answer}];
  });
}

function testbook2021(from,to,source){
  const text=read('UGC_NET_26_Nov_2021_Shift_1__Computer_Science_N_Applications___English_.txt');
  const starts=[...text.matchAll(/^\s*(\d+)\)\s*/gm)].filter(match=>Number(match[1])>=from&&Number(match[1])<=to);
  return starts.flatMap((match,index)=>{
    const number=Number(match[1]);
    const next=index+1<starts.length?starts[index+1].index:text.length;
    const block=text.slice(match.index+match[0].length,next);
    const questionEnd=block.indexOf('[Question ID');
    const answerStart=block.indexOf('Correct Answer');
    if(questionEnd<0||answerStart<0)return [];
    const question=compact(block.slice(0,questionEnd));
    const optionArea=block.slice(questionEnd,answerStart);
    const options=[...optionArea.matchAll(/^\s*([1-4])\.\s*([\s\S]*?)\s*\[Option ID\s*=\s*(\d+)\]/gm)]
      .sort((a,b)=>Number(a[1])-Number(b[1]));
    const correctId=/Correct Answer\s*:[^\n]*\n[\s\S]*?\[Option ID\s*=\s*(\d+)\]/.exec(block)?.[1];
    const answer=options.findIndex(option=>option[3]===correctId);
    if(!question||options.length!==4||answer<0)return [];
    return [{source,number,question,options:options.map(option=>compact(option[2])),answer}];
  });
}

const papers={
  j05:['j-8705-paper-ii-fae0bdd3.txt','BBCCCBCDCCDDBBCACBCBDBBABCDDDDCBDBDCCBBDBDDAADDBCC','June 2005 Paper II'],
  d05:['d-8705-paper-ii-bd25fa9b.txt','DDCACADCABBDDBBDBBCABCDDBADDDDAADCDDDBCAABCCBADBBC','December 2005 Paper II'],
  j06:['j-8706-paper-ii-5db3660f.txt','BCCACBCDCDC?CDDCBCCABABABCAACBDCABBBBBCABABDBCABAC','June 2006 Paper II'],
  d06:['d-8706-paper-ii-d8460a15.txt','BD?C?CCAABAABBBCBCCABADCADBCBBBBCDCCBDDBABABABDCBA','December 2006 Paper II'],
  j07:['j-8707-paper-ii-f0f69f4b.txt','DBDDCCAAABBCBAACCACCDACBBCACABCCDDCCCACDCCDDDDCACD','June 2007 Paper II'],
  d07:['d-8707-paper-ii-0bd07152.txt','ABCBABACBABDB?DCBADBABBCBBABDAABAAADDBABCCBBACAABD','December 2007 Paper II'],
  j08:['j-8708-paper-ii-a8f586e6.txt','DCADACACCBDCBCCDBBBCBCCDCBCDDCCCABAABBDCCADADDDBDA','June 2008 Paper II'],
  d08:['d-8708-paper-ii-498f9ce9.txt','BDABDCBDBCCDDDACAAABBDCACCBADDBDADAACDDADBCBCBADBC','December 2008 Paper II']
};
const parsed=Object.fromEntries(Object.entries(papers).map(([key,[file,answers,source]])=>[key,oldPaper(file,answers,source)]));
const november2021=testbook2021(1,100,'November 2021 keyed paper');
const sets={
  31:[...parsed.j05,...parsed.d05],
  32:[...parsed.j06,...parsed.d06],
  33:[...parsed.j07,...parsed.d07],
  34:[...parsed.j08,...parsed.d08],
  35:november2021.slice(0,100).map(row=>({...row,source:'November 2021 Computer Science'})),
  36:november2021.slice(100,150).map(row=>({...row,source:'November 2021 General Paper'}))
};
const titles={31:'June + December 2005 Paper II',32:'June + December 2006 Paper II',33:'June + December 2007 Paper II',34:'June + December 2008 Paper II',35:'November 2021 Computer Science',36:'November 2021 General Paper + new MCQs',37:'2017–2018 archive-informed MCQs',38:'2019–2020 archive-informed MCQs',39:'2024 Paper I and network-reference MCQs',40:'OS, DBMS and cloud-reference MCQs'};

const serialized=Object.fromEntries(Object.entries(sets).map(([set,rows])=>[set,rows.slice(0,100).map((row,index)=>({
  s:`Set ${set} • ${row.source} • Question ${row.number}`,
  t:row.source.includes('General')?'General Paper':'Computer Science',
  q:`[PDF-S${set}-Q${index+1}] ${row.question}`,
  o:row.options,a:row.answer,
  e:`The keyed answer is ${row.options[row.answer]}. Source: ${row.source} from the supplied UGC-NET PDF archive.`,
  mode:'selection',level:'Previous-year paper',unit:0,unitName:row.source
}))]));

const report=Object.entries(serialized).map(([set,rows])=>`Set ${set}: ${rows.length} extracted keyed questions`).join('\n');
console.log(report);
const javascript=`/* Generated by tools/generate_moocs_pdf_archive.mjs from the supplied PDF archive. */\n(function(){\nconst PDF_ARCHIVE_SETS=${JSON.stringify(serialized)};\nconst titles=${JSON.stringify(titles)};\nconst picker=document.querySelector('#exam-set');\nif(picker){for(let set=31;set<=40;set++){const option=document.createElement('option');option.value=String(set);picker.appendChild(option)}}\nfor(let set=31;set<=40;set++){\n  const sourced=PDF_ARCHIVE_SETS[set]||[];\n  const generated=(QUESTION_SETS[set]||[]).slice(sourced.length,100).map((question,index)=>({...question,s:\`Set \${set} • \${titles[set]} • Supplemental question \${index+1}\`}));\n  QUESTION_SETS[set]=sourced.concat(generated).slice(0,100);\n  const option=document.querySelector(\`#exam-set option[value="\${set}"]\`);\n  if(option)option.textContent=\`Set \${set} — \${titles[set]} (100)\`;\n}\n})();\n`;
fs.writeFileSync(output,javascript,'utf8');
console.log(`Wrote ${output}`);
