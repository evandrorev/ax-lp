# -*- coding: utf-8 -*-
"""
Gera index.html a partir do AX.dc.html do Claude Design.

O .dc.html e um modelo: os lacos <sc-for> e as marcas {{ }} sao resolvidos
aqui, em vez de no navegador. O resultado e HTML puro, com os mesmos estilos
embutidos do desenho — nada e reinterpretado.
"""
import html, json, pathlib, re

SAIDA = pathlib.Path('/home/user/ax-lp')

# ----------------------------------------------------------------- icones ---
ICON = {
 'film':'M3 5h18v14H3zM7 5v14M17 5v14M3 12h18',
 'ball':'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 7.5l4.3 3.1-1.6 5h-5.4l-1.6-5z',
 'glove':'M8 21v-3M8 18H6.5A2.5 2.5 0 0 1 4 15.5V11a2 2 0 0 1 4 0V6a2 2 0 1 1 4 0v4h4.5A2.5 2.5 0 0 1 19 12.5V15a6 6 0 0 1-6 6H8z',
 'bolt':'M13 2.5 4.8 13H11l-1 8.5L18.2 11H12l1-8.5z',
 'clock':'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 7.5V12l3 2',
 'shield':'M12 3l7 3v5.4c0 4.3-3 7.7-7 8.6-4-0.9-7-4.3-7-8.6V6l7-3z',
 'chart':'M4 20V11M10 20V4M16 20v-6M2 20h20',
 'users':'M16 20v-1.8a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4V20M9 10.2a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM22 20v-1.8a4 4 0 0 0-3-3.9',
 'lock':'M6 10.5V8a6 6 0 1 1 12 0v2.5M5 10.5h14v10H5z',
 'infinity':'M7.5 9a3 3 0 1 0 0 6c3.2 0 5.8-6 9-6a3 3 0 1 1 0 6c-3.2 0-5.8-6-9-6z',
 'headset':'M4 13v-1a8 8 0 1 1 16 0v1M4 13a2 2 0 0 1 2 2v2a2 2 0 1 1-4 0v-2a2 2 0 0 1 2-2zM20 13a2 2 0 0 1 2 2v2a2 2 0 1 1-4 0v-2a2 2 0 0 1 2-2z'}

# ------------------------------------------------------- estilos de hover ---
# style-hover="..." nao existe em HTML. Cada valor distinto vira uma classe.
HOVERS, REGRAS = {}, []
def hov(regra):
    if regra not in HOVERS:
        HOVERS[regra] = 'h%d' % (len(HOVERS) + 1)
        REGRAS.append('.%s:hover{%s}' % (HOVERS[regra], regra))
    return HOVERS[regra]

def e(t):
    return html.escape(str(t), quote=True)

def svg(d, cor, tam=20, larg='1.6'):
    return ('<svg viewBox="0 0 24 24" width="%d" height="%d" fill="none" stroke="%s" '
            'stroke-width="%s" stroke-linecap="round" stroke-linejoin="round" '
            'style="flex:none"><path d="%s"></path></svg>' % (tam, tam, cor, larg, d))

def micro(itens, cor):
    return ''.join(
        '<div style="display:flex;align-items:center;gap:11px">%s'
        '<div style="font-size:14px;line-height:1.35;color:rgba(242,244,245,0.8)">%s<br>'
        '<span style="color:rgba(242,244,245,0.5)">%s</span></div></div>'
        % (svg(m['d'], cor), e(m['t1']), e(m['t2'])) for m in itens)

# ----------------------------------------------------------------- dados ---
TINTA = lambda s: '#06130D' if s == 'Scout' else '#fff'

AGENTES = [
 dict(id='oscar', short='Oscar', name='AX Oscar', accent='#E01F3D', light='#FF4D76', icon=ICON['film'],
  topics='Filmes · Séries · Animes · Doramas · Documentários',
  h1='Tudo sobre o que você assiste,', h2='quando você quiser.',
  desc='O AX Oscar é o seu especialista em filmes e séries. Ele responde, indica, analisa e conversa com você sobre lançamentos, clássicos, curiosidades, teorias e muito mais — em qualquer hora do dia.',
  ctaLabel='Assinar o Oscar por R$ 30/mês', chatRole='Especialista em filmes e séries',
  micro=[{'d':ICON['bolt'],'t1':'Respostas','t2':'em segundos'},{'d':ICON['clock'],'t1':'Disponível','t2':'24 horas'},{'d':ICON['shield'],'t1':'Sem spoilers','t2':'(se você preferir)'}],
  q='Qual a melhor série pra assistir hoje à noite?',
  intro='Depende do que você está procurando! Aqui vão algumas ótimas opções de acordo com o seu perfil:',
  items=[('1.','Fallout','(Prime Video) – aventura e mundo imersivo'),('2.','The Last of Us','(HBO) – drama e emoção'),
         ('3.','Dark','(Netflix) – mistério e viagem no tempo'),('4.','O Problema dos 3 Corpos','(Netflix) – ficção científica'),
         ('5.','Better Call Saul','(Netflix) – roteiro impecável')],
  outro='Se quiser, posso te dar mais opções específicas com base no seu gosto. O que você prefere ver hoje?',
  chips=['Lançamentos','Séries parecidas','Filmes por gênero','Detalhes da trama'],
  stripLeft='Histórias que te acompanham.', stripRight='AX Oscar · faz parte do seu dia.'),

 dict(id='scout', short='Scout', name='AX Scout', accent='#12D18A', light='#3BE8A6', icon=ICON['ball'],
  topics='Futebol · Análises · Estatísticas · Táticas · Mercado',
  h1='Mais futebol. Mais informação,', h2='melhores decisões.',
  desc='O AX Scout analisa jogos, times, jogadores e competições. Ele traz estatísticas, táticas, análises e insights em tempo real para você acompanhar o futebol de um jeito mais inteligente.',
  ctaLabel='Assinar o Scout por R$ 30/mês', chatRole='Seu analista de futebol 24/7',
  micro=[{'d':ICON['bolt'],'t1':'Respostas','t2':'em segundos'},{'d':ICON['clock'],'t1':'Disponível','t2':'24 horas'},{'d':ICON['shield'],'t1':'Análises confiáveis','t2':'e atualizadas'}],
  q='Quais são os jogos de hoje na Champions?',
  intro='Claro! Hoje temos os seguintes jogos da Champions League:',
  items=[('16:00','Real Madrid x Manchester City',''),('16:00','Bayern de Munique x Arsenal',''),
         ('19:00','Barcelona x PSG',''),('19:00','Borussia Dortmund x Atlético de Madrid','')],
  outro='Se quiser, posso trazer as prováveis escalações, estatísticas e análises de cada jogo. Qual deles você quer analisar primeiro?',
  chips=['Jogos de hoje','Classificação','Análise de jogo','Mercado da bola'],
  stripLeft='Futebol em outro nível.', stripRight='AX Scout · faz parte do seu dia.'),

 dict(id='combat', short='Combat', name='AX Combat', accent='#9B5CFF', light='#B98BFF', icon=ICON['glove'],
  topics='Lutas · Eventos · Lutadores · Estratégias · Análises',
  h1='Lutas em outro nível.', h2='Informação que te coloca mais perto da ação.',
  desc='O AX Combat traz análises, notícias, eventos, lutadores e estratégias do mundo das lutas. UFC, boxe, MMA, jiu-jitsu e muito mais — tudo em um só lugar, com respostas rápidas e precisas.',
  ctaLabel='Assinar o Combat por R$ 30/mês', chatRole='Especialista em lutas 24/7',
  micro=[{'d':ICON['bolt'],'t1':'Respostas','t2':'em segundos'},{'d':ICON['clock'],'t1':'Disponível','t2':'24 horas'},{'d':ICON['shield'],'t1':'Conteúdo confiável','t2':'e atualizado'}],
  q='Qual a análise da luta principal do UFC deste final de semana?',
  intro='Aqui está a análise da luta principal do UFC deste final de semana — Alex Pereira vs. Jamahal Hill, meio-pesado (93 kg):',
  items=[('•','Alex Pereira:','excelente no striking, alto poder de nocaute, defesa de quedas evoluiu.'),
         ('•','Jamahal Hill:','forte no jogo de média distância, bom volume de golpes e resistência.'),
         ('•','Leitura:','luta equilibrada, com vantagem para quem controlar a distância e evitar a grade.')],
  outro='Posso detalhar o cartel dos dois, o histórico recente ou os próximos eventos do card.',
  chips=['Próximos eventos','Perfil de lutadores','Análise de luta','Rankings'],
  stripLeft='Lutas que movem o mundo.', stripRight='AX Combat · disciplina. informação. evolução.'),
]

