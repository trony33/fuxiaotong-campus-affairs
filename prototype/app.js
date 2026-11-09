const SOURCE = {
  name: '福州大学学生管理规定（2025年版）',
  publisher: '福州大学教务处 / 学生工作部（处）',
  date: '政策文件；具体适用以原文与最新通知为准',
  verified: '2026-10-17（设计稿中的示例核验日期）',
  url: 'https://jwch.fzu.edu.cn/info/1201/14309.htm'
};

const policies = [
  { id: 'leave', title: '福州大学学生管理规定（学生请假与销假）', matter: '请假与证明', code: 'LEAVE', department: '教务处 / 学生工作部（处）', status: '已发布', verified: '2026-10-17', text: '包含病假、事假、审批、任课教师通知与销假等规则。具体条件以政策原文和适用学院要求为准。', source: SOURCE },
  { id: 'national-scholarship', title: '国家奖学金相关政策', matter: '奖助学金', code: 'SCHOLARSHIP', department: '学生工作部（处）', status: '待核验', verified: '待复核', text: '国家奖学金的申请对象、评审要求和年度安排，当前示例记录待团队核验。', source: null },
  { id: 'comprehensive-scholarship', title: '优秀学生综合奖学金', matter: '奖助学金', code: 'SCHOLARSHIP', department: '学生工作部（处）', status: '已发布', verified: '2026-10-16', text: '政策资格、评审流程和动态申请时间。具体截止日期以当年通知为准。', source: null },
  { id: 'exam-registration', title: '考试报名与选课通知', matter: '考试与选课', code: 'ACADEMIC', department: '教务处', status: '待核验', verified: '待复核', text: '当前暂无已核验的本年度截止时间。发布前需关联当年通知和官方入口。', source: null }
];

const defaultState = {
  profile: { level: '本科', grade: '大三', major: '计算机科学与技术', campus: '旗山校区' },
  checklist: [],
  reminders: [],
  history: [],
  favorites: []
};

let state = loadState();
let currentPolicyFilter = 'all';
let historyMode = 'recent';
let toastTimer;

function loadState() {
  try {
    const saved = JSON.parse(localStorage.getItem('campus-affairs-prototype') || '{}');
    return { ...defaultState, ...saved, profile: { ...defaultState.profile, ...saved.profile } };
  } catch {
    return structuredClone(defaultState);
  }
}

function saveState() {
  try { localStorage.setItem('campus-affairs-prototype', JSON.stringify(state)); }
  catch { showToast('浏览器存储不可用，本次修改未保存'); }
  renderCounts();
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
}

function showToast(message) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.add('is-visible');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('is-visible'), 2500);
}

function renderCounts() {
  const count = state.checklist.filter((item) => !item.done).length;
  document.getElementById('checklist-count').textContent = count;
}

const viewTitles = {
  assistant: '智能问答', policies: '办事指南', checklist: '材料清单', reminders: '提醒中心',
  history: '历史与收藏', profile: '办事画像', admin: '知识管理'
};

