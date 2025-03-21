import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os
from datetime import datetime
import threading
import configparser
from openai import OpenAI

# Configuration section
CONFIG_FILE = "config.ini"
HISTORY_FILE = "conversation_history.json"

# Initialize configuration
def initialize_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    else:
        config['API'] = {'key': ''}
        with open(CONFIG_FILE, 'w') as f:
            config.write(f)
    return config

# Get API key from config
def get_api_key():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config['API'].get('key', '')

# Set API key
def set_api_key(api_key):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    config['API']['key'] = api_key
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)

# Load history from file
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Save history to file
def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

# Function to get agent response via OpenAI API
def get_agent_response(agent_name, user_input):
    try:
        api_key = get_api_key()
        if not api_key:
            return "Erro: API key não configurada. Por favor, configure sua chave API nas Configurações."

        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Agent prompts
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

        # Get the appropriate prompt template or use a default
        prompt_template = prompts.get(agent_name, "Você é um especialista em marketing. Forneça uma resposta útil e prática para o contexto de marketing fornecido.")
        prompt = prompt_template.format(user_input=user_input)

        # Make API call to OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ],
            max_tokens=500,
            temperature=0.7,
            top_p=1.0
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Erro ao obter resposta: {str(e)}. Verifique sua conexão ou a chave da API."

# Function to copy text to clipboard
def copy_to_clipboard(text, root):
    root.clipboard_clear()
    root.clipboard_append(text)
    messagebox.showinfo("Sucesso", "Resposta copiada para a área de transferência!")

