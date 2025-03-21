from flask import Flask, render_template, request, redirect, url_for
from openai import OpenAI
import json
import os
from datetime import datetime

app = Flask(__name__)

# Configuração da API da OpenAI
api_key = "sua-chave-api-aqui"  # Substitua pela sua chave da OpenAI
client = OpenAI(api_key=api_key)

# Arquivo para salvar o histórico
HISTORY_FILE = "conversation_history.json"

# Carregar histórico do arquivo
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Salvar histórico no arquivo
def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

# Função para obter resposta do agente via API da OpenAI
def get_agent_response(agent_name, user_input):
    try:
        prompts = {
            "Perfil do Cliente Ideal (ICP)": (
                "Você é um especialista em marketing com foco em identificar o Perfil do Cliente Ideal (ICP). "
                "Sua tarefa é analisar o contexto fornecido pelo usuário e criar um perfil detalhado do cliente ideal, "
                "incluindo faixa etária, interesses, comportamentos, dores e objetivos. Responda de forma clara e prática, "
                "como se estivesse orientando um profissional de marketing. O usuário digitou: '{user_input}'."
            ),
            "SPIN Selling": (
                "Você é um especialista em vendas usando a metodologia SPIN Selling (Situação, Problema, Implicação, Necessidade de Solução). "
                "Sua tarefa é sugerir perguntas específicas para cada etapa do SPIN Selling com base no contexto fornecido, "
                "ajudando o usuário a conduzir uma venda mais eficaz. Responda de forma estruturada e prática. O usuário digitou: '{user_input}'."
            ),
            "Oferta Exponencial": (
                "Você é um especialista em criar ofertas irresistíveis que seguem o conceito de 'Oferta Exponencial'. "
                "Sua tarefa é criar uma oferta tão atraente que o cliente se sinta compelido a aceitá-la, com base no contexto fornecido. "
                "Inclua elementos como bônus, garantias e gatilhos emocionais. Responda de forma persuasiva e detalhada. O usuário digitou: '{user_input}'."
            ),
            "Nomes Exponenciais": (
                "Você é um especialista em naming para marketing, com foco em criar nomes impactantes e memoráveis. "
                "Sua tarefa é sugerir 3 a 5 nomes criativos para a oferta, produto ou curso mencionado pelo usuário, "
                "explicando brevemente o motivo de cada escolha. Responda de forma criativa e prática. O usuário digitou: '{user_input}'."
            ),
            "Causa Surpreendente Principal": (
                "Você é um especialista em análise de problemas de marketing. "
                "Sua tarefa é identificar a causa principal e muitas vezes surpreendente dos problemas mencionados pelo usuário, "
                "explicando como essa causa pode ser usada para criar uma estratégia de vendas mais eficaz. Responda de forma analítica e estratégica. O usuário digitou: '{user_input}'."
            ),
            "Solução Primária Única": (
                "Você é um especialista em criar soluções únicas e inovadoras para problemas de marketing. "
                "Sua tarefa é propor uma solução primária que se destaque dos concorrentes, com base no contexto fornecido, "
                "explicando como ela pode ser implementada. Responda de forma inovadora e prática. O usuário digitou: '{user_input}'."
            ),
            "Temas YouTube": (
                "Você é um especialista em criação de conteúdo para YouTube. "
                "Sua tarefa é transformar a ideia fornecida pelo usuário em um tema de vídeo cativante e impossível de ignorar, "
                "explicando como o tema pode atrair visualizações. Responda de forma criativa e estratégica. O usuário digitou: '{user_input}'."
            ),
            "Títulos para YouTube": (
                "Você é um especialista em otimização de títulos para YouTube. "
                "Sua tarefa é criar 3 a 5 títulos otimizados para o contexto fornecido, que sejam chamativos e performem bem no YouTube, "
                "explicando o motivo de cada escolha. Responda de forma prática e estratégica. O usuário digitou: '{user_input}'."
            ),
            "Hooks Persuasivos": (
                "Você é um especialista em copywriting persuasivo, com foco em criar hooks (ganchos) que capturam a atenção. "
                "Sua tarefa é criar 3 a 5 hooks altamente persuasivos e chamativos com base no contexto fornecido, "
                "explicando como cada um pode engajar o público. Responda de forma criativa e persuasiva. O usuário digitou: '{user_input}'."
            ),
            "Meta Ads do Problema": (
                "Você é um especialista em Meta Ads (anúncios no Facebook e Instagram). "
                "Sua tarefa é identificar os problemas comuns no contexto fornecido que podem estar prejudicando os resultados dos anúncios, "
                "e sugerir soluções práticas para resolvê-los. Responda de forma analítica e prática. O usuário digitou: '{user_input}'."
            ),
            "A Solução Inesperada": (
                "Você é um especialista em criar anúncios criativos e inovadores. "
                "Sua tarefa é propor uma solução inesperada para o contexto fornecido, que seja capaz de capturar a atenção, "
                "desafiar crenças e gerar intenção de compra. Responda de forma criativa e estratégica. O usuário digitou: '{user_input}'."
            ),
            "Troca de Crenças": (
                "Você é um especialista em persuasão para marketing, com foco em mudar crenças do público. "
                "Sua tarefa é criar um anúncio persuasivo que mude uma crença limitante do prospect, "
                "estabelecendo uma nova premissa que facilite a venda, com base no contexto fornecido. Responda de forma persuasiva e estratégica. O usuário digitou: '{user_input}'."
            )
        }

        prompt_template = prompts.get(agent_name, "Você é um especialista em marketing. Forneça uma resposta útil e prática para o contexto de marketing fornecido.")
        prompt = prompt_template.format(user_input=user_input)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ],
            max_tokens=300,
            temperature=0.6,
            top_p=1.0
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Erro ao obter resposta: {str(e)}. Verifique sua conexão ou a chave da API."