HERO_Q    = {'Oscar':'Quais são os lançamentos de filmes este mês?','Scout':'Quais são os destaques da próxima rodada da Champions?','Combat':'Qual é a análise da luta principal deste final de semana?'}
HERO_TAGS = {'Oscar':'Filmes · Séries · Curiosidades · Recomendações','Scout':'Análises · Estatísticas · Táticas · Mercado','Combat':'Análises · Lutadores · Eventos · Estratégias'}
PAPEL     = {'Oscar':'Entretenimento','Scout':'Futebol','Combat':'Esportes de combate'}

HERO_MICRO = [{'d':ICON['bolt'],'t1':'Respostas','t2':'em segundos'},{'d':ICON['clock'],'t1':'Disponível','t2':'24 horas'},{'d':ICON['shield'],'t1':'Informações','t2':'confiáveis'}]
HERO_LIST  = [('1.','Silo','(Apple TV+) – ficção científica envolvente'),('2.','The Last of Us','(HBO) – drama e emoção'),
              ('3.','Fallout','(Prime Video) – aventura e mundo imersivo'),('4.','Black Mirror','– tecnologia e dilemas reais'),
              ('5.','O Problema dos 3 Corpos','(Netflix) – ficção científica épica')]

PLANOS = [
 dict(n='01', short='Oscar', nicho='Entretenimento', accent='#E01F3D', light='#FF4D76', cta='Assinar o Oscar',
      tagline='o amigo que assistiu e sabe falar sobre',
      features=['Recomendação a partir do que você sentiu','Final explicado, com as pistas em ordem','Anime e dorama pela porta certa','Conversas ilimitadas, 24h']),
 dict(n='02', short='Scout', nicho='Futebol', accent='#12D18A', light='#3BE8A6', cta='Assinar o Scout',
      tagline='o analista que não torce pra ninguém',
      features=['A derrota explicada em três pontos','xG e estatística avançada traduzidos','Leitura tática, elenco e mercado','Conversas ilimitadas, 24h']),
 dict(n='03', short='Combat', nicho='Lutas', accent='#9B5CFF', light='#B98BFF', cta='Assinar o Combat',
      tagline='o córner que explica entre um round e outro',
      features=['A técnica que decidiu a luta, passo a passo','Cartel, trajetória e rivalidades','Vale acordar pro card? Qual luta ver?','Conversas ilimitadas, 24h']),
]

PACOTES = [
 dict(short='Oscar', accent='#E01F3D', light='#FF4D76', nichoUp='Entretenimento',
      l1='Filmes, séries, animes e doramas.', l2='Seu público sempre conectado.',
      tiers=[(5,10),(10,8),(30,7.5),(100,6),(250,5.5),(500,5),(1000,4.5),(2500,4)]),
 dict(short='Scout', accent='#12D18A', light='#3BE8A6', nichoUp='Futebol',
      l1='Análises, estatísticas e mercado.', l2='Informação para quem vive futebol.',
      tiers=[(10,11),(30,10),(50,8),(100,7),(500,6),(1000,5.5)]),
 dict(short='Combat', accent='#9B5CFF', light='#B98BFF', nichoUp='Lutas',
      l1='MMA, UFC, boxe e artes marciais.', l2='Análises, eventos e tudo sobre o mundo das lutas.',
      tiers=[(10,12),(50,10),(100,8),(500,7),(1000,6)]),
]

PERKS = [{'d':ICON['bolt'],'t1':'Ativação imediata','t2':'Comece a usar agora'},
         {'d':ICON['chart'],'t1':'Mais margem','t2':'Preços especiais'},
         {'d':ICON['users'],'t1':'Suporte prioritário','t2':'Para revendedores'}]
NOTAS = [{'d':ICON['lock'],'t':'Sistema seguro e estável'},{'d':ICON['infinity'],'t':'Sem prazo de validade'},
         {'d':ICON['headset'],'t':'Suporte para revendedores'}]

