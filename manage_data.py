import json
import os
from tkinter import messagebox
import tkinter as tk

from settings import ARQUIVO_VENDAS


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

def atualizar_total_venda(nova_venda):
    vendas = carregar_vendas()
    vendas.append(nova_venda)
    salvar_vendas(vendas)