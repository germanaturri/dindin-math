/* DinDin Math - utilitários compartilhados pelo front-end */
const API = {
  async req(metodo, url, corpo) {
    const opcoes = { method: metodo, headers: {}, credentials: 'same-origin' };
    if (corpo !== undefined) { opcoes.headers['Content-Type'] = 'application/json'; opcoes.body = JSON.stringify(corpo); }
    const resp = await fetch(url, opcoes);
    if (resp.status === 401 && !url.startsWith('/api/auth/')) { location.href = '/app/login'; throw new Error('Sessão expirada'); }
    const tipo = resp.headers.get('Content-Type') || '';
    const dados = tipo.includes('application/json') ? await resp.json() : await resp.text();
    if (!resp.ok) { const e = new Error(dados.erro || 'Erro na requisição'); e.campos = dados.campos || {}; e.status = resp.status; throw e; }
    return dados;
  },
  get: (u) => API.req('GET', u), post: (u, c) => API.req('POST', u, c ?? {}),
  put: (u, c) => API.req('PUT', u, c), del: (u) => API.req('DELETE', u),
};

const fmt = {
  moeda: (v) => (v ?? 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }),
  data: (iso) => iso ? iso.split('-').reverse().join('/') : '',
  mes: (aaaamm) => { const [a, m] = aaaamm.split('-'); return new Date(+a, +m - 1, 1).toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' }).replace('.', '').replace(' de ', '/'); },
  mesLongo: (aaaamm) => { const [a, m] = aaaamm.split('-'); const s = new Date(+a, +m - 1, 1).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' }); return s[0].toUpperCase() + s.slice(1); },
};
const hoje = () => { const d = new Date(); d.setMinutes(d.getMinutes() - d.getTimezoneOffset()); return d.toISOString().slice(0, 10); };
const mesAtual = () => hoje().slice(0, 7);
const somarMes = (aaaamm, n) => { const [a, m] = aaaamm.split('-').map(Number); const d = new Date(a, m - 1 + n, 1); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`; };
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const $ = (sel, raiz = document) => raiz.querySelector(sel);
const $$ = (sel, raiz = document) => [...raiz.querySelectorAll(sel)];

function avisar(texto, erro = false) {
  let el = $('#aviso');
  if (!el) { el = document.createElement('div'); el.id = 'aviso'; el.className = 'aviso'; el.setAttribute('role', 'status'); document.body.appendChild(el); }
  el.textContent = texto; el.classList.toggle('erro', erro); el.classList.add('mostrar');
  clearTimeout(el._t); el._t = setTimeout(() => el.classList.remove('mostrar'), 3200);
}

/* Mostra os erros de validação devolvidos pela API embaixo de cada campo */
function mostrarErros(form, erro) {
  $$('.campo', form).forEach((c) => c.classList.remove('erro'));
  $$('.msg-campo', form).forEach((m) => (m.textContent = ''));
  const campos = erro.campos || {};
  Object.entries(campos).forEach(([nome, msg]) => {
    const campo = form.elements[nome]; if (!campo) return;
    campo.classList.add('erro');
    const m = campo.closest('.grupo')?.querySelector('.msg-campo'); if (m) m.textContent = msg;
  });
  const geral = $('.erro-geral', form);
  if (geral) { geral.textContent = erro.message; geral.style.display = 'block'; }
  else if (!Object.keys(campos).length) avisar(erro.message, true);
}
function limparErros(form) { mostrarErros(form, { campos: {}, message: '' }); const g = $('.erro-geral', form); if (g) g.style.display = 'none'; }

const MENU = [
  ['lancamentos', '↕', 'Lançamentos'],
  ['cartoes', '💳', 'Cartões e faturas'],
  ['categorias', '🏷', 'Categorias'],
];

/* Monta a barra lateral e confere a sessão; devolve o usuário logado */
async function iniciarPagina(ativa) {
  const { usuario } = await API.get('/api/auth/me').catch(() => { location.href = '/app/login'; throw new Error(); });
  const lateral = document.createElement('aside'); lateral.className = 'lateral';
  lateral.innerHTML = `<div class="marca"><span class="moeda">$</span>DinDin Math</div>
    ${MENU.map(([p, i, t]) => `<a class="item ${p === ativa ? 'ativo' : ''}" href="/app/${p}"><span class="ico">${i}</span>${t}</a>`).join('')}
    <div class="rodape"><b>${esc(usuario.nome)}</b>${esc(usuario.email)}<button class="btn sec peq" id="sair">Sair</button></div>`;
  $('.app').prepend(lateral);
  $('#sair').onclick = async () => { await API.post('/api/auth/logout'); location.href = '/app/login'; };
  return usuario;
}

function abrirPainel(id) { $('#' + id).classList.add('aberto'); setTimeout(() => $('#' + id + ' input:not([type=hidden]), #' + id + ' select')?.focus(), 50); }
function fecharPainel(id) { $('#' + id).classList.remove('aberto'); }
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') $$('.painel.aberto').forEach((p) => p.classList.remove('aberto')); });
document.addEventListener('click', (e) => { if (e.target.classList?.contains('painel')) e.target.classList.remove('aberto'); });