# Function to create agent interaction window
def open_agent_window(agent_name, history_listbox, root, history):
    agent_window = tk.Toplevel(root)
    agent_window.title(agent_name)
    agent_window.state('zoomed')  # Open in full screen
    agent_window.configure(bg="#f5f5f5")

    # Configure grid manager for the window
    agent_window.grid_rowconfigure(1, weight=1)  # Chat row expands
    agent_window.grid_rowconfigure(0, weight=0)  # Header row doesn't expand
    agent_window.grid_rowconfigure(2, weight=0)  # Button row doesn't expand
    agent_window.grid_rowconfigure(3, weight=0)  # Input bar row doesn't expand
    agent_window.grid_columnconfigure(0, weight=1)

    # Header frame with title and back button
    header_frame = tk.Frame(agent_window, bg="#f5f5f5")
    header_frame.grid(row=0, column=0, sticky="ew", pady=15, padx=30)

    # Back button
    back_button = tk.Button(
        header_frame,
        text="← Voltar",
        command=agent_window.destroy,
        font=("Montserrat", 14, "bold"),
        bg="#2196F3",
        fg="white",
        bd=0,
        padx=20,
        pady=8
    )
    back_button.pack(side="left")

    # Window title
    tk.Label(
        header_frame,
        text=f"Agente: {agent_name}",
        font=("Montserrat", 18, "bold"),
        bg="#f5f5f5",
        fg="#333333"
    ).pack(side="left", padx=15)

    # Chat area (message history)
    chat_frame = tk.Frame(agent_window, bg="#f0f0f0", bd=1, relief="sunken")
    chat_frame.grid(row=1, column=0, sticky="nsew", pady=15, padx=30)

    chat_area = scrolledtext.ScrolledText(
        chat_frame,
        height=30,
        font=("Montserrat", 14),
        bg="#f0f0f0",
        fg="#333333",
        bd=0,
        wrap="word"
    )
    chat_area.pack(pady=15, padx=15, fill="both", expand=True)
    chat_area.config(state="disabled")

    # Function to add message to chat
    def add_message_to_chat(sender, message, is_user=False):
        chat_area.config(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        tag = "user" if is_user else "agent"
        color = "#DCF8C6" if is_user else "#E0E0E0"
        align = "right" if is_user else "left"
        icon = "👤" if is_user else "🤖"

        chat_area.insert(tk.END, f"{icon} [{timestamp}] {sender}:\n", (tag, "timestamp"))
        chat_area.insert(tk.END, f"{message}\n\n", tag)
        chat_area.tag_config("user", background=color, justify=align, lmargin1=200, lmargin2=200, rmargin=40, spacing1=10, spacing3=10)
        chat_area.tag_config("agent", background=color, justify=align, lmargin1=40, lmargin2=40, rmargin=200, spacing1=10, spacing3=10)
        chat_area.tag_config("timestamp", foreground="#888888", font=("Montserrat", 11))
        chat_area.yview(tk.END)
        chat_area.config(state="disabled")

    # Button frame for additional buttons (Clear Chat and Copy Response)
    button_frame = tk.Frame(agent_window, bg="#f5f5f5")
    button_frame.grid(row=2, column=0, sticky="ew", pady=10, padx=30)

    tk.Button(
        button_frame,
        text="Limpar Chat",
        command=lambda: clear_chat(),
        font=("Montserrat", 14, "bold"),
        bg="#FF4444",
        fg="white",
        bd=0,
        padx=25,
        pady=10
    ).pack(side="left", padx=15)
    
    tk.Button(
        button_frame,
        text="Copiar Resposta",
        command=lambda: copy_last_response(),
        font=("Montserrat", 14, "bold"),
        bg="#2196F3",
        fg="white",
        bd=0,
        padx=25,
        pady=10
    ).pack(side="left", padx=15)

    # User input area
    input_frame = tk.Frame(agent_window, bg="#f5f5f5")
    input_frame.grid(row=3, column=0, sticky="ew", pady=15, padx=30)

    # Frame for text input with integrated send button
    entry_container = tk.Frame(input_frame, bg="#ffffff", bd=1, relief="sunken")
    entry_container.pack(fill="x", pady=5)

    # Placeholder for the input
    placeholder_text = "Digite sua mensagem..."
    user_input = tk.StringVar()
    user_input_entry = tk.Entry(
        entry_container,
        textvariable=user_input,
        font=("Montserrat", 16),
        bg="#ffffff",
        fg="#333333",
        bd=0,
        relief="flat",
        insertbackground="#333333",
        insertwidth=2
    )
    user_input_entry.pack(side="left", fill="x", expand=True, padx=20, pady=10)

    # Function to manage placeholder
    def on_entry_click(event):
        if user_input.get() == placeholder_text:
            user_input.set("")
            user_input_entry.config(fg="#333333")

    def on_focusout(event):
        if not user_input.get():
            user_input.set(placeholder_text)
            user_input_entry.config(fg="#888888")

    user_input.set(placeholder_text)
    user_input_entry.config(fg="#888888")
    user_input_entry.bind("<FocusIn>", on_entry_click)
    user_input_entry.bind("<FocusOut>", on_focusout)

    # Send button with icon
    send_button = tk.Button(
        entry_container,
        text="➤",
        command=lambda: submit_input(),
        font=("Montserrat", 14, "bold"),
        bg="#2196F3",
        fg="white",
        bd=0,
        relief="flat",
        padx=15,
        pady=8
    )
    send_button.pack(side="right", padx=15)

    # Attachment button (for future expansion)
    attach_button = tk.Button(
        entry_container,
        text="📎",
        font=("Montserrat", 14),
        bg="#ffffff",
        fg="#333333",
        bd=0,
        relief="flat",
        padx=15,
        pady=8
    )
    attach_button.pack(side="left", padx=15)

    # Function to process agent response in a separate thread
    def process_agent_response(user_input_text):
        # Show "Typing..." while processing
        add_message_to_chat(agent_name, "Digitando...", is_user=False)

        # Get agent response
        response = get_agent_response(agent_name, user_input_text)

        # Remove "Typing..." and add the real response
        chat_area.config(state="normal")
        chat_area.delete("end-2l", "end")
        chat_area.config(state="disabled")
        add_message_to_chat(agent_name, response, is_user=False)

        # Add to history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_entry = {
            "timestamp": timestamp,
            "agent": agent_name,
            "input": user_input_text,
            "response": response
        }
        
        history.append(history_entry)
        history_listbox.delete(0, tk.END)
        
        # Update history listbox (newest first)
        for entry in reversed(history):
            if isinstance(entry, dict):  # New format
                entry_text = f"[{entry['timestamp']}] {entry['agent']}: {entry['input'][:30]}..."
            else:  # Legacy format
                parts = entry.split("]")
                if len(parts) > 1:
                    timestamp = parts[0][1:]
                    remaining = parts[1].split("\n")[0]
                    entry_text = f"[{timestamp}] {remaining[:30]}..."
                else:
                    entry_text = entry[:50] + "..."
                    
            history_listbox.insert(tk.END, entry_text)
            
        save_history(history)

    # Function to send message
    def submit_input(event=None):
        user_input_text = user_input.get().strip()
        if user_input_text == placeholder_text or not user_input_text:
            messagebox.showwarning("Entrada Vazia", "Por favor, digite uma mensagem antes de enviar.")
            return

        # Add user message to chat immediately
        add_message_to_chat("Você", user_input_text, is_user=True)
        user_input.set(placeholder_text)
        user_input_entry.config(fg="#888888")

        # Process agent response in a separate thread
        threading.Thread(target=process_agent_response, args=(user_input_text,), daemon=True).start()

    # Function to clear chat
    def clear_chat():
        chat_area.config(state="normal")
        chat_area.delete("1.0", tk.END)
        chat_area.config(state="disabled")
        user_input.set(placeholder_text)
        user_input_entry.config(fg="#888888")

    # Function to copy last response
    def copy_last_response():
        chat_area.config(state="normal")
        chat_content = chat_area.get("1.0", tk.END).strip()
        chat_area.config(state="disabled")
        
        if chat_content:
            # Try to extract the last agent response
            parts = chat_content.split('\n\n')
            if len(parts) > 1:
                agent_parts = [p for p in parts if "🤖" in p]
                if agent_parts:
                    last_response = agent_parts[-1].split('\n', 1)[1] if '\n' in agent_parts[-1] else ""
                    if last_response:
                        copy_to_clipboard(last_response, root)
                        return
            
            messagebox.showinfo("Sem Resposta", "Nenhuma resposta do agente encontrada para copiar.")

    # Bind Enter key to send message
    user_input_entry.bind("<Return>", submit_input)