FAQS = [
 ('Como eu converso com o agente?','Assim que a assinatura é confirmada você recebe seu link de acesso. Abre no celular ou no computador e já começa a conversar, do jeito que fala com um amigo.'),
 ('É uma IA genérica com nome bonito?','Não. Cada agente domina um único assunto e responde no nível de quem acompanha aquilo há anos. Pergunte de futebol pro Oscar e ele te manda pro Scout.'),
 ('O Oscar dá spoiler?','Só se você pedir. Ele pergunta até onde você viu antes de explicar qualquer coisa.'),
 ('O Scout ou o Combat dão palpite de aposta?','Não, e não vão dar. Eles analisam o esporte: tática, técnica, estatística, história. Prognóstico e cota estão fora do produto.'),
 ('Posso assinar mais de um agente?','Sim. Cada agente é uma assinatura de R$ 30/mês, independente das outras.'),
 ('Como funciona a revenda?','Você compra créditos no atacado e ativa clientes seus. Cada crédito vale um mês de assinatura de um cliente. Não é preciso ser assinante para revender.'),
]

# ------------------------------------------------------------- montagem ---
P = []          # pedacos do HTML
w = P.append

w('''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AX — um especialista para cada assunto</title>
<meta name="description" content="Três agentes de IA especializados: Oscar (filmes e séries), Scout (futebol) e Combat (MMA, UFC e boxe). R$ 30/mês por agente, com programa de revenda por créditos.">
<meta name="theme-color" content="#08090A">
<meta property="og:title" content="AX — um especialista para cada assunto">
<meta property="og:description" content="Uma IA que só entende de uma coisa e responde como quem acompanha aquilo há anos.">
<meta property="og:type" content="website">
<link rel="icon" href="./assets/ax-logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&amp;family=Manrope:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="./styles.css">
</head>
<body>

<div style="background:#08090A;color:#F2F4F5;font-family:Manrope,system-ui,sans-serif;position:relative;overflow-x:clip">
''')

# ------------------------------------------------------------------ nav ---
NAV = [('#oscar','Oscar','color:#FF6E8C;border-bottom-color:#E01F3D'),
       ('#scout','Scout','color:#5DE3A5;border-bottom-color:#12D18A'),
       ('#combat','Combat','color:#C0A0FF;border-bottom-color:#9B5CFF'),
       ('#planos','Planos','color:#F2F4F5;border-bottom-color:rgba(255,255,255,0.5)'),
       ('#revenda','Revenda','color:#F2F4F5;border-bottom-color:rgba(255,255,255,0.5)'),
       ('#faq','Dúvidas','color:#F2F4F5;border-bottom-color:rgba(255,255,255,0.5)')]

w('<header style="position:sticky;top:0;z-index:50;background:rgba(8,9,10,0.86);backdrop-filter:blur(18px);border-bottom:1px solid rgba(255,255,255,0.07)">')
w('<div style="max-width:1280px;margin:0 auto;padding:14px 32px;display:flex;align-items:center;justify-content:space-between;gap:24px;flex-wrap:wrap">')
w('<a href="#topo" style="display:flex;align-items:center;gap:12px">'
  '<img src="./assets/ax-logo.png" alt="AX" style="width:42px;height:42px;mix-blend-mode:screen;display:block">'
  '<span style="display:flex;flex-direction:column;gap:2px;font-size:9px;letter-spacing:0.18em;text-transform:uppercase;color:rgba(242,244,245,0.55);font-weight:700;line-height:1.35;border-left:1px solid rgba(255,255,255,0.14);padding-left:12px">'
  '<span>Inteligência</span><span>especializada</span><span>sempre com você</span></span></a>')
w('<nav style="display:flex;gap:26px;align-items:center;overflow-x:auto;scrollbar-width:none">')
for href, rot, hv in NAV:
    w('<a href="%s" class="%s" style="font-size:15px;font-weight:600;color:rgba(242,244,245,0.8);padding:6px 0;border-bottom:2px solid transparent;white-space:nowrap">%s</a>'
      % (href, hov(hv), rot))
w('</nav>')
w('<a href="#planos" class="%s" style="font-size:14px;font-weight:700;padding:13px 22px;background:linear-gradient(90deg,#004AFB,#8A18FD);color:#fff;border-radius:10px;white-space:nowrap">Assinar por R$ 30 →</a>'
  % hov('color:#fff;filter:brightness(1.12)'))
w('</div></header>')

# ----------------------------------------------------------------- hero ---
w('<section id="topo" style="position:relative;overflow:hidden">')
w('<div style="position:absolute;inset:0;pointer-events:none;background:radial-gradient(760px 480px at 80% -5%, rgba(123,63,242,0.28), transparent 70%), radial-gradient(620px 420px at 20% 10%, rgba(0,74,251,0.14), transparent 70%)"></div>')
w('<div style="position:relative;max-width:1280px;margin:0 auto;padding:88px 32px 56px;display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:56px;align-items:center">')
w('<div style="display:flex;flex-direction:column;gap:26px;animation:axIn 420ms ease-out both">')
w('<div style="font-size:12px;letter-spacing:0.22em;text-transform:uppercase;color:rgba(242,244,245,0.5);font-weight:700">Mais que IA. Especialistas reais.</div>')
w('<h1 style="font-family:\'Bricolage Grotesque\',sans-serif;font-weight:800;font-size:clamp(42px,5.6vw,72px);line-height:0.98;letter-spacing:-0.04em;margin:0;max-width:11ch;text-wrap:balance">IA especializada para aquilo que <span style="color:#2F6BFF">você</span> <span style="color:#8A18FD">realmente gosta.</span></h1>')
w('<p style="font-size:18px;line-height:1.6;color:rgba(242,244,245,0.68);margin:0;max-width:520px;text-wrap:pretty">Acesse especialistas em entretenimento, futebol e lutas, disponíveis 24 horas por dia, prontos para responder, analisar e conversar com você.</p>')
w('<div style="display:flex;gap:14px;flex-wrap:wrap">'
  '<a href="#oscar" class="%s" style="display:inline-flex;align-items:center;gap:10px;padding:17px 28px;border-radius:12px;background:#F2F4F5;color:#08090A;font-weight:700;font-size:15px">Conhecer especialistas →</a>'
  '<a href="#planos" class="%s" style="display:inline-flex;align-items:center;gap:10px;padding:17px 28px;border-radius:12px;border:1px solid rgba(255,255,255,0.18);color:#F2F4F5;font-weight:600;font-size:15px">Ver planos →</a></div>'
  % (hov('color:#08090A;filter:brightness(0.9)'), hov('border-color:rgba(255,255,255,0.45)')))
