/* ==========================================================================
   AX — landing page
   Dois comportamentos: montar as faixas de revenda a partir de uma tabela
   única e manter a barra de cima acompanhando a seção visível.
   ========================================================================== */

(function () {
  'use strict';

  /* Preço da assinatura ao cliente final. A margem do revendedor é a
     diferença entre ele e o custo do crédito na faixa escolhida. */
  var PRECO_CLIENTE_FINAL = 30;

  /* ------------------------------------------------- destinos de compra ---
     Checkout de cada agente, nas duas pontas: quem assina para usar
     (client) e quem compra crédito para revender (reseller). Na revenda a
     quantidade vai na URL, para o sistema reconhecer a faixa escolhida.
     ---------------------------------------------------------------------- */

  var LINKS = {
    cliente: {
      oscar: 'https://licence.agentxlink.com/checkout/ax-oscar/client',
      scout: 'https://licence.agentxlink.com/checkout/ax-scout/client',
      combat: 'https://licence.agentxlink.com/checkout/ax-combat/client'
    },
    revenda: {
      oscar: 'https://licence.agentxlink.com/checkout/ax-oscar/reseller',
      scout: 'https://licence.agentxlink.com/checkout/ax-scout/reseller',
      combat: 'https://licence.agentxlink.com/checkout/ax-combat/reseller'
    }
  };

  /* Aponta um link para a URL indicada; externo abre em nova aba. Sem URL,
     o link mantém a âncora que já está no HTML e nada quebra. */
  function apontar(a, url) {
    if (!a || !url) return;
    a.href = url;
    if (/^https?:/i.test(url)) {
      a.target = '_blank';
      a.rel = 'noopener';
    }
  }

  function iniciarDestinos() {
    [].slice.call(document.querySelectorAll('[data-buy]')).forEach(function (a) {
      apontar(a, LINKS.cliente[a.getAttribute('data-buy')]);
    });
  }

  /* ------------------------------------------------------------ preços ---
     Cada faixa é [quantidade inicial, quantidade final, custo do crédito].
     Fonte única: o HTML não repete nenhum preço, então tela e checkout não
     têm como sair de sincronia.
     ---------------------------------------------------------------------- */

  var TABELAS = [
    {
      nome: 'Oscar',
      chave: 'oscar',
      faixas: [
        [5, 9, 10], [10, 29, 8], [30, 99, 7.5], [100, 249, 6],
        [250, 499, 5.5], [500, 999, 5], [1000, 2499, 4.5], [2500, 10000, 4]
      ]
    },
    {
      nome: 'Scout',
      chave: 'scout',
      faixas: [
        [10, 29, 11], [30, 49, 10], [50, 99, 8],
        [100, 499, 7], [500, 999, 6], [1000, 5000, 5.5]
      ]
    },
    {
      nome: 'Combat',
      chave: 'combat',
      faixas: [
        [10, 49, 12], [50, 99, 10], [100, 499, 8],
        [500, 999, 7], [1000, 5000, 6]
      ]
    }
  ];

  var moeda = new Intl.NumberFormat('pt-BR', {
    style: 'currency', currency: 'BRL',
    minimumFractionDigits: 2, maximumFractionDigits: 2
  });
  var inteiro = new Intl.NumberFormat('pt-BR');

  function margemPct(custo) {
    return Math.round(((PRECO_CLIENTE_FINAL - custo) / PRECO_CLIENTE_FINAL) * 100);
  }

  function iniciarTabelas() {
    TABELAS.forEach(function (tabela) {
      var alvo = document.querySelector('[data-tabela="' + tabela.chave + '"]');
      if (!alvo) return;

      var base = LINKS.revenda[tabela.chave];
      apontar(document.querySelector('[data-comprar="' + tabela.chave + '"]'), base);

      tabela.faixas.forEach(function (faixa) {
        var n = faixa[0];
        var custo = faixa[2];

        var a = document.createElement('a');
        a.className = 'ptable__row';
        if (base) {
          a.href = base + '?quantity=' + n;
          a.target = '_blank';
          a.rel = 'noopener';
        } else {
          a.href = '#planos';
        }
        a.setAttribute(
          'aria-label',
          'Comprar ' + inteiro.format(n) + ' créditos do ' + tabela.nome +
            ' a ' + moeda.format(custo) + ' cada'
        );
        a.innerHTML =
          '<span class="ptable__qtd">' + inteiro.format(n) + ' créditos</span>' +
          '<span class="ptable__preco">' + moeda.format(custo) + '</span>';
        alvo.appendChild(a);
      });

      /* Uma linha de resumo no lugar de repetir a margem em cada faixa. */
      var resumo = document.querySelector('[data-margem="' + tabela.chave + '"]');
      if (resumo) {
        var custos = tabela.faixas.map(function (f) { return f[2]; });
        var menor = margemPct(Math.max.apply(null, custos));
        var maior = margemPct(Math.min.apply(null, custos));
        resumo.innerHTML =
          'Preço por crédito. Cada crédito ativa um mês de um cliente seu, que paga ' +
          '<b>' + moeda.format(PRECO_CLIENTE_FINAL) + '/mês</b>. Sua margem vai de ' +
          '<b>' + menor + '%</b> a <b>' + maior + '%</b>.';
      }
    });
  }

  /* --------------------------------------------------- barra de cima -----
     O item da seção visível fica marcado e o botão da direita muda de
     conversa: na revenda ele fala com o parceiro, não com o assinante.
     ---------------------------------------------------------------------- */

  var CTA_POR_SECAO = {
    oscar:   { texto: 'Assinar por R$ 30', href: '#planos' },
    scout:   { texto: 'Assinar por R$ 30', href: '#planos' },
    combat:  { texto: 'Assinar por R$ 30', href: '#planos' },
    planos:  { texto: 'Assinar por R$ 30', href: '#planos' },
    revenda: { texto: 'Área do parceiro',  href: '#revenda' },
    faq:     { texto: 'Assinar por R$ 30', href: '#planos' }
  };
  var CTA_PADRAO = { texto: 'Assinar', href: '#planos' };

  function iniciarBarra() {
    var barra = document.getElementById('nav');
    var cta = document.getElementById('nav-cta');
    var ctaTexto = document.getElementById('nav-cta-texto');
    var itens = [].slice.call(document.querySelectorAll('[data-spy]'));
    var secoes = [].slice.call(document.querySelectorAll('[data-secao]'));
    if (!barra || !itens.length) return;

    var atual = null;

    function marcar(chave) {
      if (chave === atual) return;
      atual = chave;

      itens.forEach(function (a) {
        a.classList.toggle('is-active', a.getAttribute('data-spy') === chave);
      });

      var conf = CTA_POR_SECAO[chave] || CTA_PADRAO;
      if (ctaTexto) ctaTexto.textContent = conf.texto;
      if (cta) cta.href = conf.href;
    }

    function aoRolar() {
      barra.classList.toggle('is-stuck', window.scrollY > 8);

      /* Vale a seção que cruza a linha logo abaixo da barra. */
      var linha = barra.offsetHeight + 40;
      var visivel = null;
      secoes.forEach(function (s) {
        var caixa = s.getBoundingClientRect();
        if (caixa.top <= linha && caixa.bottom > linha) visivel = s.getAttribute('data-secao');
      });
      marcar(visivel);
    }

    window.addEventListener('scroll', aoRolar, { passive: true });
    window.addEventListener('resize', aoRolar);
    aoRolar();
  }

  /* ------------------------------------------------------------ boot ---- */

  iniciarDestinos();
  iniciarTabelas();
  iniciarBarra();
})();
