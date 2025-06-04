import tkinter as tk
from tkinter import scrolledtext


def criar_widgets(self):
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

    self.entry_quantidade = tk.Entry(
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
