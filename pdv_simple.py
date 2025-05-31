import tkinter as tk
from tkinter import messagebox, scrolledtext, Entry
import json
import os

# --- Configurações e Funções de Persistência ---
ARQUIVO_VENDAS = 'vendas_pdv.json'
VALOR_POR_ITEM = 5.00 # Definimos o valor por item aqui
CAMINHO_IMAGEM = 'logo.jpeg'  # Renomeie sua imagem se necessário

def carregar_vendas():
    """Carrega as vendas do arquivo JSON."""
    if os.path.exists(ARQUIVO_VENDAS):
        try:
            with open(ARQUIVO_VENDAS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            messagebox.showwarning("Aviso", "Arquivo de vendas corrompido ou vazio. Iniciando com vendas vazias.")
            return []
    return []

def salvar_vendas(vendas):
    """Salva as vendas no arquivo JSON."""
    with open(ARQUIVO_VENDAS, 'w', encoding='utf-8') as f:
        json.dump(vendas, f, indent=4, ensure_ascii=False)

# --- Classe Principal do Aplicativo PDV ---
class PDVApp:
    def __init__(self, master):
        self.master = master
        master.title("PDV Simples")
        # master.geometry("400x650") # Você pode remover esta linha ou ajustar o tamanho inicial
        master.resizable(True, True) # Permite redimensionar (e maximizar) a janela
        # Se quiser iniciar em tela cheia, use: master.attributes('-fullscreen', True)

        self.vendas_registradas = carregar_vendas()
        self.valor_por_item = VALOR_POR_ITEM # Usa o valor definido globalmente

        self.numero_atendimento = self._get_proximo_numero_atendimento()

        # Variáveis Tkinter para a quantidade e o total da venda
        self.quantidade_itens = tk.IntVar(value=1) # Começa com 1 item por padrão
        self.total_venda = tk.DoubleVar(value=self.valor_por_item) # Total inicial

        self._criar_widgets()
        self._atualizar_lista_vendas()
        self._atualizar_total_venda()


    def _get_proximo_numero_atendimento(self):
        """Determina o próximo número de atendimento baseado nas vendas existentes."""
        if self.vendas_registradas:
            return max(venda.get('numero_atendimento', 0) for venda in self.vendas_registradas) + 1
        return 1

    def _criar_widgets(self):
        """Cria e posiciona todos os elementos da interface."""

        # Frame para o número de atendimento
        frame_atendimento = tk.Frame(self.master, bd=2, relief="groove", padx=10, pady=10)
        frame_atendimento.pack(pady=10)

        self.label_atendimento = tk.Label(frame_atendimento,
                                          text=f"Atendimento: {self.numero_atendimento}",
                                          font=("Arial", 20, "bold"), fg="blue")
        self.label_atendimento.pack()

        # --- NOVA SEÇÃO: Quantidade de Itens ---
        frame_itens = tk.Frame(self.master, bd=2, relief="groove", padx=10, pady=10)
        frame_itens.pack(pady=10)

        tk.Label(frame_itens, text="Quantidade de Itens:", font=("Arial", 12)).pack(pady=5)

        # Entry para a quantidade
        self.entry_quantidade = Entry(frame_itens, textvariable=self.quantidade_itens,
                                      font=("Arial", 14), width=5, justify='center')
        self.entry_quantidade.pack(pady=5)
        self.quantidade_itens.trace_add("write", self._on_quantidade_change)

        # Label para mostrar o total da venda (será atualizado dinamicamente)
        self.label_total_venda = tk.Label(frame_itens,
                                          text=f"Total: R$ {0.00:.2f}",
                                          font=("Arial", 16, "bold"), fg="purple")
        self.label_total_venda.pack(pady=5)
        # --- FIM NOVA SEÇÃO ---

        # Frame para os botões de pagamento
        frame_pagamento = tk.Frame(self.master, bd=2, relief="groove", padx=10, pady=10)
        frame_pagamento.pack(pady=10)

        tk.Label(frame_pagamento, text="Método de Pagamento:", font=("Arial", 12)).pack(pady=5)

        self.metodo_pagamento = tk.StringVar(value="") # Variável para guardar a escolha do método

        self.btn_dinheiro = tk.Button(frame_pagamento, text="Dinheiro",
                                      command=lambda: self._selecionar_metodo("Dinheiro"),
                                      font=("Arial", 14), width=15, height=2)
        self.btn_dinheiro.pack(pady=5)

        self.btn_pix = tk.Button(frame_pagamento, text="Pix",
                                 command=lambda: self._selecionar_metodo("Pix"),
                                 font=("Arial", 14), width=15, height=2)
        self.btn_pix.pack(pady=5)

        # Rótulo para mostrar o método selecionado
        self.label_metodo_selecionado = tk.Label(frame_pagamento, text="Método selecionado: Nenhum",
                                                font=("Arial", 10), fg="gray")
        self.label_metodo_selecionado.pack(pady=5)

        # Botão Registrar Venda
        self.btn_registrar = tk.Button(self.master, text="Registrar Venda",
                                      command=self._registrar_venda,
                                      font=("Arial", 16, "bold"), bg="green", fg="white",
                                      padx=20, pady=10)
        self.btn_registrar.pack(pady=20)

        # Área para exibir vendas registradas
        tk.Label(self.master, text="Vendas Registradas:", font=("Arial", 12)).pack(pady=5)
        # --- MUDANÇA AQUI: expand=True e fill="both" ---
        self.lista_vendas_text = scrolledtext.ScrolledText(self.master, width=40, height=10,
                                                        font=("Courier New", 10), wrap=tk.WORD)
        self.lista_vendas_text.pack(pady=10, padx=10, expand=True, fill="both")
        # --- FIM DA MUDANÇA ---
        self.lista_vendas_text.config(state=tk.DISABLED) # Impede edição manual

    def _on_quantidade_change(self, *args):
        """Chamado quando a quantidade de itens é alterada."""
        self._atualizar_total_venda()

    def _atualizar_total_venda(self):
        """Calcula e atualiza o rótulo do valor total da venda."""
        try:
            qty = self.quantidade_itens.get()
            if qty < 1:
                qty = 1 # Garante que a quantidade mínima seja 1
                self.quantidade_itens.set(1) # Atualiza o campo de entrada
            
            calculated_total = qty * self.valor_por_item
            self.total_venda.set(calculated_total)
            self.label_total_venda.config(text=f"Total: R$ {calculated_total:.2f}")
        except tk.TclError: # Caso o usuário digite algo não numérico
            self.total_venda.set(0.00)
            self.label_total_venda.config(text="Total: R$ 0.00 (Inválido)")


    def _selecionar_metodo(self, metodo):
        """Atualiza a variável do método de pagamento e o rótulo."""
        self.metodo_pagamento.set(metodo)
        self.label_metodo_selecionado.config(text=f"Método selecionado: {metodo}")

    def _registrar_venda(self):
        """Registra a venda e atualiza a interface."""
        metodo = self.metodo_pagamento.get()
        if not metodo:
            messagebox.showwarning("Atenção", "Por favor, selecione um método de pagamento (Dinheiro ou Pix).")
            return

        try:
            qty = self.quantidade_itens.get()
            if qty < 1:
                messagebox.showwarning("Erro", "A quantidade de itens deve ser pelo menos 1.")
                return
            
            valor_final_venda = qty * self.valor_por_item
        except tk.TclError:
            messagebox.showwarning("Erro", "Quantidade de itens inválida. Digite um número inteiro.")
            return

        venda = {
            "numero_atendimento": self.numero_atendimento,
            "quantidade_itens": qty, # Salva a quantidade de itens
            "valor_total": valor_final_venda,
            "metodo_pagamento": metodo
        }
        self.vendas_registradas.append(venda)
        salvar_vendas(self.vendas_registradas)

        messagebox.showinfo("Venda Registrada",
                            f"Venda de {qty} item(s) totalizando R$ {valor_final_venda:.2f} para o Cliente {self.numero_atendimento} via {metodo}.")

        self._atualizar_lista_vendas()
        self.numero_atendimento += 1
        self.label_atendimento.config(text=f"Atendimento: {self.numero_atendimento}")
        self.metodo_pagamento.set("") # Limpa a seleção do método
        self.label_metodo_selecionado.config(text="Método selecionado: Nenhum")
        self.quantidade_itens.set(1) # Reseta a quantidade para 1 para a próxima venda

    def _atualizar_lista_vendas(self):
        """Atualiza a área de texto com as vendas registradas."""
        self.lista_vendas_text.config(state=tk.NORMAL) # Habilita para edição
        self.lista_vendas_text.delete(1.0, tk.END) # Limpa o conteúdo atual

        for venda in self.vendas_registradas:
            quantidade_itens = venda.get('quantidade_itens', 1)
            valor_total = venda.get('valor_total', 0.00)
            metodo_pagamento = venda.get('metodo_pagamento', 'Desconhecido')

            self.lista_vendas_text.insert(tk.END,
                f"Cliente {venda['numero_atendimento']}: {quantidade_itens} item(s) - R$ {valor_total:.2f} ({metodo_pagamento})\n")

        self.lista_vendas_text.config(state=tk.DISABLED) # Desabilita novamente

# --- Execução do Aplicativo ---
if __name__ == "__main__":
    root = tk.Tk() # Cria a janela principal do Tkinter
    app = PDVApp(root) # Instancia a classe do seu aplicativo
    root.mainloop() # Inicia o loop principal da interface