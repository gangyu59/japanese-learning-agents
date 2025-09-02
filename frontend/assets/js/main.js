// frontend/assets/js/main.js
export function toast(msg, type="info", ms=2500) {
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;
  el.textContent = msg;
  Object.assign(el.style, {
    position: "fixed", right: "20px", top: "20px",
    padding: "10px 16px", color: "#fff", borderRadius: "10px",
    boxShadow: "0 6px 18px rgba(0,0,0,.15)", zIndex: 10000,
    background: type === "success" ? "#22c55e" :
                type === "warning" ? "#f59e0b" :
                type === "error" ? "#ef4444" : "#3b82f6",
    transition: "transform .2s ease, opacity .2s ease"
  });
  document.body.appendChild(el);
  setTimeout(()=> { el.style.opacity = "0"; el.style.transform = "translateX(20px)"; }, ms);
  setTimeout(()=> el.remove(), ms + 220);
}

export const uid = (p="id") => `${p}_${Math.random().toString(36).slice(2,10)}`;