w('<div style="display:flex;gap:34px;flex-wrap:wrap;padding-top:6px">%s</div>' % micro(HERO_MICRO, '#8FA6FF'))
w('</div>')

# janela do produto (reta, como no desenho)
w('<div style="position:relative;animation:axIn 460ms ease-out 120ms both">')
w('<div style="position:absolute;top:-34px;right:6px;display:flex;align-items:center;gap:10px">'
  '<div style="text-align:right;font-size:11px;line-height:1.4;color:rgba(242,244,245,0.55)">Sempre aprendendo<br>para você ir além</div>'
  '<span style="width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#004AFB,#8A18FD);display:inline-flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;color:#fff">E</span></div>')
w('<div style="display:grid;grid-template-columns:150px minmax(0,1fr);background:#0D0F11;border:1px solid rgba(255,255,255,0.1);border-radius:18px;overflow:hidden;box-shadow:0 40px 120px -60px rgba(138,24,253,0.8)">')
w('<div style="border-right:1px solid rgba(255,255,255,0.07);padding:16px 14px;display:flex;flex-direction:column;gap:14px;background:#0A0B0D">'
  '<img src="./assets/ax-logo.png" alt="AX" style="width:26px;height:26px;mix-blend-mode:screen">'
  '<div style="display:flex;align-items:center;gap:8px;padding:8px 10px;border-radius:8px;background:rgba(255,255,255,0.06);font-size:11px;font-weight:600">＋ Novo chat</div>'
  '<div style="display:flex;flex-direction:column;gap:10px;font-size:11px;color:rgba(242,244,245,0.55)"><span>Especialistas</span><span>Histórico</span><span>Favoritos</span></div>'
  '<div style="font-size:9px;letter-spacing:0.16em;text-transform:uppercase;color:rgba(242,244,245,0.35);font-weight:700;margin-top:6px">Seus agentes</div>'
  '<div style="display:flex;flex-direction:column;gap:9px;font-size:11px;color:rgba(242,244,245,0.75)">%s</div></div>'
  % ''.join('<span style="display:flex;align-items:center;gap:8px"><span style="width:7px;height:7px;border-radius:50%%;background:%s;flex:none"></span>%s</span>'
            % (a['accent'], a['name']) for a in AGENTES))
w('<div style="display:flex;flex-direction:column;min-width:0">')
w('<div style="display:flex;align-items:center;gap:10px;padding:14px 18px;border-bottom:1px solid rgba(255,255,255,0.07)">'
  '<span style="width:26px;height:26px;border-radius:8px;background:rgba(224,31,61,0.18);border:1px solid rgba(224,31,61,0.5);display:inline-flex;align-items:center;justify-content:center;flex:none">%s</span>'
  '<div><div style="font-size:13px;font-weight:700;line-height:1.2">AX Oscar</div><div style="font-size:10px;color:rgba(242,244,245,0.45)">Entretenimento</div></div></div>'
  % svg(ICON['film'], '#FF6E8C', 14, '1.7'))
w('<div style="padding:18px;display:flex;flex-direction:column;gap:14px;min-width:0">')
w('<div style="align-self:flex-end;max-width:86%;background:rgba(255,255,255,0.08);border-radius:12px 12px 4px 12px;padding:10px 13px;font-size:12px;line-height:1.5">Quais são as melhores séries para maratonar em 2026?<div style="font-size:9px;color:rgba(242,244,245,0.4);text-align:right;margin-top:4px">10:24</div></div>')
w('<div style="align-self:flex-start;max-width:94%;background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.07);border-radius:12px 12px 12px 4px;padding:12px 14px;font-size:12px;line-height:1.7;display:flex;flex-direction:column;gap:5px">')
w('<span style="color:rgba(242,244,245,0.75)">Aqui estão algumas das séries mais comentadas e bem avaliadas para maratonar em 2026:</span>')
for n, titulo, resto in HERO_LIST:
    w('<span><span style="color:rgba(242,244,245,0.45)">%s</span> <em style="font-style:italic;font-weight:700">%s</em> <span style="color:rgba(242,244,245,0.6)">%s</span></span>'
      % (n, e(titulo), e(resto)))
w('<span style="color:rgba(242,244,245,0.6)">Se quiser, posso montar uma lista personalizada de acordo com o seu estilo. 🎬</span>')
w('</div>')
w('<div style="display:flex;align-items:center;gap:10px;border:1px solid rgba(255,255,255,0.09);border-radius:10px;padding:10px 12px;font-size:11px;color:rgba(242,244,245,0.4)">Pergunte ao AX Oscar...<span style="margin-left:auto;color:rgba(242,244,245,0.7)">→</span></div>')
w('</div></div></div></div></div>')

# tres portas de entrada
w('<div style="position:relative;max-width:1280px;margin:0 auto;padding:24px 32px 96px;display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px">')
for a in AGENTES:
    ac, lt = a['accent'], a['light']
    w('<a href="#%s" class="%s" style="display:flex;flex-direction:column;gap:16px;background:linear-gradient(160deg, %s1F, rgba(13,15,17,0.9) 55%%);border:1px solid %s66;border-radius:18px;padding:22px;transition:transform 220ms;color:#F2F4F5">'
      % (a['id'], hov('transform:translateY(-4px);color:#F2F4F5'), ac, ac))
    w('<div style="display:flex;align-items:center;gap:14px">'
      '<span style="width:42px;height:42px;border-radius:12px;flex:none;display:inline-flex;align-items:center;justify-content:center;background:%s26;border:1px solid %s80">%s</span>'
      '<div style="flex:1;min-width:0"><div style="font-family:\'Bricolage Grotesque\',sans-serif;font-weight:800;font-size:20px;letter-spacing:-0.02em">%s</div>'
      '<div style="font-size:13px;color:rgba(242,244,245,0.5);margin-top:2px">%s</div></div>'
      '<span style="width:34px;height:34px;border-radius:50%%;flex:none;display:inline-flex;align-items:center;justify-content:center;border:1px solid %s;color:%s;font-size:15px">→</span></div>'
      % (ac, ac, svg(a['icon'], lt, 20, '1.7'), a['name'], PAPEL[a['short']], ac, lt))
    w('<div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:13px 15px;font-size:13.5px;line-height:1.5;color:rgba(242,244,245,0.82)">%s<div style="font-size:10px;color:rgba(242,244,245,0.35);text-align:right;margin-top:6px">10:24</div></div>'
      % e(HERO_Q[a['short']]))
    w('<div style="font-size:10.5px;letter-spacing:0.16em;text-transform:uppercase;color:rgba(242,244,245,0.42);font-weight:700">%s</div>' % e(HERO_TAGS[a['short']]))
    w('</a>')
