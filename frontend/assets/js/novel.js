// frontend/assets/js/novel.js
import { NovelApi } from "./api/novelApi.js";
import { toast } from "./main.js";

const USER_ID = "u1";
const SESSION_ID = "novel-session-001";

const $ = (sel, root=document) => root.querySelector(sel);
const $$ = (sel, root=document) => Array.from(root.querySelectorAll(sel));

/* ---------- 全局状态 ---------- */
const STATE = {
  project: "春天的邂逅",
  manuscript: [],         // [{jp, zh, author}]
  outline: []             // [{title: "第一章：...", status: "completed|current|todo"}]
};
const STORE_KEY = (sid, proj) => `novel:${sid}:${proj}:manuscript`;

/* ---------- 工具 ---------- */
function escapeHtml(s=""){return s.replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
function timestamp(){const d=new Date(),p=n=>String(n).padStart(2,"0");return `${d.getFullYear()}${p(d.getMonth()+1)}${p(d.getDate())}_${p(d.getHours())}${p(d.getMinutes())}`}

/* 非侵入式半圆指示器 */
function ensureMiniLoader(){
  let el=$(".mini-loader");
  if(!el){ el=document.createElement("div"); el.className="mini-loader"; document.body.appendChild(el); }
  return el;
}
function showLoader(){ ensureMiniLoader().classList.add("show"); }
function hideLoader(){ ensureMiniLoader().classList.remove("show"); }

/* 草稿容器/已采用面板 */
function ensureDraftContainer(){
  let box=$(".chapters-list .chapter-section.current .chapter-content .current-writing .draft-content");
  if(!box){const cur=$(".chapters-list .chapter-section.current .chapter-content .current-writing");if(cur){box=document.createElement("div");box.className="draft-content";cur.appendChild(box)}}
  return box;
}
function ensureCompiledPanel(){
  let sec=$("#compiled-panel");
  if(sec) return sec.querySelector(".compiled-list");
  const tools=$(".tools-panel");
  const wrap=document.createElement("div");
  wrap.className="tool-section";
  wrap.innerHTML=`<h4>🧾 已采用内容</h4><div id="compiled-panel"><div class="compiled-list"></div></div>`;
  tools.appendChild(wrap);
  return wrap.querySelector(".compiled-list");
}

/* 解析段落节点为对象 */
function parseNodeToItem(paragraph){
  const jp=paragraph.querySelector(".japanese-text")?.textContent.trim()||"";
  const zh=paragraph.querySelector(".translation")?.textContent.trim()||"";
  const author=paragraph.querySelector(".author-indicator")?.textContent.replace("(草稿)","").trim()||"";
  return {jp, zh, author};
}

/* 渲染草稿块 */
function renderContributionHTML(agentId, text){
  const nameMap={koumi:"小美",yamada:"山田",tanaka:"田中先生",ai:"アイ",sato:"佐藤教练",membot:"记忆管家"};
  const who=nameMap[agentId]||agentId||"Agent";
  const parts=(text||"").split(/\n{2,}/); // 粗分中日
  const jp=parts[0]||text||"";
  const zh=parts[1]||"";
  return `
    <div class="paragraph draft" data-author="${who}">
      <div class="author-indicator">${who} (草稿)</div>
      <div class="text-content">
        <p class="japanese-text">${escapeHtml(jp)}</p>
        ${zh?`<p class="translation">${escapeHtml(zh)}</p>`:""}
        <div class="draft-actions">
          <button class="draft-btn" data-action="approve">✓ 采用</button>
          <button class="draft-btn" data-action="revise">✏️ 修改</button>
          <button class="draft-btn" data-action="reject">✗ 重写</button>
        </div>
      </div>
    </div>`;
}
function appendContributions(contribs){
  const box=ensureDraftContainer(); if(!box) return;
  contribs.forEach(c=>{
    const div=document.createElement("div");
    div.innerHTML=renderContributionHTML(c.agent_id, c.response);
    box.appendChild(div.firstElementChild);
  });
}

/* 统一后端返回形状 -> [{agent_id, response}] */
function normalizeContribs(r){
  if(r && Array.isArray(r.items) && r.items.length){
    return r.items.map(it=>({agent_id: it.agent_id || it.by || "agent", response: it.response || it.text || ""}));
  }
  if(r && Array.isArray(r.history) && r.history.length){
    return r.history.filter(h=>h.by && h.by!=="seed").map(h=>({agent_id:h.by,response:h.text||""}));
  }
  return [];
}

/* ---------- 右侧“已采用内容” & 导入导出 ---------- */
function renderManuscript(){
  const list=ensureCompiledPanel(); if(!list) return;
  list.innerHTML = STATE.manuscript.map(p=>`
    <div class="compiled-item">
      <div class="jp">${escapeHtml(p.jp)}</div>
      ${p.zh?`<div class="zh">${escapeHtml(p.zh)}</div>`:""}
    </div>`).join("");
}

function saveLocalOnly(){
  localStorage.setItem(STORE_KEY(SESSION_ID, STATE.project), JSON.stringify({
    project: STATE.project,
    manuscript: STATE.manuscript,
    outline: STATE.outline,
    savedAt: new Date().toISOString()
  }));
}

/* ---------- 故事大纲（可编辑） ---------- */
function collectOutlineFromDOMIfEmpty(){
  if(STATE.outline.length) return;
  const items=$$(".tool-section .outline-content .outline-item");
  if(!items.length) { // 默认
    STATE.outline = [
      {title:"第一章：相遇", status:"completed"},
      {title:"第二章：初次对话", status:"current"},
      {title:"第三章：逐渐了解", status:"todo"},
      {title:"第四章：情感萌芽", status:"todo"},
      {title:"结局：樱花再开时", status:"todo"},
    ];
    return;
  }
  STATE.outline = items.map(el=>{
    const title = el.querySelector(".outline-text")?.textContent.trim()||"未命名章节";
    const status = el.classList.contains("completed") ? "completed"
                 : el.classList.contains("current")   ? "current"
                 : "todo";
    return {title, status};
  });
}

function ensureOutlineControls(){
  const sec = $$(".tool-section").find(s => s.querySelector("h4")?.textContent.includes("故事大纲"));
  if(!sec) return null;
  if(sec.querySelector(".outline-ctrls")) return sec;
  const bar=document.createElement("div");
  bar.className="outline-ctrls";
  bar.style.cssText="display:flex;gap:8px;margin:8px 0 6px 0";
  bar.innerHTML=`
    <button class="control-btn" id="btn-outline-edit">编辑大纲</button>
    <button class="control-btn" id="btn-outline-add">添加章节</button>
    <button class="control-btn" id="btn-outline-save">保存大纲</button>`;
  sec.insertBefore(bar, sec.querySelector(".outline-content"));
  return sec;
}

function renderOutlineView(){
  const sec = ensureOutlineControls(); if(!sec) return;
  const box = sec.querySelector(".outline-content");
  box.innerHTML = STATE.outline.map((o,i)=>`
    <div class="outline-item ${o.status==='completed'?'completed':o.status==='current'?'current':''}" data-idx="${i}">
      <div class="outline-icon">${o.status==='completed'?'✓':o.status==='current'?'📝':'📖'}</div>
      <div class="outline-text">${escapeHtml(o.title)}</div>
    </div>`).join("");
}

function renderOutlineEditor(){
  const sec = ensureOutlineControls(); if(!sec) return;
  const box = sec.querySelector(".outline-content");
  box.innerHTML = STATE.outline.map((o,i)=>`
    <div class="outline-item ${o.status==='completed'?'completed':o.status==='current'?'current':''}" data-idx="${i}" style="display:flex;align-items:center;gap:8px">
      <button class="control-btn" data-act="up">↑</button>
      <button class="control-btn" data-act="down">↓</button>
      <input class="outline-input" value="${escapeHtml(o.title)}" style="flex:1;padding:6px 8px;border:1px solid #ddd;border-radius:8px"/>
      <select class="outline-status">
        <option value="todo" ${o.status==='todo'?'selected':''}>待写</option>
        <option value="current" ${o.status==='current'?'selected':''}>进行中</option>
        <option value="completed" ${o.status==='completed'?'selected':''}>已完成</option>
      </select>
      <button class="control-btn" data-act="del">删除</button>
    </div>`).join("");
}

let OUTLINE_EDITING = false;
function toggleOutlineEditing(on){
  OUTLINE_EDITING = (on!==undefined)? on : !OUTLINE_EDITING;
  if(OUTLINE_EDITING) renderOutlineEditor(); else renderOutlineView();
}

function bindOutlineEvents(){
  const sec = ensureOutlineControls(); if(!sec) return;

  sec.addEventListener("click",(e)=>{
    const t=e.target;
    if(t.id==="btn-outline-edit"){ toggleOutlineEditing(); return; }
    if(t.id==="btn-outline-add"){
      STATE.outline.push({title:`新章节 ${STATE.outline.length+1}`, status:"todo"});
      OUTLINE_EDITING ? renderOutlineEditor() : renderOutlineView();
      return;
    }
    if(t.id==="btn-outline-save"){
      // 从编辑器读取回 STATE
      if(OUTLINE_EDITING){
        const rows=$$(".outline-item", sec);
        STATE.outline = rows.map(row=>{
          const title=row.querySelector(".outline-input")?.value.trim()||"未命名章节";
          const status=row.querySelector(".outline-status")?.value||"todo";
          return {title, status};
        });
        renderOutlineView();
        OUTLINE_EDITING=false;
      }
      saveToBackend(); // 同时调用后端保存
      toast("📚 大纲已保存", "success");
      return;
    }

    const row=t.closest(".outline-item"); if(!row) return;
    const idx=Number(row.dataset.idx);
    if(t.dataset.act==="del"){ STATE.outline.splice(idx,1); renderOutlineEditor(); }
    if(t.dataset.act==="up" && idx>0){ const tmp=STATE.outline[idx-1]; STATE.outline[idx-1]=STATE.outline[idx]; STATE.outline[idx]=tmp; renderOutlineEditor(); }
    if(t.dataset.act==="down" && idx<STATE.outline.length-1){ const tmp=STATE.outline[idx+1]; STATE.outline[idx+1]=STATE.outline[idx]; STATE.outline[idx]=tmp; renderOutlineEditor(); }
  });
}

/* ---------- 与后端交互：保存/加载 ---------- */
async function saveToBackend(){
  // manuscript 与 outline 一并保存
  const payload = { session_id: SESSION_ID, project: STATE.project, manuscript: STATE.manuscript, outline: STATE.outline };
  try{
    const res = await NovelApi.save(payload);
    saveLocalOnly(); // 本地也存一份
    console.log("[save]", res);
    return res;
  }catch(e){
    console.error(e); toast("保存到后端失败，已存本地："+e.message,"warning");
    saveLocalOnly();
  }
}

async function loadFromBackend(){
  try{
    const data = await NovelApi.load(SESSION_ID, STATE.project);
    if(data && !data.not_found){
      STATE.manuscript = Array.isArray(data.manuscript) ? data.manuscript : [];
      STATE.outline = Array.isArray(data.outline) ? data.outline : [];
      renderManuscript();
      renderOutlineView();
      toast("✅ 已从后端载入历史进度", "success");
      return;
    }
    // 后端没有 -> 尝试本地
    const raw=localStorage.getItem(STORE_KEY(SESSION_ID, STATE.project));
    if(raw){
      const j=JSON.parse(raw);
      STATE.manuscript = j.manuscript||[];
      STATE.outline = j.outline||[];
      renderManuscript(); renderOutlineView();
      toast("ℹ️ 已从本地加载历史", "info");
    }else{
      collectOutlineFromDOMIfEmpty();
      renderOutlineView();
    }
  }catch(e){
    console.error(e);
    collectOutlineFromDOMIfEmpty();
    renderOutlineView();
  }
}

/* ---------- 交互：草稿按钮 & AI调用 ---------- */
function bindDraftActions(){
  document.addEventListener("click",(e)=>{
    const btn=e.target.closest(".draft-btn"); if(!btn) return;
    const action=btn.dataset.action;
    const para=btn.closest(".paragraph"); if(!para) return;

    if(action==="approve"){
      const item=parseNodeToItem(para);
      STATE.manuscript.push(item);
      renderManuscript();
      saveToBackend();

      para.classList.remove("draft"); para.classList.add("approved");
      para.querySelector(".draft-actions")?.remove();
      toast("✓ 段落已采用并加入『已采用内容』", "success");
    }else if(action==="revise"){
      toast("✏️ 已请求修改（可在输入框写提示再点『提交想法』）", "info");
    }else if(action==="reject"){
      para.style.opacity="0.6"; setTimeout(()=>para.remove(),200);
      toast("✗ 已删除草稿", "warning");
    }
  });
}

async function handleBrainstorm(){
  try{
    showLoader();
    const sel=$("#current-project");
    STATE.project = sel ? (sel.value==="spring-encounter" ? "春天的邂逅" : sel.value) : STATE.project;

    const r=await NovelApi.brainstorm(STATE.project, USER_ID, SESSION_ID);
    const items=normalizeContribs(r);
    if(items.length){
      const p=$(".writing-prompt p");
      if(p) p.textContent="AI建议片段：" + items[0].response.slice(0,120) + "…";
      appendContributions(items.slice(0,3));
    }
    console.log("[brainstorm]", r);
    toast("💡 头脑风暴完成", "success");
  }catch(e){
    console.error(e); toast("头脑风暴失败："+e.message, "error");
  }finally{
    hideLoader();
  }
}

async function handleNextParagraph(userHint=""){
  try{
    showLoader();
    const last=$(".chapters-list .chapter-section.current .chapter-content .paragraph:last-child .japanese-text");
    const lastText=last ? last.textContent.trim() : "";
    const outline={chapter:"第二章：運命の出会い"};

    const r=await NovelApi.next(outline, lastText, userHint, USER_ID, SESSION_ID, ["koumi","yamada","tanaka"]);
    const items=normalizeContribs(r);
    if(!items.length){ toast("没有收到可展示的草稿。请查看控制台响应。","warning"); console.warn("[next] unknown shape:",r); return; }
    appendContributions(items);
    console.log("[next]", r);
    toast(`已插入 ${items.length} 条草稿`, "success");
  }catch(e){
    console.error(e); toast("生成下一段失败："+e.message,"error");
  }finally{
    hideLoader();
  }
}

/* ---------- 绑定按钮 ---------- */
function bindButtons(){
  $("#btn-start-brainstorm")?.addEventListener("click", handleBrainstorm);
  $("#btn-ai-help")?.addEventListener("click", handleBrainstorm);
  $("#btn-submit-idea")?.addEventListener("click", async ()=>{
    const val=$(".user-input")?.value.trim()||"";
    if(!val) return toast("⚠️ 请输入创作内容","warning");
    $(".user-input").value="";
    await handleNextParagraph(val);
  });

  $("#btn-save-project")?.addEventListener("click", saveToBackend);
  $("#btn-export-novel")?.addEventListener("click", ()=>{
    // 仍保留导出为本地文件功能
    const md = STATE.manuscript.map((p,i)=>`${i+1}. ${p.jp}\n${p.zh?"> "+p.zh+"\n":""}`).join("\n");
    const json=JSON.stringify({project:STATE.project, manuscript:STATE.manuscript, outline:STATE.outline}, null, 2);
    const name=`${STATE.project}_${timestamp()}`;
    const blob=(name, text, type)=>{const b=new Blob([text],{type});const url=URL.createObjectURL(b);const a=document.createElement("a");a.href=url;a.download=name;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(url);a.remove()},100);}
    blob(`${name}.md`, md, "text/markdown");
    blob(`${name}.json`, json, "application/json");
    toast("📤 已导出 Markdown + JSON", "success");
  });

  $("#current-project")?.addEventListener("change", async ()=>{
    STATE.project = $("#current-project").value==="spring-encounter" ? "春天的邂逅" : $("#current-project").value;
    await loadFromBackend();
    toast(`已切换到项目：${STATE.project}`, "info");
  });

  bindOutlineEvents();
}

async function boot(){
  const sel=$("#current-project");
  if(sel) STATE.project = sel.value==="spring-encounter" ? "春天的邂逅" : sel.value;

  bindButtons();
  bindDraftActions();
  await loadFromBackend();            // 优先从后端加载历史
  console.log("📖 协作小说页面已初始化（with backend persistence）");
}

// DOM Ready 兜底
if(document.readyState==="loading"){ document.addEventListener("DOMContentLoaded", boot); } else { boot(); }
