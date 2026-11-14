/* Tela de lançamentos: extrato filtrável + formulário de inclusão/edição */
let mes = new URLSearchParams(location.search).get('mes') || mesAtual();
let categorias = [], formas = [], cartoes = [], tipoAtual = 'SAIDA', lancs = [];

async function carregarApoio() {
  [categorias, formas, cartoes] = await Promise.all([API.get('/api/categorias'), API.get('/api/formas-pagamento'), API.get('/api/cartoes')]);
  $('#fCat').innerHTML += categorias.map((c) => `<option value="${c.id}">${esc(c.nome)}</option>`).join('');
  $('#fForma').innerHTML += formas.map((f) => `<option value="${f.codigo}">${esc(f.nome)}</option>`).join('');
  $('#forma_pagamento_id').innerHTML = formas.map((f) => `<option value="${f.id}" data-cartao="${f.exige_cartao}">${esc(f.nome)}</option>`).join('');
  $('#cartao_id').innerHTML = cartoes.filter((c) => c.ativo).map((c) => `<option value="${c.id}">${esc(c.nome)}</option>`).join('') || '<option value="">Cadastre um cartão</option>';
}

async function carregar() {
  $('#mesTxt').textContent = fmt.mesLongo(mes);
  const p = new URLSearchParams({ mes });
  if ($('#fTipo').value) p.set('tipo', $('#fTipo').value);
  if ($('#fCat').value) p.set('categoria_id', $('#fCat').value);
  if ($('#fForma').value) p.set('forma', $('#fForma').value);
  if ($('#fBusca').value.trim()) p.set('busca', $('#fBusca').value.trim());
  const { itens, totais } = await API.get('/api/lancamentos?' + p);
  lancs = itens;
  $('#tEnt').textContent = fmt.moeda(totais.entradas); $('#tSai').textContent = fmt.moeda(totais.saidas);
  $('#tSal').textContent = fmt.moeda(totais.saldo); $('#tSal').className = 'val num ' + (totais.saldo >= 0 ? 'pos' : 'neg');
  $('#tQtd').textContent = `${totais.quantidade} lançamento(s)`;
  $('#lista').innerHTML = itens.length ? itens.map((l) => `<tr>
      <td class="num">${fmt.data(l.data)}</td>
      <td><b style="color:var(--tinta)">${esc(l.descricao)}</b>${l.observacao ? `<br><small style="color:var(--suave)">${esc(l.observacao)}</small>` : ''}</td>
      <td><span class="etiqueta"><span class="bola" style="background:${l.categoria_cor}"></span>${esc(l.categoria)}</span></td>
      <td>${esc(l.forma_pagamento)}${l.cartao ? `<br><small style="color:var(--suave)">${esc(l.cartao)} · fatura ${fmt.mes(l.fatura_mes)}</small>` : ''}</td>
      <td class="dir num ${l.tipo === 'ENTRADA' ? 'pos' : 'neg'}"><b>${l.tipo === 'ENTRADA' ? '+' : '−'} ${fmt.moeda(l.valor)}</b></td>
      <td class="dir" style="white-space:nowrap"><button class="icone-btn" data-editar="${l.id}" aria-label="Editar">✎</button><button class="icone-btn" data-excluir="${l.id}" aria-label="Excluir">🗑</button></td></tr>`).join('')
    : '<tr><td colspan="6" class="vazio">Nenhum lançamento neste período. Clique em <b>+ Novo lançamento</b>.</td></tr>';
}

function definirTipo(tipo) {
  tipoAtual = tipo;
  $$('.alternador button').forEach((b) => b.classList.toggle('on', b.dataset.tipo === tipo));
  const sel = $('#categoria_id'), atual = sel.value;
  sel.innerHTML = categorias.filter((c) => c.tipo === tipo).map((c) => `<option value="${c.id}">${esc(c.nome)}</option>`).join('');
  if ([...sel.options].some((o) => o.value === atual)) sel.value = atual;
  $$('#forma_pagamento_id option').forEach((o) => { o.disabled = tipo === 'ENTRADA' && o.dataset.cartao === 'true'; });
  if ($('#forma_pagamento_id').selectedOptions[0]?.disabled) $('#forma_pagamento_id').value = formas.find((f) => f.codigo === 'PIX').id;
  atualizarCartao();
}
function atualizarCartao() {
  const exige = $('#forma_pagamento_id').selectedOptions[0]?.dataset.cartao === 'true';
  $('#blocoCartao').hidden = !exige;
}

function abrirForm(l) {
  const f = $('#form'); f.reset(); limparErros(f);
  $('#tituloForm').textContent = l ? 'Editar lançamento' : 'Novo lançamento';
  f.id.value = l?.id || '';
  definirTipo(l?.tipo || 'SAIDA');
  f.descricao.value = l?.descricao || ''; f.valor.value = l ? String(l.valor).replace('.', ',') : '';
  f.data.value = l?.data || hoje(); f.observacao.value = l?.observacao || '';
  if (l) { f.categoria_id.value = l.categoria_id; f.forma_pagamento_id.value = l.forma_pagamento_id; if (l.cartao_id) f.cartao_id.value = l.cartao_id; }
  atualizarCartao(); abrirPainel('painel');
}

$('#form').addEventListener('submit', async (e) => {
  e.preventDefault(); const f = e.target; limparErros(f);
  const corpo = { tipo: tipoAtual, descricao: f.descricao.value, valor: f.valor.value, data: f.data.value,
    categoria_id: f.categoria_id.value, forma_pagamento_id: f.forma_pagamento_id.value, observacao: f.observacao.value || null };
  if (!$('#blocoCartao').hidden) corpo.cartao_id = f.cartao_id.value;
  const b = $('button[type=submit]', f); b.disabled = true;
  try {
    if (f.id.value) { await API.put('/api/lancamentos/' + f.id.value, corpo); avisar('Lançamento atualizado'); }
    else { await API.post('/api/lancamentos', corpo); avisar('Lançamento registrado'); }
    fecharPainel('painel'); carregar();
  } catch (erro) { mostrarErros(f, erro); } finally { b.disabled = false; }
});

$('#lista').addEventListener('click', async (e) => {
  const ed = e.target.closest('[data-editar]'), ex = e.target.closest('[data-excluir]');
  if (ed) abrirForm(lancs.find((l) => l.id == ed.dataset.editar));
  if (ex && confirm('Excluir este lançamento?')) {
    try { await API.del('/api/lancamentos/' + ex.dataset.excluir); avisar('Lançamento excluído'); carregar(); } catch (er) { avisar(er.message, true); }
  }
});
$$('.alternador button').forEach((b) => (b.onclick = () => definirTipo(b.dataset.tipo)));
$('#forma_pagamento_id').onchange = atualizarCartao;
$('#novo').onclick = () => abrirForm(null);
$('#mesAnt').onclick = () => { mes = somarMes(mes, -1); carregar(); };
$('#mesProx').onclick = () => { mes = somarMes(mes, 1); carregar(); };
['fTipo', 'fCat', 'fForma'].forEach((id) => ($('#' + id).onchange = carregar));
let tBusca; $('#fBusca').oninput = () => { clearTimeout(tBusca); tBusca = setTimeout(carregar, 300); };

(async () => { await iniciarPagina('lancamentos'); await carregarApoio(); await carregar(); if (location.hash === '#novo') abrirForm(null); })();