# Function to create agent blocks
def create_agent_block(frame, agent_name, description, row, col, history_listbox, root, history):
    block_frame = tk.Frame(frame, bd=2, relief="groove", padx=15, pady=15, bg="#f0f0f0")
    block_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    # Configure grid manager inside block_frame
    block_frame.grid_rowconfigure(0, weight=0)  # Icon
    block_frame.grid_rowconfigure(1, weight=0)  # Title
    block_frame.grid_rowconfigure(2, weight=1)  # Description (expands to fill space)
    block_frame.grid_rowconfigure(3, weight=0)  # Button
    block_frame.grid_columnconfigure(0, weight=1)

    # Icon
    tk.Label(block_frame, text="📋", font=("Montserrat", 20), bg="#f0f0f0").grid(row=0, column=0, sticky="w")

    # Title
    tk.Label(block_frame, text=agent_name, font=("Montserrat", 12, "bold"), bg="#f0f0f0", fg="#333333").grid(row=1, column=0, sticky="w")

    # Description
    tk.Label(block_frame, text=description, font=("Montserrat", 10), wraplength=200, justify="left", bg="#f0f0f0", fg="#666666").grid(row=2, column=0, sticky="w", pady=5)

    # Access button with black background and hover effect
    access_button = tk.Button(
        block_frame,
        text="Acessar",
        command=lambda: open_agent_window(agent_name, history_listbox, root, history),
        font=("Montserrat", 12, "bold"),
        bg="#000000",  # Black background
        fg="white",    # White text
        bd=0,
        padx=20,
        pady=8,
        relief="flat"
    )
    access_button.grid(row=3, column=0, sticky="e", pady=10)

    # Functions for hover effect
    def on_enter(e):
        access_button.config(bg="#333333")  # Dark gray when hovering

    def on_leave(e):
        access_button.config(bg="#000000")  # Back to black

    access_button.bind("<Enter>", on_enter)
    access_button.bind("<Leave>", on_leave)

