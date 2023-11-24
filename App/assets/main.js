// elements
const barrier_button_el = document.querySelector("#open_barrier");
const ai_button_el = document.querySelector("#enable_ai");

function format_date(date=null) {
  var now;
  if (date===null) {
    now = new Date();
  } else {
    now = new Date(date);
  }

  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const hour = String(now.getHours()).padStart(2, '0');
  const minute = String(now.getMinutes()).padStart(2, '0');
  const second = String(now.getSeconds()).padStart(2, '0');

  return `${year}-${month}-${day} ${hour}:${minute}:${second}`
}

// config
var barrier_is_opened = false;
var ai_is_active = false
barrier_button_el.addEventListener("click", (e)=>{
  barrier_button_toggle();
  ws.send(JSON.stringify({method: barrier_is_opened ? "open_barrier" : "close_barrier"}))
  e.stopPropagation()}
)
ai_button_el.addEventListener("click", (e)=>{
  toggle_ai_button();
  ws.send(JSON.stringify({method: ai_is_active ? "ai_enable" : "ai_disable"}))
  e.stopPropagation()}
)

function barrier_button_toggle(status=null, history_add=true, who='user') {
  if (status===null) {barrier_is_opened = !barrier_is_opened}
  else {barrier_is_opened = status}

  if (barrier_is_opened) {
    barrier_button_el.classList.toggle("button-active")
    barrier_button_el.innerHTML = `<img src="../assets/web_icons/enable.svg"  alt=\"\"/> Закрыть`
  } else {
    barrier_button_el.classList.remove("button-active")
    barrier_button_el.innerHTML = `<img src="../assets/web_icons/enable.svg" /> Открыть`
  }

  if(history_add===true) {history_obj.add(who, (barrier_is_opened) ? "opened" : "closed", format_date())}
}

function toggle_ai_button(status=null) {
  if (status===null) {ai_is_active = !ai_is_active}
  else {ai_is_active = status}

  if (ai_is_active) {
    ai_button_el.classList.toggle("button-active")
  } else {
    ai_button_el.classList.remove("button-active")
  }
}


class History {
  constructor() {
    this.is_fullscreen = false;
    this.header_el = document.querySelector(".history-header")
    this.content_el = document.querySelector(".history-content")
    this.header_icon_el = document.querySelector("#history_fullscreen_icon")

    this.minimize()
    this.header_el.addEventListener("click", ()=> {
      if (this.is_fullscreen) { this.minimize() }
      else { this.fullscreen() }
    })
  }

  minimize() {
    this.is_fullscreen = false;
    document.querySelector("body").style.gridTemplateRows = "40% 50% 10%";
    document.querySelector(".buttons-block").style.display = "grid";
    this.content_el.style.overflow = "hidden";
    this.header_icon_el.style.transform ="rotate(0deg)"
    let p = this.content_el.clientHeight % 50
    this.content_el.style.padding = `${p}px 10px ${p}px 10px`
    this.content_el.scrollTo(0, 0)
  }

  fullscreen() {
    this.is_fullscreen = true;
    document.querySelector("body").style.gridTemplateRows = "0 100% 0";
    document.querySelector(".buttons-block").style.display = "none";
    this.content_el.style.overflow = "scroll";
    this.header_icon_el.style.transform = "rotate(180deg)";
  }

  add(who, type, time) {
    var who = (who === "ai") ? `<img src="../assets/web_icons/brain.svg" />` : `<img src="../assets/web_icons/user.svg" />`;
    this.content_el.innerHTML = `
            <div class="history-content-el-${type}">
                ${who}
                ${(type==="opened") ? "Открытие" : "Закрытие"} - ${time}
            </div>
        ` + this.content_el.innerHTML
  }
}


let history_obj = new History()
const ws = new WebSocket("wss://example.ru/ws")

ws.onopen = function(event) {
    ws.send(JSON.stringify({method: "get_history"}))
    ws.send(JSON.stringify({method: "get_status_barrier_button"}))
    ws.send(JSON.stringify({method: "get_status_ai_button"}))
};

ws.onmessage = function(event) {
    let data = JSON.parse(event.data);

    if (data["method"] === "get_history") {
      data = data["history"].reverse()
      data.forEach(hist => {
        history_obj.add(hist["who"], hist["status"] ? "opened" : "closed", format_date(hist["date"]))
      })
    } else if (data["method"] === "get_status_barrier_button") {
      barrier_button_toggle(data["status"], false)
    } else if (data["method"] === "get_status_ai_button") {
      toggle_ai_button(data["status"])
    } else if (data["method"] === "change_barrier_button") {
      barrier_button_toggle(data["status"], true, data["who"])
    } else if (data["method"] === "change_ai_button") {
      toggle_ai_button(data["status"])
    }
};