w('</div></section>')

# -------------------------------------------------------------- agentes ---
for i, a in enumerate(AGENTES):
    ac, lt, tinta = a['accent'], a['light'], TINTA(a['short'])
    w('<section id="%s" style="position:relative;overflow:hidden;border-top:1px solid rgba(255,255,255,0.06)">' % a['id'])
    w('<div style="position:absolute;inset:0;pointer-events:none;background:radial-gradient(760px 480px at %s 0%%, %s2E, transparent 70%%)"></div>'
      % ('0%' if i % 2 else '100%', ac))
    w('<div style="position:relative;max-width:1280px;margin:0 auto;padding:104px 32px 0;display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:60px;align-items:center">')

    # coluna de texto
    w('<div style="display:flex;flex-direction:column;gap:24px">')
    w('<div style="display:flex;gap:10px;flex-wrap:wrap">'
      '<span style="display:inline-flex;align-items:center;gap:9px;padding:9px 16px;border-radius:999px;border:1px solid %s99;background:%s1A;font-size:10.5px;letter-spacing:0.16em;text-transform:uppercase;font-weight:700;color:%s">'
      '<span style="width:7px;height:7px;border-radius:50%%;background:%s;flex:none"></span>%s</span>'
      '<span style="display:inline-flex;align-items:center;padding:9px 16px;border-radius:999px;border:1px solid rgba(255,255,255,0.14);font-size:10.5px;letter-spacing:0.16em;text-transform:uppercase;color:rgba(242,244,245,0.6);font-weight:700">%s</span></div>'
      % (ac, ac, lt, ac, a['name'], e(a['topics'])))
    w('<h2 style="font-family:\'Bricolage Grotesque\',sans-serif;font-weight:800;font-size:clamp(38px,4.6vw,60px);line-height:1;letter-spacing:-0.04em;margin:0;max-width:14ch;text-wrap:balance">%s <span style="color:%s">%s</span></h2>'
      % (e(a['h1']), lt, e(a['h2'])))
    w('<p style="font-size:17px;line-height:1.65;color:rgba(242,244,245,0.68);margin:0;max-width:540px;text-wrap:pretty">%s</p>' % e(a['desc']))
    w('<div style="display:flex;gap:14px;flex-wrap:wrap">'
      '<a href="#planos" data-buy="%s" class="%s" style="display:inline-flex;align-items:center;padding:17px 28px;border-radius:12px;background:%s;color:%s;font-weight:800;font-size:15px;box-shadow:0 20px 50px -28px %s">%s →</a>'
      '<a href="#planos" class="%s" style="display:inline-flex;align-items:center;padding:17px 28px;border-radius:12px;border:1px solid rgba(255,255,255,0.16);color:#F2F4F5;font-weight:600;font-size:15px">Ver planos</a></div>'
      % (a['id'], hov('color:#fff;filter:brightness(1.12)'), ac, tinta, ac, e(a['ctaLabel']),
         hov('border-color:rgba(255,255,255,0.45)')))
    w('<div style="display:flex;gap:32px;flex-wrap:wrap;padding-top:4px">%s</div>' % micro(a['micro'], lt))
    w('</div>')

    # conversa de exemplo
    w('<div style="display:flex;flex-direction:column;background:#0C0E10;border:1px solid %s55;border-radius:20px;overflow:hidden;box-shadow:0 40px 120px -60px %s">' % (ac, ac))
    w('<div style="display:flex;align-items:center;gap:12px;padding:18px 20px;border-bottom:1px solid rgba(255,255,255,0.07)">'
      '<span style="width:38px;height:38px;border-radius:11px;flex:none;display:inline-flex;align-items:center;justify-content:center;background:%s26;border:1px solid %s80">%s</span>'
      '<div style="flex:1;min-width:0"><div style="font-family:\'Bricolage Grotesque\',sans-serif;font-weight:800;font-size:17px;letter-spacing:-0.02em">%s</div>'
      '<div style="display:flex;align-items:center;gap:6px;font-size:11.5px;color:rgba(242,244,245,0.5);margin-top:2px"><span style="width:7px;height:7px;border-radius:50%%;background:#12D18A;flex:none"></span>Online agora</div></div>'
      '<span style="font-size:11px;color:rgba(242,244,245,0.4);white-space:nowrap">%s</span>'
      '<span style="color:rgba(242,244,245,0.35);font-size:16px">⋮</span></div>'
      % (ac, ac, svg(a['icon'], lt, 19, '1.7'), a['name'], e(a['chatRole'])))
    w('<div style="padding:20px;display:flex;flex-direction:column;gap:16px;min-width:0">')
    w('<div style="align-self:flex-end;max-width:82%%;background:%s;color:%s;border-radius:14px 14px 4px 14px;padding:12px 15px;font-size:13.5px;line-height:1.5">%s<div style="font-size:10px;opacity:0.7;text-align:right;margin-top:5px">20:14</div></div>'
      % (ac, tinta, e(a['q'])))
    w('<div style="display:flex;gap:12px;align-items:flex-start">'
      '<span style="width:30px;height:30px;border-radius:9px;flex:none;display:inline-flex;align-items:center;justify-content:center;background:%s26;border:1px solid %s80">%s</span>'
      % (ac, ac, svg(a['icon'], lt, 15, '1.7')))
    w('<div style="flex:1;min-width:0;background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.07);border-radius:14px 14px 14px 4px;padding:15px 17px;font-size:13.5px;line-height:1.7;display:flex;flex-direction:column;gap:6px">')
    w('<span style="color:rgba(242,244,245,0.78)">%s</span>' % e(a['intro']))
    for lead, negrito, resto in a['items']:
        w('<span style="display:flex;gap:8px"><span style="color:%s;font-weight:700;flex:none;font-variant-numeric:tabular-nums">%s</span>'
          '<span><strong style="font-weight:700">%s</strong> <span style="color:rgba(242,244,245,0.65)">%s</span></span></span>'
          % (lt, lead, e(negrito), e(resto)))
    w('<span style="color:rgba(242,244,245,0.65)">%s</span>' % e(a['outro']))
    w('<div style="font-size:10px;color:rgba(242,244,245,0.35);text-align:right">20:14</div>')
    w('</div></div>')
    w('<div style="display:flex;gap:9px;flex-wrap:wrap">%s</div>'
      % ''.join('<span style="padding:9px 15px;border-radius:9px;border:1px solid rgba(255,255,255,0.12);font-size:12.5px;color:rgba(242,244,245,0.75)">%s</span>' % e(c) for c in a['chips']))
    w('<div style="display:flex;align-items:center;gap:12px;border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:13px 14px;font-size:13px;color:rgba(242,244,245,0.4)">'
      '<span style="color:rgba(242,244,245,0.3)">📎</span>Digite sua pergunta...'
      '<span style="margin-left:auto;width:32px;height:32px;border-radius:50%%;display:inline-flex;align-items:center;justify-content:center;background:%s;color:%s;font-size:13px">➤</span></div>'
      % (ac, tinta))
    w('</div></div></div>')

    # faixa de assinatura
    w('<div style="position:relative;max-width:1280px;margin:0 auto;padding:56px 32px 0">'
      '<div style="display:flex;align-items:center;justify-content:space-between;gap:24px;flex-wrap:wrap;padding-top:26px;border-top:1px solid rgba(255,255,255,0.08);font-size:10.5px;letter-spacing:0.18em;text-transform:uppercase;font-weight:700;color:rgba(242,244,245,0.45)">'
      '<span style="display:flex;align-items:center;gap:14px"><span style="width:34px;height:2px;background:%s;display:inline-block"></span>%s</span>'
      '<span>%s</span></div></div>'
      % (ac, e(a['stripLeft']), e(a['stripRight'])))
    w('<div style="height:104px"></div></section>')

