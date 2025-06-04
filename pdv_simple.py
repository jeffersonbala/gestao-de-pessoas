from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox, scrolledtext
from settings import ARQUIVO_VENDAS, CAMINHO_IMAGEM
from manage_data import salvar_vendas, carregar_vendas

class PDVApp:
    def __init__(self, master):
        self.master = master
        master.title("PDV Simples")
        master.geometry("500x700")
        master.minsize(400, 600)
        master.resizable(True, True)

        # Produtos e preços
        self.produtos = {
            "Cupcake": 3.50,
            "Doce Especial": 5.00
        }

        self.vendas_registradas = carregar_vendas()
        self.numero_atendimento = self._get_proximo_numero_atendimento()
        self.quantidade_itens = tk.IntVar(value=1)
        self.total_venda = tk.DoubleVar(value=0.0)
        self.metodo_pagamento = tk.StringVar(value="")
        self.produto_selecionado = tk.StringVar(value="Cupcake")  # Produto padrão

        # Carrega imagem topo
        try:
            imagem_topo = Image.open(CAMINHO_IMAGEM)
            imagem_topo = imagem_topo.resize((500, 100), Image.Resampling.LANCZOS)
            self.foto_topo = ImageTk.PhotoImage(imagem_topo)
            self.label_topo = tk.Label(master, image=self.foto_topo)
            self.label_topo.pack(pady=10)
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")

        self.frame_widgets = tk.Frame(master, bg='#f4f4f9', bd=5, relief="solid", padx=10, pady=10)
        self.frame_widgets.pack(padx=20, fill="both", expand=True)

        self.criar_widgets()
        self._atualizar_lista_vendas()
        self._atualizar_total_venda()

    def _get_proximo_numero_atendimento(self):
        if self.vendas_registradas:
            return max(venda.get('numero_atendimento', 0) for venda in self.vendas_registradas) + 1
        return 1

    def _on_quantidade_change(self, *args):
        self._atualizar_total_venda()

    def _on_produto_change(self, *args):
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
            produto = self.produto_selecionado.get()
            preco_unitario = self.produtos[produto]
            valor_final_venda = qty * preco_unitario
        except tk.TclError:
            messagebox.showwarning("Erro", "Quantidade inválida.")
            return

        venda = {
            "numero_atendimento": self.numero_atendimento,
            "quantidade_itens": qty,
            "produto": produto,
            "valor_total": valor_final_venda,
            "metodo_pagamento": metodo
        }

        self.vendas_registradas.append(venda)
        salvar_vendas(self.vendas_registradas)

        messagebox.showinfo(
            "Venda Registrada",
            f"Venda de {qty}x {produto}(s) totalizando R$ {valor_final_venda:.2f} para o Cliente {self.numero_atendimento} via {metodo}."
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
            try:
                self.lista_vendas_text.insert(
                    tk.END,
                    f"Cliente {venda['numero_atendimento']}: {venda['quantidade_itens']}x {venda['produto']} - "
                    f"R$ {venda['valor_total']:.2f} ({venda['metodo_pagamento']})\n"
                )
            except KeyError as e:
                print(f"Venda ignorada por falta da chave: {e} -> {venda}")
        self.lista_vendas_text.config(state=tk.DISABLED)

    def _atualizar_total_venda(self):
        try:
            qty = self.quantidade_itens.get()
            if qty < 1:
                qty = 1
                self.quantidade_itens.set(1)
            produto = self.produto_selecionado.get()
            preco_unitario = self.produtos[produto]
            calculated_total = qty * preco_unitario
            self.total_venda.set(calculated_total)
            self.label_total_venda.config(text=f"Total: R$ {calculated_total:.2f}")
        except tk.TclError:
            self.total_venda.set(0.00)
            self.label_total_venda.config(text="Total: R$ 0.00 (Inválido)")

    def criar_widgets(self):
        # Atendimento
        self.label_atendimento = tk.Label(self.frame_widgets, text=f"Atendimento: {self.numero_atendimento}", bg="#f4f4f9", font=("Arial", 14, "bold"))
        self.label_atendimento.pack(pady=(5, 10))

        # Produto
        tk.Label(self.frame_widgets, text="Selecione o Produto:", bg="#f4f4f9", font=("Arial", 12)).pack()
        produto_menu = tk.OptionMenu(self.frame_widgets, self.produto_selecionado, *self.produtos.keys())
        produto_menu.config(font=("Arial", 12), bg="#ffffff")
        produto_menu.pack(pady=5)
        self.produto_selecionado.trace_add("write", self._on_produto_change)

        # Quantidade
        tk.Label(self.frame_widgets, text="Quantidade de Itens:", bg="#f4f4f9", font=("Arial", 12)).pack()
        self.spinbox_quantidade = tk.Spinbox(self.frame_widgets, from_=1, to=100, textvariable=self.quantidade_itens, width=5, font=("Arial", 12))
        self.spinbox_quantidade.pack(pady=5)
        self.quantidade_itens.trace_add("write", self._on_quantidade_change)

        # Total
        self.label_total_venda = tk.Label(self.frame_widgets, text=f"Total: R$ {self.total_venda.get():.2f}", bg="#f4f4f9", font=("Arial", 12, "bold"))
        self.label_total_venda.pack(pady=15)

        # Método de pagamento
        self.label_metodo_selecionado = tk.Label(self.frame_widgets, text="Método selecionado: Nenhum", bg="#f4f4f9", font=("Arial", 12))
        self.label_metodo_selecionado.pack(pady=5)

        frame_botoes = tk.Frame(self.frame_widgets, bg="#f4f4f9")
        frame_botoes.pack(pady=10)
        for metodo in ["Dinheiro", "Pix"]:
            btn = tk.Button(frame_botoes, text=metodo, command=lambda m=metodo: self._selecionar_metodo(m),
                            bg="#4CAF50", fg="white", font=("Arial", 12), relief="flat", width=10)
            btn.pack(side="left", padx=5)

        # Botão registrar
        btn_registrar = tk.Button(self.frame_widgets, text="Registrar Venda", command=self._registrar_venda,
                                  bg="#4CAF50", fg="white", font=("Arial", 14), relief="flat", width=20)
        btn_registrar.pack(pady=20)

        # Lista de vendas
        tk.Label(self.frame_widgets, text="Vendas Registradas:", bg="#f4f4f9", font=("Arial", 12, "bold")).pack(pady=(10, 0))
        self.lista_vendas_text = scrolledtext.ScrolledText(self.frame_widgets, height=10, state=tk.DISABLED, font=("Arial", 12), wrap=tk.WORD)
        self.lista_vendas_text.pack(fill="both", expand=True, padx=5, pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = PDVApp(root)
    root.mainloop()
