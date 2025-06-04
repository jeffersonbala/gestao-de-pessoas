from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox, scrolledtext
from settings import ARQUIVO_VENDAS, VALOR_POR_ITEM, CAMINHO_IMAGEM
from manage_data import salvar_vendas, carregar_vendas
from gui import criar_widgets

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

        # Widgets
        self.criar_widgets()
        self._atualizar_lista_vendas()
        self._atualizar_total_venda()

    def _get_proximo_numero_atendimento(self):
        if self.vendas_registradas:
            return max(venda.get('numero_atendimento', 0) for venda in self.vendas_registradas) + 1
        return 1

    def _on_quantidade_change(self, *args):
        self._atualizar_total_venda()

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

    def criar_widgets(self):
        # Atendimento
        self.label_atendimento = tk.Label(self.frame_widgets, text=f"Atendimento: {self.numero_atendimento}", bg="#ffffff", font=("Arial", 14))
        self.label_atendimento.pack(pady=(10, 5))

        # Quantidade de itens
        tk.Label(self.frame_widgets, text="Quantidade de Itens:", bg="#ffffff").pack()
        self.spinbox_quantidade = tk.Spinbox(self.frame_widgets, from_=1, to=100, textvariable=self.quantidade_itens, width=5)
        self.spinbox_quantidade.pack(pady=5)
        self.quantidade_itens.trace_add("write", self._on_quantidade_change)

        # Total da venda
        self.label_total_venda = tk.Label(self.frame_widgets, text=f"Total: R$ {self.total_venda.get():.2f}", bg="#ffffff", font=("Arial", 12, "bold"))
        self.label_total_venda.pack(pady=10)

        # Métodos de pagamento
        self.label_metodo_selecionado = tk.Label(self.frame_widgets, text="Método selecionado: Nenhum", bg="#ffffff")
        self.label_metodo_selecionado.pack(pady=5)

        frame_botoes = tk.Frame(self.frame_widgets, bg="#ffffff")
        frame_botoes.pack(pady=5)
        for metodo in ["Dinheiro", "Pix"]:
            btn = tk.Button(frame_botoes, text=metodo, command=lambda m=metodo: self._selecionar_metodo(m))
            btn.pack(side="left", padx=5)

        # Botão registrar venda
        btn_registrar = tk.Button(self.frame_widgets, text="Registrar Venda", command=self._registrar_venda, bg="green", fg="white")
        btn_registrar.pack(pady=15)

        # Lista de vendas registradas
        tk.Label(self.frame_widgets, text="Vendas Registradas:", bg="#ffffff", font=("Arial", 12, "bold")).pack(pady=(10, 0))
        self.lista_vendas_text = scrolledtext.ScrolledText(self.frame_widgets, height=10, state=tk.DISABLED)
        self.lista_vendas_text.pack(fill="both", expand=True, padx=5, pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = PDVApp(root)
    root.mainloop()