# --------------------------------------------------------------- planos ---
w('<section id="planos" style="border-top:1px solid rgba(255,255,255,0.06)">')
w('<div style="max-width:1280px;margin:0 auto;padding:110px 32px;display:flex;flex-direction:column;gap:40px">')
w('<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:32px;align-items:end">'
  '<h2 style="font-family:\'Bricolage Grotesque\',sans-serif;font-weight:800;font-size:clamp(38px,5vw,68px);line-height:0.95;letter-spacing:-0.04em;margin:0;text-wrap:balance">Um preço. Escolha só o assunto.</h2>'
  '<p style="font-size:17px;line-height:1.55;color:rgba(242,244,245,0.66);margin:0;max-width:480px">Cada agente é uma assinatura de R$ 30 por mês, independente. Acesso liberado em minutos, cancela quando quiser. Assine um, dois ou os três.</p></div>')
w('<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px">')
for p in PLANOS:
    ac, lt, tinta = p['accent'], p['light'], TINTA(p['short'])
    w('<div style="display:flex;flex-direction:column;gap:20px;background:#0C0E10;border:1px solid %s59;border-radius:18px;padding:30px 28px;box-shadow:0 40px 100px -70px %s">' % (ac, ac))
    w('<div style="display:flex;justify-content:space-between;align-items:center">'
      '<span style="font-family:\'Bricolage Grotesque\',sans-serif;font-weight:800;font-size:14px;letter-spacing:0.08em;padding:6px 12px;border-radius:7px;background:%s;color:%s">%s</span>'
      '<span style="font-size:10.5px;letter-spacing:0.18em;text-transform:uppercase;color:rgba(242,244,245,0.42);font-weight:700">%s</span></div>'
      % (ac, tinta, p['n'], e(p['nicho'])))
    w('<div><div style="font-family:\'Bricolage Grotesque\',sans-serif;font-weight:800;font-size:32px;letter-spacing:-0.03em;line-height:1">AX %s</div>'
      '<div style="font-size:14px;color:rgba(242,244,245,0.55);margin-top:8px">%s</div></div>' % (p['short'], e(p['tagline'])))
    w('<div style="display:flex;align-items:baseline;gap:6px"><span style="font-family:\'Bricolage Grotesque\',sans-serif;font-weight:800;font-size:46px;letter-spacing:-0.035em;line-height:1">R$ 30</span><span style="color:rgba(242,244,245,0.45)">/mês</span></div>')
    w('<div style="display:flex;flex-direction:column;gap:12px;flex:1">%s</div>'
      % ''.join('<div style="display:flex;gap:12px;align-items:flex-start;font-size:15px;line-height:1.45;color:rgba(242,244,245,0.85)"><span style="color:%s;flex:none">—</span><span>%s</span></div>' % (lt, e(f)) for f in p['features']))
    w('<a href="#%s" data-buy="%s" class="%s" style="display:flex;justify-content:center;padding:16px;border-radius:11px;background:%s;color:%s;font-weight:800;font-size:14.5px">%s</a>'
      % (p['short'].lower(), p['short'].lower(), hov('filter:brightness(1.12);color:#fff'), ac, tinta, e(p['cta'])))
    w('</div>')
w('</div></div></section>')

# -------------------------------------------------------------- revenda ---
PRECO_CLIENTE = 30
def brl(x, casas=2):
    s = ('%.2f' % x) if casas else ('%d' % round(x))
    return 'R$ ' + s.replace('.', ',')
def pct(p):
    return '%d%%' % round((PRECO_CLIENTE - p) / PRECO_CLIENTE * 100)
def milhar(n):
    return '{:,}'.format(n).replace(',', '.')