# Function to view full history
def view_history(history_listbox, root, history):
    history_window = tk.Toplevel(root)
    history_window.title("Histórico de Conversas")
    history_window.geometry("800x600")
    history_window.configure(bg="#f5f5f5")

    # Add a label at the top
    tk.Label(
        history_window, 
        text="Histórico de Conversas", 
        font=("Montserrat", 16, "bold"), 
        bg="#f5f5f5", 
        fg="#333333"
    ).pack(pady=10)

    # History content frame
    history_frame = tk.Frame(history_window, bg="#ffffff", bd=1, relief="solid")
    history_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Create scrolled text widget for history display
    history_text = scrolledtext.ScrolledText(
        history_frame, 
        font=("Montserrat", 12), 
        bg="#ffffff", 
        fg="#333333", 
        wrap="word"
    )
    history_text.pack(fill="both", expand=True, padx=10, pady=10)
    history_text.config(state="normal")

    # Load and display history entries
    if not history:
        history_text.insert(tk.END, "Nenhum histórico de conversa encontrado.")
    else:
        for entry in history:
            if isinstance(entry, dict):  # New format
                timestamp = entry.get("timestamp", "Horário desconhecido")
                agent = entry.get("agent", "Agente desconhecido")
                user_input = entry.get("input", "")
                response = entry.get("response", "")
                
                history_text.insert(tk.END, f"[{timestamp}] Agente: {agent}\n", "header")
                history_text.insert(tk.END, f"Pergunta: {user_input}\n", "input")
                history_text.insert(tk.END, f"Resposta: {response}\n", "response")
                history_text.insert(tk.END, f"{'-'*80}\n\n")
            else:  # Legacy format (string)
                history_text.insert(tk.END, f"{entry}\n\n")
    
    # Configure tags for styling
    history_text.tag_config("header", foreground="#2196F3", font=("Montserrat", 12, "bold"))
    history_text.tag_config("input", foreground="#333333")
    history_text.tag_config("response", foreground="#666666")
    
    history_text.config(state="disabled")
    
    # Add buttons at the bottom
    button_frame = tk.Frame(history_window, bg="#f5f5f5")
    button_frame.pack(pady=10)
    
    tk.Button(
        button_frame,
        text="Fechar",
        command=history_window.destroy,
        font=("Montserrat", 12, "bold"),
        bg="#2196F3",
        fg="white",
        bd=0,
        padx=20,
        pady=8
    ).pack(side="left", padx=10)
    
    tk.Button(
        button_frame,
        text="Limpar Histórico",
        command=lambda: clear_history(history_text, history, history_listbox),
        font=("Montserrat", 12, "bold"),
        bg="#FF4444",
        fg="white",
        bd=0,
        padx=20,
        pady=8
    ).pack(side="left", padx=10)

# Function to clear history
def clear_history(history_text=None, history=None, history_listbox=None):
    confirm = messagebox.askyesno("Confirmar", "Tem certeza que deseja limpar todo o histórico de conversas?")
    if confirm:
        # Clear the history list
        if history is not None:
            history.clear()
            save_history(history)
        
        # Clear the history listbox
        if history_listbox is not None:
            history_listbox.delete(0, tk.END)
        
        # Update the history text widget if provided
        if history_text is not None:
            history_text.config(state="normal")
            history_text.delete("1.0", tk.END)
            history_text.insert(tk.END, "Histórico limpo.")
            history_text.config(state="disabled")
        
        messagebox.showinfo("Sucesso", "O histórico de conversas foi limpo.")

