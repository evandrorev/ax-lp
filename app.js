/* ==========================================================================
   AX — Landing page
   Três comportamentos: digitação das conversas do hero, troca de formação
   no campo do Scout e o simulador de revenda.
   ========================================================================== */

(function () {
  'use strict';

  /* ------------------------------------------------- destinos de compra ---
     Checkout de cada agente, nas duas pontas: quem assina para usar
     (cliente) e quem compra crédito para revender (revenda). Um valor vazio
     faz o botão manter a âncora atual, sem quebrar nada.
     ---------------------------------------------------------------------- */

  var LINKS = {
    cliente: {
      oscar: 'http://licence.agentxlink.com/checkout/ax-oscar/client',
      scout: 'http://licence.agentxlink.com/checkout/ax-scout/client',
      combat: 'http://licence.agentxlink.com/checkout/ax-combat/client'
    },
    revenda: {
      oscar: 'http://licence.agentxlink.com/checkout/ax-oscar/reseller',
      scout: 'http://licence.agentxlink.com/checkout/ax-scout/reseller',
      combat: 'http://licence.agentxlink.com/checkout/ax-combat/reseller'
    }
  };

  /* Aponta um link para a URL indicada; externo abre em nova aba. */
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

  var reduzMovimento =
    window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ------------------------------------------- digitação das conversas --- */

  function iniciarDigitacao() {
    var alvos = [].slice.call(document.querySelectorAll('[data-typing]'));
    if (!alvos.length) return;

    var textos = alvos.map(function (el) {
      return el.textContent;
    });
    var total = Math.max.apply(
      null,
      textos.map(function (t) {
        return t.length;
      })
    );

    function desenhar(n) {
      alvos.forEach(function (el, i) {
        el.textContent = textos[i].slice(0, n);
        var cursor = el.parentNode.querySelector('.chat__cursor');
        if (cursor) cursor.hidden = n >= textos[i].length;
      });
    }

    if (reduzMovimento) {
      desenhar(total);
      return;
    }

    var digitados = 0;
    desenhar(0);
    var timer = setInterval(function () {
      digitados = Math.min(total, digitados + 2);
      desenhar(digitados);
      if (digitados >= total) clearInterval(timer);
    }, 22);
  }

  /* ------------------------------------------- campo tático do Scout ----- */

  var FORMACOES = {
    // Linha de quatro — campo largo
    0: [
      [30, 120], [100, 40], [100, 95], [100, 145], [100, 200],
      [190, 40], [190, 95], [190, 145], [190, 200], [280, 90], [280, 150]
    ],
    // Linha de três com alas — ataca por dentro
    1: [
      [30, 120], [100, 70], [100, 120], [100, 170], [170, 25], [170, 215],
      [200, 80], [200, 120], [200, 160], [290, 90], [290, 150]
    ]
  };

  var ROTULOS = {
    0: 'Linha de quatro — campo largo',
    1: 'Linha de três com alas — ataca por dentro'
  };

  function iniciarCampo() {
    var campo = document.getElementById('campo');
    var rotulo = document.getElementById('formacao');
    var replay = document.getElementById('replay');
    if (!campo) return;

    var jogadores = [].slice.call(campo.querySelectorAll('.player'));

    function aplicar(indice) {
      var pos = FORMACOES[indice];
      jogadores.forEach(function (circulo, i) {
        if (!pos[i]) return;
        circulo.setAttribute('cx', pos[i][0]);
        circulo.setAttribute('cy', pos[i][1]);
      });
      if (rotulo) rotulo.textContent = ROTULOS[indice];
    }

    if (replay) {
      replay.addEventListener('click', function () {
        aplicar(0);
        setTimeout(function () {
          aplicar(1);
        }, 700);
      });
    }

    if (!('IntersectionObserver' in window)) return;

    var observer = new IntersectionObserver(
      function (entradas) {
        entradas.forEach(function (entrada) {
          if (!entrada.isIntersecting) return;
          observer.disconnect();
          setTimeout(function () {
            aplicar(1);
          }, 600);
        });
      },
      { threshold: 0.3 }
    );
    observer.observe(campo);
  }

  /* --------------------------------------------- simulador de revenda ---- */

  var PRECO_CLIENTE_FINAL = 30;

  // Faixas de atacado: [quantidade mínima, quantidade máxima, preço unitário].
  // Mesmos valores impressos nas tabelas do index.html.
  var TABELAS = [
    {
      nome: 'Oscar',
      chave: 'oscar',
      tema: 't-oscar',
      faixas: [
        [5, 9, 10], [10, 29, 8], [30, 99, 7.5], [100, 249, 6],
        [250, 499, 5.5], [500, 999, 5], [1000, 2499, 4.5], [2500, 10000, 4]
      ]
    },
    {
      nome: 'Scout',
      chave: 'scout',
      tema: 't-scout',
      faixas: [
        [10, 29, 11], [30, 49, 10], [50, 99, 8],
        [100, 499, 7], [500, 999, 6], [1000, 5000, 5.5]
      ]
    },
    {
      nome: 'Combat',
      chave: 'combat',
      tema: 't-combat',
      faixas: [
        [10, 49, 12], [50, 99, 10], [100, 499, 8],
        [500, 999, 7], [1000, 5000, 6]
      ]
    }
  ];

  var moeda = new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
  var moedaCheia = new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  });
  var inteiro = new Intl.NumberFormat('pt-BR');

  function iniciarSimulador() {
    var caixa = document.getElementById('simulador');
    var slider = document.getElementById('creditos');
    if (!caixa || !slider) return;

    var abas = [].slice.call(caixa.querySelectorAll('.sim__tab'));
    var saida = {
      contagem: document.getElementById('sim-count'),
      investimento: document.getElementById('sim-investimento'),
      faturamento: document.getElementById('sim-faturamento'),
      margem: document.getElementById('sim-margem'),
      margem12: document.getElementById('sim-margem12'),
      faixa: document.getElementById('sim-faixa'),
      custo: document.getElementById('sim-custo'),
      cta: document.getElementById('sim-cta')
    };

    var selecionado = 0;
    var creditos = Number(slider.value) || 30;

    function faixaDe(tabela, n) {
      for (var i = 0; i < tabela.faixas.length; i++) {
        if (n >= tabela.faixas[i][0] && n <= tabela.faixas[i][1]) return tabela.faixas[i];
      }
      return tabela.faixas[tabela.faixas.length - 1];
    }

    function render() {
      var tabela = TABELAS[selecionado];
      var min = tabela.faixas[0][0];
      var max = tabela.faixas[tabela.faixas.length - 1][1];
      var n = Math.min(Math.max(creditos, min), max);
      creditos = n;
      var faixa = faixaDe(tabela, n);
      var custo = faixa[2];
      var margemUnitaria = PRECO_CLIENTE_FINAL - custo;

      caixa.className = 'sim ' + tabela.tema;
      abas.forEach(function (aba, i) {
        aba.setAttribute('aria-selected', String(i === selecionado));
      });

      slider.min = String(min);
      slider.max = String(max);
      slider.value = String(n);

      saida.contagem.textContent =
        inteiro.format(n) + (n === 1 ? ' crédito' : ' créditos');
      saida.investimento.textContent = moedaCheia.format(n * custo);
      saida.faturamento.textContent = moedaCheia.format(n * PRECO_CLIENTE_FINAL);
      saida.margem.textContent = moedaCheia.format(n * margemUnitaria);
      saida.margem12.textContent = moedaCheia.format(n * margemUnitaria * 12);
      saida.faixa.textContent =
        inteiro.format(faixa[0]) + ' – ' + inteiro.format(faixa[1]) + ' créditos';
      saida.custo.textContent = moeda.format(custo);
      saida.cta.textContent = 'Quero revender o ' + tabela.nome + ' →';
      apontar(saida.cta, LINKS.revenda[tabela.chave]);
    }

    abas.forEach(function (aba, i) {
      aba.addEventListener('click', function () {
        selecionado = i;
        render();
      });
    });

    slider.addEventListener('input', function () {
      creditos = Number(slider.value);
      render();
    });

    render();
  }

  /* ------------------------------------------------------------ boot ---- */

  iniciarDestinos();
  iniciarDigitacao();
  iniciarCampo();
  iniciarSimulador();
})();
