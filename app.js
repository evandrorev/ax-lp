/* ==========================================================================
   AX — landing page
   Dois comportamentos: escolher a faixa de créditos em cada cartão de
   revenda e mandar cada botão para o checkout certo.
   ========================================================================== */

(function () {
  'use strict';

  /* Quanto o cliente final paga por mês. A margem do revendedor é a
     diferença entre esse valor e o custo do crédito na faixa escolhida. */
  var PRECO_CLIENTE_FINAL = 30;

  /* Checkout de cada agente, nas duas pontas: quem assina para usar
     (client) e quem compra crédito para revender (reseller). */
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

  /* Sem URL o link mantém a âncora que já está no HTML, e nada quebra. */
  function apontar(a, url) {
    if (!a || !url) return;
    a.href = url;
    if (/^https?:/i.test(url)) {
      a.target = '_blank';
      a.rel = 'noopener';
    }
  }

  var moeda = new Intl.NumberFormat('pt-BR', {
    style: 'currency', currency: 'BRL',
    minimumFractionDigits: 2, maximumFractionDigits: 2
  });
  var moedaCheia = new Intl.NumberFormat('pt-BR', {
    style: 'currency', currency: 'BRL', maximumFractionDigits: 0
  });
  var inteiro = new Intl.NumberFormat('pt-BR');

  /* Preço de cada faixa, na mesma ordem em que os botões aparecem no HTML.
     O HTML traz a quantidade em data-qtd; aqui fica só o custo. */
  var CUSTOS = {
    oscar: [10, 8, 7.5, 6, 5.5, 5, 4.5, 4],
    scout: [11, 10, 8, 7, 6, 5.5],
    combat: [12, 10, 8, 7, 6]
  };

  /* Faixa que já vem marcada em cada cartão, como no desenho. */
  var INICIAL = { oscar: 3, scout: 2, combat: 2 };

  function iniciarClientes() {
    [].slice.call(document.querySelectorAll('[data-buy]')).forEach(function (a) {
      apontar(a, LINKS.cliente[a.getAttribute('data-buy')]);
    });
  }

  function iniciarPacotes() {
    [].slice.call(document.querySelectorAll('[data-pacote]')).forEach(function (cartao) {
      var chave = cartao.getAttribute('data-pacote');
      var custos = CUSTOS[chave];
      var base = LINKS.revenda[chave];
      var botoes = [].slice.call(cartao.querySelectorAll('[data-faixa]'));
      var resumo = cartao.querySelector('[data-resumo]');
      var comprar = cartao.querySelector('[data-comprar]');
      if (!custos || !botoes.length) return;

      function escolher(i) {
        botoes.forEach(function (b, j) {
          var marca = b.querySelector('[data-marca]');
          if (marca) marca.hidden = j !== i;
          b.setAttribute('aria-pressed', String(j === i));
        });

        var creditos = Number(botoes[i].getAttribute('data-qtd'));
        var custo = custos[i];
        var margem = PRECO_CLIENTE_FINAL - custo;

        if (resumo) {
          resumo.textContent =
            inteiro.format(creditos) + ' créditos a ' + moeda.format(custo) +
            ' · investimento ' + moedaCheia.format(creditos * custo) +
            ' · margem ' + moedaCheia.format(creditos * margem) + '/mês';
        }
        /* O botão de compra carrega a quantidade escolhida até o checkout. */
        if (comprar && base) apontar(comprar, base + '?quantity=' + creditos);
      }

      botoes.forEach(function (b, i) {
        b.setAttribute('aria-pressed', 'false');
        b.addEventListener('click', function () { escolher(i); });
      });

      escolher(Math.min(INICIAL[chave] || 0, botoes.length - 1));
    });
  }

  iniciarClientes();
  iniciarPacotes();
})();
