(() => {
  "use strict";
  const $ = (q, root = document) => root.querySelector(q);
  const $$ = (q, root = document) => [...root.querySelectorAll(q)];
  const esc = (v = "") =>
    String(v).replace(
      /[&<>"']/g,
      (c) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[c],
    );
  const icons = {
    panel:
      '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M9 4v16"/>',
    chat: '<path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8A8.5 8.5 0 0 1 8.7 3.9a8.4 8.4 0 0 1 3.8-.9h.5a8.5 8.5 0 0 1 8 8v.5Z"/><path d="M8 11h8M8 15h4"/>',
    people:
      '<circle cx="9" cy="8" r="3"/><path d="M3 21v-2a6 6 0 0 1 12 0v2M16 5a3 3 0 0 1 0 6M21 21v-2a6 6 0 0 0-4-5.6"/>',
    profile:
      '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8" cy="10" r="2"/><path d="M5 17v-1a3 3 0 0 1 6 0v1M14 9h4M14 13h4"/>',
    link: '<path d="m10 13 4-4M8 16l-1 1a4.2 4.2 0 0 1-6-6l4-4a4.2 4.2 0 0 1 6 0m2 1 1-1a4.2 4.2 0 0 1 6 6l-4 4a4.2 4.2 0 0 1-6 0" transform="translate(1 1)"/>',
    sliders:
      '<path d="M4 6h6m4 0h6M4 12h10m4 0h2M4 18h2m4 0h10"/><circle cx="12" cy="6" r="2"/><circle cx="16" cy="12" r="2"/><circle cx="8" cy="18" r="2"/>',
    doc: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M8 13h8M8 17h5"/>',
    settings:
      '<path d="m9 3-1 3-3 1-2 3 2 2-1 3 3 3 3-1 2 2 3-1 1-3 3-1 1-4-3-2-1-3Z"/><circle cx="11" cy="11" r="3"/>',
    down: '<path d="m6 9 6 6 6-6"/>',
    right: '<path d="m9 6 6 6-6 6"/>',
    left: '<path d="m15 6-6 6 6 6"/>',
    up: '<path d="m6 15 6-6 6 6"/>',
    arrow: '<path d="M5 12h14m-5-5 5 5-5 5"/>',
    send: '<path d="M12 19V5m-6 6 6-6 6 6"/>',
    check: '<path d="m5 12 4 4L19 6"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    x: '<path d="m6 6 12 12M6 18 12-12"/>',
    info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7h.01"/>',
    mic: '<rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10v2a7 7 0 0 0 14 0v-2M12 19v3m-3 0h6"/>',
    phone:
      '<path d="M22 16.9v3a2 2 0 0 1-2.2 2A19.8 19.8 0 0 1 3.1 5.2 2 2 0 0 1 5.1 3h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L9 10.8a16 16 0 0 0 4.2 4.2l1.3-1.3a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2Z"/>',
    edit: '<path d="m16 3 5 5-12 12H4v-5Z"/><path d="m14 5 5 5"/>',
    search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
    star: '<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9Z"/>',
    more: '<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
    logout: '<path d="M9 3H4v18h5M9 12h12m-5-5 5 5-5 5"/>',
    download: '<path d="M12 3v12m-5-5 5 5 5-5M4 17v4h16v-4"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    shield:
      '<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6Z"/><path d="m8 12 3 3 5-5"/>',
    spark:
      '<path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5Z"/>',
    refresh:
      '<path d="M20 7v5h-5M4 17v-5h5"/><path d="M6 7a7 7 0 0 1 11-2l3 3M4 16l3 3a7 7 0 0 0 11-2"/>',
    pin: '<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
    briefcase:
      '<rect x="3" y="7" width="18" height="14" rx="2"/><path d="M8 7V3h8v4M3 12c5 4 13 4 18 0M12 12v4"/>',
    pause: '<path d="M8 5v14M16 5v14"/>',
    play: '<path d="m8 4 12 8-12 8Z"/>',
  };
  const I = (name, cls = "") =>
    `<svg class="icon ${cls}" aria-hidden="true" viewBox="0 0 24 24">${icons[name] || icons.info}</svg>`;
  const A = (act, label, icon = "", cls = "btn", extra = "") =>
    `<button class="${cls}" data-action="${act}" ${extra}>${icon ? I(icon) : ""}${label}</button>`;
  const agentImg = (name, cls = "agent-avatar") =>
    `<img class="${cls}" src="../design/fahem-wasel/${name}.svg" alt="${name === "fahem" ? "Fahem" : "Wasel"}">`;
  const people = [
    {
      id: "lina",
      name: "Lina Haddad",
      initials: "LH",
      role: "Full-stack engineer",
      location: "Doha, Qatar",
      color: "#e5e9f4",
      tags: ["Technical", "Fintech", "Full-time"],
      fit: "Strong fit",
      offer:
        "Product engineering, backend architecture and payments integrations",
      need: "A cofounder who can lead product, operations and early customers",
      bio: "I turn complicated financial workflows into products people actually enjoy using. After six years building payment systems, I’m ready to build something of my own.",
      quote:
        "I’ve built payment backends for six years. I want a partner who understands the operations behind the product.",
      secondQuote:
        "I can commit full-time now and have about a year of runway.",
      reason:
        "You understand the workflows. Lina can build the product. You’re both ready to go full-time on a fintech idea.",
      runway: "12 months",
      commitment: "Full-time now",
      email: "lina@example.com",
      reasons: [
        "Your product and operations experience complements her engineering background.",
        "You both want to build in fintech, starting with a real operational problem.",
        "You’re both based in Doha and available full-time.",
      ],
    },
    {
      id: "omar",
      name: "Omar Al-Kuwari",
      initials: "OA",
      role: "AI & machine learning engineer",
      location: "Doha, Qatar",
      color: "#ece8df",
      tags: ["Technical", "Applied AI", "Full-time"],
      fit: "Strong fit",
      offer: "Applied AI, multilingual models and production ML systems",
      need: "A product-minded cofounder with customer discovery and go-to-market skills",
      bio: "I’ve spent four years bringing language models into real products. I’m interested in practical tools for small businesses in the region, especially in Arabic.",
      quote:
        "I can build the AI, but I need someone who will spend time with customers and find the right problem.",
      secondQuote:
        "I’m in Doha, available full-time, and can go ten months without a salary.",
      reason:
        "Omar brings the AI depth. You bring product judgment and the ability to turn messy workflows into something useful.",
      runway: "10 months",
      commitment: "Full-time now",
      email: "omar@example.com",
      reasons: [
        "His AI engineering skills complement your product and operations strengths.",
        "You both want to solve practical business problems with applied AI.",
        "You can both work together in Doha, full-time.",
      ],
    },
    {
      id: "sara",
      name: "Sara Mansour",
      initials: "SM",
      role: "Product engineer & designer",
      location: "Dubai, UAE",
      color: "#e9e7f1",
      tags: ["Product engineering", "B2B SaaS", "Remote"],
      fit: "Worth a conversation",
      offer: "Frontend engineering, product design and early-stage prototyping",
      need: "A cofounder to own commercial strategy, operations and customer relationships",
      bio: "I build the first version, test it with people, and keep improving it. I’m looking for a partner who loves the business side as much as I love making the product.",
      quote:
        "I want to build software for the overlooked parts of running a business. Someone else should own the commercial side.",
      secondQuote:
        "I can work full-time remotely from Dubai, with regular trips to Doha.",
      reason:
        "Sara could own the product build while you lead customers and operations. You’d need to agree on working remotely.",
      runway: "9 months",
      commitment: "Full-time, remote",
      email: "sara@example.com",
      reasons: [
        "She can design and build a first product while you develop customer relationships.",
        "You both mentioned B2B workflow software as an area of interest.",
        "She is remote in Dubai: discuss how often you want to meet in person.",
      ],
    },
    {
      id: "yusuf",
      name: "Yusuf Rahman",
      initials: "YR",
      role: "Backend & infrastructure engineer",
      location: "Doha, Qatar",
      color: "#dfece8",
      tags: ["Backend", "Fintech", "Full-time"],
      fit: "Strong fit",
      offer: "Secure backend systems, API design and cloud infrastructure",
      need: "A business cofounder with financial operations experience",
      bio: "I’ve built infrastructure for two regional fintech companies. Now I’d like to work on a smaller, focused product with a partner who knows the problem from the inside.",
      quote:
        "I’d love to partner with someone who has worked inside banking operations. They’ll know the problems better than I do.",
      secondQuote: "I live in Doha and can commit full-time for the next year.",
      reason:
        "Yusuf is specifically looking for your financial operations background. His backend experience fills the gap you described.",
      runway: "12 months",
      commitment: "Full-time now",
      email: "yusuf@example.com",
      reasons: [
        "He explicitly wants a partner with financial operations experience.",
        "His backend and security skills complement your workflow and product skills.",
        "You share a preference for working in person in Doha.",
      ],
    },
    {
      id: "maya",
      name: "Maya Nasser",
      initials: "MN",
      role: "Software engineer",
      location: "Abu Dhabi, UAE",
      color: "#f0e7dc",
      tags: ["Full-stack", "SME tools", "Remote"],
      fit: "Worth a conversation",
      offer:
        "Full-stack development, analytics and rapid product experimentation",
      need: "Someone to lead product discovery and build partnerships in Qatar",
      bio: "I like building small, useful tools for businesses. I’m looking for a partner with direct access to the people we’d be building for.",
      quote:
        "I want to work with someone who can open doors to real businesses and test our assumptions with them.",
      secondQuote:
        "I can start full-time in a month. Remote is ideal, and I can travel.",
      reason:
        "Maya can bring your ideas to life quickly. Check whether her start date and remote setup work for you.",
      runway: "8 months",
      commitment: "Full-time in one month",
      email: "maya@example.com",
      reasons: [
        "Her engineering skills complement your customer-facing product experience.",
        "You both care about useful tools for small businesses.",
        "She starts next month and works remotely; clarify those expectations first.",
      ],
    },
  ];
  const questions = [
    {
      key: "idea",
      title: "What are you working on?",
      hint: "An idea, a problem you’ve noticed, or something you can’t stop thinking about.",
      sample:
        "I want to build simple financial workflow software for small businesses in Qatar. I’ve seen how much time teams lose to manual reconciliation and reporting.",
    },
    {
      key: "offer",
      title: "What would you bring to the partnership?",
      hint: "Tell me about your skills and the work you enjoy doing.",
      sample:
        "Product thinking, financial operations, workflow automation and customer discovery. I’m good at turning a messy process into a clear plan and getting people on board.",
    },
    {
      key: "need",
      title: "Who would make a good partner?",
      hint: "Think about the skills you need beside yours, rather than a job title.",
      sample:
        "A technical cofounder who can build a reliable first product. Ideally they’ve worked on fintech or B2B software and enjoy talking to users.",
    },
    {
      key: "commitment",
      title: "How much time can you commit?",
      hint: "There’s no right answer. What can you realistically give this right now?",
      sample:
        "I’m ready to work on this full-time, and I’d like my cofounder to be full-time too.",
    },
    {
      key: "runway",
      title: "How long could you go without a salary?",
      hint: "A rough range is fine. This helps find someone with compatible expectations.",
      sample:
        "About twelve months. I’d like to get to paying customers well before that.",
    },
    {
      key: "location",
      title: "Where would you like to build?",
      hint: "Let me know where you’re based and how you feel about working remotely.",
      sample:
        "I’m based in Doha. In person would be ideal, but I’m open to a remote cofounder in the region if we can meet regularly.",
    },
    {
      key: "dealbreakers",
      title: "Anything that wouldn’t work for you?",
      hint: "Working style, values, availability—anything we should know before an introduction.",
      sample:
        "I want someone who is honest about their availability, takes customer feedback seriously, and is happy to start small rather than raise money before testing the idea.",
    },
  ];
  const defaultProfile = {
    name: "Rigad Irhasyi",
    role: "Product & operations builder",
    idea: questions[0].sample,
    offer: questions[1].sample,
    need: questions[2].sample,
    commitment: questions[3].sample,
    runway: questions[4].sample,
    location: questions[5].sample,
    dealbreakers: questions[6].sample,
  };
  const defaultPrefs = {
    location: "Doha, Qatar",
    work: "Flexible",
    availability: "Full-time",
    sector: "Fintech, B2B SaaS, applied AI",
    skills: "Full-stack engineering, backend, AI",
    notes: "Someone who likes starting with real customer problems.",
    hideContacts: true,
    reduceMotion: false,
  };
  const seed = () => ({
    version: 1,
    page: "matches",
    collapsed: false,
    chatWidth: 42,
    profile: { ...defaultProfile },
    confirmed: true,
    answers: {},
    interviewStep: -1,
    passed: [],
    saved: [],
    intros: [
      {
        id: "incoming-yusuf",
        person: "yusuf",
        direction: "received",
        status: "pending",
        note: "Your experience in financial operations is exactly what I’m looking for. I’d love to compare ideas for a simple fintech product.",
        date: "Today",
      },
      {
        id: "incoming-maya",
        person: "maya",
        direction: "received",
        status: "pending",
        note: "I’m exploring tools for small businesses in the Gulf. Your product and operations background sounds like a great complement to mine.",
        date: "Yesterday",
      },
    ],
    prefs: { ...defaultPrefs },
    messages: [],
    documents: [],
    carousel: 0,
    agent: "wasel",
  });
  const KEY = "fahem-wasel-ux-v1";
  let state;
  try {
    state = JSON.parse(localStorage.getItem(KEY));
    if (!state || state.version !== 1) state = seed();
  } catch {
    state = seed();
  }
  let ui = {
    matchTab: "suggested",
    introTab: "received",
    query: "",
    expanded: new Set(),
    account: false,
    mobileChat: false,
    busy: false,
    docTab: "all",
    modal: null,
    searchExpanded: false,
  };
  let toastTimer, callTimer, runTimer, lastFocus;
  const person = (id) => people.find((p) => p.id === id);
  const save = () => {
    try {
      localStorage.setItem(KEY, JSON.stringify(state));
    } catch {}
  };
  const pending = () =>
    state.intros.filter(
      (i) => i.direction === "received" && i.status === "pending",
    ).length;
  const introFor = (id) =>
    state.intros.find(
      (i) =>
        i.person === id && i.status !== "declined" && i.status !== "withdrawn",
    );
  const avatar = (p, large = false) =>
    `<div class="avatar ${large ? "large" : ""}" style="--avatar:${p.color}">${esc(p.initials)}</div>`;
  const currentName = () => state.profile.name.split(" ")[0];
  const navs = [
    ["interview", "Talk to Fahem", "chat"],
    ["profile", "My profile", "profile"],
    ["matches", "Your matches", "people"],
    ["introductions", "Introductions", "link"],
    ["preferences", "Matching preferences", "sliders"],
    ["documents", "Notes & documents", "doc"],
  ];
  const titles = {
    interview: "Talk to Fahem",
    profile: "My profile",
    matches: "Your matches",
    introductions: "Introductions",
    preferences: "Matching preferences",
    documents: "Notes & documents",
    settings: "Settings",
  };
  function toast(text, undo) {
    clearTimeout(toastTimer);
    $("#toasts").innerHTML =
      `<div class="toast">${I("check")}<span>${esc(text)}</span>${undo ? A("undo-pass", "Undo", "", "", 'data-id="' + esc(undo) + '"') : ""}</div>`;
    toastTimer = setTimeout(() => {
      $("#toasts").innerHTML = "";
    }, 4500);
  }
  function render() {
    document.documentElement.classList.toggle(
      "no-animation",
      !!state.prefs.reduceMotion,
    );
    $("#app").innerHTML =
      `<div class="app-shell ${state.collapsed ? "collapsed" : ""} ${ui.mobileChat ? "mobile-chat" : ""}">
 <aside class="sidebar" aria-label="Main navigation"><div class="brand row"><img src="../design/fahem-wasel/mark.svg" alt=""><span class="brand-name">Fahem & Wasel</span>${A("collapse", "", "panel", "icon-btn collapse-button", `aria-label="${state.collapsed ? "Expand" : "Collapse"} sidebar" title="${state.collapsed ? "Expand" : "Collapse"} sidebar"`)}</div>
 <nav class="nav">${navs.slice(0, 4).map(navButton).join("")}</nav><div class="nav-separator"></div><div class="nav-label">Your space</div><nav class="nav">${navs.slice(4).map(navButton).join("")}</nav>
 <div class="sidebar-bottom"><div class="getting-started"><div class="row between"><span>Your next chapter</span><span class="muted">${state.intros.some((i) => i.status === "accepted") ? "3" : state.confirmed ? "2" : "1"} of 3</span></div><div class="progress-line"><span style="width:${state.intros.some((i) => i.status === "accepted") ? "100" : state.confirmed ? "66" : "33"}%"></span></div>${A("navigate", I("check") + "<span>Let Fahem get to know you</span>", "", "checklist done", 'data-page="interview"')}${A("navigate", I(state.confirmed ? "check" : "profile") + "<span>Review your profile</span>", "", "checklist " + (state.confirmed ? "done" : ""), 'data-page="profile"')}${A("navigate", I("link") + "<span>Make your first introduction</span>", "", "checklist", 'data-page="introductions"')}</div>
 <div class="account"><button data-action="account" aria-label="Open account menu" aria-expanded="${ui.account}"><div class="avatar">${esc(
   state.profile.name
     .split(" ")
     .map((n) => n[0])
     .slice(0, 2)
     .join(""),
 )}</div><div class="account-meta">${esc(state.profile.name)}<small>Personal workspace</small></div>${I("down")}</button></div>
 ${ui.account ? `<div class="account-menu">${A("navigate", "My profile", "profile", "", 'data-page="profile"')}${A("navigate", "Talk to Fahem", "chat", "", 'data-page="interview"')}${A("navigate", "Notes & documents", "doc", "", 'data-page="documents"')}${A("navigate", "Settings", "settings", "", 'data-page="settings"')}${A("about", "About this prototype", "info", "")}${A("reset", "Reset sample data", "refresh", "")}</div>` : ""}</div></aside>
 <div class="main-panels">${chatPanel()}<main class="workspace" id="workspace" aria-label="${titles[state.page]}"><header class="panel-topbar"><span class="page-label">${titles[state.page]}</span><div class="topbar-actions"><span class="demo-label"><i class="dot"></i>Sample workspace</span>${A("help", "", "info", "icon-btn tooltip-wrap", `aria-label="About ${titles[state.page].toLowerCase()}" data-tip="Learn how ${titles[state.page].toLowerCase()} works"`)}${A("mobile-chat", "", "chat", "icon-btn mobile-chat-toggle", 'aria-label="Open agent conversation"')}</div></header><div class="page-scroll"><div class="page-content">${pageView()}</div></div></main></div>
 <nav class="mobile-nav" aria-label="Mobile navigation">${[
   ["chat", "Chat", "chat"],
   ["matches", "Matches", "people"],
   ["introductions", "Intros", "link"],
   ["profile", "Profile", "profile"],
   ["preferences", "Preferences", "sliders"],
 ]
   .map(([page, label, icon]) =>
     A(
       page === "chat" ? "mobile-chat" : "navigate",
       I(icon) +
         `<span>${label}${page === "introductions" && pending() ? " · " + pending() : ""}</span>`,
       "",
       (ui.mobileChat && page === "chat") ||
         (!ui.mobileChat && state.page === page)
         ? "active"
         : "",
       `data-page="${page}" ${(ui.mobileChat && page === "chat") || (!ui.mobileChat && state.page === page) ? 'aria-current="page"' : ""}`,
     ),
   )
   .join("")}</nav></div>`;
    save();
    if (
      state.page === "interview" &&
      state.interviewStep >= 0 &&
      state.interviewStep < questions.length
    ) {
      let q = questions[state.interviewStep];
      $("#interview-answer").value = state.answers[q.key] || "";
    }
    scrollChat();
  }
  function navButton([page, label, icon]) {
    return A(
      "navigate",
      I(icon) +
        `<span>${label}</span>${page === "introductions" && pending() ? `<span class="badge">${pending()}</span>` : ""}`,
      "",
      state.page === page ? "active" : "",
      `data-page="${page}" title="${label}" ${state.page === page ? 'aria-current="page"' : ""}`,
    );
  }
  function chatPanel() {
    const name = state.agent === "fahem" ? "Fahem" : "Wasel";
    return `<section class="chat-panel" aria-label="Agent conversation"><header class="panel-topbar"><div class="agent-title">${agentImg(state.agent)}<div><strong>${name}<span class="muted" style="font-weight:400"> · ${name === "Fahem" ? "The one who understands" : "The one who connects"}</span></strong><small><i class="dot"></i>Here to help you find your person</small></div></div><div class="chat-menu">${A("chat-options", "", "more", "icon-btn", 'aria-label="Conversation options"')}${A("mobile-workspace", "", "panel", "icon-btn mobile-chat-toggle", 'aria-label="Back to workspace"')}</div></header>
 <div class="chat-scroll" id="chat-scroll"><div class="date-label">Today, a new beginning</div>${defaultConversation()}${state.messages.map(messageView).join("")}${ui.busy ? '<div class="busy-dots" aria-label="Agent is replying"><i></i><i></i><i></i></div>' : ""}</div>
 <div class="chat-bottom"><div class="suggestions">${(state.agent === "fahem"
   ? [
       ["sample-answer", "Try a sample answer"],
       ["navigate", "Review my profile", "profile"],
       ["call", "Talk it through"],
     ]
   : [
       ["find", "Find my cofounder"],
       ["navigate", "Refine my preferences", "preferences"],
       ["why", "Why these people?"],
     ]
 )
   .map(([action, label, page]) =>
     A(action, label, "", "", page ? `data-page="${page}"` : ""),
   )
   .join(
     "",
   )}</div><form class="composer" id="chat-form">${A("attach", "", "plus", "icon-btn", 'type="button" aria-label="Attach a document"')}<textarea id="chat-input" rows="1" aria-label="Message to ${name}" placeholder="Ask ${name} anything…"></textarea>${A("voice", "", "mic", "icon-btn", 'type="button" aria-label="Try voice input"')}<button class="icon-btn send" type="submit" aria-label="Send message">${I("send")}</button></form><div class="composer-caption">A thoughtful introduction starts with a conversation.</div></div><div class="resize-handle" role="separator" aria-label="Resize conversation panel" aria-orientation="vertical" aria-valuemin="30" aria-valuemax="60" aria-valuenow="${state.chatWidth}" tabindex="0"></div></section>`;
  }
  function defaultConversation() {
    if (state.agent === "fahem")
      return `<div class="message"><div class="speaker fahem">${I("spark")} Fahem</div><p>Good to meet you, ${esc(currentName())}. Tell me what you’re building, and I’ll help put the right words around it.</p><p>I’ll ask one question at a time. You can type, or try the sample voice conversation.</p></div>${state.interviewStep >= 0 && state.interviewStep < questions.length ? `<div class="message"><div class="speaker fahem">Fahem</div><p>${questions[state.interviewStep].title}</p><p class="muted small">${questions[state.interviewStep].hint}</p></div>` : `<div class="message"><p>You can start a fresh interview in your workspace, or take a look at the sample profile I’ve prepared for you.</p>${A("start-interview", "Let’s get to know you", "arrow", "btn blue")}</div>`}`;
    return `<div class="message"><div class="speaker">${I("spark")} Wasel</div><p>${esc(currentName())}, you don’t need another person just like you. You need someone who brings what you’re missing.</p><p>In this sample search, I’m looking for builders who complement your product and operations experience, and want to solve the same kinds of problems.</p>${searchCard()}<p><strong style="font-weight:550">Lina is a good place to start.</strong> She’s spent six years building payment systems. You know what happens on the other side of those systems.</p><p>Take a look. Tell me who feels right, and we’ll go from there.</p><div class="footnote">No one sees your contact details until you both say yes.</div></div>`;
  }
  function suggestedPeople() {
    return people.filter(
      (p) =>
        !state.passed.includes(p.id) &&
        (state.prefs.work !== "In person" || p.location.startsWith("Doha")) &&
        (state.prefs.availability !== "Available now" || p.id !== "maya"),
    );
  }
  function searchCard() {
    const list = suggestedPeople();
    if (!list.length)
      return `<div class="search-card" style="padding:15px"><p style="font-size:12px">No suggestions left in this sample batch. Review your preferences or bring someone back from Passed.</p>${A("navigate", "Review matches", "arrow", "btn", 'data-page="matches"')}</div>`;
    state.carousel = Math.min(state.carousel, list.length - 1);
    let p = list[state.carousel];
    return `<div class="search-card"><button class="search-toggle" data-action="search-details" aria-expanded="${ui.searchExpanded}"><span class="row">${I("search")} Finding your cofounder</span><span class="row"><span class="tag green">${I("check")} Done</span>${I("down")}</span></button><div class="search-details ${ui.searchExpanded ? "open" : ""}" ${ui.searchExpanded ? "" : "inert"}><div>${[
      ["Read your confirmed profile", "Complete"],
      ["Check skills and availability", "5 sample profiles"],
      ["Look for complementary strengths", list.length + " suggestions"],
    ]
      .map(
        ([s, n]) =>
          `<div class="search-step">${I("check")}${s}<span>${n}</span></div>`,
      )
      .join(
        "",
      )}</div></div><div class="search-count">5 sample profiles <span style="color:#a6ad9b">→</span> ${list.length} people worth meeting</div><div class="mini-carousel"><div class="carousel-label"><span>A few good possibilities</span><span>${state.carousel + 1} of ${list.length}</span></div><div class="mini-person" key="${p.id}"><div class="row">${avatar(p)}<div><h4>${esc(p.name)}</h4><small>${esc(p.role)}</small></div></div><p>${esc(p.reason)}</p><div class="row">${A("detail", "View profile", "", "btn", 'data-id="' + p.id + '"')}${A("request", introFor(p.id) ? "View intro" : "Request intro", "", "btn primary", 'data-id="' + p.id + '"')}</div></div><div class="row carousel-controls">${A("carousel", "", "left", "", `aria-label="Previous match" ${state.carousel === 0 ? "disabled" : ""} data-dir="-1"`)}${A("carousel", "", "right", "", `aria-label="Next match" ${state.carousel >= list.length - 1 ? "disabled" : ""} data-dir="1"`)}</div></div>${A("navigate", `View ${list.length} ${list.length === 1 ? "match" : "matches"}`, "arrow", "btn view-all", 'data-page="matches"')}</div>`;
  }
  function messageView(m) {
    return `<div class="message ${m.role === "user" ? "user" : ""}">${m.role === "agent" ? `<div class="speaker ${m.agent || ""}">${esc(m.agent === "fahem" ? "Fahem" : "Wasel")}</div>` : ""}<p>${esc(m.text).replace(/\n/g, "<br>")}</p>${m.action ? A("navigate", esc(m.action.label), "arrow", "btn", `data-page="${esc(m.action.page)}"`) : ""}</div>`;
  }
  function scrollChat() {
    requestAnimationFrame(() => {
      let c = $("#chat-scroll");
      if (c) c.scrollTop = c.scrollHeight;
    });
  }
  function pageView() {
    return (
      {
        matches: matchesView,
        profile: profileView,
        interview: interviewView,
        introductions: introsView,
        preferences: preferencesView,
        documents: documentsView,
        settings: settingsView,
      }[state.page] || matchesView
    )();
  }
  function matchesList() {
    return people.filter((p) => {
      const tab = ui.matchTab;
      if (tab === "passed" && !state.passed.includes(p.id)) return false;
      if (
        tab === "saved" &&
        (!state.saved.includes(p.id) || state.passed.includes(p.id))
      )
        return false;
      if (tab === "suggested" && state.passed.includes(p.id)) return false;
      if (state.prefs.work === "In person" && !p.location.startsWith("Doha"))
        return false;
      if (state.prefs.availability === "Available now" && p.id === "maya")
        return false;
      return (p.name + " " + p.role + " " + p.tags.join(" "))
        .toLowerCase()
        .includes(ui.query.toLowerCase());
    });
  }
  function matchesView() {
    const list = matchesList();
    return `<div class="page-intro"><div class="row between"><div><h1>Find your other half.<br>For the business.</h1><p style="margin-top:12px">Different strengths. Shared ambition.<br>A few people we think you should meet.</p></div>${A("find", "", "refresh", "icon-btn", 'aria-label="Refresh matches" title="Refresh matches"')}</div></div><div class="agent-note">${agentImg("wasel")}<p><strong>Look for what you can build together.</strong><br>These people bring skills you’re looking for—and are looking for someone like you.</p></div><div class="tabs" aria-label="Match categories">${[
      ["suggested", "For you", people.length - state.passed.length],
      [
        "saved",
        "Saved",
        state.saved.filter((id) => !state.passed.includes(id)).length,
      ],
      ["passed", "Passed", state.passed.length],
    ]
      .map(([id, label, count]) =>
        A(
          "match-tab",
          label + `<span class="count">${count}</span>`,
          "",
          ui.matchTab === id ? "active" : "",
          `data-tab="${id}" aria-pressed="${ui.matchTab === id}"`,
        ),
      )
      .join(
        "",
      )}</div><div class="toolbar"><span class="filter-count">${list.length} ${list.length === 1 ? "person" : "people"} ${ui.matchTab === "suggested" ? "worth a conversation" : ui.matchTab === "saved" ? "saved for later" : "passed"}</span><div class="search-input">${I("search")}<input id="match-search" placeholder="Find a person…" aria-label="Search matches" value="${esc(ui.query)}"></div></div><div id="match-list">${list.length ? list.map(matchCard).join("") : empty("No one here just yet.", ui.query ? "Try another name or skill." : ui.matchTab === "saved" ? "Save someone you’d like to come back to." : ui.matchTab === "passed" ? "People you pass on will appear here. You can bring them back anytime." : "Try opening up your preferences to find more possibilities.", ui.query ? "clear-search" : ui.matchTab === "suggested" ? "preferences-action" : "show-suggested", ui.query ? "Clear search" : ui.matchTab === "suggested" ? "Review preferences" : "Browse your matches")}</div><div class="match-bottom-note">All people shown are fictional sample profiles.</div>`;
  }
  function matchCard(p) {
    let intro = introFor(p.id),
      passed = state.passed.includes(p.id),
      saved = state.saved.includes(p.id),
      expanded = ui.expanded.has(p.id);
    return `<article class="match-card ${expanded ? "expanded" : ""}" id="match-${p.id}"><div class="match-summary"><div class="row">${avatar(p)}<div class="person-identity"><h3>${esc(p.name)}</h3><div class="role">${esc(p.role)}</div><div class="muted small" style="font-size:10px;margin-top:4px">${esc(p.location)}</div></div><div class="fit-label">${I(p.fit === "Strong fit" ? "spark" : "chat")}<span>${p.fit}</span></div></div><div class="row wrap match-tags">${p.tags.map((t) => `<span class="tag">${esc(t)}</span>`).join("")}</div><p class="match-reason">${esc(p.reason)}</p><div class="match-footer"><button class="detail-toggle" data-action="expand" data-id="${p.id}" aria-expanded="${expanded}">Why you two ${I("down")}</button><div class="row">${passed ? A("undo-pass", "Bring back", "", "btn", `data-id="${p.id}"`) : `${A("save", saved ? "" : "", saved ? "check" : "star", "icon-btn", `data-id="${p.id}" aria-label="${saved ? "Unsave" : "Save"} ${p.name}" title="${saved ? "Saved" : "Save for later"}" aria-pressed="${saved}"`)}${A("pass", "Pass", "", "btn quiet", `data-id="${p.id}"`)}${A("request", intro ? (intro.status === "accepted" ? "Connected" : "Intro pending") : "Request intro", intro?.status === "accepted" ? "check" : "", "btn primary", `data-id="${p.id}"`)}`}</div></div></div><div class="match-details" ${expanded ? "" : "inert"}><div><div class="details-inner"><h4>A good partnership works both ways.</h4>${p.reasons.map((r) => `<div class="row" style="align-items:flex-start;margin:11px 0;font-size:12px;line-height:1.75;color:#68725c">${I("check")}<span>${esc(r)}</span></div>`).join("")}<div class="evidence"><p>“${esc(p.quote)}”</p><small>${esc(p.name.split(" ")[0])}, in their conversation with Fahem</small></div><div class="evidence"><p>“${esc(state.profile.need)}”</p><small>You, in your profile · ${A("navigate", "Edit", "", "text-btn", 'data-page="profile"')}</small></div><div class="two-col"><div class="detail-fact"><span>What they bring</span>${esc(p.offer)}</div><div class="detail-fact"><span>What they’re looking for</span>${esc(p.need)}</div><div class="detail-fact"><span>Commitment</span>${esc(p.commitment)}</div><div class="detail-fact"><span>Runway</span>${esc(p.runway)}</div></div><div class="row between" style="margin-top:20px"><span class="small muted" style="font-size:10px">From a sample interview. No contact details shared.</span>${A("detail", "Full profile", "arrow", "text-btn", `data-id="${p.id}"`)}</div></div></div></div></article>`;
  }
  function profileView() {
    return `<div class="page-intro"><div class="row between"><div><h1>You, in your own words.</h1><p style="margin-top:10px">A starting point for the right conversation.</p></div><span class="tag ${state.confirmed ? "green" : "blue"}">${I(state.confirmed ? "check" : "edit")}${state.confirmed ? "Confirmed" : "Ready to review"}</span></div></div><div class="profile-hero"><div class="row between"><div><button data-action="edit" data-field="name" style="text-align:left;padding:0"><h2>${esc(state.profile.name)}</h2></button><button class="role" data-action="edit" data-field="role" style="padding:0;text-align:left">${esc(state.profile.role)}</button></div><div class="profile-avatar-wrap"><div class="avatar large">${esc(
      state.profile.name
        .split(" ")
        .map((n) => n[0])
        .slice(0, 2)
        .join(""),
    )}</div>${A("avatar", "", "edit", "", 'aria-label="Change profile appearance"')}</div></div><div class="location row">${I("pin")} ${esc(state.profile.location.toLowerCase().includes("doha") ? "Doha, Qatar" : state.profile.location.slice(0, 60))}<span class="tag green" style="margin-left:auto"><i class="dot"></i>Open to a cofounder</span></div></div>${[
      ["idea", "What I’m building"],
      ["offer", "What I bring"],
      ["need", "Who I’m looking for"],
      ["commitment", "My commitment"],
      ["runway", "Time to build"],
      ["location", "Where I’d like to work"],
      ["dealbreakers", "What matters to me"],
    ]
      .map(
        ([key, label]) =>
          `<section class="profile-section"><div class="row between"><h3>${label}</h3>${A("edit", "Edit", "", "text-btn", `data-field="${key}" aria-label="Edit ${label.toLowerCase()}"`)}</div><button class="profile-field" data-action="edit" data-field="${key}">${esc(state.profile[key])}${I("edit", "edit-icon")}</button>${A("evidence", I("chat") + " From your conversation with Fahem", "", "evidence-toggle", `data-field="${key}"`)}</section>`,
      )
      .join(
        "",
      )}<div class="profile-confirm">${I("shield")}<div><h3>${state.confirmed ? "Feels like you? You’re ready." : "Does this sound like you?"}</h3><p>${state.confirmed ? "You can refine this anytime." : "Check the details before Wasel starts looking."}</p></div>${A(state.confirmed ? "find" : "confirm-profile", state.confirmed ? "See my matches" : "Confirm my profile", "arrow", "btn primary")}</div><div class="sample-stamp">${I("info")}This is a sample profile. Everything stays in this browser.</div>`;
  }
  function interviewView() {
    let s = state.interviewStep;
    if (s < 0)
      return `<div class="interview-hero"><div class="duo">${agentImg("fahem", "")}${agentImg("wasel", "")}</div><h1>First, let’s get<br>to know you.</h1><p>A little about your idea. A little about you. Then, the people who could help you build it.</p>${A("start-interview", "Talk to Fahem", "arrow", "btn blue")}<div style="margin-top:13px">${A("call", "Try a voice conversation", "phone", "text-btn")}</div></div><div class="interview-stages">${[
        [
          "Tell your story",
          "Fahem asks a few thoughtful questions. About six minutes.",
        ],
        [
          "Make it yours",
          "Review your profile. Keep what feels right. Change what doesn’t.",
        ],
        [
          "Meet your possibilities",
          "Wasel finds people whose strengths complement yours.",
        ],
      ]
        .map(
          ([t, d], i) =>
            `<div class="stage"><span class="stage-number">${i + 1}</span><div><h3>${t}</h3><p>${d}</p></div></div>`,
        )
        .join(
          "",
        )}</div><div class="row between small muted" style="font-size:11px"><span>Prefer to explore first?</span>${A("navigate", "View sample matches", "arrow", "text-btn", 'data-page="matches"')}</div>`;
    if (s >= questions.length)
      return `<div class="interview-hero">${agentImg("fahem", "agent-avatar large")}<h1 style="margin-top:25px">That sounds like<br>a good beginning.</h1><p>I’ve brought your answers together. Take a moment to make sure it sounds like you.</p>${A("navigate", "Review my profile", "arrow", "btn blue", 'data-page="profile"')}</div><div class="agent-note">${I("shield")}<p>Your profile is a draft until you confirm it. Wasel will use only the details you approve.</p></div>${A("start-interview", "Start the interview again", "", "text-btn")}`;
    let q = questions[s];
    return `<div class="page-intro"><h1>A little more about you.</h1><p style="margin-top:10px">Take your time. This is a conversation, not a pitch.</p></div><div class="interview-progress"><div class="row between small muted"><span>Your conversation with Fahem</span><span>${s + 1} of ${questions.length}</span></div><div class="progress-line"><span style="width:${((s + 1) / questions.length) * 100}%"></span></div></div><form id="interview-form" class="question-card">${agentImg("fahem")}<h2>${q.title}</h2><p>${q.hint}</p><textarea id="interview-answer" aria-label="Your answer" placeholder="In your own words…" required></textarea><div class="row between">${A("sample-answer", "Use a sample answer", "", "text-btn", 'type="button"')}${A("voice", "Try voice", "mic", "btn quiet", 'type="button"')}</div><div class="question-nav">${A("question-back", "Back", "left", "btn quiet", `type="button" ${s === 0 ? "disabled" : ""}`)}<span>${s === questions.length - 1 ? "Last question. You’re nearly there." : "A few words or a whole story."}</span><button class="btn blue" type="submit">${s === questions.length - 1 ? "Create my profile" : "Continue"}${I("arrow")}</button></div></form><div class="interview-note">${I("shield")} Only what you choose to share goes into your profile. You’ll review everything first.</div>`;
  }
  function introsView() {
    let tab = ui.introTab;
    let entries = state.intros.filter((i) =>
      tab === "connected"
        ? i.status === "accepted"
        : tab === "closed"
          ? ["declined", "withdrawn"].includes(i.status)
          : i.direction === tab && i.status === "pending",
    );
    return `<div class="page-intro"><h1>A conversation away.</h1><p style="margin-top:10px">Good introductions need a yes from both sides.</p></div><div class="tabs" aria-label="Introduction categories">${[
      ["received", "Received"],
      ["sent", "Sent"],
      ["connected", "Connected"],
      ["closed", "Closed"],
    ]
      .map(([id, label]) => {
        let count = state.intros.filter((i) =>
          id === "connected"
            ? i.status === "accepted"
            : id === "closed"
              ? ["declined", "withdrawn"].includes(i.status)
              : i.direction === id && i.status === "pending",
        ).length;
        return A(
          "intro-tab",
          label + `<span class="count">${count}</span>`,
          "",
          id === tab ? "active" : "",
          `data-tab="${id}" aria-pressed="${id === tab}"`,
        );
      })
      .join(
        "",
      )}</div>${entries.length ? entries.map(introCard).join("") : empty(tab === "connected" ? "Your first hello starts here." : tab === "sent" ? "No introductions waiting." : tab === "closed" ? "Nothing closed." : "You’re all caught up.", tab === "connected" ? "When you both say yes, your contact details become available here." : tab === "sent" ? "Find someone you’d like to build with and request an introduction." : "There’s a good conversation out there. Take a look at your matches.", "show-suggested", "Explore your matches")}<div class="agent-note">${agentImg("wasel")}<p><strong>A little trust goes a long way.</strong><br>You choose who to meet. Your email stays private until an introduction is accepted.</p></div>`;
  }
  function introCard(i) {
    let p = person(i.person);
    return `<article class="intro-card" id="intro-${i.id}"><div class="row">${avatar(p)}<div class="person-identity"><h3>${esc(p.name)}</h3><div class="role">${esc(p.role)}</div></div><span class="tag ${i.status === "accepted" ? "green" : i.status === "pending" ? "orange" : ""}">${i.status === "accepted" ? "Connected" : i.status === "declined" ? "Passed this time" : i.status === "withdrawn" ? "Withdrawn" : i.direction === "received" ? "Wants to meet" : "Awaiting a reply"}</span></div><p>“${esc(i.note)}”</p>${i.status === "pending" ? `<div class="intro-timeline"><span class="complete">${I("check")} ${i.direction === "received" ? p.name.split(" ")[0] : "You"} said yes</span><span class="line"></span><span>${i.direction === "received" ? "Your turn" : p.name.split(" ")[0] + "’s turn"}</span><span class="line"></span><span>Introduction</span></div><div class="intro-actions">${A("detail", "View profile", "", "text-btn", `data-id="${p.id}"`)}<div class="row">${i.direction === "received" ? `${A("decline", "Not this time", "", "btn quiet", `data-id="${i.id}"`)}${A("accept", "Accept introduction", "link", "btn primary", `data-id="${i.id}"`)}` : `${A("withdraw", "Withdraw", "", "text-btn", `data-id="${i.id}"`)}${A("preview-recipient", "Preview recipient", "", "btn", `data-id="${i.id}"`)}`}</div></div>` : i.status === "accepted" ? `<div class="contact-panel"><div class="row">${I("check")}<strong style="font-size:12px">You both said yes. Say hello.</strong></div><a href="mailto:${p.email}">${p.email}</a><small>Fictional sample email. ${A("copy-contact", "Copy contact", "", "text-btn", `data-id="${p.id}"`)}</small></div>` : `<div class="row between small muted"><span>No contact details were shared.</span>${A("show-suggested", "Find someone else", "arrow", "text-btn")}</div>`}</article>`;
  }
  function preferencesView() {
    const p = state.prefs;
    return `<div class="page-intro"><h1>Who would you build with?</h1><p style="margin-top:10px">Give Wasel a little direction. Leave room for a surprise.</p></div><form id="prefs-form"><section class="settings-section"><h2>Skills & interests</h2><div class="form-group"><label for="pref-skills">Skills you’re looking for</label><input name="skills" id="pref-skills" value="${esc(p.skills)}"><small>Think about what complements your strengths.</small></div><div class="form-group"><label for="pref-sector">Areas you’d like to explore</label><input name="sector" id="pref-sector" value="${esc(p.sector)}"></div></section><section class="settings-section"><h2>Working together</h2><div class="form-group"><label for="pref-location">Where you’re based</label><input id="pref-location" name="location" value="${esc(p.location)}"></div><div class="form-group"><label for="pref-work">How you’d like to work</label><select name="work" id="pref-work">${["Flexible", "In person", "Remote"].map((v) => `<option ${v === p.work ? "selected" : ""}>${v}</option>`).join("")}</select><small>“In person” keeps this sample list to people based in Doha.</small></div><div class="form-group"><label for="pref-availability">Their availability</label><select name="availability" id="pref-availability">${["Full-time", "Available now", "Open to a gradual start"].map((v) => `<option ${v === p.availability ? "selected" : ""}>${v}</option>`).join("")}</select><small>“Available now” excludes sample profiles starting later.</small></div><div class="form-group"><label for="pref-notes">Anything else that matters?</label><textarea name="notes" id="pref-notes">${esc(p.notes)}</textarea></div></section><div class="sticky-save"><span>Preferences are saved on this device.</span><button type="submit" class="btn primary">Save preferences ${I("check")}</button></div></form><div class="settings-note">Sample matching responds to working location and availability. The other fields are ready for the matching service.</div>`;
  }
  function documentsView() {
    const docs = [
      {
        id: "interview",
        title: "Your conversation with Fahem",
        type: "Interview notes",
        date: "Today · 7 questions",
        icon: "chat",
      },
      {
        id: "profile",
        title: "Your cofounder profile",
        type: "Profile summary",
        date: "Today · Latest version",
        icon: "profile",
      },
      ...state.documents,
    ];
    const list = docs.filter(
      (d) =>
        (ui.docTab === "all" ||
          (ui.docTab === "notes"
            ? d.id === "interview"
            : d.id !== "interview")) &&
        d.title.toLowerCase().includes(ui.query.toLowerCase()),
    );
    return `<div class="page-intro"><div class="row between"><div><h1>The story so far.</h1><p style="margin-top:10px">Your words, notes and supporting documents.</p></div>${A("attach", "", "plus", "icon-btn", 'aria-label="Add a document"')}</div></div><div class="tabs">${[
      ["all", "Everything"],
      ["notes", "Conversations"],
      ["files", "Documents"],
    ]
      .map(([id, t]) =>
        A(
          "doc-tab",
          t,
          "",
          ui.docTab === id ? "active" : "",
          `data-tab="${id}" aria-pressed="${id === ui.docTab}"`,
        ),
      )
      .join(
        "",
      )}</div><div class="toolbar"><span class="filter-count">${list.length} items</span>${A("attach", "Add document", "plus", "btn")}</div>${list.map((d) => `<div class="document-row"><div class="doc-icon">${I(d.icon || "doc")}</div><div><h3>${esc(d.title)}</h3><small>${esc(d.date)} · ${esc(d.type)}</small></div>${A("open-doc", "", "right", "icon-btn", `data-id="${esc(d.id)}" aria-label="Open ${esc(d.title)}"`)}</div>`).join("")}${!list.length ? empty("A little room for context.", "Add a document or revisit your conversation with Fahem.", "attach", "Add a document") : ""}<div class="settings-note">Files added here are a local UX preview. Only the file name is kept; documents are not uploaded or read.</div>`;
  }
  function settingsView() {
    return `<div class="page-intro"><h1>Make yourself at home.</h1><p style="margin-top:10px">A few small things, just how you like them.</p></div><section class="settings-section"><h2>Your experience</h2><div class="switch-row"><div><h3>Reduce motion</h3><p>Keep transitions and animations still.</p></div><button class="switch" data-action="motion" role="switch" aria-label="Reduce motion" aria-checked="${!!state.prefs.reduceMotion}"><span></span></button></div><div class="switch-row"><div><h3>Contact details stay private</h3><p>Only shared after you both accept an introduction.</p></div><span class="tag green">${I("shield")} Always on</span></div>${A("edit", "Edit your name", "edit", "btn", 'data-field="name"')}</section><section class="settings-section"><h2>About this workspace</h2><p class="small muted">A frontend prototype for Fahem & Wasel. All matches, agent replies and introductions are samples. No AI or real messaging service is connected.</p><div class="stack">${A("export", "Download your demo data", "download", "btn")}${A("reset", "Reset sample workspace", "refresh", "btn")}</div><div class="settings-note">Reset removes only this prototype’s saved state in this browser.</div></section>`;
  }
  function empty(title, desc, act, label) {
    return `<div class="empty"><div class="empty-symbol">${I("people")}</div><h2>${title}</h2><p>${desc}</p>${A(act, label, "arrow", "btn")}</div>`;
  }
  function navigate(page) {
    if (!titles[page]) return;
    const input = $("#chat-input");
    if (input) ui.chatDraft = input.value;
    state.page = page;
    ui.query = "";
    ui.mobileChat = false;
    ui.account = false;
    if (page === "interview") state.agent = "fahem";
    render();
    if (ui.chatDraft && $("#chat-input")) $("#chat-input").value = ui.chatDraft;
    $(".page-scroll")?.scrollTo(0, 0);
  }
  function refreshChatCard() {
    const old = $(".search-card");
    if (old) old.outerHTML = searchCard();
  }
  function updateWorkspace() {
    refreshChatCard();
    const root = $(".page-content");
    const focus = document.activeElement?.id;
    const pos = document.activeElement?.selectionStart;
    root.innerHTML = pageView();
    if (focus && $("#" + focus)) {
      const el = $("#" + focus);
      el.focus();
      if (typeof pos === "number" && el.setSelectionRange)
        el.setSelectionRange(pos, pos);
    }
  }
  function openModal(title, body, actions = "", wide = false) {
    lastFocus = document.activeElement;
    ui.modal = title;
    $("#overlays").innerHTML =
      `<div class="overlay"><section class="modal ${wide ? "wide" : ""}" role="dialog" aria-modal="true" aria-labelledby="modal-title" tabindex="-1"><div class="modal-header"><h2 id="modal-title">${title}</h2>${A("close", "", "x", "icon-btn modal-close", 'aria-label="Close dialog"')}</div>${body}${actions ? `<div class="modal-actions">${actions}</div>` : ""}</section></div>`;
    $("#app").inert = true;
    requestAnimationFrame(() => {
      const target =
        $('.modal textarea,.modal input:not([type="file"]),.modal select') ||
        $(".modal");
      target?.focus();
    });
  }
  function closeModal() {
    $("#app").inert = false;
    clearInterval(callTimer);
    clearTimeout(runTimer);
    $("#overlays").innerHTML = "";
    ui.modal = null;
    lastFocus?.isConnected && lastFocus.focus({ preventScroll: true });
  }
  function detailModal(id) {
    const p = person(id);
    if (!p) return;
    let intro = introFor(id);
    openModal(
      p.name,
      `<div class="row">${avatar(p, true)}<div><h3>${p.role}</h3><p style="margin:5px 0 0;font-size:12px">${p.location}</p></div></div><div class="row wrap" style="margin:20px 0">${p.tags.map((t) => `<span class="tag">${t}</span>`).join("")}</div><p>${p.bio}</p><div class="divider"></div><h3>Why you two</h3>${p.reasons.map((r) => `<p style="font-size:12px;margin:12px 0">${I("check")} ${r}</p>`).join("")}<blockquote>“${p.quote}”<br><small>From ${p.name.split(" ")[0]}’s sample conversation</small></blockquote><div class="two-col"><div class="detail-fact"><span>What they bring</span>${p.offer}</div><div class="detail-fact"><span>What they need</span>${p.need}</div><div class="detail-fact"><span>Availability</span>${p.commitment}</div><div class="detail-fact"><span>Time to build</span>${p.runway}</div></div><div class="sample-stamp" style="margin-top:20px">${I("shield")}Fictional sample profile. Contact details are private.</div>`,
      A("close", "Close", "", "btn") +
        A(
          "request",
          intro ? "View introduction" : "Request intro",
          "link",
          "btn primary",
          `data-id="${id}"`,
        ),
      true,
    );
  }
  function requestModal(id) {
    const p = person(id);
    if (!p) return;
    let existing = introFor(id);
    if (existing) {
      closeModal();
      navigate("introductions");
      ui.introTab =
        existing.status === "accepted" ? "connected" : existing.direction;
      updateWorkspace();
      return;
    }
    openModal(
      `Say hello to ${p.name.split(" ")[0]}.`,
      `<div class="row" style="margin-bottom:18px">${avatar(p)}<div><h3>${p.name}</h3><span class="small muted">${p.role}</span></div></div><p>A little context makes a better introduction. Edit this note to make it sound like you.</p><label for="intro-note">Your introduction note</label><textarea id="intro-note" maxlength="1000" style="margin-top:9px">${esc(`Hi ${p.name.split(" ")[0]}, I’m exploring financial workflow software for small businesses. Your ${p.id === "omar" ? "AI" : "engineering"} experience feels like a great complement to my product and operations background. I’d love to compare ideas and see what we could build together.`)}</textarea><div class="word-count" id="intro-count">Personal, specific and brief.</div><div class="row small muted" style="margin-top:18px;align-items:flex-start;line-height:1.8">${I("shield")}Only this note and your profile are shared. Contact details appear after you both say yes.</div>`,
      A("close", "Not now", "", "btn") +
        A(
          "send-intro",
          "Request introduction",
          "arrow",
          "btn primary",
          `data-id="${id}"`,
        ),
    );
  }
  function editModal(field) {
    let labels = {
      name: "Your name",
      role: "Your headline",
      ...Object.fromEntries(questions.map((q) => [q.key, q.title])),
    };
    if (!labels[field]) return;
    let value = state.profile[field];
    openModal(
      labels[field],
      `<p>${field === "name" || field === "role" ? "Make this feel like you." : "Keep it specific and in your own words. Wasel will use your updated profile for future matches."}</p><label class="sr-label" for="edit-field">${labels[field]}</label>${field === "name" || field === "role" ? `<input id="edit-field" value="${esc(value)}" maxlength="100" style="width:100%;margin-top:9px">` : `<textarea id="edit-field" maxlength="1600" style="margin-top:9px">${esc(value)}</textarea>`}<div class="word-count" id="edit-count">${value.length} characters</div>`,
      A("close", "Cancel", "", "btn") +
        A(
          "save-field",
          "Save changes",
          "check",
          "btn primary",
          `data-field="${field}" disabled`,
        ),
    );
  }
  function startInterview() {
    closeModal();
    state.agent = "fahem";
    state.page = "interview";
    state.interviewStep = 0;
    state.answers = {};
    state.messages = [];
    ui.mobileChat = false;
    render();
    $("#interview-answer")?.focus();
  }
  function submitInterview(text) {
    text = text.trim();
    if (!text) return;
    let q = questions[state.interviewStep];
    if (!q) return;
    state.answers[q.key] = text;
    state.messages.push({ role: "user", text });
    state.interviewStep++;
    if (state.interviewStep >= questions.length) {
      state.profile = { ...state.profile, ...state.answers };
      state.confirmed = false;
      state.messages.push({
        role: "agent",
        agent: "fahem",
        text: "Thank you. I’ve put your answers into a profile, keeping your own words. Review it, change anything that doesn’t feel right, then let Wasel take it from there.",
        action: { label: "Review my profile", page: "profile" },
      });
    } else
      state.messages.push({
        role: "agent",
        agent: "fahem",
        text: questions[state.interviewStep].title,
      });
    render();
    $("#interview-answer")?.focus();
  }
  function sampleAnswer() {
    let q = questions[state.interviewStep];
    if (q) {
      if ($("#interview-answer")) {
        $("#interview-answer").value = q.sample;
        state.answers[q.key] = q.sample;
        save();
        $("#interview-answer").focus();
      } else {
        submitChat(q.sample);
      }
    } else {
      navigate("interview");
      toast("Start the interview to try the sample answers.");
    }
  }
  function findMatches() {
    if (!state.confirmed) {
      openModal(
        "First, make sure it sounds like you.",
        "<p>Review and confirm your profile so Wasel has the right starting point.</p>",
        A("close", "Not now", "", "btn") +
          A("review-profile", "Review profile", "arrow", "btn blue"),
      );
      return;
    }
    state.agent = "wasel";
    let step = 0;
    let steps = [
      "Read your confirmed profile",
      "Check skills and availability",
      "Look for complementary strengths",
    ];
    const body = () =>
      `<div class="row" style="margin-bottom:20px">${agentImg("wasel")}<p style="margin:0">A few good people. Give me a moment.</p></div>${steps.map((t, i) => `<div class="loading-step">${i < step ? I("check") : i === step ? '<span class="spinner"></span>' : I("clock")}<span>${t}</span>${i < step ? '<span class="tag green" style="margin-left:auto">Done</span>' : ""}</div>`).join("")}<div class="settings-note">Previewing the sample matching flow.</div>`;
    openModal("Finding your people.", body());
    function tick() {
      if (!ui.modal) return;
      step++;
      if (step === 3) {
        closeModal();
        ui.matchTab = "suggested";
        navigate("matches");
        state.messages.push({
          role: "agent",
          agent: "wasel",
          text: `I’ve refreshed your sample matches. ${matchesList().length} people fit your current location and availability preferences. Open “Why you two” to see the thinking behind each one.`,
          action: { label: "View matches", page: "matches" },
        });
        render();
        toast("Your matches are ready.");
        return;
      }
      let m = $(".modal");
      m.querySelectorAll(".loading-step").forEach((e) => e.remove());
      let note = $(".modal .settings-note");
      note?.remove();
      let div = document.createElement("div");
      div.innerHTML = body();
      m.querySelector(".modal-header").nextElementSibling?.remove();
      m.append(div);
      runTimer = setTimeout(tick, 650);
    }
    runTimer = setTimeout(tick, 650);
  }
  function voiceModal(mode = "voice") {
    let q = questions[state.interviewStep] || questions[0];
    ui.voiceMode = mode;
    ui.callSeconds = 0;
    ui.callPaused = false;
    openModal(
      mode === "call" ? "A conversation with Fahem" : "Try a voice answer",
      `<div class="call-view"><div class="call-badge"><span class="tag blue">Interactive sample · no microphone used</span></div>${agentImg("fahem")}<h2>${mode === "call" ? "Let’s talk it through." : "Your story, in your voice."}</h2><p>${esc(q.title)}</p><div class="waveform" aria-hidden="true">${Array.from({ length: 21 }, (_, i) => `<i style="--i:${i};background:${i % 3 === 0 ? "#4667cb" : "#adbce6"}"></i>`).join("")}</div><span class="call-time">00:00</span><div class="call-controls">${A("pause-call", "", "pause", "icon-btn", 'aria-label="Pause sample conversation"')}${A("end-call", "", "phone", "icon-btn end-call", 'aria-label="End sample conversation"')}</div><div class="voice-sample"><div class="small muted" style="margin-bottom:8px">Sample transcript</div><p>${esc(q.sample)}</p></div><p class="small muted" style="margin-top:15px;font-size:10px">Use this answer to preview transcription and review. No audio is recorded or sent.</p></div>`,
      A("close", "Cancel", "", "btn") +
        A("use-transcript", "Use this answer", "check", "btn blue"),
    );
    callTimer = setInterval(() => {
      if (!ui.callPaused) {
        ui.callSeconds++;
        let el = $(".call-time");
        if (el)
          el.textContent = `${String(Math.floor(ui.callSeconds / 60)).padStart(2, "0")}:${String(ui.callSeconds % 60).padStart(2, "0")}`;
      }
    }, 1000);
  }
  function attachModal() {
    openModal(
      "A little more context.",
      `<p>Add a document to preview how it would sit alongside your conversation. Nothing is uploaded or read.</p><div class="attachment-area">${I("doc")}<div class="small">Choose a CV, pitch deck or a few notes.</div><input id="local-file" type="file" accept=".pdf,.txt,.md,.doc,.docx" aria-label="Choose local document"></div><p id="file-selection" style="font-size:11px;margin-top:15px">Or use a sample document to explore the flow.</p>`,
      A("sample-doc", "Use sample CV", "", "btn") +
        A("add-file", "Add to my documents", "plus", "btn primary", "disabled"),
    );
  }
  function openDoc(id) {
    if (id === "interview") {
      openModal(
        "Your conversation with Fahem",
        questions
          .map(
            (q) =>
              `<div style="margin-bottom:22px"><h3>${q.title}</h3><p style="margin-top:8px">${esc(state.answers[q.key] || state.profile[q.key])}</p></div>`,
          )
          .join(""),
        A(
          "download-doc",
          "Download notes",
          "download",
          "btn",
          `data-id="${id}"`,
        ) + A("close", "Close", "", "btn primary"),
        true,
      );
    } else if (id === "profile") {
      closeModal();
      navigate("profile");
    } else {
      let d = state.documents.find((d) => d.id === id);
      if (!d) return;
      openModal(
        esc(d.title),
        `<div class="row" style="margin-bottom:20px"><div class="doc-icon">${I("doc")}</div><div><h3>${esc(d.type)}</h3><span class="small muted">Added ${esc(d.date)}</span></div></div><p>${d.sample ? "Sample CV: Product and operations experience, financial workflows, customer discovery, Python and automation." : "This document is represented by its file name only. Its contents were not read or uploaded."}</p><div class="settings-note">In the connected app, you’ll review any profile updates suggested from your documents.</div>`,
        A(
          "remove-doc",
          "Remove document",
          "",
          "btn danger",
          `data-id="${id}"`,
        ) + A("close", "Close", "", "btn primary"),
      );
    }
  }
  function download(name, text, type = "text/plain") {
    const blob = new Blob([text], { type });
    const url = URL.createObjectURL(blob);
    let a = document.createElement("a");
    a.href = url;
    a.download = name;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function submitChat(text) {
    text = text.trim();
    if (!text || ui.busy) return;
    if (
      state.agent === "fahem" &&
      state.interviewStep >= 0 &&
      state.interviewStep < questions.length
    ) {
      submitInterview(text);
      return;
    }
    state.messages.push({ role: "user", text });
    ui.busy = true;
    render();
    setTimeout(() => {
      ui.busy = false;
      let lower = text.toLowerCase();
      let response, action;
      if (/hello|hi\b|hey/.test(lower)) {
        response = `Hi ${currentName()}. We can explore your matches, refine what you’re looking for, or start with your story.`;
      } else if (/why|reason|fit/.test(lower)) {
        response =
          "I’m looking for complementary strengths, compatible availability, and something you both want to build. For example, Lina brings payment engineering while you bring product and financial operations. Every match has supporting quotes under “Why you two”.";
        action = { label: "See why you fit", page: "matches" };
      } else if (/profile|skill|about me/.test(lower)) {
        response =
          "Your profile should sound like you. Open any section to edit it, or ask Fahem to start a fresh interview.";
        action = { label: "Review your profile", page: "profile" };
      } else if (/intro|meet|contact/.test(lower)) {
        response =
          "Open a profile and choose “Request intro”. You’ll review the note first. Once the other person accepts, contact details appear in your introductions.";
        action = { label: "View introductions", page: "introductions" };
      } else if (/remote|location|preference|full.time/.test(lower)) {
        response =
          "You can adjust location and availability in your matching preferences. I’ll keep the sample matches in step with those choices.";
        action = { label: "Refine your preferences", page: "preferences" };
      } else if (/interview|start|story/.test(lower)) {
        response =
          "Fahem will take you through seven questions about your idea, your strengths, and the partner you’re looking for. You can use sample answers to move through it quickly.";
        action = { label: "Talk to Fahem", page: "interview" };
      } else {
        response =
          "For this preview, I can walk you through your profile, explain the sample matches, or help you explore an introduction. Which would you like to try?";
      }
      state.messages.push({
        role: "agent",
        agent: state.agent,
        text: response,
        action,
      });
      render();
    }, 650);
  }
  document.addEventListener("click", async (e) => {
    const el = e.target.closest("[data-action]");
    if (!el || el.disabled) return;
    const { action, id, field, page, tab } = el.dataset;
    switch (action) {
      case "navigate":
        closeModal();
        navigate(page);
        break;
      case "collapse":
        state.collapsed = !state.collapsed;
        render();
        break;
      case "account":
        ui.account = !ui.account;
        render();
        break;
      case "mobile-chat":
        ui.mobileChat = true;
        ui.account = false;
        render();
        break;
      case "mobile-workspace":
        ui.mobileChat = false;
        render();
        break;
      case "match-tab":
        ui.matchTab = tab;
        ui.query = "";
        updateWorkspace();
        break;
      case "intro-tab":
        ui.introTab = tab;
        updateWorkspace();
        break;
      case "doc-tab":
        ui.docTab = tab;
        updateWorkspace();
        break;
      case "expand": {
        const card = $("#match-" + id);
        if (!card) break;
        ui.expanded.has(id) ? ui.expanded.delete(id) : ui.expanded.add(id);
        card.classList.toggle("expanded", ui.expanded.has(id));
        el.setAttribute("aria-expanded", ui.expanded.has(id));
        card.querySelector(".match-details").inert = !ui.expanded.has(id);
        break;
      }
      case "search-details":
        ui.searchExpanded = !ui.searchExpanded;
        el.setAttribute("aria-expanded", ui.searchExpanded);
        $(".search-details")?.classList.toggle("open", ui.searchExpanded);
        if ($(".search-details"))
          $(".search-details").inert = !ui.searchExpanded;
        break;
      case "carousel":
        state.carousel = Math.max(
          0,
          Math.min(
            suggestedPeople().length - 1,
            state.carousel + Number(el.dataset.dir),
          ),
        );
        save();
        {
          const draft = $("#chat-input")?.value || "";
          $(".chat-panel").outerHTML = chatPanel();
          $("#chat-input").value = draft;
          scrollChat();
        }
        break;
      case "save":
        state.saved.includes(id)
          ? (state.saved = state.saved.filter((x) => x !== id))
          : state.saved.push(id);
        save();
        updateWorkspace();
        toast(
          state.saved.includes(id)
            ? "Saved for a little later."
            : "Removed from saved matches.",
        );
        break;
      case "pass": {
        const card = $("#match-" + id);
        card?.classList.add("removing");
        setTimeout(() => {
          if (!state.passed.includes(id)) state.passed.push(id);
          save();
          updateWorkspace();
          toast(person(id).name.split(" ")[0] + " moved to Passed.", id);
        }, 210);
        break;
      }
      case "undo-pass":
        state.passed = state.passed.filter((x) => x !== id);
        save();
        updateWorkspace();
        toast("Back in your possibilities.");
        break;
      case "detail":
        detailModal(id);
        break;
      case "request":
        requestModal(id);
        break;
      case "send-intro": {
        let note = $("#intro-note").value.trim();
        if (!note) {
          $("#intro-note").focus();
          break;
        }
        if (introFor(id)) {
          closeModal();
          break;
        }
        state.intros.push({
          id: "intro-" + Date.now(),
          person: id,
          direction: "sent",
          status: "pending",
          note,
          date: "Today",
        });
        state.messages.push({
          role: "agent",
          agent: "wasel",
          text: `Your sample introduction to ${person(id).name.split(" ")[0]} is ready and waiting for their reply. You can preview the recipient’s side in Introductions. No real message was sent.`,
          action: { label: "View introduction", page: "introductions" },
        });
        closeModal();
        render();
        toast("Sample introduction requested.");
        break;
      }
      case "accept": {
        let i = state.intros.find((x) => x.id === id);
        if (i && i.status === "pending") {
          i.status = "accepted";
          ui.introTab = "connected";
          render();
          toast("You’re connected. Time for a first hello.");
        }
        break;
      }
      case "decline": {
        let i = state.intros.find((x) => x.id === id);
        if (!i) break;
        openModal(
          "Not the right fit this time?",
          `<p>That’s okay. We’ll close this sample introduction without sharing any contact details.</p>`,
          A("close", "Keep introduction", "", "btn") +
            A(
              "confirm-decline",
              "Pass this time",
              "",
              "btn primary",
              `data-id="${id}"`,
            ),
        );
        break;
      }
      case "confirm-decline": {
        let i = state.intros.find((x) => x.id === id);
        if (i) i.status = "declined";
        closeModal();
        render();
        toast("Introduction closed. Your contact details stayed private.");
        break;
      }
      case "withdraw": {
        let i = state.intros.find((x) => x.id === id);
        if (!i) break;
        openModal(
          "Withdraw this introduction?",
          "<p>The pending sample request will close. Your contact details stay private.</p>",
          A("close", "Keep request", "", "btn") +
            A(
              "confirm-withdraw",
              "Withdraw request",
              "",
              "btn primary",
              `data-id="${id}"`,
            ),
        );
        break;
      }
      case "confirm-withdraw": {
        let i = state.intros.find((x) => x.id === id);
        if (i) i.status = "withdrawn";
        closeModal();
        render();
        toast("Introduction withdrawn.");
        break;
      }
      case "preview-recipient": {
        let i = state.intros.find((x) => x.id === id);
        if (!i) break;
        let p = person(i.person);
        openModal(
          `${p.name.split(" ")[0]}’s side of the introduction`,
          `<span class="tag orange" style="margin-bottom:16px">Recipient preview · sample interaction</span><p>This is what ${p.name.split(" ")[0]} would see. Try accepting or declining to explore what happens next.</p><div class="row">${avatar(
            {
              initials: state.profile.name
                .split(" ")
                .map((n) => n[0])
                .slice(0, 2)
                .join(""),
              color: "#e2e8d8",
            },
          )}<div><h3>${esc(state.profile.name)}</h3><span class="small muted">${esc(state.profile.role)}</span></div></div><blockquote>“${esc(i.note)}”</blockquote><p class="small">Contact details remain private until this invitation is accepted.</p>`,
          A("preview-decline", "Decline", "", "btn", `data-id="${id}"`) +
            A(
              "preview-accept",
              "Accept introduction",
              "link",
              "btn primary",
              `data-id="${id}"`,
            ),
        );
        break;
      }
      case "preview-accept":
      case "preview-decline": {
        let i = state.intros.find((x) => x.id === id);
        if (i && i.status === "pending") {
          i.status = action === "preview-accept" ? "accepted" : "declined";
          ui.introTab = i.status === "accepted" ? "connected" : "closed";
        }
        closeModal();
        navigate("introductions");
        toast(
          action === "preview-accept"
            ? "Sample acceptance complete. You’re connected."
            : "Sample introduction declined. No contacts shared.",
        );
        break;
      }
      case "copy-contact": {
        const p = person(id);
        if (
          !p ||
          !state.intros.some((i) => i.person === id && i.status === "accepted")
        )
          break;
        try {
          await navigator.clipboard.writeText(p.email);
          toast("Sample email copied.");
        } catch {
          openModal(
            "Your sample contact",
            `<p>Select and copy: <strong>${esc(p.email)}</strong></p>`,
            A("close", "Done", "", "btn primary"),
          );
        }
        break;
      }
      case "edit":
        editModal(field);
        break;
      case "save-field": {
        let v = $("#edit-field").value.trim();
        if (!v) break;
        state.profile[field] = v;
        state.confirmed = false;
        closeModal();
        render();
        toast("Profile updated. Confirm it when you’re ready.");
        break;
      }
      case "evidence": {
        let q = questions.find((q) => q.key === field);
        openModal(
          "In your own words.",
          `<h3>${q.title}</h3><blockquote>“${esc(state.answers[field] || questions.find((x) => x.key === field).sample)}”</blockquote><p class="small">${state.answers[field] ? "From your local practice interview." : "From the sample interview."} You can always update the profile if your thinking changes.</p>`,
          A("close", "Close", "", "btn") +
            A(
              "edit",
              "Edit this section",
              "edit",
              "btn primary",
              `data-field="${field}"`,
            ),
        );
        break;
      }
      case "avatar":
        openModal(
          "A small personal touch.",
          `<p>Choose a color for your sample profile.</p><div class="row wrap">${["#dce4cf", "#e5e9f4", "#f1e5d8", "#ece5ef", "#d9e8e5"].map((c, i) => `<button data-action="avatar-color" data-color="${c}" style="width:50px;height:50px;background:${c};border-radius:50%;border:2px solid #fff" aria-label="Choose ${["sage", "blue", "sand", "lilac", "teal"][i]} profile color"></button>`).join("")}</div>`,
          A("close", "Cancel", "", "btn"),
        );
        break;
      case "avatar-color":
        state.avatarColor = el.dataset.color;
        closeModal();
        render();
        toast("Profile color updated.");
        break;
      case "start-interview":
        if (state.interviewStep > 0 && state.interviewStep < questions.length) {
          navigate("interview");
        } else startInterview();
        break;
      case "question-back":
        if (state.interviewStep > 0) {
          let q = questions[state.interviewStep];
          state.answers[q.key] = $("#interview-answer")?.value || "";
          state.interviewStep--;
          render();
        }
        break;
      case "sample-answer":
        sampleAnswer();
        break;
      case "confirm-profile":
        state.confirmed = true;
        state.agent = "wasel";
        save();
        state.messages.push({
          role: "agent",
          agent: "wasel",
          text: "Fahem’s handed me your confirmed profile. Let’s find someone who brings what you’re missing.",
          action: { label: "Find my cofounder", page: "matches" },
        });
        render();
        toast("Profile confirmed. Wasel can take it from here.");
        break;
      case "review-profile":
        closeModal();
        navigate("profile");
        break;
      case "find":
        findMatches();
        break;
      case "why":
        submitChat("Why do you think these people are a good fit?");
        break;
      case "preferences-action":
        navigate("preferences");
        break;
      case "clear-search":
        ui.query = "";
        updateWorkspace();
        break;
      case "show-suggested":
        ui.matchTab = "suggested";
        navigate("matches");
        break;
      case "voice":
        voiceModal();
        break;
      case "call":
        voiceModal("call");
        break;
      case "pause-call":
        ui.callPaused = !ui.callPaused;
        $(".waveform")?.classList.toggle("paused", ui.callPaused);
        el.innerHTML = I(ui.callPaused ? "play" : "pause");
        el.setAttribute(
          "aria-label",
          ui.callPaused
            ? "Resume sample conversation"
            : "Pause sample conversation",
        );
        break;
      case "end-call":
        closeModal();
        toast("Sample conversation ended.");
        break;
      case "use-transcript": {
        const q = questions[state.interviewStep] || questions[0];
        closeModal();
        if ($("#interview-answer")) {
          $("#interview-answer").value = q.sample;
          state.answers[q.key] = q.sample;
          save();
          $("#interview-answer").focus();
        } else {
          $("#chat-input").value = q.sample;
          $("#chat-input").focus();
        }
        toast("Sample transcript ready. Review it before continuing.");
        break;
      }
      case "attach":
        attachModal();
        break;
      case "sample-doc":
        state.documents.push({
          id: "doc-" + Date.now(),
          title: "Rigad — sample CV.pdf",
          type: "Sample document",
          date: "Today",
          icon: "doc",
          sample: true,
        });
        closeModal();
        navigate("documents");
        toast("Sample CV added to your documents.");
        break;
      case "add-file": {
        let f = $("#local-file")?.files[0];
        if (!f) break;
        state.documents.push({
          id: "doc-" + Date.now(),
          title: f.name,
          type: "Local file reference",
          date: "Today",
          icon: "doc",
        });
        closeModal();
        navigate("documents");
        toast("Document name added. No file was uploaded.");
        break;
      }
      case "open-doc":
        openDoc(id);
        break;
      case "remove-doc":
        state.documents = state.documents.filter((d) => d.id !== id);
        closeModal();
        render();
        toast("Document reference removed.");
        break;
      case "download-doc":
        download(
          "fahem-interview-notes.txt",
          questions
            .map(
              (q) =>
                q.title + "\n" + (state.answers[q.key] || state.profile[q.key]),
            )
            .join("\n\n"),
        );
        toast("Interview notes downloaded.");
        break;
      case "motion":
        state.prefs.reduceMotion = !state.prefs.reduceMotion;
        render();
        toast(
          state.prefs.reduceMotion ? "Motion reduced." : "Motion restored.",
        );
        break;
      case "export":
        download(
          "fahem-wasel-demo.json",
          JSON.stringify(state, null, 2),
          "application/json",
        );
        toast("Demo data downloaded.");
        break;
      case "reset":
        openModal(
          "A fresh beginning?",
          `<p>This resets the sample profile, interview, preferences and introductions in this browser. Your other projects are unaffected.</p>`,
          A("close", "Keep my workspace", "", "btn") +
            A("confirm-reset", "Reset sample data", "refresh", "btn primary"),
        );
        break;
      case "confirm-reset":
        closeModal();
        state = seed();
        ui = {
          matchTab: "suggested",
          introTab: "received",
          query: "",
          expanded: new Set(),
          account: false,
          mobileChat: false,
          busy: false,
          docTab: "all",
          modal: null,
          searchExpanded: false,
        };
        render();
        toast("A fresh sample workspace is ready.");
        break;
      case "chat-options":
        openModal(
          "Your conversation.",
          `<div class="stack">${A("call", "Try a voice conversation", "phone", "btn")}${A("switch-agent", state.agent === "wasel" ? "Talk to Fahem" : "Talk to Wasel", "chat", "btn")}${A("clear-chat", "Clear practice messages", "refresh", "btn")}</div><div class="settings-note">The introductory sample conversation stays in place.</div>`,
        );
        break;
      case "switch-agent":
        state.agent = state.agent === "fahem" ? "wasel" : "fahem";
        closeModal();
        render();
        break;
      case "clear-chat":
        state.messages = [];
        closeModal();
        render();
        toast("Practice messages cleared.");
        break;
      case "help": {
        const helps = {
          matches: [
            "A few people worth meeting.",
            "Open “Why you two” to see complementary strengths and supporting quotes. Save a profile for later, pass, or request an introduction.",
          ],
          profile: [
            "Your story, with your approval.",
            "Click any section to edit it. Supporting quotes come from the sample interview, or your own practice answers. Confirm your profile before searching.",
          ],
          interview: [
            "Start with a conversation.",
            "Fahem asks seven questions. Type your answer or use the sample answer. Voice is an interactive simulation for this frontend preview.",
          ],
          introductions: [
            "A yes from both sides.",
            "Accept a received request, or send one from a match. For a sent request, “Preview recipient” lets you try the other side. No real messages are sent.",
          ],
          preferences: [
            "A little direction for Wasel.",
            "Location and availability filter the sample profiles. The other fields are saved for a future matching service.",
          ],
          documents: [
            "Keep your context together.",
            "Review your interview and profile. Try a sample CV, or add a local file name. Files are not uploaded or analyzed.",
          ],
          settings: [
            "A workspace to try things.",
            "Use the sample data freely. Reset the workspace any time to return to the original demo.",
          ],
        };
        let [title, body] = helps[state.page];
        openModal(
          title,
          `<p>${body}</p>`,
          A("close", "Got it", "", "btn primary"),
        );
        break;
      }
      case "about":
        openModal(
          "Two agents. One good introduction.",
          `<div class="duo" style="margin:20px 0 30px">${agentImg("fahem", "")}${agentImg("wasel", "")}</div><p><strong>Fahem understands.</strong> Your idea, your strengths, and what you need beside you.</p><p><strong>Wasel connects.</strong> A few complementary people and a thoughtful first introduction.</p><div class="divider"></div><p class="small">This is a local frontend prototype. All people, conversations and actions are samples. No AI, real messages, microphone recording or backend is connected.</p>`,
          A("close", "Make yourself at home", "", "btn primary"),
        );
        break;
      case "close":
        closeModal();
        break;
    }
    save();
  });
  document.addEventListener("submit", (e) => {
    if (e.target.id === "chat-form") {
      e.preventDefault();
      const input = $("#chat-input");
      const t = input.value;
      input.value = "";
      submitChat(t);
    }
    if (e.target.id === "interview-form") {
      e.preventDefault();
      submitInterview($("#interview-answer").value);
    }
    if (e.target.id === "prefs-form") {
      e.preventDefault();
      let data = Object.fromEntries(new FormData(e.target));
      Object.assign(state.prefs, data);
      save();
      toast("Preferences saved. Your sample matches are updated.");
    }
  });
  document.addEventListener("input", (e) => {
    if (e.target.id === "match-search") {
      ui.query = e.target.value;
      updateWorkspace();
    }
    if (e.target.id === "edit-field") {
      let t = e.target.value;
      $("#edit-count").textContent = t.length + " characters";
      let b = $('[data-action="save-field"]');
      b.disabled = !t.trim() || t === state.profile[b.dataset.field];
    }
    if (e.target.id === "intro-note") {
      const b = $('[data-action="send-intro"]');
      if (b) b.disabled = !e.target.value.trim();
      $("#intro-count").textContent =
        e.target.value.length + " / 1000 characters";
    }
    if (e.target.id === "interview-answer") {
      let q = questions[state.interviewStep];
      if (q) {
        state.answers[q.key] = e.target.value;
        save();
      }
    }
  });
  document.addEventListener("change", (e) => {
    if (e.target.id === "local-file") {
      let file = e.target.files[0];
      $('[data-action="add-file"]').disabled = !file;
      $("#file-selection").textContent = file
        ? `${file.name} · ${(file.size / 1024).toFixed(0)} KB · local preview only`
        : "Choose a file, or use a sample document.";
    }
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (ui.modal) closeModal();
      else if (ui.account) {
        ui.account = false;
        render();
      }
    }
    if (e.key === "Enter" && !e.shiftKey && e.target.id === "chat-input") {
      e.preventDefault();
      let text = e.target.value;
      e.target.value = "";
      submitChat(text);
    }
    if (e.key === "Tab" && ui.modal) {
      const list = $$(
        ".modal button:not(:disabled),.modal input,.modal textarea,.modal select,.modal a[href]",
      ).filter((el) => !el.hidden);
      if (list.length) {
        const first = list[0],
          last = list[list.length - 1];
        if (
          e.shiftKey &&
          (document.activeElement === first ||
            document.activeElement === $(".modal"))
        ) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    }
    if (
      e.target.matches(".resize-handle") &&
      ["ArrowLeft", "ArrowRight", "Home"].includes(e.key)
    ) {
      e.preventDefault();
      state.chatWidth =
        e.key === "Home"
          ? 42
          : Math.max(
              30,
              Math.min(60, state.chatWidth + (e.key === "ArrowRight" ? 2 : -2)),
            );
      document.documentElement.style.setProperty(
        "--chat",
        state.chatWidth + "%",
      );
      e.target.setAttribute("aria-valuenow", state.chatWidth);
      save();
    }
  });
  document.addEventListener("pointerdown", (e) => {
    if (!e.target.closest(".resize-handle")) return;
    e.preventDefault();
    const handle = e.target.closest(".resize-handle");
    handle.setPointerCapture(e.pointerId);
    const panel = $(".main-panels");
    let move = (evt) => {
      let box = panel.getBoundingClientRect();
      state.chatWidth = Math.max(
        30,
        Math.min(60, ((evt.clientX - box.left) / box.width) * 100),
      );
      document.documentElement.style.setProperty(
        "--chat",
        state.chatWidth + "%",
      );
      handle.setAttribute("aria-valuenow", Math.round(state.chatWidth));
    };
    const end = () => {
      handle.removeEventListener("pointermove", move);
      handle.removeEventListener("pointerup", end);
      save();
    };
    handle.addEventListener("pointermove", move);
    handle.addEventListener("pointerup", end);
  });
  document.addEventListener("dblclick", (e) => {
    if (e.target.matches(".resize-handle")) {
      state.chatWidth = 42;
      document.documentElement.style.setProperty("--chat", "42%");
      e.target.setAttribute("aria-valuenow", "42");
      save();
    }
  });
  // Keep the sample appearance preference separate from profile information.
  const style = document.createElement("style");
  style.id = "personal-avatar-style";
  document.head.append(style);
  const syncAvatar = () => {
    style.textContent = state.avatarColor
      ? `.profile-hero .avatar{background:${/^#[0-9a-f]{6}$/i.test(state.avatarColor) ? state.avatarColor : "#dce4cf"}}`
      : "";
  };
  new MutationObserver(syncAvatar).observe($("#app"), { childList: true });
  document.documentElement.style.setProperty("--chat", state.chatWidth + "%");
  render();
  syncAvatar();
})();
