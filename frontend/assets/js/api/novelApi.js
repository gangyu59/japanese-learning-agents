// frontend/assets/js/api/novelApi.js
const SAME_ORIGIN = location.port === "8000";
const API_ROOT = SAME_ORIGIN
  ? "/api/v1/novel"
  : `${location.protocol}//${location.hostname}:8000/api/v1/novel`;

async function apiPost(path, body) {
  const url = `${API_ROOT}${path}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  const ct = res.headers.get("content-type") || "";
  if (!res.ok || ct.includes("text/html")) {
    const text = await res.text();
    throw new Error(`API ${url} failed: ${res.status}. ${text.slice(0, 200)}`);
  }
  return res.json();
}
async function apiGet(path, params) {
  const search = new URLSearchParams(params||{}).toString();
  const url = `${API_ROOT}${path}${search?`?${search}`:""}`;
  const res = await fetch(url, { method: "GET" });
  const ct = res.headers.get("content-type") || "";
  if (!res.ok || ct.includes("text/html")) {
    const text = await res.text();
    throw new Error(`API ${url} failed: ${res.status}. ${text.slice(0, 200)}`);
  }
  return res.json();
}

export const NovelApi = {
  brainstorm: (theme, user_id, session_id, agents=null) =>
    apiPost("/brainstorm", { theme, user_id, session_id, agents, topic: theme }),

  roles: (theme, constraints, user_id, session_id) =>
    apiPost("/characters", { theme, constraints, user_id, session_id }),

  next: (outline, lastParagraph, userHint, user_id, session_id, order=null) => {
    const seed = `${lastParagraph || ""}\n${userHint || ""}`.trim();
    return apiPost("/round_robin", { seed, turns: 3, session_id })
      .catch(() => apiPost("/next", {
        outline, last_paragraph: lastParagraph, user_hint: userHint,
        user_id, session_id, order, turns: 3
      }));
  },

  discuss: (conflict, options, user_id, session_id) =>
    apiPost("/live_discussion", { question: conflict, session_id }),

  arbitrate: (choice, user_id, session_id) =>
    apiPost("/arbitrate", { decision: choice, reason: "user" }),

  // 新增：持久化
  save: ({session_id, project, outline, manuscript}) =>
    apiPost("/save", { session_id, project, outline, manuscript }),
  load: (session_id, project) =>
    apiGet("/load", { session_id, project }),
};
