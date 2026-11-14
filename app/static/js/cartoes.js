/* Tela de cartões de crédito */
let cartoes = [];
async function carregar() {
  cartoes = await API.get('/api/cartoes');
  $('#cartoes').innerHTML = cartoes.map((c) => {
    const uso = c.limite > 0 ? Math.min(100, (c.usado / c.limite) * 100) : 0;
    return `<div class="cartao" style="${c.ativo ? '' : 'opacity:.6'}">
      <div style="display:flex;justify-content:space-between;align-items:start">
        <div><h3 style="margin:0">${esc(c.nome)}</h3><small style="color:var(--suave)">${c.bandeira} · fecha dia ${c.dia_fechamento} · vence dia ${c.dia_vencimento}${c.ativo ? '' : ' · desativado'}</small></div>
        <div style="white-space:nowrap"><button class="icone-btn" data-editar="${c.id}" aria-label="Editar">✎</button><button class="icone-btn" data-excluir="${c.id}" aria-label="Excluir">🗑</button></div></div>
      <div class="barra ${uso > 90 ? 'critico' : uso > 70 ? 'alerta' : ''}" style="margin:16px 0 8px"><i style="width:${uso}%"></i></div>
      <div style="display:flex;justify-content:space-between;font-size:13px"><span>Usado <b class="num">${fmt.moeda(c.usado)}</b></span><span>Disponível <b class="num">${fmt.moeda(c.disponivel)}</b></span></div>
      <small style="color:var(--suave)">Limite ${fmt.moeda(c.limite)}</small>
      <div data-faturas="${c.id}"></div></div>`;
  }).join('') || '<div class="cartao vazio">Nenhum cartão cadastrado.</div>';
  if (window.aoCarregarCartoes) window.aoCarregarCartoes(cartoes);
}
function abrirForm(c) {
  const f = $('#form'); f.reset(); limparErros(f);
  $('#tituloForm').textContent = c ? 'Editar cartão' : 'Novo cartão';
  f.id.value = c?.id || ''; f.nome.value = c?.nome || ''; f.bandeira.value = c?.bandeira || 'VISA';
  f.limite.value = c ? String(c.limite).replace('.', ',') : ''; f.dia_fechamento.value = c?.dia_fechamento || '';
  f.dia_vencimento.value = c?.dia_vencimento || ''; f.ativo.checked = c ? c.ativo : true;
  abrirPainel('painel');
}
$('#form').addEventListener('submit', async (e) => {
  e.preventDefault(); const f = e.target; limparErros(f);
  const corpo = { nome: f.nome.value, bandeira: f.bandeira.value, limite: f.limite.value || '0',
    dia_fechamento: f.dia_fechamento.value, dia_vencimento: f.dia_vencimento.value, ativo: f.ativo.checked };
  try { f.id.value ? await API.put('/api/cartoes/' + f.id.value, corpo) : await API.post('/api/cartoes', corpo);
        avisar('Cartão salvo'); fecharPainel('painel'); carregar(); }
  catch (er) { mostrarErros(f, er); if (er.status === 409) avisar(er.message, true); }
});
document.addEventListener('click', async (e) => {
  const ed = e.target.closest('[data-editar]'), ex = e.target.closest('[data-excluir]');
  if (ed) abrirForm(cartoes.find((c) => c.id == ed.dataset.editar));
  if (ex && confirm('Excluir este cartão?')) {
    try { await API.del('/api/cartoes/' + ex.dataset.excluir); avisar('Cartão excluído'); carregar(); } catch (er) { avisar(er.message, true); }
  }
});
$('#novo').onclick = () => abrirForm(null);
(async () => { await iniciarPagina('cartoes'); carregar(); })();