w('<section id="revenda" style="position:relative;overflow:hidden;border-top:1px solid rgba(255,255,255,0.06)">')
w('<div style="position:absolute;inset:0;pointer-events:none;background:radial-gradient(900px 480px at 50% 0%, rgba(123,63,242,0.22), transparent 70%)"></div>')
w('<div style="position:relative;max-width:1280px;margin:0 auto;padding:110px 32px;display:flex;flex-direction:column;gap:44px">')
w('<div style="display:flex;flex-direction:column;align-items:center;text-align:center;gap:16px">'
  '<div style="font-size:11px;letter-spacing:0.24em;text-transform:uppercase;color:rgba(242,244,245,0.5);font-weight:700">Para revendedores</div>'
  '<h2 style="font-family:\'Bricolage Grotesque\',sans-serif;font-weight:800;font-size:clamp(36px,4.8vw,62px);line-height:1;letter-spacing:-0.04em;margin:0;max-width:20ch;text-wrap:balance">Mais possibilidades <span style="color:rgba(242,244,245,0.42)">para o seu negócio.</span></h2>'
  '<p style="font-size:17px;color:rgba(242,244,245,0.6);margin:0">Mesmo sistema, mais vantagens.</p>'
  '<div style="display:flex;gap:40px;flex-wrap:wrap;justify-content:center;padding-top:10px">%s</div></div>'
  % ''.join('<div style="display:flex;align-items:center;gap:11px">%s<div style="text-align:left;font-size:14px;line-height:1.35">'
            '<span style="font-weight:700">%s</span><br><span style="color:rgba(242,244,245,0.5)">%s</span></div></div>'
            % (svg(p['d'], '#8FA6FF'), e(p['t1']), e(p['t2'])) for p in PERKS))

w('<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px;align-items:start">')
for t in PACOTES:
    ac, lt, tinta, chave = t['accent'], t['light'], TINTA(t['short']), t['short'].lower()
    w('<div data-pacote="%s" style="display:flex;flex-direction:column;gap:18px;background:#0B0C0E;border:1px solid %s80;border-radius:20px;padding:26px 24px;box-shadow:0 0 70px -30px %sAA">'
      % (chave, ac, ac))
    w('<div style="display:flex;align-items:center;gap:12px">'
      '<img src="./assets/ax-logo.png" alt="AX" style="width:30px;height:30px;mix-blend-mode:screen;flex:none">'
      '<span style="font-family:\'Bricolage Grotesque\',sans-serif;font-weight:800;font-size:27px;letter-spacing:-0.03em;color:%s">%s</span>'
      '<span style="margin-left:auto;padding:6px 12px;border-radius:999px;border:1px solid %sAA;color:%s;font-size:9.5px;letter-spacing:0.14em;text-transform:uppercase;font-weight:700;white-space:nowrap">%s</span></div>'
      % (lt, t['short'], ac, lt, e(t['nichoUp'])))
    w('<div style="font-size:14.5px;line-height:1.55;color:rgba(242,244,245,0.72)">%s<br><span style="color:rgba(242,244,245,0.5)">%s</span></div>'
      % (e(t['l1']), e(t['l2'])))
    w('<div style="display:flex;align-items:center;gap:9px;font-size:10.5px;letter-spacing:0.16em;text-transform:uppercase;font-weight:700;color:rgba(242,244,245,0.6)">%sPacotes de créditos (revenda)</div>'
      % svg('M12 7c4.4 0 8-1.1 8-2.5S16.4 2 12 2 4 3.1 4 4.5 7.6 7 12 7zM4 4.5v15C4 20.9 7.6 22 12 22s8-1.1 8-2.5v-15M4 12c0 1.4 3.6 2.5 8 2.5s8-1.1 8-2.5', lt, 15))

    # Cada faixa e um botao de escolha. O botao de compra la embaixo leva a
    # quantidade escolhida ate o checkout.
    w('<div style="display:flex;flex-direction:column;gap:7px">')
    for idx, (qtd, preco) in enumerate(t['tiers']):
        w('<button type="button" data-faixa="%d" data-qtd="%d" style="position:relative;display:flex;align-items:center;justify-content:space-between;gap:12px;width:100%%;text-align:left;padding:13px 15px;border-radius:10px;cursor:pointer;font-size:13.5px;font-variant-numeric:tabular-nums;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);color:#F2F4F5">'
          % (idx, qtd))
        w('<span data-marca hidden style="position:absolute;inset:-1px;border-radius:10px;pointer-events:none;background:%s2E;border:1px solid %s"></span>' % (ac, ac))
        w('<span style="position:relative;font-weight:600">%s créditos</span>'
          '<span style="position:relative;font-weight:700;white-space:nowrap">%s</span></button>'
          % (milhar(qtd), brl(preco)))
    w('</div>')

    w('<div style="font-size:12px;line-height:1.6;color:rgba(242,244,245,0.5);margin-top:auto">Preço por crédito. Cada crédito ativa um mês de um cliente seu, que paga '
      '<strong style="color:rgba(242,244,245,0.8)">R$ 30,00/mês</strong>. Sua margem vai de '
      '<strong style="color:rgba(242,244,245,0.8)">%s</strong> a <strong style="color:rgba(242,244,245,0.8)">%s</strong>.</div>'
      % (pct(t['tiers'][0][1]), pct(t['tiers'][-1][1])))
    w('<div data-resumo style="padding:13px 15px;border-radius:11px;background:%s1A;border:1px solid %s66;font-size:13px;line-height:1.5;color:#F2F4F5"></div>' % (ac, ac))
    w('<a href="#planos" data-comprar="%s" class="%s" style="display:flex;justify-content:center;padding:16px;border-radius:11px;background:%s;color:%s;font-weight:800;font-size:14.5px">Quero revender o %s →</a>'
      % (chave, hov('color:#fff;filter:brightness(1.1)'), ac, tinta, t['short']))
    w('</div>')
w('</div>')

w('<div style="display:flex;align-items:center;justify-content:space-between;gap:24px;flex-wrap:wrap;padding-top:26px;border-top:1px solid rgba(255,255,255,0.08)">'
  '<div style="display:flex;gap:30px;flex-wrap:wrap">%s</div>'
  '<span style="font-size:10.5px;letter-spacing:0.18em;text-transform:uppercase;font-weight:700;color:rgba(242,244,245,0.4)">Mesmo sistema. Mais lucro para você.</span></div>'
  % ''.join('<span style="display:flex;align-items:center;gap:10px;font-size:13.5px;color:rgba(242,244,245,0.65)">%s%s</span>'
            % (svg(n['d'], 'rgba(242,244,245,0.5)', 17), e(n['t'])) for n in NOTAS))