# Function to open settings window
def open_settings(root):
    settings_window = tk.Toplevel(root)
    settings_window.title("Configurações")
    settings_window.geometry("500x300")
    settings_window.configure(bg="#f5f5f5")
    
    # Add a label at the top
    tk.Label(
        settings_window, 
        text="Configurações da Aplicação", 
        font=("Montserrat", 16, "bold"), 
        bg="#f5f5f5", 
        fg="#333333"
    ).pack(pady=10)
    
    # Create a frame for the settings content
    settings_frame = tk.Frame(settings_window, bg="#ffffff", bd=1, relief="solid")
    settings_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    # API Key settings
    tk.Label(
        settings_frame, 
        text="Chave da API OpenAI:", 
        font=("Montserrat", 12, "bold"), 
        bg="#ffffff", 
        fg="#333333",
        anchor="w"
    ).pack(fill="x", padx=20, pady=(20, 5))
    
    # Get current API key
    current_key = get_api_key()
    displayed_key = "•" * 8 + current_key[-4:] if current_key else ""
    
    api_key_var = tk.StringVar(value=displayed_key)
    api_key_entry = tk.Entry(
        settings_frame, 
        textvariable=api_key_var, 
        font=("Montserrat", 12), 
        bg="#f5f5f5", 
        fg="#333333", 
        show="•",
        width=40
    )
    api_key_entry.pack(padx=20, pady=5)
    
    # Function to toggle API key visibility
    def toggle_key_visibility():
        if api_key_entry.cget('show') == '•':
            api_key_entry.config(show='')
            view_key_button.config(text="Ocultar Chave")
        else:
            api_key_entry.config(show='•')
            view_key_button.config(text="Ver Chave")
    
    # Function to update API key
    def update_api_key():
        new_key = api_key_var.get().strip()
        if new_key and new_key != displayed_key:
            set_api_key(new_key)
            messagebox.showinfo("Sucesso", "Chave da API atualizada com sucesso!")
            settings_window.destroy()
        elif not new_key:
            messagebox.showwarning("Aviso", "Por favor, insira uma chave da API.")
    
    # Add buttons for API key management
    key_buttons_frame = tk.Frame(settings_frame, bg="#ffffff")
    key_buttons_frame.pack(fill="x", padx=20, pady=5)
    
    view_key_button = tk.Button(
        key_buttons_frame,
        text="Ver Chave",
        command=toggle_key_visibility,
        font=("Montserrat", 10),
        bg="#2196F3",
        fg="white",
        bd=0,
        padx=10,
        pady=2
    )
    view_key_button.pack(side="left", pady=5)
    
    # Buttons at the bottom
    button_frame = tk.Frame(settings_window, bg="#f5f5f5")
    button_frame.pack(pady=10)
    
    tk.Button(
        button_frame,
        text="Cancelar",
        command=settings_window.destroy,
        font=("Montserrat", 12, "bold"),
        bg="#9E9E9E",
        fg="white",
        bd=0,
        padx=20,
        pady=8
    ).pack(side="left", padx=10)
    
    tk.Button(
        button_frame,
        text="Salvar",
        command=update_api_key,
        font=("Montserrat", 12, "bold"),
        bg="#4CAF50",
        fg="white",
        bd=0,
        padx=20,
        pady=8
    ).pack(side="left", padx=10)