function navigate(view) {
  if (!viewTitles[view]) return;
  document.querySelectorAll('.view').forEach((element) => element.classList.toggle('is-visible', element.id === `view-${view}`));
  document.querySelectorAll('.nav-item').forEach((element) => element.classList.toggle('is-active', element.dataset.view === view));
  document.getElementById('page-title').textContent = viewTitles[view];
  if (view === 'policies') renderPolicies();
  if (view === 'checklist') renderChecklist();
  if (view === 'reminders') renderReminders();
  if (view === 'history') renderHistory();
  if (view === 'profile') renderProfile();
  if (view === 'admin') renderAdmin();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

document.querySelectorAll('[data-view]').forEach((button) => button.addEventListener('click', () => navigate(button.dataset.view)));

function addMessage(role, html) {
  const stream = document.getElementById('chat-stream');
  stream.querySelector('.welcome-line')?.remove();
  const item = document.createElement('div');
  item.className = `chat-message ${role}`;
  item.innerHTML = `<span class="agent-avatar" aria-hidden="true">${role === 'user' ? '林' : '✳'}</span><div class="bubble">${html}</div>`;
  stream.append(item);
  item.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  return item;
}

function makeAnswer(question) {
  const q = question.toLowerCase();
  if (/奖学金|助学金|兼得/.test(question)) {
    const asksForDate = /今年|截止|什么时候|哪天|日期/.test(question);
    const details = `
      <p><strong>先区分“奖学金”和“助学金”。</strong>你问到的几类资助是否可以兼得，需要分别核对各自当年的正式文件；当前演示知识样例给出的规则是：国家奖学金与国家励志奖学金不能同时获得，符合条件的学生可按政策同时申请国家助学金。</p>
      <p><strong>下一步：</strong>${asksForDate ? '查看学生工作部（处）或学院发布的当年评审通知，当前知识库不能确认具体截止日期。' : '查看当年评审通知中的对象、资格和互斥条款。'}研究生资助政策与本科生政策不应混用。</p>
      <p><strong>适用对象：</strong>${escapeHtml(state.profile.level)} · ${escapeHtml(state.profile.grade)}。具体结论以对应政策版本为准。</p>`;
    const actions = asksForDate
      ? ['添加个人提醒', '查看奖助学金政策', '反馈问题']
      : ['查看奖助学金政策', '反馈问题'];
    return { badge: '需核对年度通知', warning: true, html: details, source: null, actions };
  }
  if (/今年|截止|什么时候|哪天|日期/.test(question)) {
    const details = `
      <p><strong>我目前无法确认具体截止日期。</strong>现有演示知识记录未包含已核验的当年截止时间，不能根据往年时间推测。</p>
      <p><strong>建议：</strong>查看学生工作部（处）或学院发布的当年通知；如果通知内容仍不明确，请联系负责部门确认。</p>
      <p class="risk-copy">日期属于动态信息，确认前不要把历史时间当作本年度安排。</p>`;
    return { badge: '时间未核验', warning: true, html: details, source: null, actions: ['添加个人提醒', '查看负责部门'] };
  }
  if (/请假|销假|病假|事假/.test(question)) {
    const details = `
      <p><strong>办理思路：</strong>按请假类型和天数核对适用的审批层级；病假还要查看医院证明要求。当前示例政策记录显示，病假 3 天及以内由辅导员批准，超过 3 天由辅导员签署意见并报分管院领导批准。该条款必须以已核验的政策原文及学院规定为准。</p>
      <ol><li>准备书面请假申请；病假按原文准备相应医院证明。</li><li>按请假天数完成对应审批。</li><li>依流程通知学院教学干事和任课教师。</li><li>假期结束后及时办理销假。</li></ol>
      <p><strong>与你的画像：</strong>${escapeHtml(state.profile.level)} · ${escapeHtml(state.profile.grade)}。如果是研究生或特殊培养类别，请先核对对应管理规定。</p>`;
    return { badge: '已匹配政策样例', warning: false, html: details, source: SOURCE, actions: ['生成材料清单', '查看完整来源', '反馈回答'] };
  }
  if (/研究生/.test(question)) {
    const details = `<p><strong>适用对象需要区分。</strong>当前示例政策记录主要覆盖本科生，不能直接把本科生条件套用到研究生。请查询研究生院发布的对应政策，或联系研究生院确认。</p><p>如果你补充具体事务类型，我可以在已收录政策范围内继续筛选。</p>`;
    return { badge: '适用范围不匹配', warning: true, html: details, source: null, actions: ['查看办事指南', '查看负责部门'] };
  }
  const details = `<p><strong>当前知识库尚未找到足以支持确定回答的政策证据。</strong>为了避免给你错误流程，我不会根据一般经验猜测。</p><p>你可以换一种说法，补充事务类型，或者通过官方部门渠道确认。收到新政策后，需经过录入和核验才能用于正式回答。</p>`;
  return { badge: '知识库暂未覆盖', warning: true, html: details, source: null, actions: ['浏览办事指南', '反馈未解决问题'] };
}

function renderSource(source) {
  if (!source) return '';
  return `<div class="answer-source"><div class="source-main"><span class="source-icon">▤</span><span><strong>${escapeHtml(source.name)}</strong><small>${escapeHtml(source.publisher)} · 核验时间 ${escapeHtml(source.verified)}</small></span></div><button class="text-button source-detail-button">来源详情 ↗</button></div>`;
}

function makeChecklist() {
  const items = ['书面请假申请', '病假证明（按适用政策要求准备）', '审批记录/辅导员意见', '通知任课教师', '假期结束后办理销假'];
  const existing = new Set(state.checklist.map((item) => item.text));
  items.forEach((text) => { if (!existing.has(text)) state.checklist.push({ id: crypto.randomUUID(), text, done: false }); });
  saveState();
  navigate('checklist');
  showToast('材料清单已生成，请按你的实际情况核对');
}

function doAction(action) {
  if (action.includes('材料清单')) return makeChecklist();
  if (action.includes('提醒')) return openReminderModal();
  if (action.includes('来源')) return openSourceModal(SOURCE);
  if (action.includes('办事指南') || action.includes('政策')) return navigate('policies');
  if (action.includes('反馈')) { showToast('反馈入口已打开（演示状态）'); return; }
  if (action.includes('部门')) { showToast('请通过学校官网查询并联系负责部门'); return; }
}

function askQuestion(question) {
  const cleanQuestion = question.trim();
  if (!cleanQuestion) return;
  addMessage('user', escapeHtml(cleanQuestion));
  const answer = makeAnswer(cleanQuestion);
  const record = { id: crypto.randomUUID(), question: cleanQuestion, date: new Date().toISOString(), answer: answer.badge };
  state.history.unshift(record);
  state.history = state.history.slice(0, 30);
  saveState();
  const response = document.createElement('div');
  response.className = 'chat-message assistant';
  response.innerHTML = `<span class="agent-avatar" aria-hidden="true">✳</span><div class="answer-card"><div class="answer-heading"><strong>办事助手</strong><span class="risk-badge ${answer.warning ? 'warn' : ''}">${answer.badge}</span></div><div class="answer-text">${answer.html}</div>${renderSource(answer.source)}<div class="answer-actions">${answer.actions.map((label) => `<button class="action-button">${escapeHtml(label)}</button>`).join('')}</div><div class="answer-disclaimer">演示回答 · 政策结论以核验后的官方文件为准</div></div>`;
  document.getElementById('chat-stream').append(response);
  response.querySelectorAll('.action-button').forEach((button) => button.addEventListener('click', () => doAction(button.textContent)));
  response.querySelector('.source-detail-button')?.addEventListener('click', () => openSourceModal(answer.source));
  response.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
}

document.getElementById('question-form').addEventListener('submit', (event) => {
  event.preventDefault();
  const input = document.getElementById('question-input');
  askQuestion(input.value);
  input.value = '';
  document.getElementById('char-count').textContent = '0/500';
});

document.querySelectorAll('[data-question]').forEach((button) => button.addEventListener('click', () => {
  const question = button.dataset.question;
  navigate('assistant');
  askQuestion(question);
}));

document.getElementById('question-input').addEventListener('input', (event) => {
  document.getElementById('char-count').textContent = `${event.target.value.length}/500`;
  event.target.style.height = 'auto';
  event.target.style.height = `${Math.min(event.target.scrollHeight, 140)}px`;
});

document.getElementById('new-chat').addEventListener('click', () => {
  document.getElementById('chat-stream').innerHTML = '<div class="welcome-line"><span class="agent-avatar" aria-hidden="true">✳</span><span>选择一个常见问题，或输入你正在办理的校园事务。</span></div>';
  document.getElementById('question-input').focus();
});

document.getElementById('help-button').addEventListener('click', () => showToast('原型演示：当前不连接实时政策检索或大模型服务'));

function renderPolicies() {
  const query = (document.getElementById('policy-search')?.value || '').trim().toLowerCase();
  const filtered = policies.filter((policy) => (currentPolicyFilter === 'all' || policy.code === currentPolicyFilter)
    && `${policy.title} ${policy.matter} ${policy.department} ${policy.text}`.toLowerCase().includes(query));
  const grid = document.getElementById('policy-grid');
  grid.innerHTML = filtered.length ? filtered.map((policy) => `
    <article class="policy-item">
      <div class="policy-item-top"><div><span class="matter-label">${policy.matter}</span><h3>${escapeHtml(policy.title)}</h3></div><span class="status-pill ${policy.status === '待核验' ? 'pending' : ''}">${policy.status}</span></div>
      <p>${escapeHtml(policy.text)}</p>
      <div class="policy-meta"><span>${escapeHtml(policy.department)} · 核验 ${policy.verified}</span><span class="policy-actions"><button class="policy-open" data-open-policy="${policy.id}">查看详情</button><button class="favorite-button" data-favorite="${policy.id}">${state.favorites.includes(policy.id) ? '★ 已收藏' : '☆ 收藏'}</button></span></div>
    </article>`).join('') : '<div class="empty-state"><span class="empty-symbol">⌕</span><strong>没有匹配的事务</strong><p>试试更短的关键词，或选择其他分类。</p></div>';
  grid.querySelectorAll('[data-open-policy]').forEach((button) => button.addEventListener('click', () => {
    const policy = policies.find((item) => item.id === button.dataset.openPolicy);
    if (policy.source) openSourceModal(policy.source);
    else showToast(policy.status === '待核验' ? '该政策仍待核验，不能作为确定性回答依据' : policy.text);
  }));
  grid.querySelectorAll('[data-favorite]').forEach((button) => button.addEventListener('click', () => {
    const id = button.dataset.favorite;
    state.favorites = state.favorites.includes(id) ? state.favorites.filter((item) => item !== id) : [...state.favorites, id];
    saveState(); renderPolicies(); showToast('收藏状态已更新');
  }));
}

document.querySelectorAll('[data-policy-filter]').forEach((button) => button.addEventListener('click', () => {
  currentPolicyFilter = button.dataset.policyFilter;
  document.querySelectorAll('[data-policy-filter]').forEach((item) => item.classList.toggle('is-selected', item === button));
  renderPolicies();
}));
document.getElementById('policy-search').addEventListener('input', renderPolicies);

function renderChecklist() {
  const wrap = document.getElementById('checklist-wrap');
  if (!state.checklist.length) {
    wrap.innerHTML = '<div class="empty-state"><span class="empty-symbol">☑</span><strong>还没有材料清单</strong><p>在请假流程的回答中选择“生成材料清单”，或浏览办事指南后开始整理。</p><button class="primary-button" id="go-policies">浏览办事指南</button></div>';
    wrap.querySelector('#go-policies').addEventListener('click', () => navigate('policies'));
    return;
  }
  const done = state.checklist.filter((item) => item.done).length;
  wrap.innerHTML = `<section class="checklist-group"><div class="checklist-group-head"><div><strong>请假办理准备</strong><small>事项来源：病假流程回答 · 用户确认后生成</small></div><span class="check-progress">${done}/${state.checklist.length} 已完成</span></div><div class="checklist-items">${state.checklist.map((item) => `<label class="checklist-row ${item.done ? 'is-done' : ''}"><input type="checkbox" data-check-id="${item.id}" ${item.done ? 'checked' : ''}><span>${escapeHtml(item.text)}</span></label>`).join('')}</div></section><div class="coverage-note"><span>ⓘ</span><p>请按具体政策和学院要求核对材料；清单是准备辅助，不是审批提交。</p></div>`;
  wrap.querySelectorAll('[data-check-id]').forEach((input) => input.addEventListener('change', () => {
    const item = state.checklist.find((row) => row.id === input.dataset.checkId);
    if (item) item.done = input.checked;
    saveState(); renderChecklist();
  }));
}

document.getElementById('clear-checklist').addEventListener('click', () => {
  state.checklist = state.checklist.filter((item) => !item.done);
  saveState(); renderChecklist(); showToast('已移除完成项目');
});

function openReminderModal() {
  const modal = document.getElementById('reminder-modal');
  const date = modal.querySelector('[name="date"]');
  date.min = new Date().toISOString().slice(0, 10);
  date.value = date.min;
  modal.showModal();
}
document.getElementById('create-reminder').addEventListener('click', openReminderModal);
document.getElementById('reminder-form').addEventListener('submit', (event) => {
  if (event.submitter?.value === 'cancel') {
    event.preventDefault();
    event.currentTarget.closest('dialog').close('cancel');
    return;
  }
  event.preventDefault();
  const data = new FormData(event.currentTarget);
  state.reminders.push({ id: crypto.randomUUID(), title: data.get('title'), date: data.get('date'), time: data.get('time'), status: '个人提醒' });
  saveState(); event.currentTarget.closest('dialog').close(); event.currentTarget.reset();
  renderReminders(); showToast('个人提醒已添加（非官方截止通知）');
});

function renderReminders() {
  const list = document.getElementById('reminder-list');
  const sorted = [...state.reminders].sort((a, b) => `${a.date} ${a.time}`.localeCompare(`${b.date} ${b.time}`));
  if (!sorted.length) {
    list.innerHTML = '<div class="empty-state"><span class="empty-symbol">◷</span><strong>暂时没有提醒</strong><p>为自己创建办事计划。提醒内容由你管理，不代表官方截止日期。</p></div>';
    return;
  }
  list.innerHTML = sorted.map((item) => {
    const day = new Date(`${item.date}T00:00:00`).getDate();
    const month = new Date(`${item.date}T00:00:00`).toLocaleDateString('zh-CN', { month: 'long' });
    return `<div class="reminder-item"><span class="date-block"><strong>${day}</strong><small>${month}</small></span><span class="reminder-info"><strong>${escapeHtml(item.title)}</strong><small>${item.date} · ${item.time} · 站内提醒</small></span><span class="reminder-state">个人计划</span><button class="remove-reminder" data-remove-reminder="${item.id}" aria-label="删除提醒" title="删除提醒">×</button></div>`;
  }).join('');
  list.querySelectorAll('[data-remove-reminder]').forEach((button) => button.addEventListener('click', () => {
    state.reminders = state.reminders.filter((item) => item.id !== button.dataset.removeReminder);
    saveState(); renderReminders(); showToast('提醒已取消');
  }));
}

function renderHistory() {
  const list = document.getElementById('history-list');
  const rows = historyMode === 'recent'
    ? state.history.map((item) => ({ id: item.id, title: item.question, meta: `${new Date(item.date).toLocaleString('zh-CN')} · ${item.answer}`, icon: '↺' }))
    : state.favorites.map((id) => { const item = policies.find((policy) => policy.id === id); return item ? { id, title: item.title, meta: `${item.matter} · ${item.status}`, icon: '▤' } : null; }).filter(Boolean);
  list.innerHTML = rows.length ? rows.map((item) => `<div class="history-item"><span class="history-symbol">${item.icon}</span><span><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.meta)}</small></span>${historyMode === 'favorites' ? `<button data-remove-favorite="${item.id}" aria-label="取消收藏" title="取消收藏">★</button>` : ''}</div>`).join('') : `<div class="empty-state"><span class="empty-symbol">${historyMode === 'recent' ? '↺' : '☆'}</span><strong>${historyMode === 'recent' ? '还没有问答记录' : '还没有收藏'}</strong><p>${historyMode === 'recent' ? '你在智能问答中咨询后，记录会显示在这里。' : '在办事指南中点击收藏，可以保存常用政策。'}</p></div>`;
  list.querySelectorAll('[data-remove-favorite]').forEach((button) => button.addEventListener('click', () => {
    state.favorites = state.favorites.filter((id) => id !== button.dataset.removeFavorite); saveState(); renderHistory(); showToast('已取消收藏');
  }));
}

document.querySelectorAll('[data-history-tab]').forEach((button) => button.addEventListener('click', () => {
  historyMode = button.dataset.historyTab;
  document.querySelectorAll('[data-history-tab]').forEach((item) => item.classList.toggle('is-selected', item === button));
  renderHistory();
}));

function renderProfile() {
  const form = document.getElementById('profile-form');
  for (const [key, value] of Object.entries(state.profile)) if (form.elements[key]) form.elements[key].value = value;
  document.getElementById('fact-level').textContent = state.profile.level;
  document.getElementById('fact-grade').textContent = state.profile.grade;
  document.getElementById('fact-campus').textContent = state.profile.campus;
}

document.getElementById('profile-form').addEventListener('submit', (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  state.profile = Object.fromEntries(['level', 'grade', 'major', 'campus'].map((key) => [key, form.get(key)]));
  saveState(); renderProfile(); showToast('办事画像已保存');
});
document.getElementById('clear-profile').addEventListener('click', () => {
  state.profile = { ...defaultState.profile, level: '未设置', grade: '未设置', campus: '未设置' };
  saveState(); renderProfile(); showToast('画像已清除，回答将不再按画像筛选');
});

function renderAdmin() {
  const body = document.getElementById('admin-policy-rows');
  body.innerHTML = policies.map((policy) => `<tr><td><span class="admin-policy-name"><strong>${escapeHtml(policy.title)}</strong><small>${policy.matter}</small></span></td><td>${escapeHtml(policy.department)}</td><td><span class="status-pill ${policy.status === '待核验' ? 'pending' : ''}">${policy.status}</span></td><td>${policy.verified}</td><td><button class="admin-action" data-admin-action="${policy.id}">${policy.status === '待核验' ? '开始核验' : '查看记录'}</button></td></tr>`).join('');
  body.querySelectorAll('[data-admin-action]').forEach((button) => button.addEventListener('click', () => {
    const policy = policies.find((item) => item.id === button.dataset.adminAction);
    showToast(policy.status === '待核验' ? '核验清单：确认官方链接、适用对象、发布日期和关键条款' : '记录详情：包含政策版本、来源和最后核验时间');
  }));
}
document.getElementById('new-policy').addEventListener('click', () => showToast('新建草稿入口（静态原型）'));

function openSourceModal(source) {
  if (!source) return;
  const modal = document.getElementById('source-modal');
  document.getElementById('source-title').textContent = '政策来源与核验信息';
  document.getElementById('source-content').innerHTML = `<dl class="source-detail"><div><dt>文件名称</dt><dd>${escapeHtml(source.name)}</dd></div><div><dt>发布部门</dt><dd>${escapeHtml(source.publisher)}</dd></div><div><dt>日期说明</dt><dd>${escapeHtml(source.date)}</dd></div><div><dt>最后核验时间</dt><dd>${escapeHtml(source.verified)}</dd></div><div><dt>官方链接</dt><dd><a href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">${escapeHtml(source.url)}</a></dd></div></dl>`;
  document.getElementById('source-link').href = source.url;
  modal.showModal();
}
document.getElementById('close-source').addEventListener('click', () => document.getElementById('source-modal').close());
document.getElementById('source-close-button').addEventListener('click', () => document.getElementById('source-modal').close());

document.getElementById('clear-profile').setAttribute('title', '清除个人画像信息');
renderCounts();
renderPolicies();