BLOCOS = [
 ('Assinar não é pré-requisito','A AX vende a assinatura direto ao cliente final e vende créditos a quem quer revender. Você pode ter sido assinante e virado parceiro depois, ou entrar direto na revenda por reconhecer a demanda no seu público.'),
 ('O que fica do nosso lado','IA, infraestrutura, manutenção e evolução do agente. Do seu lado ficam a audiência, o preço que você cobra e o relacionamento com o cliente.'),
 ('Sem meta mínima','Comece pela menor faixa do agente que combina com o seu público, teste com gente real e só aumente o pedido depois de vender.'),
]
w('<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:32px;padding-top:12px">%s</div>'
  % ''.join('<div><div style="font-weight:700;margin-bottom:8px">%s</div><div style="font-size:15px;line-height:1.6;color:rgba(242,244,245,0.6)">%s</div></div>'
            % (e(t_), e(d_)) for t_, d_ in BLOCOS))
w('</div></section>')

# ------------------------------------------------------------------ faq ---
w('<section id="faq" style="border-top:1px solid rgba(255,255,255,0.06)">')
w('<div style="max-width:1280px;margin:0 auto;padding:110px 32px;display:flex;flex-direction:column;gap:44px">')
w('<h2 style="font-family:\'Bricolage Grotesque\',sans-serif;font-weight:800;font-size:clamp(34px,4.4vw,62px);line-height:0.95;letter-spacing:-0.04em;margin:0;max-width:760px;text-wrap:balance">O que perguntam antes da primeira mensagem.</h2>')
w('<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:1px;background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.1);border-radius:20px;overflow:hidden">%s</div>'
  % ''.join('<div style="background:#08090A;padding:28px;display:flex;flex-direction:column;gap:12px">'
            '<div style="font-weight:700;font-size:17px">%s</div>'
            '<div style="font-size:15px;line-height:1.6;color:rgba(242,244,245,0.65)">%s</div></div>' % (e(q), e(r)) for q, r in FAQS))
w('</div></section>')

# ------------------------------------------------------------ cta final ---
w('<section style="position:relative;overflow:hidden;border-top:1px solid rgba(255,255,255,0.06)">')
w('<div style="position:absolute;inset:0;pointer-events:none;background:radial-gradient(900px 500px at 50% 120%, rgba(0,74,251,0.28), transparent 70%)"></div>')
w('<div style="position:relative;max-width:1280px;margin:0 auto;padding:130px 32px 140px;display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:40px;align-items:center">')
w('<div style="display:flex;flex-direction:column;gap:20px">'
  '<img src="./assets/ax-logo.png" alt="AX" style="width:72px;height:72px;mix-blend-mode:screen">'
  '<h2 style="font-family:\'Bricolage Grotesque\',sans-serif;font-weight:800;font-size:clamp(38px,5.2vw,76px);line-height:0.94;letter-spacing:-0.04em;margin:0;text-wrap:balance">Sobre o que você quer conversar hoje?</h2>'
  '<span style="font-size:15px;color:rgba(242,244,245,0.55)">R$ 30/mês · acesso em minutos · cancela quando quiser</span></div>')
FINAL = [('oscar','Oscar','#E01F3D','#fff','Filmes, séries, animes →'),
         ('scout','Scout','#12D18A','#06130D','Futebol →'),
         ('combat','Combat','#9B5CFF','#fff','MMA, UFC, boxe →')]
w('<div style="display:flex;flex-direction:column;gap:12px">')
for chave, nome, ac, tinta, legenda in FINAL:
    w('<a href="#%s" data-buy="%s" class="%s" style="display:flex;justify-content:space-between;align-items:center;padding:22px 26px;border-radius:14px;background:%s;color:%s;font-weight:800;font-size:18px">'
      '<span>%s</span><span style="font-weight:500;font-size:14px;opacity:0.85">%s</span></a>'
      % (chave, chave, hov('color:%s;filter:brightness(1.12)' % tinta), ac, tinta, nome, legenda))
w('</div></div></section>')

# --------------------------------------------------------------- rodape ---
w('<footer style="border-top:1px solid rgba(255,255,255,0.08)">'
  '<div style="max-width:1280px;margin:0 auto;padding:28px 32px;display:flex;flex-wrap:wrap;gap:20px 32px;align-items:center;justify-content:space-between;font-size:13px;color:rgba(242,244,245,0.5)">'
  '<div style="display:flex;align-items:center;gap:10px"><img src="./assets/ax-logo.png" alt="AX" style="width:26px;height:26px;mix-blend-mode:screen"><span>AX — um especialista para cada assunto</span></div>'
  '<div style="display:flex;gap:24px;flex-wrap:wrap">%s</div></div></footer>'
  % ''.join('<a href="#%s" style="color:rgba(242,244,245,0.5)">%s</a>' % (h[1:], r) for h, r, _ in NAV[:5]))

w('</div>\n<script src="./app.js" defer></script>\n</body>\n</html>\n')

# ------------------------------------------------------------- gravacao ---
(SAIDA / 'index.html').write_text('\n'.join(P), encoding='utf-8')

CSS = """/* ==========================================================================
   AX — landing page
   A folha e curta de proposito: o desenho traz os estilos embutidos em cada
   elemento. Aqui ficam so a base da pagina e as regras de :hover, que nao
   cabem num atributo style.
   ========================================================================== */

html { scroll-behavior: smooth; scroll-padding-top: 96px; }
html, body {
  margin: 0; padding: 0;
  background: #08090A; color: #F2F4F5;
  font-family: Manrope, system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}
a { color: #F2F4F5; text-decoration: none; }
a:hover { color: #FF8095; }
button { font-family: inherit; }
img { display: block; max-width: 100%; }

@keyframes axIn { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }
@keyframes axBlink { 0%, 49% { opacity: 1; } 50%, 100% { opacity: 0; } }

/* Hover de cada elemento do desenho. */
""" + '\n'.join(REGRAS) + """

@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  * { animation: none !important; transition: none !important; }
}
"""
(SAIDA / 'styles.css').write_text(CSS, encoding='utf-8')
print('index.html %d bytes | styles.css %d bytes | %d regras de hover'
      % ((SAIDA/'index.html').stat().st_size, (SAIDA/'styles.css').stat().st_size, len(REGRAS)))