# Lista de agentes
agents = [
    ("Perfil do Cliente Ideal (ICP)", "Entenda se o seu cliente ideal melhor que ele mesmo se entende."),
    ("SPIN Selling", "Descubra perguntas relevantes para aplicar a metodologia SPIN Selling em suas vendas."),
    ("Oferta Exponencial", "Como criar uma oferta tão boa que as pessoas se sintam estúpidas em dizer não!"),
    ("Nomes Exponenciais", "Como criar os melhores nomes para a sua oferta, produto ou curso."),
    ("Causa Surpreendente Principal", "Encontre o real culpado dos problemas do seu prospect e o venda."),
    ("Solução Primária Única", "Crie uma solução única diferente de todos os seus concorrentes."),
    ("Temas YouTube", "Transforme uma ideia sem graça em um vídeo impossível de ignorar."),
    ("Títulos para YouTube", "Crie títulos otimizados para performar no YouTube."),
    ("Hooks Persuasivos", "Atenção é o nome do jogo. Portanto, crie hooks (ganchos) altamente persuasivos e chamativos."),
    ("Meta Ads do Problema", "Revele como os problemas comuns podem piorar os resultados."),
    ("A Solução Inesperada", "Como criar anúncios altamente persuasivos para capturar a atenção, desafiar crenças e gerar intenção de compra."),
    ("Troca de Crenças", "Crie um anúncio persuasivo para estabelecer a Premissa Persuasiva na mente do seu prospect e facilitar a venda.")
]

# Carregar o histórico ao iniciar
history = load_history()

# Rota para a página inicial
@app.route('/')
def index():
    # Mostrar apenas as últimas 10 entradas do histórico
    recent_history = history[-10:] if len(history) > 10 else history
    return render_template('index.html', agents=agents, recent_history=recent_history)

# Rota para a página do agente
@app.route('/agent/<agent_name>', methods=['GET', 'POST'])
def agent_page(agent_name):
    if agent_name not in [agent[0] for agent in agents]:
        return "Agente não encontrado", 404

    if request.method == 'POST':
        user_input = request.form['user_input']
        if not user_input:
            return render_template('agent.html', agent_name=agent_name, error="Por favor, digite uma mensagem antes de enviar.")

        # Obter resposta do agente
        response = get_agent_response(agent_name, user_input)

        # Adicionar ao histórico
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_entry = f"[{timestamp}] {agent_name}: {user_input}\nResposta: {response}\n{'-'*50}"
        history.append(history_entry)
        save_history(history)

        return render_template('agent.html', agent_name=agent_name, user_input=user_input, response=response)

    return render_template('agent.html', agent_name=agent_name)

# Rota para a página de histórico
@app.route('/history')
def history_page():
    return render_template('history.html', history=history)

# Rota para limpar o histórico
@app.route('/clear_history', methods=['POST'])
def clear_history():
    global history
    history = []
    save_history(history)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)