# Function to show about dialog
def show_about(root):
    about_window = tk.Toplevel(root)
    about_window.title("Sobre A.R.O.S.")
    about_window.geometry("400x300")
    about_window.configure(bg="#ffffff")
    about_window.resizable(False, False)
    
    # Center the window
    about_window.update_idletasks()
    width = about_window.winfo_width()
    height = about_window.winfo_height()
    x = (about_window.winfo_screenwidth() // 2) - (width // 2)
    y = (about_window.winfo_screenheight() // 2) - (height // 2)
    about_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    # Logo/Icon placeholder
    tk.Label(about_window, text="🤖", font=("Montserrat", 48), bg="#ffffff").pack(pady=(20, 10))
    
    # App name
    tk.Label(
        about_window, 
        text="A.R.O.S. - Agentes Resolutivos", 
        font=("Montserrat", 16, "bold"), 
        bg="#ffffff"
    ).pack()
    
    # Version
    tk.Label(
        about_window, 
        text="Versão 1.0.0", 
        font=("Montserrat", 10), 
        bg="#ffffff", 
        fg="#666666"
    ).pack()
    
    # Description
    tk.Label(
        about_window, 
        text="Uma ferramenta com IA para auxiliar em diversas tarefas de marketing.", 
        font=("Montserrat", 10), 
        bg="#ffffff", 
        wraplength=300,
        justify="center"
    ).pack(pady=10)
    
    # Credits
    tk.Label(
        about_window, 
        text="© 2025 A.R.O.S. - Agentes Resolutivos", 
        font=("Montserrat", 8), 
        bg="#ffffff", 
        fg="#666666"
    ).pack(pady=(20, 0))
    
    # Close button
    tk.Button(
        about_window,
        text="Fechar",
        command=about_window.destroy,
        font=("Montserrat", 10, "bold"),
        bg="#2196F3",
        fg="white",
        bd=0,
        padx=20,
        pady=5
    ).pack(pady=10)

# Check for API key on startup
def check_api_key(root):
    api_key = get_api_key()
    if not api_key:
        messagebox.showwarning(
            "Chave da API Necessária", 
            "Nenhuma chave da API encontrada. Por favor, configure sua chave da API OpenAI nas Configurações."
        )
        open_settings(root)

# Main function to run the application
def main():
    # Main application window
    root = tk.Tk()
    root.title("A.R.O.S. - Agentes Resolutivos")
    root.geometry("1200x700")
    root.configure(bg="#ffffff")

    # Initialize configuration
    initialize_config()
    
    # Load history
    history = load_history()

    # Top bar
    top_frame = tk.Frame(root, bg="#333333", height=50)
    top_frame.pack(side="top", fill="x")
    tk.Label(top_frame, text="A.R.O.S. - Agentes Resolutivos", font=("Montserrat", 16, "bold"), fg="white", bg="#333333").pack(side="left", padx=20, pady=10)
    
    # Add settings button to top bar
    tk.Button(
        top_frame,
        text="⚙️ Configurações",
        command=lambda: open_settings(root),
        font=("Montserrat", 10, "bold"),
        bg="#333333",
        fg="white",
        bd=0,
        padx=15,
        pady=5
    ).pack(side="right", padx=5)
    
    tk.Button(
        top_frame,
        text="Sair (ESC)",
        command=root.quit,
        font=("Montserrat", 10, "bold"),
        bg="#FF4444",
        fg="white",
        bd=0,
        padx=15,
        pady=5
    ).pack(side="right", padx=20)

    # Side menu
    side_frame = tk.Frame(root, bg="#e0e0e0", width=250)
    side_frame.pack(side="left", fill="y")

    tk.Label(side_frame, text="Menu", font=("Montserrat", 14, "bold"), bg="#e0e0e0", fg="#333333").pack(pady=10)

    menu_buttons = [
        ("📖 Instruções", lambda: messagebox.showinfo("Instruções", "Bem-vindo ao A.R.O.S.! Clique em um agente para interagir.")),
        ("🤖 Agentes", lambda: None),
        ("📜 Histórico", lambda: view_history(history_listbox, root, history)),
        ("⚙️ Configurações", lambda: open_settings(root)),
        ("💡 Sugestões", lambda: messagebox.showinfo("Sugestões", "Envie suas sugestões para nossa equipe!")),
        ("ℹ️ Sobre", lambda: show_about(root))
    ]

    for text, command in menu_buttons:
        button = tk.Button(
            side_frame,
            text=text,
            command=command,
            font=("Montserrat", 12),
            bg="#e0e0e0",
            fg="#333333",
            bd=0,
            anchor="w",
            padx=20,
            pady=5
        )
        button.pack(fill="x")
        
        # Add hover effect
        def on_enter(e, btn=button):
            btn.config(bg="#d0d0d0")
        
        def on_leave(e, btn=button):
            btn.config(bg="#e0e0e0")
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    tk.Label(side_frame, text="Histórico Recente", font=("Montserrat", 12, "bold"), bg="#e0e0e0", fg="#333333").pack(pady=10)
    
    # Frame for history listbox with scrollbar
    history_list_frame = tk.Frame(side_frame, bg="#e0e0e0")
    history_list_frame.pack(fill="x", padx=10, pady=5)
    
    history_listbox = tk.Listbox(
        history_list_frame, 
        font=("Montserrat", 10), 
        bg="#ffffff", 
        fg="#333333", 
        bd=2, 
        relief="groove", 
        height=10
    )
    history_listbox.pack(side="left", fill="both", expand=True)
    
    # Add scrollbar to history listbox
    history_scrollbar = tk.Scrollbar(history_list_frame, orient="vertical")
    history_scrollbar.pack(side="right", fill="y")
    history_listbox.config(yscrollcommand=history_scrollbar.set)
    history_scrollbar.config(command=history_listbox.yview)
    
    # Populate history listbox with existing entries (newest first)
    for entry in reversed(history):
        if isinstance(entry, dict):  # New format
            timestamp = entry.get("timestamp", "")
            agent = entry.get("agent", "")
            user_input = entry.get("input", "")[:30]
            history_listbox.insert(tk.END, f"[{timestamp}] {agent}: {user_input}...")
        else:  # Legacy format
            parts = entry.split("]")
            if len(parts) > 1:
                timestamp = parts[0][1:]
                remaining = parts[1].split("\n")[0]
                history_listbox.insert(tk.END, f"[{timestamp}] {remaining[:30]}...")
    
    # Add clear history button below listbox
    tk.Button(
        side_frame,
        text="Limpar Histórico",
        command=lambda: clear_history(None, history, history_listbox),
        font=("Montserrat", 10),
        bg="#FF4444",
        fg="white",
        bd=0,
        padx=10,
        pady=5
    ).pack(pady=5)
    
    # Add double-click event to history listbox to view full entry
    def on_history_double_click(event):
        selection = history_listbox.curselection()
        if selection:
            index = selection[0]
            # Calculate the actual index in the history list (reversed order in listbox)
            actual_index = len(history) - 1 - index
            if 0 <= actual_index < len(history):
                view_history_entry(history[actual_index], root)
    
    history_listbox.bind("<Double-1>", on_history_double_click)
    
    # Main area with agent blocks
    main_frame = tk.Frame(root, bg="#ffffff")
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)
    
    tk.Label(main_frame, text="Todos os Agentes", font=("Montserrat", 18, "bold"), bg="#ffffff", fg="#333333").pack(anchor="w")
    
    blocks_frame = tk.Frame(main_frame, bg="#ffffff")
    blocks_frame.pack(expand=True, fill="both")
    
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
    
    # Configure grid for blocks
    for i in range(4):  # 4 rows
        blocks_frame.grid_rowconfigure(i, weight=1)
    for j in range(3):  # 3 columns
        blocks_frame.grid_columnconfigure(j, weight=1)
    
    # Create agent blocks
    for idx, (agent_name, description) in enumerate(agents):
        row = idx // 3
        col = idx % 3
        create_agent_block(blocks_frame, agent_name, description, row, col, history_listbox, root, history)
    
    # Function to view a single history entry
    def view_history_entry(entry, root):
        entry_window = tk.Toplevel(root)
        entry_window.title("Detalhes da Conversa")
        entry_window.geometry("600x400")
        entry_window.configure(bg="#f5f5f5")
        
        detail_text = scrolledtext.ScrolledText(entry_window, font=("Montserrat", 12), bg="#ffffff")
        detail_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        if isinstance(entry, dict):
            timestamp = entry.get("timestamp", "Horário desconhecido")
            agent = entry.get("agent", "Agente desconhecido")
            user_input = entry.get("input", "")
            response = entry.get("response", "")
            
            detail_text.insert(tk.END, f"Data/Hora: {timestamp}\n", "header")
            detail_text.insert(tk.END, f"Agente: {agent}\n\n", "header")
            detail_text.insert(tk.END, f"Pergunta:\n{user_input}\n\n", "input")
            detail_text.insert(tk.END, f"Resposta:\n{response}\n", "response")
        else:
            detail_text.insert(tk.END, entry)
        
        detail_text.tag_configure("header", foreground="#2196F3", font=("Montserrat", 12, "bold"))
        detail_text.tag_configure("input", foreground="#333333")
        detail_text.tag_configure("response", foreground="#666666")
        detail_text.config(state="disabled")
        
        # Button frame
        button_frame = tk.Frame(entry_window, bg="#f5f5f5")
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="Fechar",
            command=entry_window.destroy,
            font=("Montserrat", 10, "bold"),
            bg="#2196F3",
            fg="white",
            bd=0,
            padx=15,
            pady=5
        ).pack(side="left", padx=10)
        
        # Add copy button for response
        if isinstance(entry, dict) and entry.get("response"):
            tk.Button(
                button_frame,
                text="Copiar Resposta",
                command=lambda: copy_to_clipboard(entry.get("response", ""), root),
                font=("Montserrat", 10, "bold"),
                bg="#4CAF50",
                fg="white",
                bd=0,
                padx=15,
                pady=5
            ).pack(side="left", padx=10)
    
    # Bind ESC key to quit
    root.bind("<Escape>", lambda e: root.quit())
    
    # Check API key
    check_api_key(root)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()