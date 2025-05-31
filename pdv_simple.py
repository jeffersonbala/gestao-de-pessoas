from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox, scrolledtext, Entry
import json
import os

ARQUIVO_VENDAS = 'vendas_pdv.json'
VALOR_POR_ITEM = 5.00
CAMINHO_IMAGEM = 'logo.jpeg'  # imagem do topo (banner)

def carregar_vendas():
    if os.path.exists(ARQUIVO_VENDAS):
        try:
            with open(ARQUIVO_VENDAS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            messagebox.showwarning("Aviso", "Arquivo corrompido. Começando vazio.")
            return []
    return []

def salvar_vendas(vendas):
    with open(ARQUIVO_VENDAS, 'w', encoding='utf-8') as f:
        json.dump(vendas, f, indent=4, ensure_ascii=False)

class PDVApp:
    def __init__(self, master):
        self.master = master
        master.title("PDV Simples")
        master.geometry("500x700")
        master.minsize(400, 600)
        master.resizable(True, True)

        self.vendas_registradas = carregar_vendas()
        self.valor_por_item = VALOR_POR_ITEM
        self.numero_atendimento = self._get_proximo_numero_atendimento()
        self.quantidade_itens = tk.IntVar(value=1)
        self.total_venda = tk.DoubleVar(value=self.valor_por_item)
        self.metodo_pagamento = tk.StringVar(value="")

        # Carrega imagem do topo (banner)
        imagem_topo = Image.open(CAMINHO_IMAGEM)
        imagem_topo = imagem_topo.resize((500, 100), Image.Resampling.LANCZOS)
        self.foto_topo = ImageTk.PhotoImage(imagem_topo)
        self.label_topo = tk.Label(master, image=self.foto_topo)
        self.label_topo.pack(pady=10)

        # Frame principal (fundo branco) para widgets
        self.frame_widgets = tk.Frame(master, bg='#ffffff', bd=2, relief="groove")
        self.frame_widgets.pack(padx=10, fill="both", expand=True)

        self._criar_widgets()
        self._atualizar_lista_vendas()
        self._atualizar_total_venda()

    def _get_proximo_numero_atendimento(self):
        if self.vendas_registradas:
            return max(venda.get('numero_atendimento', 0) for venda in self.vendas_registradas) + 1
        return 1

    def _criar_widgets(self):
        # Seção de Atendimento
        frame_atendimento = tk.Frame(self.frame_widgets, bg='#ffffff', pady=5)
        frame_atendimento.pack(fill='x')
        self.label_atendimento = tk.Label(
            frame_atendimento,
            text=f"Atendimento: {self.numero_atendimento}",
            font=("Arial", 20, "bold"),
            fg="blue",
            bg='#ffffff'
        )
        self.label_atendimento.pack()

        # Seção de Quantidade de Itens
        frame_itens = tk.Frame(self.frame_widgets, bg='#ffffff', pady=5)
        frame_itens.pack(fill='x')

        tk.Label(
            frame_itens,
            text="Quantidade de Itens:",
            font=("Arial", 12),
            bg='#ffffff'
        ).pack(anchor='w', padx=5)

        self.entry_quantidade = Entry(
            frame_itens,
            textvariable=self.quantidade_itens,
            font=("Arial", 14),
            width=5,
            justify='center'
        )
        self.entry_quantidade.pack(padx=5, pady=5)
        self.quantidade_itens.trace_add("write", self._on_quantidade_change)

        self.label_total_venda = tk.Label(
            frame_itens,
            text=f"Total: R$ {0.00:.2f}",
            font=("Arial", 16, "bold"),
            fg="purple",
            bg='#ffffff'
        )
        self.label_total_venda.pack(padx=5, pady=5)

        # Seção de Método de Pagamento
        frame_pagamento = tk.Frame(self.frame_widgets, bg='#ffffff', pady=5)
        frame_pagamento.pack(fill='x')

        tk.Label(
            frame_pagamento,
            text="Método de Pagamento:",
            font=("Arial", 12),
            bg='#ffffff'
        ).pack(anchor='w', padx=5, pady=5)

        self.btn_dinheiro = tk.Button(
            frame_pagamento,
            text="Dinheiro",
            command=lambda: self._selecionar_metodo("Dinheiro"),
            font=("Arial", 14),
            width=15,
            height=2
        )
        self.btn_dinheiro.pack(pady=5)

        self.btn_pix = tk.Button(
            frame_pagamento,
            text="Pix",
            command=lambda: self._selecionar_metodo("Pix"),
            font=("Arial", 14),
            width=15,
            height=2
        )
        self.btn_pix.pack(pady=5)

        self.label_metodo_selecionado = tk.Label(
            frame_pagamento,
            text="Método selecionado: Nenhum",
            font=("Arial", 10),
            fg="gray",
            bg='#ffffff'
        )
        self.label_metodo_selecionado.pack(pady=5)

        # Botão Registrar Venda
        self.btn_registrar = tk.Button(
            self.frame_widgets,
            text="Registrar Venda",
            command=self._registrar_venda,
            font=("Arial", 16, "bold"),
            bg="green",
            fg="white",
            padx=20,
            pady=10
        )
        self.btn_registrar.pack(pady=10)

        # Seção de Vendas Registradas
        tk.Label(
            self.frame_widgets,
            text="Vendas Registradas:",
            font=("Arial", 12),
            bg='#ffffff'
        ).pack(anchor='w', padx=5)

        self.lista_vendas_text = scrolledtext.ScrolledText(
            self.frame_widgets,
            width=40,
            height=10,
            font=("Courier New", 10),
            wrap=tk.WORD
        )
        self.lista_vendas_text.pack(padx=5, pady=10, expand=True, fill="both")
        self.lista_vendas_text.config(state=tk.DISABLED)

    def _on_quantidade_change(self, *args):
        self._atualizar_total_venda()

    def _atualizar_total_venda(self):
        try:
            qty = self.quantidade_itens.get()
            if qty < 1:
                qty = 1
                self.quantidade_itens.set(1)
            calculated_total = qty * self.valor_por_item
            self.total_venda.set(calculated_total)
            self.label_total_venda.config(text=f"Total: R$ {calculated_total:.2f}")
        except tk.TclError:
            self.total_venda.set(0.00)
            self.label_total_venda.config(text="Total: R$ 0.00 (Inválido)")

    def _selecionar_metodo(self, metodo):
        self.metodo_pagamento.set(metodo)
        self.label_metodo_selecionado.config(text=f"Método selecionado: {metodo}")

    def _registrar_venda(self):
        metodo = self.metodo_pagamento.get()
        if not metodo:
            messagebox.showwarning("Atenção", "Selecione um método de pagamento.")
            return

        try:
            qty = self.quantidade_itens.get()
            if qty < 1:
                messagebox.showwarning("Erro", "Quantidade deve ser pelo menos 1.")
                return
            valor_final_venda = qty * self.valor_por_item
        except tk.TclError:
            messagebox.showwarning("Erro", "Quantidade inválida.")
            return

        venda = {
            "numero_atendimento": self.numero_atendimento,
            "quantidade_itens": qty,
            "valor_total": valor_final_venda,
            "metodo_pagamento": metodo
        }
        self.vendas_registradas.append(venda)
        salvar_vendas(self.vendas_registradas)

        messagebox.showinfo(
            "Venda Registrada",
            f"Venda de {qty} item(s) totalizando R$ {valor_final_venda:.2f} para o Cliente {self.numero_atendimento} via {metodo}."
        )

        self._atualizar_lista_vendas()
        self.numero_atendimento += 1
        self.label_atendimento.config(text=f"Atendimento: {self.numero_atendimento}")
        self.metodo_pagamento.set("")
        self.label_metodo_selecionado.config(text="Método selecionado: Nenhum")
        self.quantidade_itens.set(1)

    def _atualizar_lista_vendas(self):
        self.lista_vendas_text.config(state=tk.NORMAL)
        self.lista_vendas_text.delete(1.0, tk.END)
        for venda in self.vendas_registradas:
            quantidade_itens = venda.get('quantidade_itens', 1)
            valor_total = venda.get('valor_total', 0.00)
            metodo_pagamento = venda.get('metodo_pagamento', 'Desconhecido')
            self.lista_vendas_text.insert(
                tk.END,
                f"Cliente {venda['numero_atendimento']}: {quantidade_itens} item(s) - R$ {valor_total:.2f} ({metodo_pagamento})\n"
            )
        self.lista_vendas_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = PDVApp(root)
    root.mainloop()
